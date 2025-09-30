import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database import models
from backend.app.security import get_password_hash, create_access_token
from backend.main import app
from backend.app.database.db import get_db
from backend.app.database.models import Base


# Используем отдельную БД для тестов
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Фикстура для базы
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)   # создаём таблицы
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine) # чистим таблицы после теста


# Фикстура для клиента
@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture(scope="function")
def test_user_and_token(db):
    # создаём юзера
    user = models.Player(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_verified=True  # делаем сразу верифицированным
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # создаём токен
    token = create_access_token({"sub": user.email})
    return user, token