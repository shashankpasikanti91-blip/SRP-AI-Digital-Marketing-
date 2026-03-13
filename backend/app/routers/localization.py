"""
Localization Router — Phase 14 Global Localization
====================================================

Endpoints:
  GET  /localization/countries              — list supported countries
  GET  /localization/languages              — list supported languages
  GET  /localization/states/{country_code}  — list states for a country
  POST /localization/context                — build localization context
  POST /localization/seo-keywords           — generate localized SEO keywords
  POST /localization/campaign-prompt        — generate bilingual campaign AI prompt
  POST /localization/whatsapp-prompt        — generate bilingual WhatsApp status prompt
  GET  /localization/festivals              — get festival suggestions
  GET  /localization/poster-layout          — get poster layout specification
  GET  /localization/template-suggestions   — get regional template suggestions

All endpoints are READ-HEAVY and work alongside existing routers without
modifying them.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.services.localization_engine import (
    LocalizationEngine,
    LocalizationContext,
    LanguageMode,
    get_country_list,
    get_language_list,
    COUNTRIES,
    INDIA_STATE_LANGUAGE_MAP,
    FESTIVAL_CALENDARS,
    GLOBAL_LANGUAGES,
)

router = APIRouter(prefix="/localization", tags=["Localization — Phase 14"])


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class LocalizationContextRequest(BaseModel):
    country_code: str = Field(..., description="ISO country code: IN, MY, ID, TH, SG, AU, NZ")
    state: Optional[str] = Field(None, description="State name (important for India)")
    city: Optional[str] = None
    industry: Optional[str] = "general"
    language_mode: LanguageMode = "english"


class SEOKeywordsRequest(BaseModel):
    country_code: str
    city: str
    industry: str
    state: Optional[str] = None
    language_mode: LanguageMode = "english"


class CampaignPromptRequest(BaseModel):
    country_code: str
    state: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = "general"
    language_mode: LanguageMode = "english"
    campaign_type: str = Field(..., description="e.g. 'health camp', 'grand sale', 'new arrival'")
    org_name: Optional[str] = ""
    additional_details: Optional[dict] = None


class WhatsAppPromptRequest(BaseModel):
    country_code: str
    state: Optional[str] = None
    city: Optional[str] = None
    industry: Optional[str] = "general"
    language_mode: LanguageMode = "english"
    campaign_type: str
    org_name: Optional[str] = ""
    offer_details: Optional[str] = None


class CurrencyFormatRequest(BaseModel):
    amount: float
    currency_code: str


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@router.get("/countries", summary="List all supported countries")
def list_countries():
    """
    Returns all countries supported by the localization engine with
    currency, language, and bilingual support metadata.
    """
    return {
        "countries": get_country_list(),
        "total": len(get_country_list()),
    }


@router.get("/languages", summary="List all supported languages")
def list_languages():
    """
    Returns all languages supported by the platform, including
    ISO codes, scripts, and countries where each is applicable.
    """
    return {
        "languages": get_language_list(),
        "total": len(get_language_list()),
    }


@router.get("/states/{country_code}", summary="List states/regions for a country")
def list_states(country_code: str):
    """
    Returns state-language mapping for a country.
    Most useful for India where states determine regional language.
    """
    code = country_code.upper()
    if code not in COUNTRIES:
        raise HTTPException(status_code=404, detail=f"Country '{code}' not supported.")

    if code == "IN":
        states = [
            {"name": state, "language": lang, "country": "IN"}
            for state, lang in INDIA_STATE_LANGUAGE_MAP.items()
        ]
        return {"country_code": code, "states": states, "total": len(states)}

    return {
        "country_code": code,
        "states": [],
        "note": "State-level language mapping not required for this country.",
    }


@router.post("/context", summary="Build a full localization context")
def build_context(req: LocalizationContextRequest):
    """
    Resolves full localization context including:
    - Primary & secondary language
    - Currency info
    - Bilingual requirement
    - Marketing style
    """
    try:
        ctx = LocalizationEngine.build_localization_context(
            country_code=req.country_code,
            state=req.state,
            city=req.city,
            industry=req.industry,
            language_mode=req.language_mode,
        )
        return ctx.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seo-keywords", summary="Generate localized SEO keywords")
def generate_seo_keywords(req: SEOKeywordsRequest):
    """
    Generates a full localized SEO keyword set for a city/industry,
    including English and local language keywords + near-me variants.

    Examples:
      best restaurant Kuala Lumpur
      restaurant near me KL
      kedai makan terbaik Kuala Lumpur
    """
    try:
        ctx = LocalizationEngine.build_localization_context(
            country_code=req.country_code,
            state=req.state,
            city=req.city,
            industry=req.industry,
            language_mode=req.language_mode,
        )
        keywords = LocalizationEngine.generate_seo_keywords(
            country_code=req.country_code,
            city=req.city,
            industry=req.industry,
            state=req.state,
            secondary_language=ctx.secondary_language,
        )
        return keywords.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaign-prompt", summary="Generate bilingual campaign AI prompt")
def generate_campaign_prompt(req: CampaignPromptRequest):
    """
    Builds a structured AI prompt for bilingual campaign generation.
    Feed this prompt to the existing AI service to get localized content.
    """
    try:
        ctx = LocalizationEngine.build_localization_context(
            country_code=req.country_code,
            state=req.state,
            city=req.city,
            industry=req.industry,
            language_mode=req.language_mode,
        )
        prompt = LocalizationEngine.build_campaign_prompt(
            context=ctx,
            campaign_type=req.campaign_type,
            org_name=req.org_name or "",
            additional_details=req.additional_details,
        )
        return {
            "prompt": prompt,
            "context": ctx.model_dump(),
            "note": "Feed this prompt to your AI service to generate localized marketing content.",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/whatsapp-prompt", summary="Generate bilingual WhatsApp status prompt")
def generate_whatsapp_prompt(req: WhatsAppPromptRequest):
    """
    Builds a WhatsApp status AI generation prompt with bilingual support.
    """
    try:
        ctx = LocalizationEngine.build_localization_context(
            country_code=req.country_code,
            state=req.state,
            city=req.city,
            industry=req.industry,
            language_mode=req.language_mode,
        )
        prompt = LocalizationEngine.build_whatsapp_status_prompt(
            context=ctx,
            campaign_type=req.campaign_type,
            org_name=req.org_name or "",
            offer_details=req.offer_details,
        )
        return {
            "prompt": prompt,
            "context": ctx.model_dump(),
            "bilingual": ctx.bilingual_required,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/festivals", summary="Festival campaign suggestions")
def get_festivals(
    country_code: str = Query(..., description="ISO country code"),
    month: Optional[int] = Query(None, description="Month number (1-12), omit for all"),
    state: Optional[str] = Query(None, description="State name (India only)"),
    industry: Optional[str] = Query(None, description="Filter by industry relevance"),
):
    """
    Returns festival campaign suggestions for a country/month.

    India: Diwali, Ugadi, Pongal, Holi, Eid...
    Malaysia: Hari Raya, Chinese New Year, Deepavali...
    Indonesia: Ramadan, Lebaran...
    Thailand: Songkran, Loy Krathong...
    """
    try:
        festivals = LocalizationEngine.get_festival_suggestions(
            country_code=country_code.upper(),
            month=month,
            state=state,
            industry=industry,
        )
        return {
            "country_code": country_code.upper(),
            "festivals": festivals,
            "total": len(festivals),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/poster-layout", summary="Get poster layout spec for a context")
def get_poster_layout(
    country_code: str = Query(...),
    language_mode: LanguageMode = Query("english"),
    state: Optional[str] = Query(None),
    industry: Optional[str] = Query("general"),
):
    """
    Returns poster layout specification for a country/language combination.
    Used by the poster generator to adapt layout for bilingual content.
    """
    try:
        ctx = LocalizationEngine.build_localization_context(
            country_code=country_code.upper(),
            state=state,
            industry=industry,
            language_mode=language_mode,
        )
        layout = LocalizationEngine.get_poster_layout_spec(context=ctx)
        return layout.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/template-suggestions", summary="Get regional template suggestions")
def get_template_suggestions(
    country_code: str = Query(...),
    industry: str = Query(...),
    state: Optional[str] = Query(None),
):
    """
    Returns recommended template slugs for a country/industry combination,
    including both industry-specific and festival-based templates.
    """
    try:
        suggestions = LocalizationEngine.get_regional_template_suggestions(
            country_code=country_code.upper(),
            industry=industry,
            state=state,
        )
        return {
            "country_code": country_code.upper(),
            "industry": industry,
            "templates": suggestions,
            "total": len(suggestions),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/format-currency", summary="Format a price in a specific currency")
def format_currency(req: CurrencyFormatRequest):
    """Formats a numeric amount using the correct symbol and locale for a currency."""
    formatted = LocalizationEngine.format_currency(req.amount, req.currency_code)
    return {"formatted": formatted, "amount": req.amount, "currency_code": req.currency_code}


@router.get("/detect-language", summary="Detect language for a country/state")
def detect_language(
    country_code: str = Query(...),
    state: Optional[str] = Query(None),
):
    """
    Quick endpoint to detect the primary and secondary language
    for a given country/state combination.
    """
    try:
        result = LocalizationEngine.resolve_languages(
            country_code=country_code.upper(),
            state=state,
        )
        return {
            "country_code": country_code.upper(),
            "state": state,
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pricing-usd", summary="Get USD pricing tiers")
def get_usd_pricing():
    """
    Returns the platform's global USD pricing tiers.
    Used by the marketing landing page for international visitors.
    """
    return {
        "currency": "USD",
        "currency_symbol": "$",
        "note": "Local taxes and currency conversion may apply depending on your country.",
        "plans": [
            {
                "name": "Starter",
                "price_usd": 0,
                "period": "forever",
                "badge": "Free Forever",
                "features": [
                    "100 leads/month",
                    "500 AI credits/month",
                    "1 user",
                    "Basic AI agents",
                    "Email & WhatsApp inbox",
                    "Community support",
                ],
            },
            {
                "name": "Growth",
                "price_usd": 19,
                "period": "/month",
                "badge": "Most Popular",
                "features": [
                    "2,000 leads/month",
                    "10,000 AI credits/month",
                    "5 users",
                    "All 10 AI agents",
                    "All channels (9 platforms)",
                    "Priority email support",
                    "AI follow-up sequences",
                    "Campaign planner",
                ],
            },
            {
                "name": "Professional",
                "price_usd": 49,
                "period": "/month",
                "badge": "Best Value",
                "features": [
                    "10,000 leads/month",
                    "50,000 AI credits/month",
                    "15 users",
                    "Everything in Growth",
                    "Multi-brand workspaces",
                    "Custom AI persona training",
                    "White-label reports",
                    "Dedicated support",
                ],
            },
            {
                "name": "Enterprise",
                "price_usd": 99,
                "period": "/month",
                "badge": "Full Power",
                "features": [
                    "Unlimited leads",
                    "Unlimited AI credits",
                    "Unlimited users",
                    "Everything in Professional",
                    "Custom AI fine-tuning",
                    "On-premise deploy",
                    "99.9% SLA",
                    "Dedicated AI engineer",
                ],
            },
        ],
    }


@router.get("/supported-markets", summary="Get all supported markets overview")
def get_supported_markets():
    """
    Returns a complete overview of all supported markets including
    countries, languages, bilingual support, and currency info.
    """
    markets = []
    for code, cfg in COUNTRIES.items():
        langs = LocalizationEngine.resolve_languages(code)
        markets.append({
            "country_code": code,
            "country_name": cfg["name"],
            "currency_code": cfg["currency_code"],
            "currency_symbol": cfg["currency_symbol"],
            "primary_language": langs["primary_language"],
            "secondary_language": langs["secondary_language"],
            "bilingual_supported": cfg["bilingual_supported"],
            "language_modes": cfg["language_modes"],
            "marketing_style": cfg["marketing_style"],
        })

    supported_languages = [
        {"code": k, "name": v["name"], "script": v["script"]}
        for k, v in GLOBAL_LANGUAGES.items()
    ]

    return {
        "supported_markets": markets,
        "supported_languages": supported_languages,
        "total_countries": len(markets),
        "total_languages": len(supported_languages),
    }
