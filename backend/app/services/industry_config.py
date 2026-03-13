"""
Industry & Country Strategy Config — SRP Marketing OS
======================================================

Config-driven strategy mappings for:
  - Industry: campaign objectives, CTA style, tone, trust/urgency balance
  - Country/Locale: language defaults, design style, cultural tone, bilingual defaults

IMPORTANT:  All logic here is pure config — no hardcoded branch logic scattered
            in agents or routers. Consumers query this module to get defaults,
            then override with user input.

Supported Industries:
  hospital_clinic, school_education, restaurant_cafe, retail_shop,
  real_estate, salon_beauty, gym_fitness, digital_agency,
  pharmacy, coaching_institute, event_management, general_business

Supported Countries (Phase 14 scope):
  IN, AU, NZ, MY, SG, ID, TH

Usage:
    from app.services.industry_config import get_industry_config, get_locale_profile

    ind = get_industry_config("hospital_clinic")
    loc = get_locale_profile("IN", state="Telangana")
"""

from __future__ import annotations
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════════
# INDUSTRY STRATEGY CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

INDUSTRY_CONFIG: dict[str, dict] = {

    "hospital_clinic": {
        "label": "Hospital / Clinic",
        "icon": "🏥",
        "default_campaign_objectives": [
            "patient_acquisition",
            "health_camp_promotion",
            "appointment_booking",
            "awareness",
        ],
        "cta_style": "appointment_booking",          # book_now | call_now | appointment_booking | learn_more
        "tone_default": "trust",                     # trust | urgency | promotional | informational
        "trust_vs_urgency": 0.8,                     # 1.0 = pure trust, 0.0 = pure urgency
        "required_fields": ["doctor_name", "services", "phone"],
        "recommended_platforms": ["whatsapp", "facebook", "instagram"],
        "template_families": [
            "orthopedic_health_camp", "diabetes_health_camp", "cardiac_checkup_camp",
            "eye_camp", "dental_camp", "general_health_camp",
        ],
        "default_hashtags_en": ["#HealthCamp", "#FreeCheckup", "#HealthAwareness"],
        "compliance_note": "Avoid absolute medical claims. Use 'may help', 'consult our doctor'.",
        "bilingual_recommended": True,
        "copy_length": "medium",                     # short | medium | long
    },

    "school_education": {
        "label": "School / Education",
        "icon": "🎓",
        "default_campaign_objectives": [
            "admissions",
            "enrollment_boost",
            "event_announcement",
            "brand_awareness",
        ],
        "cta_style": "apply_now",                    # apply_now | register | learn_more | call_now
        "tone_default": "trust",
        "trust_vs_urgency": 0.7,
        "required_fields": ["org_name", "admission_year"],
        "recommended_platforms": ["facebook", "whatsapp", "instagram"],
        "template_families": [
            "coaching_institute", "school_admission", "skill_training", "event_announcement",
        ],
        "default_hashtags_en": ["#Admissions", "#Education", "#SchoolLife"],
        "compliance_note": "Focus on quality and outcomes, not just price.",
        "bilingual_recommended": True,
        "copy_length": "medium",
    },

    "restaurant_cafe": {
        "label": "Restaurant / Cafe",
        "icon": "🍽️",
        "default_campaign_objectives": [
            "foot_traffic",
            "online_orders",
            "special_offer",
            "new_menu_launch",
        ],
        "cta_style": "order_now",
        "tone_default": "promotional",
        "trust_vs_urgency": 0.4,
        "required_fields": ["org_name", "offer_price"],
        "recommended_platforms": ["instagram", "facebook", "whatsapp"],
        "template_families": ["restaurant_offer", "hotel_event"],
        "default_hashtags_en": ["#FoodLovers", "#TasteOfIndia", "#SpecialOffer"],
        "compliance_note": None,
        "bilingual_recommended": True,
        "copy_length": "short",
    },

    "retail_shop": {
        "label": "Retail / Shop",
        "icon": "🛍️",
        "default_campaign_objectives": [
            "sale_conversion",
            "foot_traffic",
            "product_launch",
            "clearance",
        ],
        "cta_style": "shop_now",
        "tone_default": "urgency",
        "trust_vs_urgency": 0.3,
        "required_fields": ["org_name", "offer_price"],
        "recommended_platforms": ["instagram", "facebook", "whatsapp"],
        "template_families": ["retail_discount", "garment_sale", "electronics_sale", "furniture_sale"],
        "default_hashtags_en": ["#Sale", "#MegaSale", "#ShopNow"],
        "compliance_note": None,
        "bilingual_recommended": True,
        "copy_length": "short",
    },

    "real_estate": {
        "label": "Real Estate",
        "icon": "🏠",
        "default_campaign_objectives": [
            "property_enquiry",
            "site_visit",
            "launch_awareness",
            "resale_listing",
        ],
        "cta_style": "book_site_visit",
        "tone_default": "trust",
        "trust_vs_urgency": 0.75,
        "required_fields": ["org_name", "location", "price"],
        "recommended_platforms": ["facebook", "instagram", "linkedin"],
        "template_families": ["real_estate_launch", "rental_property"],
        "default_hashtags_en": ["#RealEstate", "#NewLaunch", "#PropertyInvestment"],
        "compliance_note": "RERA compliance — include RERA number where applicable.",
        "bilingual_recommended": True,
        "copy_length": "medium",
    },

    "salon_beauty": {
        "label": "Salon / Beauty",
        "icon": "💅",
        "default_campaign_objectives": [
            "appointment_booking",
            "package_promotion",
            "seasonal_offer",
            "new_service_launch",
        ],
        "cta_style": "book_now",
        "tone_default": "promotional",
        "trust_vs_urgency": 0.5,
        "required_fields": ["org_name", "services"],
        "recommended_platforms": ["instagram", "facebook", "whatsapp"],
        "template_families": ["beauty_salon", "spa_wellness"],
        "default_hashtags_en": ["#BeautySalon", "#SpecialOffer", "#BookNow"],
        "compliance_note": None,
        "bilingual_recommended": False,
        "copy_length": "short",
    },

    "gym_fitness": {
        "label": "Gym / Fitness",
        "icon": "💪",
        "default_campaign_objectives": [
            "membership_sales",
            "free_trial",
            "event_bootcamp",
            "challenge_launch",
        ],
        "cta_style": "join_now",
        "tone_default": "urgency",
        "trust_vs_urgency": 0.4,
        "required_fields": ["org_name"],
        "recommended_platforms": ["instagram", "facebook"],
        "template_families": ["gym_offer"],
        "default_hashtags_en": ["#FitnessGoals", "#GymLife", "#JoinNow"],
        "compliance_note": None,
        "bilingual_recommended": False,
        "copy_length": "short",
    },

    "digital_agency": {
        "label": "Digital Agency / Tech Services",
        "icon": "💻",
        "default_campaign_objectives": [
            "lead_generation",
            "portfolio_showcase",
            "service_launch",
            "thought_leadership",
        ],
        "cta_style": "get_quote",
        "tone_default": "professional",
        "trust_vs_urgency": 0.65,
        "required_fields": ["org_name", "service_name"],
        "recommended_platforms": ["linkedin", "instagram", "facebook"],
        "template_families": ["event_announcement", "skill_training"],
        "default_hashtags_en": ["#DigitalMarketing", "#WebDesign", "#GrowthHacking"],
        "compliance_note": None,
        "bilingual_recommended": False,
        "copy_length": "medium",
    },

    "pharmacy": {
        "label": "Pharmacy / Medicine Retail",
        "icon": "💊",
        "default_campaign_objectives": [
            "discount_promotion",
            "health_awareness",
            "seasonal_offer",
        ],
        "cta_style": "visit_now",
        "tone_default": "trust",
        "trust_vs_urgency": 0.7,
        "required_fields": ["org_name", "offer_price"],
        "recommended_platforms": ["whatsapp", "facebook"],
        "template_families": ["pharmacy_sale"],
        "default_hashtags_en": ["#Pharmacy", "#HealthOffer", "#MedicineSale"],
        "compliance_note": "Do not make medical claims. Stick to product/pricing offers.",
        "bilingual_recommended": True,
        "copy_length": "short",
    },

    "coaching_institute": {
        "label": "Coaching / Training Institute",
        "icon": "📚",
        "default_campaign_objectives": [
            "enrollment",
            "batch_launch",
            "free_demo",
            "results_showcase",
        ],
        "cta_style": "enroll_now",
        "tone_default": "trust",
        "trust_vs_urgency": 0.6,
        "required_fields": ["org_name", "services"],
        "recommended_platforms": ["facebook", "instagram", "whatsapp"],
        "template_families": ["coaching_institute", "skill_training"],
        "default_hashtags_en": ["#Coaching", "#Admissions", "#StudyWithUs"],
        "compliance_note": None,
        "bilingual_recommended": True,
        "copy_length": "medium",
    },

    "event_management": {
        "label": "Events / Programmes",
        "icon": "🎪",
        "default_campaign_objectives": [
            "ticket_sales",
            "registration",
            "awareness",
        ],
        "cta_style": "register_now",
        "tone_default": "urgency",
        "trust_vs_urgency": 0.45,
        "required_fields": ["org_name", "date_range"],
        "recommended_platforms": ["facebook", "instagram", "whatsapp"],
        "template_families": ["event_announcement", "walkin_drive"],
        "default_hashtags_en": ["#Event", "#RegisterNow", "#DontMissOut"],
        "compliance_note": None,
        "bilingual_recommended": True,
        "copy_length": "medium",
    },

    "general_business": {
        "label": "General Local Business",
        "icon": "🏪",
        "default_campaign_objectives": [
            "brand_awareness",
            "promotional_offer",
            "foot_traffic",
        ],
        "cta_style": "contact_us",
        "tone_default": "promotional",
        "trust_vs_urgency": 0.5,
        "required_fields": ["org_name"],
        "recommended_platforms": ["facebook", "instagram", "whatsapp"],
        "template_families": ["retail_discount", "event_announcement"],
        "default_hashtags_en": ["#LocalBusiness", "#SpecialOffer"],
        "compliance_note": None,
        "bilingual_recommended": False,
        "copy_length": "short",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# LOCALE / MARKET PROFILES
# ═══════════════════════════════════════════════════════════════════════════════

LOCALE_PROFILES: dict[str, dict] = {

    "IN": {
        "name": "India",
        "content_formality": "warm_formal",
        "design_style": "vibrant",
        "text_density": "high",
        "cta_tone": "direct_action",
        "cultural_sensitivities": [
            "family_values",
            "trust_in_authority",
            "community_pride",
        ],
        "bilingual_default": True,
        "trilingual_possible": True,
        "default_language_mode": "bilingual",
        "primary_language": "english",
        "cta_examples": {
            "hospital": "Book Free Checkup Now",
            "education": "Secure Your Seat Today",
            "retail": "Grab This Offer Now",
        },
        "state_profiles": {
            "Telangana":        {"secondary_language": "telugu",  "formality": "warm", "cta_style": "direct"},
            "Andhra Pradesh":   {"secondary_language": "telugu",  "formality": "warm", "cta_style": "direct"},
            "Tamil Nadu":       {"secondary_language": "tamil",   "formality": "formal", "cta_style": "respectful"},
            "Karnataka":        {"secondary_language": "kannada", "formality": "warm", "cta_style": "direct"},
            "Kerala":           {"secondary_language": "malayalam", "formality": "formal", "cta_style": "professional"},
            "Maharashtra":      {"secondary_language": "marathi", "formality": "warm", "cta_style": "energetic"},
            "Gujarat":          {"secondary_language": "gujarati", "formality": "business", "cta_style": "value-focused"},
            "Delhi":            {"secondary_language": "hindi",   "formality": "semi-formal", "cta_style": "urgency"},
            "Uttar Pradesh":    {"secondary_language": "hindi",   "formality": "formal", "cta_style": "community"},
            "Punjab":           {"secondary_language": "punjabi", "formality": "energetic", "cta_style": "bold"},
            "West Bengal":      {"secondary_language": "bengali", "formality": "warm", "cta_style": "cultural"},
        },
    },

    "AU": {
        "name": "Australia",
        "content_formality": "casual_professional",
        "design_style": "clean_minimal",
        "text_density": "low",
        "cta_tone": "friendly_direct",
        "cultural_sensitivities": ["anti-hype", "straightforward", "no-exaggeration"],
        "bilingual_default": False,
        "trilingual_possible": False,
        "default_language_mode": "english",
        "primary_language": "english",
        "cta_examples": {
            "hospital": "Book Now",
            "education": "Enrol Today",
            "retail": "Shop the Sale",
        },
        "state_profiles": {
            "New South Wales":  {"formality": "professional", "cta_style": "direct"},
            "Victoria":         {"formality": "professional", "cta_style": "direct"},
            "Queensland":       {"formality": "casual", "cta_style": "friendly"},
            "Western Australia": {"formality": "casual", "cta_style": "outdoor-friendly"},
        },
    },

    "NZ": {
        "name": "New Zealand",
        "content_formality": "friendly_community",
        "design_style": "clean_natural",
        "text_density": "low",
        "cta_tone": "community_driven",
        "cultural_sensitivities": ["Māori_respect", "eco_values", "community_trust"],
        "bilingual_default": False,
        "trilingual_possible": False,
        "default_language_mode": "english",
        "primary_language": "english",
        "cta_examples": {
            "hospital": "Book an Appointment",
            "education": "Apply Now",
            "retail": "Shop Now",
        },
        "state_profiles": {},
    },

    "MY": {
        "name": "Malaysia",
        "content_formality": "warm_multicultural",
        "design_style": "modern_vibrant",
        "text_density": "medium",
        "cta_tone": "polite_direct",
        "cultural_sensitivities": [
            "multicultural_respect",
            "halal_awareness",
            "multi_ethnic_inclusivity",
        ],
        "bilingual_default": True,
        "trilingual_possible": True,
        "default_language_mode": "bilingual",
        "primary_language": "english",
        "secondary_language_default": "malay",
        "cta_examples": {
            "hospital": "Book Your Appointment",
            "education": "Daftar Sekarang",    # Register Now in Malay
            "retail": "Dapatkan Tawaran Ini",  # Get This Offer in Malay
        },
        "state_profiles": {
            "Kuala Lumpur":  {"secondary_language": "malay", "formality": "professional"},
            "Selangor":      {"secondary_language": "malay", "formality": "warm"},
            "Penang":        {"secondary_language": "malay", "formality": "multicultural"},
            "Johor":         {"secondary_language": "malay", "formality": "warm"},
            "Sabah":         {"secondary_language": "malay", "formality": "community"},
            "Sarawak":       {"secondary_language": "malay", "formality": "community"},
        },
    },

    "SG": {
        "name": "Singapore",
        "content_formality": "professional_concise",
        "design_style": "premium_clean",
        "text_density": "low",
        "cta_tone": "efficient_direct",
        "cultural_sensitivities": [
            "multi_ethnic_sensitivity",
            "professional_image",
            "no_excessive_claims",
        ],
        "bilingual_default": False,
        "trilingual_possible": False,
        "default_language_mode": "english",
        "primary_language": "english",
        "cta_examples": {
            "hospital": "Book Now",
            "education": "Apply Today",
            "retail": "Shop Now",
        },
        "state_profiles": {},
    },

    "ID": {
        "name": "Indonesia",
        "content_formality": "warm_community",
        "design_style": "bold_mobile_friendly",
        "text_density": "medium",
        "cta_tone": "community_warm",
        "cultural_sensitivities": [
            "halal_awareness",
            "community_respect",
            "family_values",
        ],
        "bilingual_default": True,
        "trilingual_possible": False,
        "default_language_mode": "bilingual",
        "primary_language": "english",
        "secondary_language_default": "bahasa_indonesia",
        "cta_examples": {
            "hospital": "Daftar Sekarang",
            "education": "Daftar Sekarang",
            "retail": "Beli Sekarang",
        },
        "state_profiles": {
            "Jakarta":       {"secondary_language": "bahasa_indonesia", "formality": "modern"},
            "Surabaya":      {"secondary_language": "bahasa_indonesia", "formality": "community"},
            "Bali":          {"secondary_language": "bahasa_indonesia", "formality": "tourism_friendly"},
        },
    },

    "TH": {
        "name": "Thailand",
        "content_formality": "polite_warm",
        "design_style": "visual_heavy_colorful",
        "text_density": "medium",
        "cta_tone": "polite_direct",
        "cultural_sensitivities": [
            "royalty_respect",
            "politeness_hierarchy",
            "festive_seasonal",
        ],
        "bilingual_default": True,
        "trilingual_possible": False,
        "default_language_mode": "bilingual",
        "primary_language": "english",
        "secondary_language_default": "thai",
        "cta_examples": {
            "hospital": "จองเลย",   # Book Now in Thai
            "education": "สมัครเลย",
            "retail": "ซื้อเลย",
        },
        "state_profiles": {
            "Bangkok":       {"secondary_language": "thai", "formality": "modern"},
            "Chiang Mai":    {"secondary_language": "thai", "formality": "community"},
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# CULTURAL CONTEXT STYLES
# ═══════════════════════════════════════════════════════════════════════════════

CULTURAL_STYLES: dict[str, dict] = {
    "formal": {
        "tone": "Formal and respectful. Use complete sentences. Avoid slang.",
        "cta_modifier": "professional",
        "emoji_use": "none",
    },
    "modern": {
        "tone": "Modern, clean, and direct. Short sentences. Confident.",
        "cta_modifier": "action-forward",
        "emoji_use": "minimal",
    },
    "premium": {
        "tone": "Premium, aspirational, and exclusive. Avoid discount language.",
        "cta_modifier": "experience-focused",
        "emoji_use": "none",
    },
    "community_trust": {
        "tone": "Community-friendly, warm, and local. Emphasise familiarity and trust.",
        "cta_modifier": "inclusive",
        "emoji_use": "moderate",
    },
    "festive": {
        "tone": "Festive, celebratory, and joyful. Use seasonal imagery and greetings.",
        "cta_modifier": "celebratory",
        "emoji_use": "moderate",
    },
    "family_oriented": {
        "tone": "Family-centric, caring, and values-driven.",
        "cta_modifier": "caring",
        "emoji_use": "light",
    },
    "institutional": {
        "tone": "Institutional, authoritative, and informative.",
        "cta_modifier": "informational",
        "emoji_use": "none",
    },
    "local_retail": {
        "tone": "Local, energetic, and price-focused. FOMO-driven.",
        "cta_modifier": "urgency",
        "emoji_use": "moderate",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_industry_config(industry: str) -> dict:
    """
    Return strategy config for the given industry slug.
    Falls back to 'general_business' if not found.
    """
    return INDUSTRY_CONFIG.get(industry, INDUSTRY_CONFIG["general_business"])


def get_locale_profile(
    country_code: str,
    state: Optional[str] = None,
) -> dict:
    """
    Return the locale profile for a country (and optionally state).
    Falls back to a sensible default if not found.
    """
    profile = LOCALE_PROFILES.get(country_code.upper(), LOCALE_PROFILES["SG"])  # SG = clean default
    if state and "state_profiles" in profile:
        state_data = profile["state_profiles"].get(state, {})
        # Merge state-level overrides into profile copy
        merged = dict(profile)
        merged["active_state"] = state
        merged["state_overrides"] = state_data
        if "secondary_language" in state_data:
            merged["secondary_language_default"] = state_data["secondary_language"]
        return merged
    return profile


def get_cultural_style(style_key: str) -> dict:
    """Return cultural style configuration."""
    return CULTURAL_STYLES.get(style_key, CULTURAL_STYLES["modern"])


def list_industries() -> list[dict]:
    """List all supported industries with label and icon."""
    return [
        {
            "slug": k,
            "label": v["label"],
            "icon": v["icon"],
            "cta_style": v["cta_style"],
            "tone_default": v["tone_default"],
            "bilingual_recommended": v["bilingual_recommended"],
        }
        for k, v in INDUSTRY_CONFIG.items()
    ]


def list_locales() -> list[dict]:
    """List all supported locale profiles."""
    return [
        {
            "country_code": k,
            "name": v["name"],
            "design_style": v["design_style"],
            "bilingual_default": v["bilingual_default"],
            "default_language_mode": v["default_language_mode"],
        }
        for k, v in LOCALE_PROFILES.items()
    ]


def get_template_suggestions(
    industry: str,
    country_code: str,
    campaign_type: Optional[str] = None,
) -> list[str]:
    """
    Return recommended template slugs for a given industry + country combination.
    """
    ind_cfg = get_industry_config(industry)
    templates = list(ind_cfg.get("template_families", []))

    # Country-specific overrides
    if country_code in ("AU", "NZ", "SG"):
        # Prefer cleaner templates for English-only professional markets
        # Filter out health camp templates for non-healthcare
        if industry not in ("hospital_clinic", "pharmacy"):
            templates = [t for t in templates if "camp" not in t]

    return templates if templates else ["retail_discount"]
