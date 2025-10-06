from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./debug.db"  # дефолт на SQLite

    class Config:
        env_file = "../../.env"

settings = Settings()