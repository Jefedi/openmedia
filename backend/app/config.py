"""Configuration de l'application OpenMedia"""
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration principale de l'application"""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore"
    )

    # =============================================================================
    # GENERAL
    # =============================================================================
    PROJECT_NAME: str = "OpenMedia"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "info"

    # API
    API_V1_PREFIX: str = "/api/v1"

    # =============================================================================
    # DATABASE
    # =============================================================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    DATABASE_URL: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Construire l'URL de la base de données"""
        if isinstance(v, str) and v:
            return v

        return PostgresDsn.build(
            scheme="postgresql",
            username=info.data.get("POSTGRES_USER"),
            password=info.data.get("POSTGRES_PASSWORD"),
            host=info.data.get("POSTGRES_HOST", "db"),
            port=info.data.get("POSTGRES_PORT", 5432),
            path=f"{info.data.get('POSTGRES_DB', '')}",
        ).unicode_string()

    # Pool de connexions
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False

    # =============================================================================
    # REDIS
    # =============================================================================
    REDIS_PASSWORD: str
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    REDIS_URL: Optional[RedisDsn] = None

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_connection(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Construire l'URL Redis"""
        if isinstance(v, str) and v:
            return v

        password = info.data.get("REDIS_PASSWORD")
        host = info.data.get("REDIS_HOST", "redis")
        port = info.data.get("REDIS_PORT", 6379)
        db = info.data.get("REDIS_DB", 0)

        return f"redis://:{password}@{host}:{port}/{db}"

    # =============================================================================
    # MEILISEARCH
    # =============================================================================
    MEILI_URL: str = "http://search:7700"
    MEILI_MASTER_KEY: str

    # =============================================================================
    # SECURITY
    # =============================================================================
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("SECRET_KEY", "JWT_SECRET_KEY")
    @classmethod
    def validate_secret_keys(cls, v: str) -> str:
        """Valider que les clés secrètes sont suffisamment longues"""
        if len(v) < 32:
            raise ValueError("Les clés secrètes doivent faire au moins 32 caractères")
        return v

    # Password hashing
    PASSWORD_HASH_SCHEMES: List[str] = ["argon2", "bcrypt"]
    PASSWORD_MIN_LENGTH: int = 8

    # Login protection
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_DURATION: int = 900  # 15 minutes

    # =============================================================================
    # CORS
    # =============================================================================
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parser les origins CORS depuis string ou liste"""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("BACKEND_CORS_ORIGINS doit être une liste ou une string JSON")

    # =============================================================================
    # RATE LIMITING
    # =============================================================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    DEFAULT_API_KEY_RATE_LIMIT: int = 100  # Par heure
    DEFAULT_API_KEY_DAILY_LIMIT: int = 2000

    # =============================================================================
    # CELERY
    # =============================================================================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def assemble_celery_broker(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Construire l'URL du broker Celery"""
        if isinstance(v, str) and v:
            return v

        password = info.data.get("REDIS_PASSWORD")
        host = info.data.get("REDIS_HOST", "redis")
        port = info.data.get("REDIS_PORT", 6379)

        return f"redis://:{password}@{host}:{port}/1"

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def assemble_celery_backend(cls, v: Optional[str], info: ValidationInfo) -> str:
        """Construire l'URL du result backend Celery"""
        if isinstance(v, str) and v:
            return v

        password = info.data.get("REDIS_PASSWORD")
        host = info.data.get("REDIS_HOST", "redis")
        port = info.data.get("REDIS_PORT", 6379)

        return f"redis://:{password}@{host}:{port}/2"

    # =============================================================================
    # EXTERNAL APIs
    # =============================================================================
    TMDB_API_KEY: Optional[str] = None
    TMDB_API_READ_TOKEN: Optional[str] = None
    TRAKT_CLIENT_ID: Optional[str] = None
    TRAKT_CLIENT_SECRET: Optional[str] = None
    OMDB_API_KEY: Optional[str] = None

    # =============================================================================
    # EMAIL (Optionnel)
    # =============================================================================
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@openmedia.example"
    SMTP_TLS: bool = True

    # =============================================================================
    # MONITORING
    # =============================================================================
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: Optional[str] = None

    # =============================================================================
    # BACKUP
    # =============================================================================
    BACKUP_ENABLED: bool = False
    BACKUP_PATH: str = "/backups"
    BACKUP_RETENTION_DAYS: int = 30

    # =============================================================================
    # FIRST USER (Super Admin)
    # =============================================================================
    FIRST_SUPERUSER_EMAIL: str = "admin@openmedia.local"
    FIRST_SUPERUSER_PASSWORD: str  # Doit être défini dans .env

    # =============================================================================
    # PAGINATION
    # =============================================================================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # =============================================================================
    # IMPORTS
    # =============================================================================
    IMDB_DATASETS_PATH: str = "/data/imdb"


# Instance globale des settings
settings = Settings()
