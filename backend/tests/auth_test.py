import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.db import get_db
from backend.main import app
from backend.app.database import models
from backend.app.database.models import Base
from backend.app.security import create_email_token, get_password_hash

# --- Настраиваем in-memory SQLite для теста ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # для простоты файл, можно и "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Заменяем зависимость get_db на тестовую
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture
def test_user():
    """Создаём пользователя вручную в базе"""
    db = TestingSessionLocal()
    user = models.Player(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password"),
        is_verified=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


def test_verify_email(test_user):
    # Генерируем токен
    token = create_email_token({"sub": test_user.email})

    # Отправляем запрос
    response = client.get(f"/verify-email?token={token}")
    assert response.status_code == 200
    assert response.json()["message"] == "Email successfully verified"

    # Проверяем, что в базе юзер стал подтверждён
    db = TestingSessionLocal()
    user = db.query(models.Player).filter(models.Player.email == test_user.email).first()
    assert user.is_verified is True
    db.close()
