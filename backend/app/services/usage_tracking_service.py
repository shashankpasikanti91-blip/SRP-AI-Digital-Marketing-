"""
Usage Tracking Service — SRP Marketing OS
==========================================

Tracks every AI call per tenant for:
  - Billing accuracy
  - Cost visibility
  - Per-feature analytics
  - SaaS plan enforcement data

All AI calls (model_router calls) should call UsageTracker.log_usage()
after completion so that every request is accounted for.

Table: ai_usage_log (created by migration 009_ai_usage_tracking)

Usage:
    from app.services.usage_tracking_service import UsageTracker
    await UsageTracker.log_usage(db, tenant_id=..., bucket=..., model=..., tokens_in=..., ...)
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.services.model_router import FeatureBucket, get_model_router

logger = logging.getLogger(__name__)

# Feature bucket → billing category for plan limits
BUCKET_CATEGORY_MAP: dict[str, str] = {
    FeatureBucket.text_basic.value:        "text_generation",
    FeatureBucket.text_marketing.value:    "text_generation",
    FeatureBucket.translation.value:       "translation",
    FeatureBucket.localization.value:      "text_generation",
    FeatureBucket.seo_keywords.value:      "text_generation",
    FeatureBucket.campaign_strategy.value: "text_generation",
    FeatureBucket.image_prompting.value:   "text_generation",
    FeatureBucket.image_generation.value:  "image_generation",
    FeatureBucket.lead_classification.value: "text_generation",
    FeatureBucket.email_copywriting.value: "text_generation",
    FeatureBucket.chatbot.value:           "text_generation",
}


class UsageTracker:
    """
    Records AI usage to the ai_usage_log table.

    All methods are static/async for clean call-site ergonomics.
    DB writes are non-blocking and failures are logged but not raised,
    so a tracking failure never breaks the actual AI response.
    """

    @staticmethod
    async def log_usage(
        db: "AsyncSession",
        *,
        tenant_id: uuid.UUID,
        feature_bucket: str,
        model_id: str,
        provider: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost_usd: float = 0.0,
        country_code: Optional[str] = None,
        language_mode: Optional[str] = None,
        industry: Optional[str] = None,
        platform: Optional[str] = None,
        creatives_count: int = 0,
        translations_count: int = 0,
        images_count: int = 0,
        user_id: Optional[uuid.UUID] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        extra_metadata: Optional[dict] = None,
    ) -> None:
        """
        Asynchronously log a single AI usage event.

        Failures are caught and logged — they never raise to the caller.
        """
        try:
            from sqlalchemy import text
            await db.execute(
                text("""
                    INSERT INTO ai_usage_log (
                        id, tenant_id, user_id,
                        feature_bucket, billing_category,
                        model_id, provider,
                        input_tokens, output_tokens, total_tokens, estimated_cost_usd,
                        country_code, language_mode, industry, platform,
                        creatives_count, translations_count, images_count,
                        success, error_message, extra_metadata,
                        created_at
                    ) VALUES (
                        :id, :tenant_id, :user_id,
                        :feature_bucket, :billing_category,
                        :model_id, :provider,
                        :input_tokens, :output_tokens, :total_tokens, :estimated_cost_usd,
                        :country_code, :language_mode, :industry, :platform,
                        :creatives_count, :translations_count, :images_count,
                        :success, :error_message, CAST(:extra_metadata AS JSONB),
                        :created_at
                    )
                """),
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "user_id": user_id,
                    "feature_bucket": feature_bucket,
                    "billing_category": BUCKET_CATEGORY_MAP.get(feature_bucket, "text_generation"),
                    "model_id": model_id,
                    "provider": provider,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "estimated_cost_usd": estimated_cost_usd,
                    "country_code": country_code,
                    "language_mode": language_mode,
                    "industry": industry,
                    "platform": platform,
                    "creatives_count": creatives_count,
                    "translations_count": translations_count,
                    "images_count": images_count,
                    "success": success,
                    "error_message": error_message,
                    "extra_metadata": str(extra_metadata) if extra_metadata else None,
                    "created_at": datetime.now(timezone.utc),
                },
            )
            await db.commit()
        except Exception as exc:
            # Non-fatal: log and continue
            logger.error(f"UsageTracker.log_usage failed (tenant={tenant_id}): {exc}")

    @staticmethod
    async def get_tenant_usage_summary(
        db: "AsyncSession",
        tenant_id: uuid.UUID,
        month: Optional[str] = None,   # "YYYY-MM" — defaults to current month
    ) -> dict:
        """
        Return a monthly usage summary for a tenant.
        Used for plan limit checking and admin dashboards.
        """
        if month is None:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        year, mon = month.split("-")
        try:
            from sqlalchemy import text
            result = await db.execute(
                text("""
                    SELECT
                        billing_category,
                        COUNT(*) as request_count,
                        SUM(total_tokens) as total_tokens,
                        SUM(estimated_cost_usd) as total_cost_usd,
                        SUM(creatives_count) as total_creatives,
                        SUM(translations_count) as total_translations,
                        SUM(images_count) as total_images
                    FROM ai_usage_log
                    WHERE tenant_id = :tenant_id
                      AND EXTRACT(YEAR FROM created_at) = :year
                      AND EXTRACT(MONTH FROM created_at) = :month
                      AND success = TRUE
                    GROUP BY billing_category
                """),
                {"tenant_id": tenant_id, "year": int(year), "month": int(mon)},
            )
            rows = result.fetchall()

            summary: dict = {
                "month": month,
                "tenant_id": str(tenant_id),
                "text_generation": {"requests": 0, "tokens": 0, "cost_usd": 0.0, "creatives": 0},
                "translation": {"requests": 0, "tokens": 0, "cost_usd": 0.0, "translates": 0},
                "image_generation": {"requests": 0, "tokens": 0, "cost_usd": 0.0, "images": 0},
                "total_cost_usd": 0.0,
            }

            for row in rows:
                cat = row.billing_category or "text_generation"
                if cat not in summary:
                    summary[cat] = {"requests": 0, "tokens": 0, "cost_usd": 0.0}
                summary[cat]["requests"] = int(row.request_count or 0)
                summary[cat]["tokens"] = int(row.total_tokens or 0)
                summary[cat]["cost_usd"] = round(float(row.total_cost_usd or 0.0), 6)
                if cat == "text_generation":
                    summary[cat]["creatives"] = int(row.total_creatives or 0)
                if cat == "translation":
                    summary[cat]["translates"] = int(row.total_translations or 0)
                if cat == "image_generation":
                    summary[cat]["images"] = int(row.total_images or 0)
                summary["total_cost_usd"] += float(row.total_cost_usd or 0.0)

            summary["total_cost_usd"] = round(summary["total_cost_usd"], 6)
            return summary

        except Exception as exc:
            logger.error(f"UsageTracker.get_tenant_usage_summary failed: {exc}")
            return {"month": month, "tenant_id": str(tenant_id), "error": str(exc)}

    @staticmethod
    async def get_tenant_monthly_counts(
        db: "AsyncSession",
        tenant_id: uuid.UUID,
        month: Optional[str] = None,
    ) -> dict:
        """
        Return simple monthly counts per billing category.
        Used by plan_limit_service for quick limit checks.
        """
        if month is None:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        year, mon = month.split("-")
        try:
            from sqlalchemy import text
            result = await db.execute(
                text("""
                    SELECT
                        billing_category,
                        COALESCE(SUM(creatives_count), COUNT(*)) as count
                    FROM ai_usage_log
                    WHERE tenant_id = :tenant_id
                      AND EXTRACT(YEAR FROM created_at) = :year
                      AND EXTRACT(MONTH FROM created_at) = :month
                      AND success = TRUE
                    GROUP BY billing_category
                """),
                {"tenant_id": tenant_id, "year": int(year), "month": int(mon)},
            )
            rows = result.fetchall()
            counts = {row.billing_category: int(row.count or 0) for row in rows}
            return counts
        except Exception as exc:
            logger.error(f"UsageTracker.get_tenant_monthly_counts failed: {exc}")
            return {}
