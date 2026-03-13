"""
Language Service — bilingual campaign content generation for Indian regional languages.

Supported language pairs:
  english + telugu   (Andhra Pradesh / Telangana)
  english + hindi     (North India / national)
  english + tamil     (Tamil Nadu)
  english + kannada   (Karnataka)
  english + malayalam (Kerala)

AI is used ONLY for:
  - headline generation
  - translation to regional language
  - CTA writing
  - campaign summary

NOT used for visual layout — that comes from PosterTemplate.
"""

import json
from typing import Literal

from pydantic import BaseModel

from app.config import settings

# ── Supported Language Codes ───────────────────────────────────────────

SUPPORTED_LANGUAGES = {
    "english": {"name": "English", "code": "en", "script": "Latin"},
    "telugu": {"name": "Telugu", "code": "te", "script": "Telugu", "region": "Telangana/AP"},
    "hindi": {"name": "Hindi", "code": "hi", "script": "Devanagari", "region": "North India"},
    "tamil": {"name": "Tamil", "code": "ta", "script": "Tamil", "region": "Tamil Nadu"},
    "kannada": {"name": "Kannada", "code": "kn", "script": "Kannada", "region": "Karnataka"},
    "malayalam": {"name": "Malayalam", "code": "ml", "script": "Malayalam", "region": "Kerala"},
}

RegionalLanguage = Literal["telugu", "hindi", "tamil", "kannada", "malayalam"]


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
        "telugu": (
            "Translate to natural, spoken Telugu used in Telangana/Andhra Pradesh. "
            "Use Telugu script (not transliteration). Keep medical/technical terms readable "
            "(e.g. X-Ray stays as X-Ray). Make it warm and community-friendly. "
            "Example: 'Free Health Camp' → 'ఉచిత ఆరోగ్య శిబిరం'"
        ),
        "hindi": (
            "Translate to clear, conversational Hindi (Devanagari script). "
            "Prefer common words over formal Sanskrit. Keep English brand names intact. "
            "Example: 'Free Health Camp' → 'निःशुल्क स्वास्थ्य शिविर'"
        ),
        "tamil": (
            "Translate to modern Tamil used in Tamil Nadu (Tamil script). "
            "Keep medical and technical terms in English where commonly understood. "
            "Example: 'Free Health Camp' → 'இலவச உடல்நல முகாம்'"
        ),
        "kannada": (
            "Translate to natural Kannada used in Karnataka (Kannada script). "
            "Example: 'Free Health Camp' → 'ಉಚಿತ ಆರೋಗ್ಯ ಶಿಬಿರ'"
        ),
        "malayalam": (
            "Translate to natural Malayalam (Malayalam script). "
            "Example: 'Free Health Camp' → 'സൗജന്യ ആരോഗ്യ ക്യാമ്പ്'"
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
    }

    @staticmethod
    async def _call_ai(system: str, prompt: str, output_model: type[BaseModel]):
        """Call OpenAI and parse structured JSON output."""
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        schema = output_model.model_json_schema()
        response = await client.chat.completions.create(
            model="gpt-4o",
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

        system_prompt = f"""You are a bilingual marketing content specialist for Indian regional markets.

Your task:
1. Generate compelling English poster text for the campaign context
2. Translate ALL text fields into {regional_lang} ({SUPPORTED_LANGUAGES[regional_lang]['script']} script)

Translation rules:
{translation_hint}

Important:
- Titles must be SHORT and PUNCHY (max 6-8 words)
- Medical terms like "X-Ray", "ECG", "CT Scan" stay in English in both languages
- Keep phone numbers, prices, and addresses the same
- Social captions should be 2-3 sentences max
- Generate 8-12 relevant hashtags (mix English + regional city/topic)
- CTA must create urgency (e.g. "Call Now", "Register Today", "Don't Miss!")
- Badge text: SHORT, CAPS, impactful (FREE CHECKUP / NOW HIRING / MEGA SALE)"""

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
            # Fallback — return English-only with error hint in regional
            return BilingualCampaignContent(
                language=regional_lang,
                english_title=f"{inp.department or inp.template_slug.replace('_', ' ').title()} at {inp.city}",
                regional_title=f"[Translation failed: {str(e)[:50]}]",
                english_subtitle=f"Expert care in {inp.city}",
                regional_subtitle="",
                english_badge=tpl["badge"],
                regional_badge=tpl["badge"],
                english_services=services_list,
                regional_services=services_list,
                offer_line_english=f"Only {inp.offer_price}" if inp.offer_price else "",
                offer_line_regional="",
                date_line_english=inp.date_range or "",
                date_line_regional="",
                english_cta="Call Now to Register",
                regional_cta="",
                social_caption_english=f"Join us for {inp.template_slug.replace('_', ' ')} at {inp.city}!",
                social_caption_regional="",
                hashtags=[f"#{inp.city}", "#Health", f"#{inp.industry}"],
                summary=f"Campaign for {inp.template_slug} in {inp.city}",
            )

    @staticmethod
    async def translate_text(text: str, target_language: RegionalLanguage) -> str:
        """Translate a single text string to the target regional language."""
        hint = LanguageService.TRANSLATION_GUIDANCE.get(target_language, "")

        class TranslationOutput(BaseModel):
            translated: str

        try:
            result = await LanguageService._call_ai(
                f"You are a translator. {hint} Return JSON with 'translated' field.",
                f"Translate to {target_language}: {text}",
                TranslationOutput,
            )
            return result.translated
        except Exception:
            return text

    @staticmethod
    def get_supported_languages() -> dict:
        return SUPPORTED_LANGUAGES
