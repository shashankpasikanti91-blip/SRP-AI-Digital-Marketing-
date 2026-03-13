"""
SRP Marketing OS — Localization Engine (Phase 14)
==================================================

Global localization and multi-country support module.

Responsibilities:
- Country & language rules
- State-language mapping (India)
- Bilingual generation logic
- Regional marketing tone & cultural adaptation
- Festival campaign suggestions per region
- Currency formatting
- Localized SEO keyword generation
- WhatsApp status bilingual formatting
- Poster layout country adaptation

Supported Countries:
  India, Malaysia, Indonesia, Thailand, Singapore, Australia, New Zealand

IMPORTANT: This module is purely additive — it does NOT modify existing
language_service.py or any Phase-13 modules.
"""

from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════════════════════════
# COUNTRY REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

COUNTRIES: dict[str, dict] = {
    "IN": {
        "name": "India",
        "currency_code": "INR",
        "currency_symbol": "₹",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": "regional",    # state-based
        "bilingual_supported": True,
        "marketing_style": "vibrant, emotional, family-oriented, trust-focused",
        "festival_calendar": "india",
        "language_modes": ["english", "local", "bilingual"],
        "english_only": False,
    },
    "MY": {
        "name": "Malaysia",
        "currency_code": "MYR",
        "currency_symbol": "RM",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": "malay",
        "bilingual_supported": True,
        "marketing_style": "multicultural, inclusive, modern, warm",
        "festival_calendar": "malaysia",
        "language_modes": ["english", "local", "bilingual"],
        "english_only": False,
    },
    "ID": {
        "name": "Indonesia",
        "currency_code": "IDR",
        "currency_symbol": "Rp",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": "bahasa_indonesia",
        "bilingual_supported": True,
        "marketing_style": "community-driven, respectful, aspirational",
        "festival_calendar": "indonesia",
        "language_modes": ["english", "local", "bilingual"],
        "english_only": False,
    },
    "TH": {
        "name": "Thailand",
        "currency_code": "THB",
        "currency_symbol": "฿",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": "thai",
        "bilingual_supported": True,
        "marketing_style": "polite, visual-heavy, festive, royalty-respectful",
        "festival_calendar": "thailand",
        "language_modes": ["english", "local", "bilingual"],
        "english_only": False,
    },
    "SG": {
        "name": "Singapore",
        "currency_code": "SGD",
        "currency_symbol": "S$",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": None,
        "bilingual_supported": False,
        "marketing_style": "professional, efficiency-focused, premium, multi-ethnic",
        "festival_calendar": "singapore",
        "language_modes": ["english"],
        "english_only": True,
    },
    "AU": {
        "name": "Australia",
        "currency_code": "AUD",
        "currency_symbol": "A$",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": None,
        "bilingual_supported": False,
        "marketing_style": "casual, direct, outdoors-friendly, humorous",
        "festival_calendar": "australia",
        "language_modes": ["english"],
        "english_only": True,
    },
    "NZ": {
        "name": "New Zealand",
        "currency_code": "NZD",
        "currency_symbol": "NZ$",
        "price_usd": None,
        "default_language": "english",
        "secondary_language": None,
        "bilingual_supported": False,
        "marketing_style": "friendly, eco-conscious, community-focused",
        "festival_calendar": "new_zealand",
        "language_modes": ["english"],
        "english_only": True,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# INDIA STATE → LANGUAGE MAPPING
# ═══════════════════════════════════════════════════════════════════════════════

INDIA_STATE_LANGUAGE_MAP: dict[str, str] = {
    # South India
    "Telangana": "telugu",
    "Andhra Pradesh": "telugu",
    "Tamil Nadu": "tamil",
    "Karnataka": "kannada",
    "Kerala": "malayalam",
    # West
    "Maharashtra": "marathi",
    "Gujarat": "gujarati",
    "Goa": "english",
    # North India (all map to Hindi)
    "Uttar Pradesh": "hindi",
    "Rajasthan": "hindi",
    "Madhya Pradesh": "hindi",
    "Delhi": "hindi",
    "Haryana": "hindi",
    "Punjab": "punjabi",
    "Himachal Pradesh": "hindi",
    "Uttarakhand": "hindi",
    "Bihar": "hindi",
    "Jharkhand": "hindi",
    "Chhattisgarh": "hindi",
    # East
    "West Bengal": "bengali",
    "Odisha": "odia",
    "Assam": "assamese",
    # Northeast
    "Manipur": "english",
    "Meghalaya": "english",
    "Mizoram": "english",
    "Nagaland": "english",
    "Tripura": "bengali",
    "Arunachal Pradesh": "english",
    "Sikkim": "english",
    # Islands / UT
    "Andaman and Nicobar Islands": "english",
    "Lakshadweep": "malayalam",
    "Jammu and Kashmir": "hindi",
    "Ladakh": "hindi",
    "Chandigarh": "hindi",
    "Puducherry": "tamil",
    "Dadra and Nagar Haveli": "gujarati",
    "Daman and Diu": "gujarati",
}

# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE REGISTRY — PHASE 14 EXTENDED VERSION
# ═══════════════════════════════════════════════════════════════════════════════

GLOBAL_LANGUAGES: dict[str, dict] = {
    "english": {
        "name": "English",
        "code": "en",
        "script": "Latin",
        "direction": "ltr",
        "countries": ["IN", "MY", "ID", "TH", "SG", "AU", "NZ"],
    },
    "telugu": {
        "name": "Telugu",
        "code": "te",
        "script": "Telugu",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Telangana", "Andhra Pradesh"],
    },
    "hindi": {
        "name": "Hindi",
        "code": "hi",
        "script": "Devanagari",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Uttar Pradesh", "Rajasthan", "Madhya Pradesh", "Delhi", "Haryana", "Bihar", "Chhattisgarh"],
    },
    "tamil": {
        "name": "Tamil",
        "code": "ta",
        "script": "Tamil",
        "direction": "ltr",
        "countries": ["IN", "SG", "MY"],
        "states": ["Tamil Nadu", "Puducherry"],
    },
    "kannada": {
        "name": "Kannada",
        "code": "kn",
        "script": "Kannada",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Karnataka"],
    },
    "malayalam": {
        "name": "Malayalam",
        "code": "ml",
        "script": "Malayalam",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Kerala", "Lakshadweep"],
    },
    "marathi": {
        "name": "Marathi",
        "code": "mr",
        "script": "Devanagari",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Maharashtra"],
    },
    "gujarati": {
        "name": "Gujarati",
        "code": "gu",
        "script": "Gujarati",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Gujarat"],
    },
    "bengali": {
        "name": "Bengali",
        "code": "bn",
        "script": "Bengali",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["West Bengal", "Tripura"],
    },
    "punjabi": {
        "name": "Punjabi",
        "code": "pa",
        "script": "Gurmukhi",
        "direction": "ltr",
        "countries": ["IN"],
        "states": ["Punjab"],
    },
    "malay": {
        "name": "Bahasa Melayu",
        "code": "ms",
        "script": "Latin",
        "direction": "ltr",
        "countries": ["MY"],
    },
    "bahasa_indonesia": {
        "name": "Bahasa Indonesia",
        "code": "id",
        "script": "Latin",
        "direction": "ltr",
        "countries": ["ID"],
    },
    "thai": {
        "name": "Thai",
        "code": "th",
        "script": "Thai",
        "direction": "ltr",
        "countries": ["TH"],
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FESTIVAL CALENDAR
# ═══════════════════════════════════════════════════════════════════════════════

FESTIVAL_CALENDARS: dict[str, list[dict]] = {
    "india": [
        {"name": "Diwali", "month": 10, "industry_relevance": ["all"], "type": "national", "template_slug": "diwali_offer"},
        {"name": "Ugadi", "month": 3, "industry_relevance": ["all"], "type": "regional", "states": ["Telangana", "Andhra Pradesh", "Karnataka"], "template_slug": "ugadi_offer"},
        {"name": "Pongal", "month": 1, "industry_relevance": ["all"], "type": "regional", "states": ["Tamil Nadu"], "template_slug": "pongal_offer"},
        {"name": "Holi", "month": 3, "industry_relevance": ["all"], "type": "national", "template_slug": "holi_offer"},
        {"name": "Eid ul-Fitr", "month": 4, "industry_relevance": ["all"], "type": "national", "template_slug": "eid_offer"},
        {"name": "Navratri", "month": 10, "industry_relevance": ["all"], "type": "national", "template_slug": "navratri_offer"},
        {"name": "Onam", "month": 9, "industry_relevance": ["all"], "type": "regional", "states": ["Kerala"], "template_slug": "onam_offer"},
        {"name": "Ganesh Chaturthi", "month": 9, "industry_relevance": ["all"], "type": "regional", "states": ["Maharashtra", "Karnataka"], "template_slug": "ganesh_chaturthi_offer"},
        {"name": "Durga Puja", "month": 10, "industry_relevance": ["all"], "type": "regional", "states": ["West Bengal"], "template_slug": "durga_puja_offer"},
        {"name": "Independence Day", "month": 8, "industry_relevance": ["all"], "type": "national", "template_slug": "independence_day"},
        {"name": "Republic Day", "month": 1, "industry_relevance": ["all"], "type": "national", "template_slug": "republic_day"},
    ],
    "malaysia": [
        {"name": "Hari Raya Aidilfitri", "month": 4, "industry_relevance": ["all"], "type": "national", "template_slug": "hari_raya_offer"},
        {"name": "Chinese New Year", "month": 1, "industry_relevance": ["all"], "type": "national", "template_slug": "cny_offer"},
        {"name": "Deepavali", "month": 11, "industry_relevance": ["all"], "type": "national", "template_slug": "deepavali_offer"},
        {"name": "Malaysia Day", "month": 9, "industry_relevance": ["all"], "type": "national", "template_slug": "malaysia_day"},
    ],
    "indonesia": [
        {"name": "Ramadan", "month": 3, "industry_relevance": ["all"], "type": "national", "template_slug": "ramadan_promo"},
        {"name": "Eid ul-Fitr (Lebaran)", "month": 4, "industry_relevance": ["all"], "type": "national", "template_slug": "lebaran_offer"},
        {"name": "Independence Day", "month": 8, "industry_relevance": ["all"], "type": "national", "template_slug": "independence_id"},
    ],
    "thailand": [
        {"name": "Songkran (Thai New Year)", "month": 4, "industry_relevance": ["all"], "type": "national", "template_slug": "songkran_offer"},
        {"name": "Loy Krathong", "month": 11, "industry_relevance": ["all"], "type": "national", "template_slug": "loy_krathong"},
        {"name": "National Day", "month": 12, "industry_relevance": ["all"], "type": "national", "template_slug": "thailand_national_day"},
    ],
    "singapore": [
        {"name": "Chinese New Year", "month": 1, "industry_relevance": ["all"], "type": "national", "template_slug": "cny_sg"},
        {"name": "National Day", "month": 8, "industry_relevance": ["all"], "type": "national", "template_slug": "sg_national_day"},
        {"name": "Deepavali", "month": 11, "industry_relevance": ["all"], "type": "national", "template_slug": "deepavali_sg"},
    ],
    "australia": [
        {"name": "Australia Day", "month": 1, "industry_relevance": ["all"], "type": "national", "template_slug": "australia_day"},
        {"name": "Christmas", "month": 12, "industry_relevance": ["all"], "type": "national", "template_slug": "christmas_au"},
        {"name": "EOFY Sale", "month": 6, "industry_relevance": ["retail", "ecommerce"], "type": "commercial", "template_slug": "eofy_sale"},
    ],
    "new_zealand": [
        {"name": "Waitangi Day", "month": 2, "industry_relevance": ["all"], "type": "national", "template_slug": "waitangi_day"},
        {"name": "Christmas", "month": 12, "industry_relevance": ["all"], "type": "national", "template_slug": "christmas_nz"},
    ],
}

# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE TRANSLATION GUIDANCE (Extended for Phase-14 new languages)
# ═══════════════════════════════════════════════════════════════════════════════

TRANSLATION_GUIDANCE: dict[str, str] = {
    "malay": (
        "Translate to natural Bahasa Melayu (Malaysian Malay, Latin script). "
        "Use polite, friendly tone suitable for multi-ethnic Malaysian audience. "
        "Keep brand names and technical terms in English. "
        "Example: 'Free Health Check' → 'Pemeriksaan Kesihatan Percuma'"
    ),
    "bahasa_indonesia": (
        "Translate to modern Bahasa Indonesia (Latin script). "
        "Use warm, community-friendly tone. Keep English technical/brand terms. "
        "Example: 'Special Discount Today Only' → 'Diskon Spesial Hari Ini Saja'"
    ),
    "thai": (
        "Translate to modern Thai script. "
        "Use polite kha/khrap particles appropriately based on context. "
        "Marketing tone should be warm and polite. Keep English brand names. "
        "Example: 'Special Offer' → 'ข้อเสนอพิเศษ'"
    ),
    "marathi": (
        "Translate to natural Marathi (Devanagari script). "
        "Use conversational Marathi tone for Maharashtra market. "
        "Example: 'Free Health Camp' → 'मोफत आरोग्य शिबिर'"
    ),
    "gujarati": (
        "Translate to natural Gujarati (Gujarati script). "
        "Business-friendly, warm tone for Gujarat market. "
        "Example: 'Special Offer Today' → 'આજે વિશેષ ઓફર'"
    ),
    "bengali": (
        "Translate to modern Bengali (Bengali script). "
        "Warm and expressive tone for West Bengal/Bangladesh market. "
        "Example: 'Free Health Camp' → 'বিনামূল্যে স্বাস্থ্য শিবির'"
    ),
    "punjabi": (
        "Translate to Punjabi (Gurmukhi script). "
        "Energetic, warm tone for Punjab market. "
        "Example: 'Special Discount' → 'ਵਿਸ਼ੇਸ਼ ਛੋਟ'"
    ),
}

# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════════════════════════

LanguageMode = Literal["english", "local", "bilingual"]
CountryCode = Literal["IN", "MY", "ID", "TH", "SG", "AU", "NZ"]


class LocalizationContext(BaseModel):
    """Full localization context for a tenant / campaign request."""
    country_code: str = Field(..., description="ISO 3166-1 alpha-2 country code (IN/MY/ID/TH/SG/AU/NZ)")
    state: Optional[str] = Field(None, description="State/province name (critical for India)")
    city: Optional[str] = None
    industry: Optional[str] = "general"
    language_mode: LanguageMode = Field("english", description="english | local | bilingual")
    # Auto-resolved fields (populated by engine)
    primary_language: Optional[str] = None
    secondary_language: Optional[str] = None
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None
    bilingual_required: Optional[bool] = None
    marketing_style: Optional[str] = None


class LocalizedCampaignContent(BaseModel):
    """Bilingual campaign content packet returned by localization engine."""
    country: str
    language_mode: str
    primary_language: str
    secondary_language: Optional[str] = None

    english_headline: str
    local_headline: Optional[str] = None

    english_body: str
    local_body: Optional[str] = None

    english_cta: str
    local_cta: Optional[str] = None

    english_hashtags: list[str] = []
    local_hashtags: list[str] = []

    poster_layout_hint: str = "standard"
    currency_display: str = "USD"


class LocalizedSEOKeywords(BaseModel):
    """SEO keywords localised for a city/country/language."""
    country: str
    city: str
    industry: str
    english_keywords: list[str]
    local_keywords: list[str]
    near_me_keywords: list[str]
    combined_keywords: list[str]


class LocalizedWhatsAppStatus(BaseModel):
    """WhatsApp status bilingual content."""
    english_message: str
    local_message: Optional[str] = None
    cta: str
    language: str


class PosterLayoutSpec(BaseModel):
    """Poster layout specification adjusted for country/language."""
    country_code: str
    language_mode: str
    has_local_script: bool
    layout_style: str              # standard | bilingual_stack | bilingual_side
    headline_size: str             # large | medium
    show_local_headline: bool
    show_local_cta: bool
    rtl: bool = False
    font_hint: str = "Noto Sans"
    industry_color_palette: dict = {}


# ═══════════════════════════════════════════════════════════════════════════════
# LOCALIZATION ENGINE — CORE CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class LocalizationEngine:
    """
    Central localization engine for SRP Marketing OS (Phase 14).

    This engine is additive and wraps / extends existing services without
    modifying them.
    """

    # ── Country Resolution ──────────────────────────────────────────────

    @staticmethod
    def get_country_config(country_code: str) -> dict:
        """Return country configuration by ISO code."""
        code = country_code.upper()
        if code not in COUNTRIES:
            raise ValueError(f"Unsupported country code: {code}. Supported: {list(COUNTRIES.keys())}")
        return COUNTRIES[code]

    @staticmethod
    def get_supported_countries() -> list[dict]:
        """Return list of all supported countries with metadata."""
        return [
            {"code": k, **{key: v for key, v in v.items()}}
            for k, v in COUNTRIES.items()
        ]

    # ── Language Resolution ─────────────────────────────────────────────

    @staticmethod
    def resolve_language_for_india(state: Optional[str]) -> str:
        """Resolve regional language for an Indian state."""
        if not state:
            return "hindi"
        return INDIA_STATE_LANGUAGE_MAP.get(state, "hindi")

    @classmethod
    def resolve_languages(cls, country_code: str, state: Optional[str] = None) -> dict[str, Optional[str]]:
        """
        Resolve primary + secondary language for a given country/state.
        Returns:
          primary_language: always english for non-India English-only
          secondary_language: local language or None
        """
        config = cls.get_country_config(country_code)

        if config["english_only"]:
            return {"primary_language": "english", "secondary_language": None}

        secondary = config.get("secondary_language")
        if country_code == "IN":
            secondary = cls.resolve_language_for_india(state)

        return {"primary_language": "english", "secondary_language": secondary}

    @classmethod
    def build_localization_context(
        cls,
        country_code: str,
        state: Optional[str] = None,
        city: Optional[str] = None,
        industry: Optional[str] = "general",
        language_mode: LanguageMode = "english",
    ) -> LocalizationContext:
        """Build a full LocalizationContext for a campaign request."""
        config = cls.get_country_config(country_code)
        langs = cls.resolve_languages(country_code, state)

        bilingual = (
            language_mode == "bilingual"
            and config["bilingual_supported"]
            and langs["secondary_language"] is not None
        )

        return LocalizationContext(
            country_code=country_code,
            state=state,
            city=city,
            industry=industry,
            language_mode=language_mode,
            primary_language=langs["primary_language"],
            secondary_language=langs["secondary_language"] if bilingual or language_mode == "local" else None,
            currency_code=config["currency_code"],
            currency_symbol=config["currency_symbol"],
            bilingual_required=bilingual,
            marketing_style=config["marketing_style"],
        )

    # ── AI Prompt Generation ────────────────────────────────────────────

    @classmethod
    def build_campaign_prompt(
        cls,
        context: LocalizationContext,
        campaign_type: str,
        org_name: str = "",
        additional_details: Optional[dict] = None,
    ) -> str:
        """
        Build a structured AI prompt for bilingual campaign generation
        that feeds into the existing AI service.
        """
        config = cls.get_country_config(context.country_code)
        country_name = config["name"]
        style = config["marketing_style"]

        location_str = ", ".join(filter(None, [context.city, context.state, country_name]))

        details = additional_details or {}
        detail_lines = "\n".join([f"- {k}: {v}" for k, v in details.items()])

        if context.bilingual_required and context.secondary_language:
            lang_config = GLOBAL_LANGUAGES.get(context.secondary_language, {})
            sec_lang_name = lang_config.get("name", context.secondary_language)
            translation_note = (
                TRANSLATION_GUIDANCE.get(context.secondary_language)
                or f"Translate to {sec_lang_name}."
            )

            prompt = f"""You are a professional marketing copywriter specializing in {country_name} markets.

Generate BILINGUAL marketing content for a {campaign_type} campaign.

CONTEXT:
- Location: {location_str}
- Organization: {org_name or 'the business'}
- Industry: {context.industry}
- Language Mode: Bilingual (English + {sec_lang_name})
- Marketing Style: {style}
{detail_lines}

OUTPUT FORMAT (JSON):
{{
  "english_headline": "...",
  "local_headline": "... (in {sec_lang_name})",
  "english_body": "2-3 sentence campaign description",
  "local_body": "... (in {sec_lang_name})",
  "english_cta": "Clear action phrase",
  "local_cta": "... (in {sec_lang_name})",
  "english_hashtags": ["#tag1", "#tag2", "#tag3"],
  "local_hashtags": ["#localtag1", "#localtag2"],
  "poster_layout_hint": "bilingual_stack"
}}

TRANSLATION GUIDANCE:
{translation_note}

Keep it culturally appropriate, punchy, and action-oriented."""
        else:
            prompt = f"""You are a professional marketing copywriter specializing in {country_name} markets.

Generate marketing content for a {campaign_type} campaign.

CONTEXT:
- Location: {location_str}
- Organization: {org_name or 'the business'}
- Industry: {context.industry}
- Language: English only
- Marketing Style: {style}
{detail_lines}

OUTPUT FORMAT (JSON):
{{
  "english_headline": "...",
  "local_headline": null,
  "english_body": "2-3 sentence campaign description",
  "local_body": null,
  "english_cta": "Clear action phrase",
  "local_cta": null,
  "english_hashtags": ["#tag1", "#tag2", "#tag3"],
  "local_hashtags": [],
  "poster_layout_hint": "standard"
}}

Keep it culturally appropriate, punchy, and action-oriented."""

        return prompt

    # ── SEO Keywords ────────────────────────────────────────────────────

    @classmethod
    def generate_seo_keywords(
        cls,
        country_code: str,
        city: str,
        industry: str,
        state: Optional[str] = None,
        secondary_language: Optional[str] = None,
    ) -> LocalizedSEOKeywords:
        """
        Generate localized SEO keyword patterns for a city/country/industry.
        Returns structured keyword sets for English + local language.
        """
        config = cls.get_country_config(country_code)
        country_name = config["name"]

        # English keyword patterns
        english_keywords = [
            f"best {industry} in {city}",
            f"top {industry} {city}",
            f"{industry} services {city}",
            f"{industry} {city} {state}" if state else f"{industry} {city} {country_name}",
            f"affordable {industry} {city}",
            f"{industry} specialist {city}",
            f"trusted {industry} {city}",
            f"{city} {industry} offers",
            f"{industry} deals {city}",
        ]

        near_me_keywords = [
            f"{industry} near me",
            f"best {industry} near me",
            f"{industry} near {city}",
            f"nearest {industry} {city}",
            f"{industry} open now {city}",
        ]

        # Local language keyword patterns
        local_keywords: list[str] = []
        if secondary_language:
            local_keyword_templates = {
                "telugu": [
                    f"బెస్ట్ {industry} {city}లో",
                    f"{city}లో {industry} సేవలు",
                    f"{industry} దగ్గర {city}",
                ],
                "hindi": [
                    f"{city} में बेस्ट {industry}",
                    f"{city} के पास {industry}",
                    f"सबसे अच्छा {industry} {city} में",
                ],
                "tamil": [
                    f"{city}ல் சிறந்த {industry}",
                    f"{city} {industry} சேவைகள்",
                ],
                "kannada": [
                    f"{city}ನಲ್ಲಿ ಅತ್ಯುತ್ತಮ {industry}",
                    f"{city} {industry} ಸೇವೆಗಳು",
                ],
                "malayalam": [
                    f"{city}ൽ മികച്ച {industry}",
                    f"{city} {industry} സേവനങ്ങൾ",
                ],
                "marathi": [
                    f"{city}मध्ये सर्वोत्तम {industry}",
                    f"{city} {industry} सेवा",
                ],
                "malay": [
                    f"{industry} terbaik di {city}",
                    f"kedai {industry} {city}",
                    f"{industry} berhampiran {city}",
                ],
                "bahasa_indonesia": [
                    f"{industry} terbaik di {city}",
                    f"toko {industry} {city}",
                    f"{industry} terdekat {city}",
                ],
                "thai": [
                    f"{industry}ที่ดีที่สุดใน{city}",
                    f"บริการ{industry} {city}",
                ],
            }
            local_keywords = local_keyword_templates.get(secondary_language, [])

        combined = english_keywords + near_me_keywords + local_keywords

        return LocalizedSEOKeywords(
            country=country_name,
            city=city,
            industry=industry,
            english_keywords=english_keywords,
            local_keywords=local_keywords,
            near_me_keywords=near_me_keywords,
            combined_keywords=combined,
        )

    # ── WhatsApp Status ─────────────────────────────────────────────────

    @classmethod
    def build_whatsapp_status_prompt(
        cls,
        context: LocalizationContext,
        campaign_type: str,
        org_name: str,
        offer_details: Optional[str] = None,
    ) -> str:
        """Build AI prompt for bilingual WhatsApp status generation."""
        config = cls.get_country_config(context.country_code)
        country_name = config["name"]
        location_str = ", ".join(filter(None, [context.city, context.state, country_name]))

        if context.bilingual_required and context.secondary_language:
            lang_config = GLOBAL_LANGUAGES.get(context.secondary_language, {})
            sec_lang_name = lang_config.get("name", context.secondary_language)
            translation_note = (
                TRANSLATION_GUIDANCE.get(context.secondary_language)
                or f"Translate to {sec_lang_name}."
            )

            return f"""Generate a bilingual WhatsApp status message for:

Organization: {org_name}
Campaign: {campaign_type}
Location: {location_str}
Offer Details: {offer_details or 'Special promotion'}
Languages: English + {sec_lang_name}

OUTPUT FORMAT:
English Message (2-3 lines, emoji-friendly):
[english message here]

{sec_lang_name} Message:
[local language translation here]

CTA (short, action-oriented):
[CTA in English]

TRANSLATION GUIDANCE: {translation_note}

Keep each section under 200 characters. Use WhatsApp-friendly emojis."""
        else:
            return f"""Generate a WhatsApp status message for:

Organization: {org_name}
Campaign: {campaign_type}
Location: {location_str}
Offer Details: {offer_details or 'Special promotion'}

OUTPUT FORMAT:
Message (2-3 lines, emoji-friendly):
[message here]

CTA (short):
[CTA here]

Max 300 characters total. Use WhatsApp-friendly emojis."""

    # ── Poster Layout ───────────────────────────────────────────────────

    @classmethod
    def get_poster_layout_spec(
        cls,
        context: LocalizationContext,
    ) -> PosterLayoutSpec:
        """Return poster layout specification for a localization context."""
        country_code = context.country_code
        language_mode = context.language_mode
        secondary_language = context.secondary_language

        # Scripts that have non-Latin characters
        non_latin_scripts = {
            "telugu", "hindi", "tamil", "kannada", "malayalam",
            "marathi", "gujarati", "bengali", "punjabi", "thai",
        }

        has_local_script = (
            secondary_language is not None
            and secondary_language in non_latin_scripts
        )

        if language_mode == "bilingual" and secondary_language:
            layout_style = "bilingual_stack"
            show_local_headline = True
            show_local_cta = True
        elif language_mode == "local" and secondary_language:
            layout_style = "local_primary"
            show_local_headline = True
            show_local_cta = True
        else:
            layout_style = "standard"
            show_local_headline = False
            show_local_cta = False

        # Font hints based on script
        font_map = {
            "telugu": "Noto Sans Telugu",
            "hindi": "Noto Sans Devanagari",
            "tamil": "Noto Sans Tamil",
            "kannada": "Noto Sans Kannada",
            "malayalam": "Noto Sans Malayalam",
            "marathi": "Noto Sans Devanagari",
            "gujarati": "Noto Sans Gujarati",
            "bengali": "Noto Sans Bengali",
            "punjabi": "Noto Sans Gurmukhi",
            "thai": "Noto Sans Thai",
            "malay": "Inter",
            "bahasa_indonesia": "Inter",
        }
        font_hint = font_map.get(secondary_language or "", "Inter")

        return PosterLayoutSpec(
            country_code=country_code,
            language_mode=language_mode,
            has_local_script=has_local_script,
            layout_style=layout_style,
            headline_size="large" if not has_local_script else "medium",
            show_local_headline=show_local_headline,
            show_local_cta=show_local_cta,
            rtl=False,
            font_hint=font_hint,
            industry_color_palette=cls._get_industry_palette(context.industry or "general"),
        )

    @staticmethod
    def _get_industry_palette(industry: str) -> dict:
        """Return color palette hint for an industry."""
        palettes = {
            "hospital": {"primary": "#1E3A8A", "accent": "#10B981", "bg": "#F0FDF4"},
            "restaurant": {"primary": "#DC2626", "accent": "#F59E0B", "bg": "#FFF7ED"},
            "real_estate": {"primary": "#1E40AF", "accent": "#0EA5E9", "bg": "#F0F9FF"},
            "education": {"primary": "#7C3AED", "accent": "#A78BFA", "bg": "#F5F3FF"},
            "retail": {"primary": "#EC4899", "accent": "#F43F5E", "bg": "#FFF1F2"},
            "fitness": {"primary": "#16A34A", "accent": "#22C55E", "bg": "#F0FDF4"},
            "beauty": {"primary": "#DB2777", "accent": "#F472B6", "bg": "#FDF4FF"},
            "finance": {"primary": "#0F766E", "accent": "#14B8A6", "bg": "#F0FDFA"},
            "recruitment": {"primary": "#1D4ED8", "accent": "#3B82F6", "bg": "#EFF6FF"},
        }
        return palettes.get(industry, {"primary": "#4F46E5", "accent": "#7C3AED", "bg": "#F5F3FF"})

    # ── Festival Suggestions ────────────────────────────────────────────

    @classmethod
    def get_festival_suggestions(
        cls,
        country_code: str,
        month: Optional[int] = None,
        state: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> list[dict]:
        """Return relevant festival campaign suggestions for a country/month."""
        config = cls.get_country_config(country_code)
        calendar_key = config["festival_calendar"]
        festivals = FESTIVAL_CALENDARS.get(calendar_key, [])

        results = []
        for fest in festivals:
            # Filter by month if provided
            if month is not None and fest.get("month") != month:
                continue
            # Filter by state for India regional festivals
            if fest.get("states") and state and state not in fest["states"]:
                continue
            # Filter by industry relevance
            relevance = fest.get("industry_relevance", ["all"])
            if industry and "all" not in relevance and industry not in relevance:
                continue
            results.append(fest)

        return results

    # ── Currency Formatting ─────────────────────────────────────────────

    @staticmethod
    def format_currency(amount: float, currency_code: str) -> str:
        """Format a price amount for a given currency code."""
        formats = {
            "INR": f"₹{amount:,.0f}",
            "MYR": f"RM {amount:,.2f}",
            "IDR": f"Rp {amount:,.0f}",
            "THB": f"฿{amount:,.0f}",
            "SGD": f"S${amount:,.2f}",
            "AUD": f"A${amount:,.2f}",
            "NZD": f"NZ${amount:,.2f}",
            "USD": f"${amount:,.2f}",
        }
        return formats.get(currency_code.upper(), f"{currency_code} {amount:,.2f}")

    @staticmethod
    def format_usd(amount_usd: float) -> str:
        """Format a price in USD."""
        if amount_usd == 0:
            return "Free"
        return f"${amount_usd:,.0f}"

    # ── Language Mode Validation ────────────────────────────────────────

    @classmethod
    def validate_language_mode(
        cls,
        country_code: str,
        requested_mode: str,
    ) -> str:
        """
        Validate and normalise language mode for a country.
        English-only countries will always return 'english'.
        """
        config = cls.get_country_config(country_code)
        if config["english_only"]:
            return "english"
        if requested_mode not in config["language_modes"]:
            return config["language_modes"][0]  # default to first available
        return requested_mode

    # ── Template Suggestions ────────────────────────────────────────────

    @classmethod
    def get_regional_template_suggestions(
        cls,
        country_code: str,
        industry: str,
        state: Optional[str] = None,
    ) -> list[dict]:
        """Suggest relevant template slugs for a country/industry combination."""
        base_templates = {
            "hospital": ["health_camp", "doctor_consultation", "free_checkup", "specialist_clinic"],
            "restaurant": ["food_offer", "new_menu", "special_discount", "dine_in_offer"],
            "real_estate": ["property_launch", "site_visit", "plot_sale", "apartment_offer"],
            "education": ["admissions_open", "free_demo", "course_offer", "scholarship"],
            "retail": ["grand_sale", "season_offer", "new_arrival", "clearance_sale"],
            "fitness": ["gym_membership", "free_trial", "transformation_challenge"],
            "beauty": ["salon_offer", "bridal_package", "skincare_promo"],
            "recruitment": ["job_opening", "walkin_drive", "fresher_jobs", "career_fair"],
        }

        templates = base_templates.get(industry, ["general_offer", "special_promotion"])

        # Add festival templates from calendar
        config = cls.get_country_config(country_code)
        calendar_key = config["festival_calendar"]
        festival_templates = [
            f["template_slug"]
            for f in FESTIVAL_CALENDARS.get(calendar_key, [])
            if (not f.get("states") or not state or state in (f.get("states") or []))
        ]

        return [
            {"slug": t, "type": "industry", "country": config["name"]}
            for t in templates
        ] + [
            {"slug": t, "type": "festival", "country": config["name"]}
            for t in festival_templates[:5]   # top 5 festival templates
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS (module-level exports)
# ═══════════════════════════════════════════════════════════════════════════════

def get_country_list() -> list[dict]:
    """Return all supported countries for API consumption."""
    return [
        {
            "code": code,
            "name": cfg["name"],
            "currency_code": cfg["currency_code"],
            "currency_symbol": cfg["currency_symbol"],
            "default_language": cfg["default_language"],
            "secondary_language": cfg.get("secondary_language"),
            "bilingual_supported": cfg["bilingual_supported"],
            "language_modes": cfg["language_modes"],
        }
        for code, cfg in COUNTRIES.items()
    ]


def get_language_list() -> list[dict]:
    """Return all supported global languages for API consumption."""
    return [
        {
            "code": lang_key,
            "name": v["name"],
            "iso_code": v["code"],
            "script": v["script"],
            "countries": v.get("countries", []),
        }
        for lang_key, v in GLOBAL_LANGUAGES.items()
    ]


def detect_language_for_tenant(country_code: str, state: Optional[str] = None) -> dict:
    """Quick utility to detect language pair for a tenant profile."""
    engine = LocalizationEngine
    result = engine.resolve_languages(country_code, state)
    return result
