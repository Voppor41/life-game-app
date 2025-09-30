import os
from dotenv import load_dotenv
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.app.config import settings

load_dotenv()

database_url = os.getenv("DATABASE_URL")
engine = create_engine(database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_database_url():

    if database_url:
        # Если есть не-ASCII символы в пароле, кодируем их
        if "postgresql" in database_url:
            # Разбираем URL и кодируем компоненты
            from urllib.parse import urlparse, urlunparse, quote

            parsed = urlparse(database_url)
            if parsed.password:
                # Кодируем пароль
                encoded_password = quote(parsed.password)
                # Собираем URL обратно
                netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"

                encoded_url = urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                return encoded_url

    return database_url or "sqlite:///./app.db"


SQLALCHEMY_DATABASE_URL = get_database_url()

print(f"Database URL: {SQLALCHEMY_DATABASE_URL}")  # Для отладки

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base = declarative_base()

except Exception as e:
    print(f"❌ Database connection error: {e}")
    # Fallback на SQLite если PostgreSQL недоступен
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
