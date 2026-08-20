from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Enterprise Application Settings powered by Pydantic v2 BaseSettings.
    Automatically parses environment variables and applies strict type validation.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # General Project Info
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    PROJECT_NAME: str = "DataPulse AI - Enterprise Data Intelligence Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database Configuration (PostgreSQL)
    POSTGRES_USER: str = "datapulse_user"
    POSTGRES_PASSWORD: str = "datapulse_password"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "datapulse_warehouse"

    ASYNC_DATABASE_URL: str = (
        "postgresql+asyncpg://datapulse_user:datapulse_password@localhost:5432/datapulse_warehouse"
    )
    SYNC_DATABASE_URL: str = (
        "postgresql+psycopg2://datapulse_user:datapulse_password@localhost:5432/datapulse_warehouse"
    )

    # File Storage Paths (Raw, Processed, Quarantine)
    STORAGE_RAW_PATH: Path = Path("./data/raw")
    STORAGE_PROCESSED_PATH: Path = Path("./data/processed")
    STORAGE_QUARANTINE_PATH: Path = Path("./data/quarantine")

    # Enterprise JWT Security
    SECRET_KEY: str = "super_secret_jwt_key_change_in_production_32bytes_min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # LLM Settings (OpenAI / Ollama)
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.0

    # Airflow Integration
    AIRFLOW_HOST: str = "http://localhost:8080"
    AIRFLOW_USER: str = "admin"
    AIRFLOW_PASSWORD: str = "admin"

    def initialize_storage_directories(self) -> None:
        """Ensure all required data persistence directories exist at runtime."""
        self.STORAGE_RAW_PATH.mkdir(parents=True, exist_ok=True)
        self.STORAGE_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
        self.STORAGE_QUARANTINE_PATH.mkdir(parents=True, exist_ok=True)


# Global Singleton Settings Instance
settings = Settings()
settings.initialize_storage_directories()
