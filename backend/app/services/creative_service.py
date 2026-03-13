"""
Creative Service — SRP Marketing OS
=====================================

The central creative generation pipeline.

This service orchestrates:
  1.  Input validation + locale profile resolution
  2.  Industry strategy config resolution
  3.  Cultural context selection
  4.  AI content generation (via model_router — centralized, cost-aware)
  5.  Template selection (locale + industry + platform aware)
  6.  Placeholder injection into template data
  7.  Structured creative output (multi-format)
  8.  Optional bilingual / trilingual output
  9.  Optional AI image generation (only when explicitly enabled)
  10. Usage tracking log

Input:  CreativeRequest  — rich, locale-aware
Output: CreativeOutput   — structured JSON with headline, CTA, caption, hashtags,
                          template data, poster_json, optional translations

Architecture Principle:
  AI generates TEXT ONLY.
  Template system handles VISUAL layout.
  AI image generation is OPTIONAL and OFF by default.

Usage:
    from app.services.creative_service import CreativeService
    output = await CreativeService.generate(db, tenant, request)
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

from app.services.model_router import FeatureBucket, get_model_router
from app.services.industry_config import (
    get_industry_config,
    get_locale_profile,
    get_cultural_style,
    get_template_suggestions,
)
from app.services.localization_engine import (
    LocalizationEngine,
    GLOBAL_LANGUAGES,
    TRANSLATION_GUIDANCE,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.tenant import Tenant

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST / OUTPUT MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class CreativeRequest(BaseModel):
    """
    Rich input schema for the creative generation pipeline.
    All fields are optional except the minimum required set.
    """
    # Tenant context
    tenant_id: Optional[uuid.UUID] = None

    # Business details
    business_name: str = Field(..., description="Trading name of the business")
    industry: str = Field("general_business", description="Industry slug from INDUSTRY_CONFIG")
    service_or_product: Optional[str] = Field(None, description="Specific service/product being promoted")
    offer_details: Optional[str] = Field(None, description="Discount, price, or special offer details")
    tagline: Optional[str] = None

    # Campaign context
    campaign_type: str = Field("general_promotion", description="e.g. health_camp, grand_sale, new_launch, admission")
    campaign_objective: Optional[str] = None

    # Location
    country_code: str = Field("IN", description="ISO country code: IN, AU, NZ, MY, SG, ID, TH")
    state_or_region: Optional[str] = None
    city: Optional[str] = None

    # Audience
    target_audience: Optional[str] = None

    # Language
    language_mode: str = Field("english", description="english | bilingual | trilingual")
    primary_language: str = "english"
    secondary_language: Optional[str] = None   # auto-resolved from locale if not given
    tertiary_language: Optional[str] = None    # for trilingual

    # Cultural context
    cultural_style: str = Field("modern", description="formal|modern|premium|community_trust|festive|family_oriented|institutional|local_retail")
    festival_or_season: Optional[str] = None    # e.g. "Diwali", "Eid", "Christmas", "EOFY"
    brand_theme: Optional[str] = None           # e.g. "blue healthcare", "warm restaurant", "premium real estate"

    # Output platform
    platform: str = Field("instagram_square", description="instagram_square|instagram_story|facebook_post|whatsapp_share|linkedin_banner")
    output_type: str = Field("social_post", description="social_post|story_poster|flyer|banner_ad|whatsapp_flyer")
    tone: str = Field("professional", description="professional|casual|friendly|urgent|inspirational|festive")

    # Template
    template_slug: Optional[str] = None         # override template auto-selection

    # Optional brand fields for template placeholders
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_qualification: Optional[str] = None
    services: Optional[list[str]] = None
    date_range: Optional[str] = None
    event_time: Optional[str] = None
    offer_price: Optional[str] = None
    original_price: Optional[str] = None

    # Feature flags
    generate_poster: bool = True                # generate template JSON
    generate_ai_image: bool = False             # ONLY if plan allows + explicitly requested


class LocalizedText(BaseModel):
    """A text field with optional translations."""
    primary: str
    secondary: Optional[str] = None             # second language
    tertiary: Optional[str] = None              # third language (trilingual)


class CreativeOutput(BaseModel):
    """
    Structured creative output from the pipeline.
    """
    # Core marketing copy
    headline: LocalizedText
    subheadline: LocalizedText
    cta: LocalizedText
    caption: LocalizedText
    hashtags: list[str]

    # Extended copy
    short_copy: Optional[str] = None
    long_copy: Optional[str] = None
    ad_copy_short: Optional[str] = None    # ≤90 chars

    # Locale context
    country_code: str
    language_mode: str
    primary_language: str
    secondary_language: Optional[str] = None
    tertiary_language: Optional[str] = None
    cultural_style: str
    currency_symbol: Optional[str] = None

    # Template data
    template_slug: Optional[str] = None
    template_placeholders: dict = Field(default_factory=dict)
    poster_json: Optional[dict] = None           # full poster JSON from PosterGenerator

    # Image
    ai_image_used: bool = False
    ai_image_url: Optional[str] = None
    ai_image_prompt: Optional[str] = None

    # Meta
    model_used: Optional[str] = None
    provider_used: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    generation_notes: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════════════
# INTERNAL AI OUTPUT SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

class _AIContentOutput(BaseModel):
    """Structured JSON output from the AI for creative content."""
    headline_primary: str
    headline_secondary: Optional[str] = None
    headline_tertiary: Optional[str] = None
    subheadline_primary: str
    subheadline_secondary: Optional[str] = None
    cta_primary: str
    cta_secondary: Optional[str] = None
    cta_tertiary: Optional[str] = None
    caption: str
    caption_secondary: Optional[str] = None
    hashtags: list[str]
    short_copy: str
    long_copy: Optional[str] = None
    ad_copy_short: str


# ═══════════════════════════════════════════════════════════════════════════════
# CREATIVE SERVICE
# ═══════════════════════════════════════════════════════════════════════════════

class CreativeService:
    """
    Unified creative generation pipeline.

    Steps:
      1. Resolve locale + language settings
      2. Resolve industry strategy config
      3. Build AI prompt with full localization context
      4. Call AI via model_router (cost-controlled)
      5. Parse structured output
      6. Select + build template placeholders
      7. Optionally generate poster JSON
      8. Log usage
      9. Return CreativeOutput
    """

    @classmethod
    async def generate(
        cls,
        db: "AsyncSession",
        tenant: "Tenant",
        request: CreativeRequest,
    ) -> CreativeOutput:
        """Main entry point: generate a complete creative package."""
        notes: list[str] = []
        router = get_model_router()

        # ── Step 1: Resolve locale context ────────────────────────────
        locale_profile = get_locale_profile(request.country_code, state=request.state_or_region)
        loc_ctx = LocalizationEngine.build_localization_context(
            country_code=request.country_code,
            state=request.state_or_region,
            city=request.city,
            industry=request.industry,
            language_mode=request.language_mode,  # type: ignore[arg-type]
        )

        # Resolve secondary language if not explicitly set
        secondary_lang = request.secondary_language or loc_ctx.secondary_language
        tertiary_lang = request.tertiary_language

        # For English-only markets, force monolingual
        if locale_profile.get("bilingual_default") is False and request.language_mode == "english":
            secondary_lang = None
            tertiary_lang = None

        # ── Step 2: Industry config ────────────────────────────────────
        ind_cfg = get_industry_config(request.industry)
        cultural_style_cfg = get_cultural_style(request.cultural_style)

        # ── Step 3: Build AI prompt ────────────────────────────────────
        prompt = cls._build_prompt(request, loc_ctx, ind_cfg, cultural_style_cfg,
                                   secondary_lang, tertiary_lang)

        # ── Step 4: AI call via model_router ──────────────────────────
        bucket = FeatureBucket.text_marketing
        client, model_id = router.resolve(bucket)
        model_key_for_provider, provider = router.get_model_id_and_provider(bucket)

        input_tokens = 0
        output_tokens = 0
        estimated_cost = 0.0
        ai_data: dict = {}

        try:
            response = await client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": _CREATIVE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                max_tokens=2500,
                temperature=0.75,
            )
            raw = response.choices[0].message.content or "{}"
            if raw.startswith("```"):
                raw = raw.split("```")[-2].lstrip("json").strip()
            ai_data = json.loads(raw)
            if response.usage:
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
            estimated_cost = router.estimate_cost(bucket, input_tokens, output_tokens)
        except Exception as exc:
            logger.error(f"CreativeService AI call failed: {exc}")
            notes.append(f"AI generation warning: {str(exc)[:120]}")
            # Use safe fallback values
            ai_data = cls._build_fallback_content(request)

        # ── Step 5: Parse AI output ────────────────────────────────────
        def _get(key: str, default: str = "") -> str:
            return str(ai_data.get(key) or default)

        parsed = _AIContentOutput(
            headline_primary=_get("headline_primary", request.business_name),
            headline_secondary=_get("headline_secondary") or None,
            headline_tertiary=_get("headline_tertiary") or None,
            subheadline_primary=_get("subheadline_primary", ""),
            subheadline_secondary=_get("subheadline_secondary") or None,
            cta_primary=_get("cta_primary", ind_cfg.get("cta_examples", {}).get("general", "Contact Us")),
            cta_secondary=_get("cta_secondary") or None,
            cta_tertiary=_get("cta_tertiary") or None,
            caption=_get("caption", ""),
            caption_secondary=_get("caption_secondary") or None,
            hashtags=ai_data.get("hashtags", ind_cfg.get("default_hashtags_en", ["#Marketing"])),
            short_copy=_get("short_copy", ""),
            long_copy=_get("long_copy") or None,
            ad_copy_short=_get("ad_copy_short", ""),
        )

        # ── Step 6: Template selection ─────────────────────────────────
        template_slug = request.template_slug
        if not template_slug:
            suggestions = get_template_suggestions(request.industry, request.country_code, request.campaign_type)
            template_slug = suggestions[0] if suggestions else "retail_discount"
            notes.append(f"Template auto-selected: {template_slug}")

        # Build template placeholders
        placeholders = cls._build_placeholders(request, parsed, loc_ctx)

        # ── Step 7: Generate poster JSON (optional) ────────────────────
        poster_json: Optional[dict] = None
        if request.generate_poster:
            try:
                poster_json = await cls._generate_poster(
                    db=db,
                    tenant=tenant,
                    request=request,
                    parsed=parsed,
                    template_slug=template_slug,
                    secondary_lang=secondary_lang,
                )
            except Exception as exc:
                logger.error(f"Poster generation failed: {exc}")
                notes.append(f"Poster generation skipped: {str(exc)[:100]}")

        # ── Step 8: Log usage ──────────────────────────────────────────
        if db and tenant:
            from app.services.usage_tracking_service import UsageTracker
            try:
                await UsageTracker.log_usage(
                    db,
                    tenant_id=tenant.id,
                    feature_bucket=bucket.value,
                    model_id=model_id,
                    provider=provider,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    estimated_cost_usd=estimated_cost,
                    country_code=request.country_code,
                    language_mode=request.language_mode,
                    industry=request.industry,
                    platform=request.platform,
                    creatives_count=1,
                    translations_count=1 if secondary_lang else 0,
                    success=True,
                )
            except Exception as exc:
                logger.warning(f"Usage tracking failed (non-fatal): {exc}")

        # ── Step 9: Compile output ─────────────────────────────────────
        return CreativeOutput(
            headline=LocalizedText(
                primary=parsed.headline_primary,
                secondary=parsed.headline_secondary,
                tertiary=parsed.headline_tertiary,
            ),
            subheadline=LocalizedText(
                primary=parsed.subheadline_primary,
                secondary=parsed.subheadline_secondary,
            ),
            cta=LocalizedText(
                primary=parsed.cta_primary,
                secondary=parsed.cta_secondary,
                tertiary=parsed.cta_tertiary,
            ),
            caption=LocalizedText(
                primary=parsed.caption,
                secondary=parsed.caption_secondary,
            ),
            hashtags=parsed.hashtags[:15],
            short_copy=parsed.short_copy or None,
            long_copy=parsed.long_copy,
            ad_copy_short=parsed.ad_copy_short[:90] if parsed.ad_copy_short else None,
            country_code=request.country_code,
            language_mode=request.language_mode,
            primary_language=request.primary_language,
            secondary_language=secondary_lang,
            tertiary_language=tertiary_lang,
            cultural_style=request.cultural_style,
            currency_symbol=loc_ctx.currency_symbol,
            template_slug=template_slug,
            template_placeholders=placeholders,
            poster_json=poster_json,
            ai_image_used=False,
            model_used=model_id,
            provider_used=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=estimated_cost,
            generation_notes=notes,
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    @classmethod
    def _build_prompt(
        cls,
        req: CreativeRequest,
        loc_ctx,
        ind_cfg: dict,
        cultural_style_cfg: dict,
        secondary_lang: Optional[str],
        tertiary_lang: Optional[str],
    ) -> str:
        """Build the AI prompt for creative generation."""
        country_cfg = LocalizationEngine.get_country_config(req.country_code)
        country_name = country_cfg["name"]
        marketing_style = country_cfg.get("marketing_style", "professional")

        location_str = ", ".join(filter(None, [req.city, req.state_or_region, country_name]))

        # Language instruction
        lang_instruction = ""
        primary_lang_name = GLOBAL_LANGUAGES.get(req.primary_language, {}).get("name", "English")

        if secondary_lang and req.language_mode in ("bilingual", "trilingual"):
            sec_lang_cfg = GLOBAL_LANGUAGES.get(secondary_lang, {})
            sec_lang_name = sec_lang_cfg.get("name", secondary_lang)
            translation_hint = TRANSLATION_GUIDANCE.get(secondary_lang, f"Translate to {sec_lang_name} naturally.")
            lang_instruction = (
                f"\nLANGUAGE MODE: Bilingual — {primary_lang_name} + {sec_lang_name}\n"
                f"Translation guidance: {translation_hint}\n"
                f"Populate all *_secondary fields in {sec_lang_name}.\n"
            )
            if tertiary_lang and req.language_mode == "trilingual":
                tri_lang_name = GLOBAL_LANGUAGES.get(tertiary_lang, {}).get("name", tertiary_lang)
                lang_instruction += f"Also populate *_tertiary fields in {tri_lang_name}.\n"
        else:
            lang_instruction = f"\nLANGUAGE MODE: Monolingual — {primary_lang_name} only.\n"

        # Festival context
        festival_line = ""
        if req.festival_or_season:
            festival_line = f"\nFESTIVAL/SEASON CONTEXT: {req.festival_or_season} — adapt tone and copy accordingly.\n"

        prompt = f"""Generate marketing creative content for the following campaign:

BUSINESS: {req.business_name}
INDUSTRY: {req.industry} — {ind_cfg.get("label", "")}
CAMPAIGN TYPE: {req.campaign_type}
SERVICE/PRODUCT: {req.service_or_product or "General services"}
OFFER: {req.offer_details or "Not specified"}
LOCATION: {location_str}
TARGET AUDIENCE: {req.target_audience or "General public"}
PLATFORM: {req.platform}
TONE: {req.tone}
CULTURAL STYLE: {req.cultural_style} — {cultural_style_cfg.get("tone", "")}
MARKETING STYLE (country standard): {marketing_style}
CTA STYLE: {ind_cfg.get("cta_style", "contact_us")}
TRUST vs URGENCY BALANCE: {ind_cfg.get("trust_vs_urgency", 0.5)} (0=urgency, 1=trust)
{lang_instruction}
{festival_line}
COMPLIANCE NOTE: {ind_cfg.get("compliance_note") or "None"}

OUTPUT FORMAT — Return ONLY valid JSON with these exact keys:
{{
    "headline_primary": "Main headline in {primary_lang_name} (compelling, short)",
    "headline_secondary": "Same headline in secondary language (or empty string if monolingual)",
    "headline_tertiary": "Same headline in tertiary language (or empty string)",
    "subheadline_primary": "Supporting subheadline in {primary_lang_name}",
    "subheadline_secondary": "Subheadline in secondary language (or empty)",
    "cta_primary": "Clear call-to-action in {primary_lang_name}",
    "cta_secondary": "CTA in secondary language (or empty)",
    "cta_tertiary": "CTA in tertiary language (or empty)",
    "caption": "Social media caption in {primary_lang_name} (2-3 sentences with emoji if appropriate)",
    "caption_secondary": "Caption in secondary language (or empty)",
    "hashtags": ["#tag1", "#tag2", ...up to 12 relevant hashtags],
    "short_copy": "2-3 sentence promotional copy in {primary_lang_name}",
    "long_copy": "5-6 sentence detailed copy in {primary_lang_name} (or empty for short format)",
    "ad_copy_short": "Under 90 characters paid ad copy in {primary_lang_name}"
}}"""
        return prompt

    @classmethod
    def _build_fallback_content(cls, req: CreativeRequest) -> dict:
        """Return minimal safe fallback when AI fails."""
        return {
            "headline_primary": f"Special Offer from {req.business_name}",
            "subheadline_primary": req.offer_details or "Quality service you can trust",
            "cta_primary": "Contact Us Today",
            "caption": f"{req.business_name} — {req.offer_details or 'Special offer available now.'}",
            "hashtags": ["#SpecialOffer", f"#{req.business_name.replace(' ', '')}"],
            "short_copy": f"Visit {req.business_name} for our latest {req.campaign_type} offer.",
            "ad_copy_short": f"{req.business_name} — {req.offer_details or 'Special offer'}",
        }

    @classmethod
    def _build_placeholders(
        cls,
        req: CreativeRequest,
        parsed: _AIContentOutput,
        loc_ctx,
    ) -> dict:
        """Build template placeholder dict from request + AI output."""
        return {
            "{{brand_name}}": req.business_name,
            "{{headline}}": parsed.headline_primary,
            "{{subheadline}}": parsed.subheadline_primary,
            "{{cta}}": parsed.cta_primary,
            "{{caption}}": parsed.caption,
            "{{offer}}": req.offer_details or "",
            "{{phone}}": req.phone or "",
            "{{website}}": req.website or "",
            "{{location}}": req.address or "",
            "{{city}}": req.city or "",
            "{{state_or_region}}": req.state_or_region or "",
            "{{country}}": loc_ctx.country_code,
            "{{doctor_name}}": req.doctor_name or "",
            "{{tagline}}": req.tagline or "",
            "{{service_name}}": req.service_or_product or "",
            "{{festival_name}}": req.festival_or_season or "",
            "{{offer_price}}": req.offer_price or "",
            "{{original_price}}": req.original_price or "",
            "{{date_range}}": req.date_range or "",
            "{{hashtags}}": " ".join(parsed.hashtags[:10]),
            # Bilingual variants
            "{{headline_secondary}}": parsed.headline_secondary or "",
            "{{cta_secondary}}": parsed.cta_secondary or "",
        }

    @classmethod
    async def _generate_poster(
        cls,
        db,
        tenant,
        request: CreativeRequest,
        parsed: _AIContentOutput,
        template_slug: str,
        secondary_lang: Optional[str],
    ) -> Optional[dict]:
        """
        Attempt to generate a poster JSON via PosterGenerator.
        Returns None if poster generation fails.
        """
        try:
            from app.services.language_service import CampaignContentInput
            from app.services.poster_generator import PosterGenerator
            from sqlalchemy import select
            from app.models.brand_profile import BrandProfile

            # Load brand profile
            brand = None
            if tenant and db:
                try:
                    bp_result = await db.execute(
                        select(BrandProfile).where(BrandProfile.tenant_id == tenant.id)
                    )
                    brand = bp_result.scalar_one_or_none()
                except Exception:
                    brand = None

            # Build CampaignContentInput for PosterGenerator
            campaign_input = CampaignContentInput(
                template_slug=template_slug,
                industry=request.industry,
                city=request.city or "",
                locality=None,
                state=request.state_or_region or "General",
                department=None,
                doctor_name=request.doctor_name,
                doctor_qualification=request.doctor_qualification,
                date_range=request.date_range,
                event_time=request.event_time,
                offer_price=request.offer_price,
                original_price=request.original_price,
                services=request.services or [],
                org_name=request.business_name,
                phone=request.phone or "",
                primary_language=request.primary_language,
                secondary_language=secondary_lang,  # type: ignore[arg-type]
            )

            poster = await PosterGenerator.generate_poster_json(
                campaign_input=campaign_input,
                brand=brand,
                template_slug=template_slug,
                platform=request.platform,
            )
            return poster
        except Exception as exc:
            logger.warning(f"_generate_poster failed (non-fatal): {exc}")
            return None


# ── System Prompt ──────────────────────────────────────────────────────────────

_CREATIVE_SYSTEM_PROMPT = """You are an expert multilingual marketing copywriter specializing in:
- Multi-country, multi-language marketing content
- Culture-aware, locale-sensitive campaigns
- Industry-specific messaging (healthcare, education, retail, real estate, etc.)
- Bilingual and trilingual content for India, Malaysia, Indonesia, Thailand, Singapore, Australia, New Zealand

Rules:
- Match the requested tone and cultural style exactly
- For bilingual/trilingual requests, translate ALL requested secondary/tertiary fields accurately
- Use the regional script for translations (not transliteration)
- Keep CTAs action-oriented and concise
- Keep hashtags relevant and searchable
- Keep ad_copy_short under 90 characters
- Return ONLY valid JSON — no markdown, no extra text"""
