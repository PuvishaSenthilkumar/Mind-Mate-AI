"""
Centralized app configuration.
All secrets/keys are read from environment variables (.env) — never hard-coded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict # pyright: ignore[reportMissingImports]


class Settings(BaseSettings):
    # Database
    # Use SQLite by default for local development. Override with a .env to use Postgres.
    DATABASE_URL: str = "sqlite:///./mindmate.db"

    # JWT
    JWT_SECRET_KEY: str = "CHANGE_ME"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # AI provider
    AI_PROVIDER: str = "gemini"  # "gemini" | "anthropic" | "openai" | "mock"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    # App / CORS
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    ENVIRONMENT: str = "development"

    # Crisis / safety resources (fully configurable, never diagnostic)
    CRISIS_HOTLINE_NAME: str = "Global crisis support"
    CRISIS_HOTLINE_NUMBER: str = "Use local emergency services"
    CRISIS_TEXT_LINE: str = "Use a local crisis text service if available"
    CRISIS_INTERNATIONAL_URL: str = "https://findahelpline.com"

    # Email / SMTP
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = ""
    EMAILS_FROM_NAME: str = "MindMate AI"
    EMAIL_OTP_EXPIRE_MINUTES: int = 15

    # SMS / MSG91
    MSG91_AUTH_KEY: str = ""
    MSG91_SENDER_ID: str = "MNDMTE"
    MSG91_TEMPLATE_ID: str = ""
    SMS_OTP_EXPIRE_MINUTES: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
