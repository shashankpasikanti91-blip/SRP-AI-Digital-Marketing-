"""
Language Service — bilingual / trilingual campaign content generation.

Supported language pairs (India):
  english + telugu    (Andhra Pradesh / Telangana)
  english + hindi     (North India / national)
  english + tamil     (Tamil Nadu)
  english + kannada   (Karnataka)
  english + malayalam (Kerala)
  english + bengali   (West Bengal)
  english + marathi   (Maharashtra)
  english + gujarati  (Gujarat)
  english + punjabi   (Punjab)
  english + odia      (Odisha)

Supported language pairs (SE Asia / Oceania):
  english + malay          (Malaysia / Brunei)
  english + chinese_simplified  (Malaysia / Singapore)
  english + indonesian     (Indonesia)
  english + thai           (Thailand)

AI is used ONLY for:
  - headline generation
  - translation to regional language
  - CTA writing
  - campaign summary

NOT used for visual layout — that comes from PosterTemplate.

IMPORTANT: Any translation failure is handled gracefully.
  - Primary provider: OpenAI (gpt-4o-mini) — most reliable for multilingual
  - Fallback provider: OpenRouter
  - On failure: clean English-only output (no error text in poster fields)
"""

import json
import logging
from typing import Literal

from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

# ── Supported Language Codes ───────────────────────────────────────────

SUPPORTED_LANGUAGES = {
    # ── Indian Languages ─────────────────────────────────────────────
    "english":    {"name": "English",       "code": "en", "script": "Latin"},
    "telugu":     {"name": "Telugu",        "code": "te", "script": "Telugu",      "region": "Telangana/AP"},
    "hindi":      {"name": "Hindi",         "code": "hi", "script": "Devanagari",  "region": "North India"},
    "tamil":      {"name": "Tamil",         "code": "ta", "script": "Tamil",       "region": "Tamil Nadu"},
    "kannada":    {"name": "Kannada",       "code": "kn", "script": "Kannada",     "region": "Karnataka"},
    "malayalam":  {"name": "Malayalam",     "code": "ml", "script": "Malayalam",   "region": "Kerala"},
    "bengali":    {"name": "Bengali",       "code": "bn", "script": "Bengali",     "region": "West Bengal"},
    "marathi":    {"name": "Marathi",       "code": "mr", "script": "Devanagari",  "region": "Maharashtra"},
    "gujarati":   {"name": "Gujarati",      "code": "gu", "script": "Gujarati",    "region": "Gujarat"},
    "punjabi":    {"name": "Punjabi",       "code": "pa", "script": "Gurmukhi",    "region": "Punjab"},
    "odia":       {"name": "Odia",          "code": "or", "script": "Odia",        "region": "Odisha"},
    # ── South-East Asia / Oceania ─────────────────────────────────────
    "malay":              {"name": "Bahasa Melayu",      "code": "ms", "script": "Latin",    "region": "Malaysia/Brunei"},
    "indonesian":         {"name": "Bahasa Indonesia",   "code": "id", "script": "Latin",    "region": "Indonesia"},
    "thai":               {"name": "Thai",               "code": "th", "script": "Thai",     "region": "Thailand"},
    "chinese_simplified": {"name": "Chinese (Simplified)", "code": "zh", "script": "Han",   "region": "Malaysia/Singapore/China"},
}

RegionalLanguage = Literal[
    "telugu", "hindi", "tamil", "kannada", "malayalam",
    "bengali", "marathi", "gujarati", "punjabi", "odia",
    "malay", "indonesian", "thai", "chinese_simplified",
]


# ── Bilingual Content Models ───────────────────────────────────────────

class BilingualBlock(BaseModel):
    english: str
    regional: str
    language: str


class BilingualCampaignContent(BaseModel):
    """Complete bilingual content package for a campaign poster."""
    language: str                        # e.g. "telugu"

    # Title / headline
    english_title: str
    regional_title: str

    # Subtitle
    english_subtitle: str
    regional_subtitle: str

    # Badge text (e.g. FREE CHECKUP / FLAT 40% OFF)
    english_badge: str
    regional_badge: str

    # Services / checklist items
    english_services: list[str]
    regional_services: list[str]

    # Offer / price block
    offer_line_english: str = ""
    offer_line_regional: str = ""

    # Date / event info
    date_line_english: str = ""
    date_line_regional: str = ""

    # CTA
    english_cta: str
    regional_cta: str

    # Social caption (for post body)
    social_caption_english: str
    social_caption_regional: str
    hashtags: list[str]

    # Campaign summary
    summary: str


class CampaignContentInput(BaseModel):
    """Dynamic inputs that vary per campaign — city, doctor, dates, etc."""
    template_slug: str              # orthopedic_health_camp | walkin_drive | ...
    industry: str                   # hospital | recruitment | restaurant | ...

    # Location
    city: str
    locality: str | None = None
    state: str = "Telangana"

    # Campaign specifics
    department: str | None = None          # "Orthopaedics" | "Cardiology"
    doctor_name: str | None = None         # "Dr. Ramana Reddy"
    doctor_qualification: str | None = None  # "MS Ortho, AIIMS"

    # Dates
    date_range: str | None = None          # "15th - 20th March 2026"
    event_time: str | None = None          # "9 AM - 5 PM"

    # Offer pricing
    offer_price: str | None = None         # "₹299"
    original_price: str | None = None      # "₹1,500"

    # Services / checklist
    services: list[str] | None = None      # ["X-Ray", "Consultation", "Physiotherapy"]

    # Job / recruitment specifics
    job_title: str | None = None
    vacancies: str | None = None
    salary_range: str | None = None
    experience: str | None = None

    # Brand info
    org_name: str = ""
    phone: str = ""

    # Language settings
    primary_language: str = "english"
    secondary_language: RegionalLanguage | None = None


# ── Language Service ───────────────────────────────────────────────────

class LanguageService:

    # ── Translation context by language ───────────────────────────────

    TRANSLATION_GUIDANCE = {
        # ── Indian Languages ────────────────────────────────────────────
        "telugu": (
            "CRITICAL SCRIPT RULE: Use ONLY Telugu Unicode script (U+0C00–U+0C7F). "
            "This is a HARD REQUIREMENT — NEVER use Hindi/Devanagari (U+0900–U+097F) for any Telugu field. "
            "The city (e.g. Nagpur, Pune, Mumbai) does NOT determine the script — Telugu ALWAYS uses Telugu script. "
            "Translate to natural spoken Telugu used in Telangana/Andhra Pradesh. "
            "Keep medical/technical terms readable (e.g. X-Ray stays as X-Ray). Warm and community-friendly tone. "
            "Examples: 'ఉచిత ఆరోగ్య శిబిరం', 'మహా సేల్', 'ఈరోజే కొనండి', 'భారీ తగ్గింపు', 'ఇప్పుడే కాల్ చేయండి'."
        ),
        "hindi": (
            "SCRIPT RULE: Use ONLY Hindi Devanagari script (U+0900–U+097F). "
            "Translate to clear, conversational Hindi. "
            "Prefer common words over formal Sanskrit. Keep English brand names intact. "
            "Example: 'Free Health Camp' → 'निःशुल्क स्वास्थ्य शिविर'"
        ),
        "tamil": (
            "SCRIPT RULE: Use ONLY Tamil Unicode script (U+0B80–U+0BFF). NEVER use Devanagari. "
            "Translate to modern Tamil used in Tamil Nadu. "
            "Keep medical and technical terms in English where commonly understood. "
            "Example: 'Free Health Camp' → 'இலவச உடல்நல முகாம்'"
        ),
        "kannada": (
            "SCRIPT RULE: Use ONLY Kannada Unicode script (U+0C80–U+0CFF). NEVER use Devanagari. "
            "Translate to natural Kannada used in Karnataka. "
            "Example: 'Free Health Camp' → 'ಉಚಿತ ಆರೋಗ್ಯ ಶಿಬಿರ'"
        ),
        "malayalam": (
            "SCRIPT RULE: Use ONLY Malayalam Unicode script (U+0D00–U+0D7F). NEVER use Devanagari. "
            "Translate to natural Malayalam used in Kerala. "
            "Example: 'Free Health Camp' → 'സൗജന്യ ആരോഗ്യ ക്യാമ്പ്'"
        ),
        "bengali": (
            "SCRIPT RULE: Use ONLY Bengali/Bangla Unicode script (U+0980–U+09FF). NEVER use Devanagari. "
            "Translate to standard Bengali used in West Bengal. Keep brand and technical terms intact. "
            "Example: 'Free Health Camp' → 'বিনামূল্যে স্বাস্থ্য শিবির'"
        ),
        "marathi": (
            "SCRIPT RULE: Use Marathi Devanagari script. You are writing Marathi, NOT Hindi. "
            "Translate to natural spoken Marathi used in Maharashtra. "
            "Example: 'Free Health Camp' → 'मोफत आरोग्य शिबिर'"
        ),
        "gujarati": (
            "SCRIPT RULE: Use ONLY Gujarati Unicode script (U+0A80–U+0AFF). NEVER use Devanagari. "
            "Translate to natural Gujarati used in Gujarat. "
            "Example: 'Free Health Camp' → 'મફત આરોગ્ય કેમ્પ'"
        ),
        "punjabi": (
            "SCRIPT RULE: Use ONLY Gurmukhi Unicode script (U+0A00–U+0A7F). NEVER use Devanagari. "
            "Translate to Punjabi used in Punjab, India. "
            "Example: 'Free Health Camp' → 'ਮੁਫਤ ਸਿਹਤ ਕੈਂਪ'"
        ),
        "odia": (
            "SCRIPT RULE: Use ONLY Odia Unicode script (U+0B00–U+0B7F). NEVER use Devanagari. "
            "Translate to natural Odia used in Odisha. "
            "Example: 'Free Health Camp' → 'ମୁଫ୍ତ ସ୍ୱାସ୍ଥ୍ୟ ଶିବିର'"
        ),
        # ── South-East Asia / Oceania ───────────────────────────────────
        "malay": (
            "Translate to standard Bahasa Melayu used in Malaysia. "
            "Use formal but accessible Malay. Keep English brand names, medical terms, and short "
            "technical words intact. Use Latin script. "
            "Example: 'Free Health Camp' → 'Kamp Kesihatan Percuma'"
        ),
        "indonesian": (
            "Translate to standard Bahasa Indonesia as used in Indonesia. "
            "Keep it clear, modern, and accessible. Latin script. "
            "Keep English brand names and technical terms when widely used. "
            "Example: 'Free Health Camp' → 'Kamp Kesehatan Gratis'"
        ),
        "thai": (
            "Translate to standard Thai (Thai script) suitable for professional marketing. "
            "Be polite and respectful. Keep English product/brand names as-is. "
            "Example: 'Free Health Camp' → 'ค่ายสุขภาพฟรี'"
        ),
        "chinese_simplified": (
            "Translate to Simplified Chinese (简体中文) appropriate for Malaysia/Singapore audience. "
            "Use clear, concise business/marketing language. Keep medical terms readable. "
            "Example: 'Free Health Camp' → '免费健康营'"
        ),
    }

    # ── Template content generators (English base) ────────────────────

    TEMPLATE_PROMPTS = {
        "orthopedic_health_camp": {
            "title_hint": "Create a compelling event title for a free orthopaedic health camp",
            "badge": "FREE CHECKUP",
            "services_default": ["Orthopaedic Consultation", "X-Ray", "Physiotherapy Session", "Bone Density Test"],
        },
        "diabetes_health_camp": {
            "title_hint": "Create a title for a diabetes screening and awareness camp",
            "badge": "FREE SCREENING",
            "services_default": ["Blood Sugar Test", "HbA1c Test", "Diet Consultation", "Diabetes Education"],
        },
        "cardiac_checkup_camp": {
            "title_hint": "Create a title for a free cardiac health screening camp",
            "badge": "FREE ECG",
            "services_default": ["ECG", "BP Check", "Cardiologist Consultation", "Lipid Profile"],
        },
        "job_opening": {
            "title_hint": "Create a concise hiring announcement title",
            "badge": "NOW HIRING",
            "services_default": [],
        },
        "walkin_drive": {
            "title_hint": "Create an urgent walk-in interview announcement",
            "badge": "WALK-IN INTERVIEW",
            "services_default": [],
        },
        "restaurant_offer": {
            "title_hint": "Create an appetising restaurant offer announcement",
            "badge": "LIMITED OFFER",
            "services_default": [],
        },
        "furniture_sale": {
            "title_hint": "Create a compelling furniture sale announcement",
            "badge": "MEGA SALE",
            "services_default": [],
        },
        # ── Healthcare extensions ──────────────────────────────────────
        "eye_camp": {
            "title_hint": "Create a title for a free eye check-up and vision care camp",
            "badge": "FREE EYE CHECK",
            "services_default": ["Vision Test", "Cataract Screening", "Spectacle Distribution", "Doctor Consultation"],
        },
        "dental_camp": {
            "title_hint": "Create a title for a dental health check-up camp",
            "badge": "FREE DENTAL CHECK",
            "services_default": ["Teeth Cleaning", "Cavity Check", "Orthodontic Consultation", "Fluoride Treatment"],
        },
        "general_health_camp": {
            "title_hint": "Create a title for a multi-speciality free health screening camp",
            "badge": "FREE HEALTH CHECK",
            "services_default": ["BP & Sugar Test", "BMI Check", "ECG", "Doctor Consultation", "Nutrition Advice"],
        },
        "pharmacy_sale": {
            "title_hint": "Create a title for a pharmacy discount sale announcement",
            "badge": "UPTO 20% OFF",
            "services_default": ["All Branded Medicines", "Generic Medicines", "Health Supplements", "Baby Products"],
        },
        # ── Food & Restaurant ──────────────────────────────────────────
        "bakery_offer": {
            "title_hint": "Create a title for a bakery or sweet shop special offer",
            "badge": "SPECIAL OFFER",
            "services_default": ["Custom Cakes", "Fresh Pastries", "Traditional Sweets", "Gift Hampers"],
        },
        "hotel_event": {
            "title_hint": "Create a title for a hotel banquet or catering event",
            "badge": "GRAND LAUNCH",
            "services_default": [],
        },
        # ── Retail & Products ──────────────────────────────────────────
        "retail_discount": {
            "title_hint": "Create a title for a retail shop discount or season sale",
            "badge": "MEGA SALE",
            "services_default": [],
        },
        "garment_sale": {
            "title_hint": "Create a title for a garment or clothing season sale",
            "badge": "UPTO 50% OFF",
            "services_default": [],
        },
        "electronics_sale": {
            "title_hint": "Create a title for an electronics and mobile store sale",
            "badge": "BIG SALE",
            "services_default": ["Mobiles", "Laptops", "Smart TVs", "Accessories"],
        },
        # ── Real Estate ────────────────────────────────────────────────
        "real_estate_launch": {
            "title_hint": "Create a title for a new residential property or plot launch",
            "badge": "NEW LAUNCH",
            "services_default": ["2BHK & 3BHK Flats", "Easy EMI Options", "RERA Approved", "Ready to Move"],
        },
        "rental_property": {
            "title_hint": "Create a title for a rental property, PG or hostel availability",
            "badge": "AVAILABLE NOW",
            "services_default": [],
        },
        # ── Education ──────────────────────────────────────────────────
        "coaching_institute": {
            "title_hint": "Create a title for a coaching institute or tuition centre admission",
            "badge": "ADMISSIONS OPEN",
            "services_default": ["NEET Coaching", "JEE Coaching", "IAS/IPS Preparation", "Board Exam Coaching"],
        },
        "school_admission": {
            "title_hint": "Create a title for school admission announcement",
            "badge": "ADMISSIONS OPEN",
            "services_default": ["LKG to X Admissions", "CBSE Curriculum", "Sports & Extracurricular", "Transport Facility"],
        },
        "skill_training": {
            "title_hint": "Create a title for skill training, computer course or spoken English",
            "badge": "ENROLL NOW",
            "services_default": ["Computer Basics", "MS Office", "Tally", "Spoken English", "Digital Marketing"],
        },
        # ── Beauty & Wellness ──────────────────────────────────────────
        "beauty_salon": {
            "title_hint": "Create a title for a beauty parlour or salon special offer",
            "badge": "SPECIAL PACKAGE",
            "services_default": [],
        },
        "gym_offer": {
            "title_hint": "Create a title for a gym or fitness centre membership offer",
            "badge": "JOIN NOW",
            "services_default": ["Weight Training", "Cardio", "Yoga Classes", "Personal Training", "Diet Consultation"],
        },
        "spa_wellness": {
            "title_hint": "Create a title for a spa or wellness centre offer",
            "badge": "RELAX & REFRESH",
            "services_default": ["Full Body Massage", "Facial", "Aromatherapy", "Couple Package"],
        },
        # ── Events & Services ──────────────────────────────────────────
        "event_announcement": {
            "title_hint": "Create a title for a community or cultural event announcement",
            "badge": "JOIN US",
            "services_default": [],
        },
        "wedding_services": {
            "title_hint": "Create a title for a wedding services or venue booking advertisement",
            "badge": "BOOK NOW",
            "services_default": ["Photography", "Catering", "Hall Booking", "Decoration", "DJ Music"],
        },
        "automobile_service": {
            "title_hint": "Create a title for an automobile or vehicle service centre offer",
            "badge": "SERVICE OFFER",
            "services_default": ["Free Vehicle Check", "Oil Change", "AC Service", "Battery Check"],
        },
        "travel_tour": {
            "title_hint": "Create a title for a travel agency tour package offer",
            "badge": "BOOK NOW",
            "services_default": ["Pilgrimage Tours", "Hill Station Packages", "Family Tours", "Bus/Train/Air Booking"],
        },
        # ── Malaysia 🇲🇾 territory templates ──────────────────────────────────
        # These use the same visual layout as their generic equivalents
        # but the AI prompt is tuned for Malaysia (Bahasa Melayu context)
        "malaysia_hospital_premium": {
            "title_hint": "Create a compelling hospital health camp title suited for Malaysia — use local context (Bahasa Melayu/English bilingual)",
            "badge": "PEMERIKSAAN PERCUMA",  # Free Checkup in BM
            "services_default": ["Perundingan Doktor", "Ujian Darah", "Pemeriksaan BP", "ECG", "Khidmat Pakar"],
        },
        "malaysia_job_opening": {
            "title_hint": "Create an impactful Malaysian job vacancy announcement — bilingual Bahasa Melayu / English",
            "badge": "JAWATAN KOSONG",  # Job Vacancy in BM
            "services_default": [],
        },
        "malaysia_walkin_drive": {
            "title_hint": "Create an urgent Malaysian walk-in interview announcement — Bahasa Melayu + English",
            "badge": "TEMUDUGA TERBUKA",  # Open Interview in BM
            "services_default": [],
        },
        "malaysia_retail_sale": {
            "title_hint": "Create a Malaysian retail sale campaign — bilingual Bahasa Melayu / English",
            "badge": "JUALAN MEGA",  # Mega Sale in BM
            "services_default": [],
        },
    }

    @staticmethod
    async def _call_ai(system: str, prompt: str, output_model: type[BaseModel]):
        """
        Call AI via ModelRouter with automatic fallback.

        Strategy:
          1. Try primary model (OpenAI gpt-4o-mini — most reliable for multilingual)
          2. If primary fails, try fallback model (OpenRouter)
          3. If both fail, raise the last exception

        This ensures translation works even when one provider is down or returns 401.
        """
        from app.services.model_router import get_model_router, FeatureBucket
        router = get_model_router()
        schema = output_model.model_json_schema()

        last_exc: Exception | None = None
        for use_fallback in (False, True):
            try:
                client, model = router.resolve(FeatureBucket.translation, use_fallback=use_fallback)
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": system + "\n\nReturn ONLY valid JSON matching this schema:\n" + json.dumps(schema),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=2000,
                    temperature=0.6,
                )
                raw = response.choices[0].message.content or "{}"
                if raw.startswith("```"):
                    raw = raw.split("```")[-2].lstrip("json").strip()
                return output_model.model_validate(json.loads(raw))
            except Exception as e:
                last_exc = e
                if not use_fallback:
                    logger.warning(
                        f"[LanguageService] Primary AI provider failed: {type(e).__name__}: {str(e)[:120]}. "
                        "Retrying with fallback provider..."
                    )
                else:
                    logger.error(
                        f"[LanguageService] Fallback AI provider also failed: {type(e).__name__}: {str(e)[:120]}"
                    )

        raise last_exc  # type: ignore[misc]

    @staticmethod
    async def generate_bilingual_content(
        inp: CampaignContentInput,
    ) -> BilingualCampaignContent:
        """
        Main entry point. Generates complete bilingual campaign content.
        1. Generate English base content for the template
        2. Translate to the regional language
        3. Return structured BilingualCampaignContent
        """

        tpl = LanguageService.TEMPLATE_PROMPTS.get(inp.template_slug, LanguageService.TEMPLATE_PROMPTS["orthopedic_health_camp"])
        regional_lang = inp.secondary_language or "telugu"
        translation_hint = LanguageService.TRANSLATION_GUIDANCE.get(regional_lang, "")

        services_list = inp.services or tpl["services_default"]
        services_str = ", ".join(services_list) if services_list else "General services"

        # Build prompt
        context_parts = [
            f"Template type: {inp.template_slug}",
            f"Industry: {inp.industry}",
            f"Organisation: {inp.org_name or 'the organisation'}",
            f"City: {inp.city}",
        ]
        if inp.locality:
            context_parts.append(f"Locality: {inp.locality}")
        if inp.department:
            context_parts.append(f"Department: {inp.department}")
        if inp.doctor_name:
            context_parts.append(f"Doctor: {inp.doctor_name} ({inp.doctor_qualification or ''})")
        if inp.date_range:
            context_parts.append(f"Dates: {inp.date_range}")
        if inp.event_time:
            context_parts.append(f"Time: {inp.event_time}")
        if inp.offer_price:
            context_parts.append(f"Consultation price: {inp.offer_price} (original: {inp.original_price or 'free'})")
        if inp.job_title:
            context_parts.append(f"Job: {inp.job_title}, Vacancies: {inp.vacancies or '?'}, Salary: {inp.salary_range or 'competitive'}")
        context_parts.append(f"Services/highlights: {services_str}")
        context_parts.append(f"Phone: {inp.phone or 'contact number'}")
        context_parts.append(f"Regional language for translation: {regional_lang}")

        context = "\n".join(context_parts)

        class FullContentOutput(BaseModel):
            english_title: str
            regional_title: str
            english_subtitle: str
            regional_subtitle: str
            english_badge: str
            regional_badge: str
            english_services: list[str]
            regional_services: list[str]
            offer_line_english: str
            offer_line_regional: str
            date_line_english: str
            date_line_regional: str
            english_cta: str
            regional_cta: str
            social_caption_english: str
            social_caption_regional: str
            hashtags: list[str]
            summary: str

        lang_info = SUPPORTED_LANGUAGES.get(regional_lang, {"name": regional_lang.title(), "script": "unknown"})
        lang_display = lang_info["name"]
        lang_script = lang_info["script"]

        system_prompt = f"""You are a professional multilingual marketing content specialist.
You create compelling campaign poster content for local businesses across India, SE Asia, and Oceania.

Your task:
1. Generate engaging English poster text tailored to the campaign context
2. Translate ALL text fields into {lang_display} ({lang_script} script)

Translation rules:
{translation_hint if translation_hint else f"Translate naturally into {lang_display}. Keep brand names, prices, and phone numbers the same."}

CRITICAL SCRIPT ENFORCEMENT:
- For Telugu: ONLY use Telugu Unicode (U+0C00–U+0C7F). ABSOLUTELY NEVER use Devanagari/Hindi script.
- For Tamil: ONLY use Tamil Unicode (U+0B80–U+0BFF). NEVER use Devanagari.
- For Kannada: ONLY use Kannada Unicode (U+0C80–U+0CFF). NEVER use Devanagari.
- For Bengali: ONLY use Bengali Unicode (U+0980–U+09FF). NEVER use Devanagari.
- For Gujarati: ONLY use Gujarati Unicode (U+0A80–U+0AFF). NEVER use Devanagari.
- For Punjabi: ONLY use Gurmukhi Unicode (U+0A00–U+0A7F). NEVER use Devanagari.
- For Odia: ONLY use Odia Unicode (U+0B00–U+0B7F). NEVER use Devanagari.
- The city's geographic location (e.g. Nagpur, Pune) does NOT change the required script.
- If secondary_language is Telugu, ALL regional_* fields MUST contain Telugu script only.

General rules:
- Titles must be SHORT and PUNCHY (max 6-8 words in each language)
- Technical/medical terms (X-Ray, ECG, CT Scan, NEET, etc.) stay in English in both languages
- Keep phone numbers, prices, dates, and addresses identical in both languages
- Social captions: 2-3 sentences max, warm and human
- Generate 8-12 relevant hashtags (mix English + language-relevant city/topic tags)
- CTA must create urgency: "Call Now", "Register Today", "Book Your Spot", "Don't Miss!"
- Badge text: SHORT, CAPS, high impact (FREE CHECKUP / NOW HIRING / MEGA SALE)
- If the language uses a non-Latin script, ensure proper Unicode output (not romanisation)
- Return ONLY valid translated text — not instructions, not placeholders, not explanations"""

        try:
            result = await LanguageService._call_ai(system_prompt, context, FullContentOutput)
            return BilingualCampaignContent(
                language=regional_lang,
                english_title=result.english_title,
                regional_title=result.regional_title,
                english_subtitle=result.english_subtitle,
                regional_subtitle=result.regional_subtitle,
                english_badge=result.english_badge or tpl["badge"],
                regional_badge=result.regional_badge,
                english_services=result.english_services or services_list,
                regional_services=result.regional_services,
                offer_line_english=result.offer_line_english,
                offer_line_regional=result.offer_line_regional,
                date_line_english=result.date_line_english,
                date_line_regional=result.date_line_regional,
                english_cta=result.english_cta,
                regional_cta=result.regional_cta,
                social_caption_english=result.social_caption_english,
                social_caption_regional=result.social_caption_regional,
                hashtags=result.hashtags,
                summary=result.summary,
            )
        except Exception as e:
            # Graceful fallback — return English-only content.
            # NEVER put raw exception/error text into poster fields (it would render on the poster).
            logger.error(f"[LanguageService] Bilingual content generation failed after all retries: {e}")
            title = (
                f"{inp.department or inp.template_slug.replace('_', ' ').title()} at {inp.city}"
            )
            badge_text = tpl.get("badge", "SPECIAL OFFER")
            cta_text = "Call Now to Register"
            caption_text = (
                f"Join us for {inp.template_slug.replace('_', ' ')} in {inp.city}!"
            )
            hashtags = [f"#{inp.city.replace(' ', '')}", "#Health", f"#{inp.industry.title()}"]
            return BilingualCampaignContent(
                language=regional_lang,
                # English fields — populated with sensible fallback
                english_title=title,
                english_subtitle=f"Expert care in {inp.city}",
                english_badge=badge_text,
                english_services=services_list,
                offer_line_english=f"Only {inp.offer_price}" if inp.offer_price else "",
                date_line_english=inp.date_range or "",
                english_cta=cta_text,
                social_caption_english=caption_text,
                # Regional fields — empty string, NOT error message
                # The poster will gracefully show only English when regional is empty
                regional_title="",
                regional_subtitle="",
                regional_badge=badge_text,
                regional_services=services_list,  # Reuse English services as-is
                offer_line_regional="",
                date_line_regional="",
                regional_cta="",
                social_caption_regional="",
                hashtags=hashtags,
                summary=f"Campaign for {inp.template_slug} in {inp.city}",
            )

    @staticmethod
    async def translate_text(text: str, target_language: str) -> str:
        """Translate a single text string to the target language with fallback."""
        hint = LanguageService.TRANSLATION_GUIDANCE.get(
            target_language,
            f"Translate naturally and accurately into {target_language.replace('_', ' ').title()}.",
        )

        class TranslationOutput(BaseModel):
            translated: str

        try:
            result = await LanguageService._call_ai(
                f"You are a professional translator. {hint} Return JSON with 'translated' field only.",
                f"Translate to {target_language}: {text}",
                TranslationOutput,
            )
            return result.translated
        except Exception:
            return text  # Return original on failure — never crash

    @staticmethod
    def get_supported_languages() -> dict:
        return SUPPORTED_LANGUAGES
