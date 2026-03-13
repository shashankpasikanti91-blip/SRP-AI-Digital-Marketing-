"""
AI Marketing OS - Configuration
Loads all environment variables and app settings.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Marketing OS"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"  # development | production | testing
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production-super-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/ai_marketing_os"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── CORS ──────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://app.aimarketingos.com",        "https://app.srpailabs.com",    ]

    # ── Email / SMTP ──────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "AI Marketing OS"
    SMTP_FROM_EMAIL: str = "noreply@aimarketingos.com"
    SMTP_TLS: bool = True

    # ── AI / OpenAI ───────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    AI_MODEL: str = "openai:gpt-4o"   # legacy pydantic-ai model string (kept for compatibility)
    AI_MAX_TOKENS: int = 2500
    AI_TEMPERATURE: float = 0.75

    # ── Model Router (centralized model selection) ────────────────────────
    # Set preferred provider: openrouter | openai
    # If openrouter, set OPENROUTER_API_KEY. If openai, set OPENAI_API_KEY.
    AI_PREFERRED_PROVIDER: str = "openrouter"       # openrouter | openai
    APP_URL: str = "https://app.srpailabs.com"  # sent as HTTP-Referer to OpenRouter

    # ── Creative Generation Feature Flags ────────────────────────────────
    # AI image generation is OFF by default. Enable only in premium flows.
    IMAGE_GENERATION_ENABLED: bool = False
    # If True, image generation is only available on pro/agency/enterprise plans
    IMAGE_GENERATION_PREMIUM_ONLY: bool = True

    # ── Usage Tracking ────────────────────────────────────────────────────
    USAGE_TRACKING_ENABLED: bool = True
    USAGE_TRACKING_LOG_LEVEL: str = "all"   # all | errors_only | none

    # ── Social Media APIs ─────────────────────────────────────────────────
    FACEBOOK_ACCESS_TOKEN: str = ""
    FACEBOOK_PAGE_ID: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_ACCOUNT_ID: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_ORG_ID: str = ""

    # ── Multi-tenancy ─────────────────────────────────────────────────────
    DEFAULT_TENANT_ID: str = "default"

    # ── Rate Limiting ─────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()
