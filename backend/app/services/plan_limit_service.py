"""
Plan Limit Service — SRP Marketing OS
=======================================

SaaS plan enforcement for multi-tenant billing control.

Plans:
  starter   — Entry-level limits
  pro       — Mid-tier limits
  agency    — High-volume agency limits
  enterprise — Unlimited (or very high limits)

Limits are checked BEFORE AI calls. If over limit, a 402/429 error is raised
so the tenant is prompted to upgrade.

Usage:
    from app.services.plan_limit_service import PlanLimitService
    await PlanLimitService.check_limit(db, tenant, "text_generation")
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException, status

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


# ── Plan Definitions ──────────────────────────────────────────────────────────

PLAN_LIMITS: dict[str, dict] = {
    "starter": {
        "text_generation":  50,      # per month
        "translation":      20,
        "image_generation": 0,       # not included in starter
        "creatives":        20,
        "description": "Starter plan: 50 AI text/month, 20 translations, no AI images.",
    },
    "pro": {
        "text_generation":  500,
        "translation":      200,
        "image_generation": 20,
        "creatives":        200,
        "description": "Pro plan: 500 AI text/month, 200 translations, 20 AI images.",
    },
    "agency": {
        "text_generation":  2000,
        "translation":      1000,
        "image_generation": 100,
        "creatives":        1000,
        "description": "Agency plan: 2,000 AI text/month, 1,000 translations, 100 AI images.",
    },
    "enterprise": {
        "text_generation":  99999,
        "translation":      99999,
        "image_generation": 99999,
        "creatives":        99999,
        "description": "Enterprise plan: effectively unlimited.",
    },
}

# Alias mapping for flexible plan naming
PLAN_ALIASES: dict[str, str] = {
    "free": "starter",
    "basic": "starter",
    "business": "pro",
    "professional": "pro",
    "enterprise": "enterprise",
    "unlimited": "enterprise",
}


def resolve_plan(plan_name: str) -> str:
    """Normalise plan name to one of our canonical plan keys."""
    name = (plan_name or "starter").lower().strip()
    return PLAN_ALIASES.get(name, name if name in PLAN_LIMITS else "starter")


def get_plan_limits(plan_name: str) -> dict:
    """Return limit dict for a plan."""
    canonical = resolve_plan(plan_name)
    return PLAN_LIMITS.get(canonical, PLAN_LIMITS["starter"])


class PlanLimitService:
    """
    Check and enforce plan-based usage limits.

    All methods are static/async.
    Raises HTTP 402 (Payment Required) if over limit.
    """

    @staticmethod
    async def check_limit(
        db: "AsyncSession",
        tenant: "Tenant",
        category: str,             # text_generation | translation | image_generation | creatives
        requested_count: int = 1,
    ) -> None:
        """
        Check if the tenant is within their monthly plan limits for the given category.

        Raises HTTPException 402 if over limit.
        Returns silently if within limits.
        """
        from app.services.usage_tracking_service import UsageTracker

        plan_name = getattr(tenant, "plan", "starter") or "starter"
        limits = get_plan_limits(plan_name)
        limit = limits.get(category, 0)

        if limit >= 99999:
            # Enterprise / unlimited — skip DB check
            return

        if limit == 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "plan_limit",
                    "message": f"Your {plan_name} plan does not include {category}. Please upgrade.",
                    "category": category,
                    "plan": plan_name,
                    "upgrade_required": True,
                },
            )

        # Get current month usage
        counts = await UsageTracker.get_tenant_monthly_counts(db, tenant.id)
        current = counts.get(category, 0)

        if current + requested_count > limit:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "error": "plan_limit_exceeded",
                    "message": (
                        f"Monthly limit reached for {category}. "
                        f"Used: {current}/{limit}. Upgrade your plan for more."
                    ),
                    "category": category,
                    "used": current,
                    "limit": limit,
                    "plan": plan_name,
                    "upgrade_required": True,
                },
            )

    @staticmethod
    async def get_usage_status(
        db: "AsyncSession",
        tenant: "Tenant",
    ) -> dict:
        """
        Return a full usage status dict for a tenant.
        Useful for dashboard widgets and admin views.
        """
        from app.services.usage_tracking_service import UsageTracker

        plan_name = getattr(tenant, "plan", "starter") or "starter"
        limits = get_plan_limits(plan_name)
        counts = await UsageTracker.get_tenant_monthly_counts(db, tenant.id)

        status_items = {}
        for category, limit in limits.items():
            if category == "description":
                continue
            used = counts.get(category, 0)
            status_items[category] = {
                "used": used,
                "limit": limit if limit < 99999 else None,
                "remaining": max(0, limit - used) if limit < 99999 else None,
                "percent_used": round((used / limit) * 100, 1) if limit > 0 and limit < 99999 else 0,
                "at_limit": used >= limit if limit < 99999 else False,
            }

        return {
            "plan": plan_name,
            "description": PLAN_LIMITS.get(resolve_plan(plan_name), {}).get("description", ""),
            "usage": status_items,
        }

    @staticmethod
    def is_image_generation_enabled(tenant: "Tenant") -> bool:
        """
        Returns True if the tenant's plan includes AI image generation.
        Used alongside the IMAGE_GENERATION_ENABLED feature flag.
        """
        from app.config import settings
        # Global feature flag must be on
        if not getattr(settings, "IMAGE_GENERATION_ENABLED", False):
            return False
        # Plan must include it
        plan_name = getattr(tenant, "plan", "starter") or "starter"
        limits = get_plan_limits(plan_name)
        return limits.get("image_generation", 0) > 0

    @staticmethod
    def list_plans() -> list[dict]:
        """Return all plan definitions for display."""
        result = []
        for plan_key, limits in PLAN_LIMITS.items():
            result.append({
                "plan": plan_key,
                "description": limits.get("description", ""),
                "limits": {k: v for k, v in limits.items() if k != "description"},
            })
        return result
