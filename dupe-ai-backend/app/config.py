import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    ENV: str = os.getenv("ENV", "production")
    CORS_ALLOW_ORIGINS: str = os.getenv("CORS_ALLOW_ORIGINS", "*")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # DB
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()
    DB_SSLMODE: str = os.getenv("DB_SSLMODE", "").strip().lower()  # "", "disable", "require"

    # Redis / Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # IAP / Apple (server-side verification; wire later)
    APPSTORE_ISSUER_ID: str = os.getenv("APPSTORE_ISSUER_ID", "")
    APPSTORE_KEY_ID: str = os.getenv("APPSTORE_KEY_ID", "")
    APPSTORE_PRIVATE_KEY: str = os.getenv("APPSTORE_PRIVATE_KEY", "")
    APPSTORE_BUNDLE_ID: str = os.getenv("APPSTORE_BUNDLE_ID", "")
    APPSTORE_ENV: str = os.getenv("APPSTORE_ENV", "Sandbox")  # "Production" later

settings = Settings()
