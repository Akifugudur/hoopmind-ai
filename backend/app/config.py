from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    app_name: str = "HoopMind AI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://hoopmind:hoopmind123@localhost:5432/hoopminddb"
    postgres_user: str = "hoopmind"
    postgres_password: str = "hoopmind123"
    postgres_db: str = "hoopminddb"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # ML
    model_dir: str = "ml_models"
    secret_key: str = "dev-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
