"""
Creatives Router — Unified AI Creative Generation API
POST /api/v1/creatives/generate  → Full locale-aware creative pipeline
GET  /api/v1/creatives/industries → Industry config catalogue
GET  /api/v1/creatives/locales    → Locale/country profiles
GET  /api/v1/creatives/plans      → SaaS plan tiers + limits
GET  /api/v1/creatives/usage      → Tenant usage status
GET  /api/v1/creatives/models     → Model routing assignments (admin transparency)
"""
from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_tenant
from app.database import get_db
from app.models.tenant import Tenant
from app.services.creative_service import CreativeRequest, CreativeOutput, CreativeService
from app.services.industry_config import (
    list_industries,
    list_locales,
    get_industry_config,
    get_locale_profile,
    CULTURAL_STYLES,
)
from app.services.plan_limit_service import PlanLimitService, PLAN_LIMITS
from app.services.model_router import BUCKET_MODEL_MAP, MODELS, get_model_router

router = APIRouter(prefix="/creatives", tags=["Creatives"])

# ── Singletons ────────────────────────────────────────────────────────────────

_creative_service: CreativeService | None = None


def _get_creative_service() -> CreativeService:
    global _creative_service
    if _creative_service is None:
        _creative_service = CreativeService()
    return _creative_service


# ── Creative Generation ───────────────────────────────────────────────────────

@router.post(
    "/generate",
    response_model=CreativeOutput,
    summary="Generate locale-aware AI creatives",
    description=(
        "Generates a full creative set (headline, CTA, caption, hashtags, ad copy, "
        "poster template placeholders) using the AI model appropriate for your plan. "
        "Set `generate_poster=true` to include the poster JSON for the frontend renderer. "
        "Set `generate_ai_image=true` only on Pro/Agency/Enterprise plans (billed separately)."
    ),
)
async def generate_creative(
    request: CreativeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
) -> CreativeOutput:
    """Main creative generation endpoint — locale-aware, industry-tuned, plan-checked."""
    svc = _get_creative_service()
    return await svc.generate(db=db, tenant=tenant, request=request)


# ── Industry Catalogue ────────────────────────────────────────────────────────

@router.get(
    "/industries",
    summary="List all supported industries",
    response_model=list[dict],
)
async def list_supported_industries() -> list[dict[str, Any]]:
    """Returns all 12 industry configs (label, tone, cta_style, templates, etc.)."""
    industries = []
    for key in list_industries():
        cfg = get_industry_config(key)
        industries.append({
            "key": key,
            "label": cfg.label,
            "tone_default": cfg.tone_default,
            "cta_style": cfg.cta_style,
            "bilingual_recommended": cfg.bilingual_recommended,
            "template_families": cfg.template_families,
            "compliance_note": cfg.compliance_note,
        })
    return industries


@router.get(
    "/industries/{industry_key}",
    summary="Get a single industry config",
)
async def get_industry(industry_key: str) -> dict[str, Any]:
    cfg = get_industry_config(industry_key)
    return {
        "key": industry_key,
        "label": cfg.label,
        "tone_default": cfg.tone_default,
        "cta_style": cfg.cta_style,
        "trust_vs_urgency": cfg.trust_vs_urgency,
        "bilingual_recommended": cfg.bilingual_recommended,
        "template_families": cfg.template_families,
        "compliance_note": cfg.compliance_note,
    }


# ── Locale / Country Profiles ─────────────────────────────────────────────────

@router.get(
    "/locales",
    summary="List all supported locale/country profiles",
    response_model=list[dict],
)
async def list_supported_locales() -> list[dict[str, Any]]:
    """Returns all 7 country profiles with formality, design style, bilingual defaults, etc."""
    locales = []
    for code in list_locales():
        profile = get_locale_profile(code)
        locales.append({
            "country_code": code,
            "content_formality": profile.content_formality,
            "design_style": profile.design_style,
            "text_density": profile.text_density,
            "cta_tone": profile.cta_tone,
            "bilingual_default": profile.bilingual_default,
            "cultural_sensitivities": profile.cultural_sensitivities,
            "has_state_profiles": bool(profile.state_profiles),
            "state_count": len(profile.state_profiles) if profile.state_profiles else 0,
        })
    return locales


@router.get(
    "/locales/{country_code}",
    summary="Get a single country profile (with state sub-profiles)",
)
async def get_locale(country_code: str) -> dict[str, Any]:
    profile = get_locale_profile(country_code.upper())
    result: dict[str, Any] = {
        "country_code": country_code.upper(),
        "content_formality": profile.content_formality,
        "design_style": profile.design_style,
        "text_density": profile.text_density,
        "cta_tone": profile.cta_tone,
        "bilingual_default": profile.bilingual_default,
        "cultural_sensitivities": profile.cultural_sensitivities,
    }
    if profile.state_profiles:
        result["state_profiles"] = {
            state: {
                "primary_language": sp.primary_language,
                "secondary_language": sp.secondary_language,
                "bilingual_recommended": sp.bilingual_recommended,
                "regional_style_notes": sp.regional_style_notes,
            }
            for state, sp in profile.state_profiles.items()
        }
    return result


@router.get(
    "/cultural-styles",
    summary="List available cultural design styles",
)
async def list_cultural_styles() -> dict[str, Any]:
    """Returns all 8 cultural styles with tone, design principle, and template hints."""
    return {
        key: {
            "tone": style.tone,
            "design_principle": style.design_principle,
            "colour_palette_hint": style.colour_palette_hint,
            "typography_hint": style.typography_hint,
            "layout_hint": style.layout_hint,
        }
        for key, style in CULTURAL_STYLES.items()
    }


# ── SaaS Plan Tiers ───────────────────────────────────────────────────────────

@router.get(
    "/plans",
    summary="List all SaaS plan tiers and limits",
)
async def list_plans() -> dict[str, Any]:
    """Returns starter/pro/agency/enterprise monthly usage limits for all billing categories."""
    return {
        plan: {
            "text_generation": limits.text_generation,
            "translation": limits.translation,
            "image_generation": limits.image_generation,
            "description": {
                "starter": "50 AI generations/month, no images",
                "pro": "500 AI generations/month, 20 images",
                "agency": "2 000 AI generations/month, 100 images",
                "enterprise": "Unlimited",
            }.get(plan, plan),
        }
        for plan, limits in PLAN_LIMITS.items()
    }


# ── Tenant Usage Status ────────────────────────────────────────────────────────

@router.get(
    "/usage",
    summary="Get current tenant's AI usage vs plan limits",
)
async def get_usage(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_current_tenant)],
) -> dict[str, Any]:
    """Returns per-category usage counts, limits remaining, and overage warnings for the current month."""
    svc = PlanLimitService()
    return await svc.get_usage_status(db, tenant)


# ── Model Routing Transparency ────────────────────────────────────────────────

@router.get(
    "/models",
    summary="Show model routing assignments per feature bucket (admin transparency)",
)
async def show_model_routing() -> dict[str, Any]:
    """
    Returns which AI model is assigned to each feature bucket.
    This helps operators verify cost-tier assignments without reading source code.
    """
    router_instance = get_model_router()
    result = {}
    for bucket, (primary_key, fallback_key) in BUCKET_MODEL_MAP.items():
        primary = MODELS.get(primary_key)
        fallback = MODELS.get(fallback_key) if fallback_key else None
        # try resolving to confirm it works
        try:
            _, active_model_id = router_instance.resolve(bucket)
        except Exception:
            active_model_id = primary.model_id if primary else "unknown"

        result[bucket.value] = {
            "active_model": active_model_id,
            "primary": {
                "model_id": primary.model_id,
                "provider": primary.provider,
                "input_cost_per_1k": primary.input_cost_per_1k,
                "output_cost_per_1k": primary.output_cost_per_1k,
            } if primary else None,
            "fallback": {
                "model_id": fallback.model_id,
                "provider": fallback.provider,
            } if fallback else None,
        }
    return result
