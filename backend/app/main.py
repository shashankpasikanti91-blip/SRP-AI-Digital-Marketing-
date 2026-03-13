"""
SRP Marketing OS — FastAPI Application Factory
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.database import create_tables
from app.routers import (
    ai_assistant,
    analytics,
    auth,
    crm,
    email_campaigns,
    leads,
    social,
    webhooks,
    notifications,
    settings as settings_router,
    # New AI-powered routers
    business,
    campaigns,
    content,
    conversations,
    followups,
    chatbot,
    agents,
    linkedin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    # Tables are created via Alembic migrations — skip auto-create to avoid
    # permission errors on restricted DB users (e.g. Supabase ats_user).
    # Uncomment the block below only for a fresh local dev DB with full DDL access.
    # if settings.APP_ENV in ("development", "testing"):
    #     await create_tables()
    yield
    # Cleanup on shutdown (close connections, etc.) handled by SQLAlchemy pool


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "SRP Marketing OS — Multi-tenant AI Marketing Automation Platform. "
            "Capture leads, manage CRM, schedule social posts, automate emails, and leverage AI."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── Exception Handlers ───────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────────────
    api_prefix = "/api/v1"
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(leads.router, prefix=api_prefix)
    app.include_router(crm.router, prefix=api_prefix)
    app.include_router(social.router, prefix=api_prefix)
    app.include_router(email_campaigns.router, prefix=api_prefix)
    app.include_router(ai_assistant.router, prefix=api_prefix)
    app.include_router(analytics.router, prefix=api_prefix)
    app.include_router(webhooks.router, prefix=api_prefix)
    app.include_router(notifications.router, prefix=api_prefix)
    app.include_router(settings_router.router, prefix=api_prefix)
    # New AI-powered routers
    app.include_router(business.router, prefix=api_prefix)
    app.include_router(campaigns.router, prefix=api_prefix)
    app.include_router(content.router, prefix=api_prefix)
    app.include_router(conversations.router, prefix=api_prefix)
    app.include_router(followups.router, prefix=api_prefix)
    app.include_router(chatbot.router, prefix=api_prefix)
    app.include_router(agents.router, prefix=api_prefix)
    app.include_router(linkedin.router, prefix=api_prefix)
    # Regional marketing — bilingual posters & brand profiles
    from app.routers import posters as posters_router
    app.include_router(posters_router.router, prefix=api_prefix)

    # Phase 14 — Global Localization + Multi-country Support
    from app.routers import localization as localization_router
    app.include_router(localization_router.router, prefix=api_prefix)

    # Phase 15 — Unified AI Creative Generation (locale-aware, plan-gated)
    from app.routers import creatives as creatives_router
    app.include_router(creatives_router.router, prefix=api_prefix)

    # ── Health Check ──────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "env": settings.APP_ENV,
        }

    return app


app = create_app()
