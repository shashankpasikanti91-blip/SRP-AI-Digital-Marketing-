"""Settings Router — tenant configuration management"""

import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.dependencies import DB, CurrentTenant

router = APIRouter(prefix="/settings", tags=["Settings"])


# ── Default settings structure ─────────────────────────────────────────────

DEFAULT_SETTINGS = {
    "branding": {
        "primary_color": "#6366f1",
        "accent_color": "#22c55e",
        "logo_url": None,
    },
    "notifications": {
        "email_new_lead": True,
        "email_deal_won": True,
        "email_campaign_complete": True,
        "browser_push": False,
    },
    "leads": {
        "auto_ai_score": True,
        "default_source": "website",
        "duplicate_check": True,
    },
    "social": {
        "default_platforms": ["facebook", "instagram", "linkedin"],
        "auto_publish": False,
        "approval_required": False,
    },
    "email": {
        "unsubscribe_footer": True,
        "track_opens": True,
        "track_clicks": True,
    },
    "crm": {
        "currency": "USD",
        "fiscal_year_start": 1,
        "deal_expiry_days": 90,
    },
    "ai": {
        "auto_classify_leads": True,
        "ai_model": "gpt-4o",
        "language": "en",
        "tone": "professional",
    },
    "integrations": {
        "facebook_connected": False,
        "instagram_connected": False,
        "linkedin_connected": False,
        "smtp_configured": False,
    },
}


class SettingsResponse(BaseModel):
    settings: Dict[str, Any]
    plan: str
    api_key: str
    webhook_url: str


class UpdateSettingsRequest(BaseModel):
    settings: Dict[str, Any] = Field(..., description="Partial settings object — deep-merged with existing")


@router.get("/", response_model=SettingsResponse)
async def get_settings(tenant: CurrentTenant):
    """Get all tenant settings with defaults filled in."""
    stored = {}
    if tenant.settings:
        try:
            stored = json.loads(tenant.settings)
        except (json.JSONDecodeError, TypeError):
            stored = {}

    # Deep merge with defaults
    merged = _deep_merge(DEFAULT_SETTINGS.copy(), stored)

    return SettingsResponse(
        settings=merged,
        plan=tenant.plan,
        api_key=tenant.api_key,
        webhook_url=f"/api/v1/webhooks/lead/{tenant.api_key}",
    )


@router.patch("/", response_model=SettingsResponse)
async def update_settings(payload: UpdateSettingsRequest, tenant: CurrentTenant, db: DB):
    """Update tenant settings — deep-merges provided values."""
    stored = {}
    if tenant.settings:
        try:
            stored = json.loads(tenant.settings)
        except (json.JSONDecodeError, TypeError):
            stored = {}

    updated = _deep_merge(stored, payload.settings)
    tenant.settings = json.dumps(updated)
    await db.flush()
    await db.refresh(tenant)

    merged = _deep_merge(DEFAULT_SETTINGS.copy(), updated)
    return SettingsResponse(
        settings=merged,
        plan=tenant.plan,
        api_key=tenant.api_key,
        webhook_url=f"/api/v1/webhooks/lead/{tenant.api_key}",
    )


@router.get("/integrations")
async def get_integration_status(tenant: CurrentTenant):
    """Check which integrations are configured."""
    from app.config import settings as app_settings
    return {
        "facebook": {
            "connected": bool(app_settings.FACEBOOK_ACCESS_TOKEN),
            "page_id": app_settings.FACEBOOK_PAGE_ID or None,
        },
        "instagram": {
            "connected": bool(app_settings.INSTAGRAM_ACCESS_TOKEN),
            "account_id": app_settings.INSTAGRAM_ACCOUNT_ID or None,
        },
        "linkedin": {
            "connected": bool(app_settings.LINKEDIN_ACCESS_TOKEN),
            "org_id": app_settings.LINKEDIN_ORG_ID or None,
        },
        "openai": {
            "connected": bool(app_settings.OPENAI_API_KEY),
            "model": app_settings.AI_MODEL,
        },
        "smtp": {
            "connected": bool(app_settings.SMTP_USER and app_settings.SMTP_PASSWORD),
            "host": app_settings.SMTP_HOST,
        },
    }


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
