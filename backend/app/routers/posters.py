"""
Posters Router — brand profiles, poster templates, and poster variant generation.

Endpoints:
  POST /posters/brand-profile          — create/update brand profile
  GET  /posters/brand-profile          — get tenant brand profile
  GET  /posters/templates              — list available poster templates
  POST /posters/generate               — generate poster JSON for one platform
  POST /posters/generate-all-variants  — generate all social media variants
  GET  /posters/variants               — list generated variants
  GET  /posters/variants/{id}          — get single variant
  DELETE /posters/variants/{id}        — delete variant
  GET  /posters/languages              — list supported languages
  GET  /posters/template-categories    — list template slugs & categories
"""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.dependencies import DB, CurrentTenant
from app.models.brand_profile import BrandProfile
from app.models.poster_template import PosterTemplate
from app.models.poster_variant import PosterVariant, SocialPlatformVariant
from app.services.language_service import (
    CampaignContentInput,
    LanguageService,
    SUPPORTED_LANGUAGES,
)
from app.services.poster_generator import PosterGenerator, SYSTEM_TEMPLATES
from app.services.social_variant_service import SocialVariantService, VARIANT_SPECS

router = APIRouter(prefix="/posters", tags=["Posters & Brand"])


# ── Pydantic Schemas ────────────────────────────────────────────────────

class BrandProfileCreate(BaseModel):
    brand_name: str = Field(..., max_length=200)
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = "#1E40AF"
    secondary_color: str = "#FFFFFF"
    accent_color: str = "#F59E0B"
    background_color: str = "#F8FAFC"
    text_color: str = "#1F2937"
    font_family: str = "Inter"
    regional_font_family: str = "Noto Sans"
    footer_text: Optional[str] = None
    phone_numbers: Optional[list[str]] = None
    address: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_links: Optional[dict] = None
    industry: Optional[str] = None
    default_languages: Optional[list[str]] = None
    city: Optional[str] = None
    state: Optional[str] = None
    watermark_text: Optional[str] = None
    accreditation_logos: Optional[list[dict]] = None


class GeneratePosterRequest(BaseModel):
    template_slug: str = Field(..., description="Template slug: orthopedic_health_camp | eye_camp | dental_camp | job_opening | ...")
    platform: str = Field("instagram_square", description="instagram_square | instagram_story | facebook_post | whatsapp_share | linkedin_banner")
    city: str
    locality: Optional[str] = None
    state: str = "Telangana"
    industry: str = "hospital"
    org_name: Optional[str] = None   # Brand / organisation name from form
    department: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_qualification: Optional[str] = None
    date_range: Optional[str] = None
    event_time: Optional[str] = None
    offer_price: Optional[str] = None
    original_price: Optional[str] = None
    services: Optional[list[str]] = None
    job_title: Optional[str] = None
    vacancies: Optional[str] = None
    salary_range: Optional[str] = None
    experience: Optional[str] = None
    phone: str = ""
    primary_language: str = "english"
    secondary_language: Optional[str] = None  # telugu | hindi | tamil | kannada | malayalam
    campaign_id: Optional[str] = None


class GenerateAllVariantsRequest(GeneratePosterRequest):
    platforms: Optional[list[str]] = None  # defaults to all 5 platforms


# ── Endpoints ────────────────────────────────────────────────────────────

@router.get("/languages")
async def list_languages():
    """List all supported regional languages for bilingual campaign generation."""
    return {"languages": SUPPORTED_LANGUAGES}


@router.get("/template-categories")
async def list_template_categories():
    """List all available poster template slugs with their default settings."""
    from app.services.language_service import LanguageService as LS
    template_slugs = list(SYSTEM_TEMPLATES.keys())
    template_prompts = LS.TEMPLATE_PROMPTS
    return {
        "templates": [
            {
                "slug": slug,
                "label": slug.replace("_", " ").title(),
                "badge": template_prompts.get(slug, {}).get("badge", ""),
                "default_services": template_prompts.get(slug, {}).get("services_default", []),
                "recommended_languages": ["english", "telugu", "hindi"],
            }
            for slug in template_slugs
        ],
        "platform_variants": VARIANT_SPECS,
    }


@router.post("/brand-profile", status_code=status.HTTP_201_CREATED)
async def create_brand_profile(body: BrandProfileCreate, tenant: CurrentTenant, db: DB):
    """Create or update the tenant brand profile (one per tenant)."""
    existing = (await db.execute(
        select(BrandProfile).where(BrandProfile.tenant_id == tenant.id)
    )).scalar_one_or_none()

    if existing:
        # Update
        for k, v in body.model_dump(exclude_none=True).items():
            setattr(existing, k, v)
        await db.commit()
        await db.refresh(existing)
        return {"id": str(existing.id), "message": "Brand profile updated", "brand_profile": _brand_dict(existing)}
    else:
        profile = BrandProfile(tenant_id=tenant.id, **body.model_dump())
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        return {"id": str(profile.id), "message": "Brand profile created", "brand_profile": _brand_dict(profile)}


@router.get("/brand-profile")
async def get_brand_profile(tenant: CurrentTenant, db: DB):
    """Get the current tenant brand profile."""
    profile = (await db.execute(
        select(BrandProfile).where(BrandProfile.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found. Please create one first.")
    return _brand_dict(profile)


@router.get("/templates")
async def list_poster_templates(
    tenant: CurrentTenant,
    db: DB,
    category: Optional[str] = None,
):
    """List available poster templates (system + tenant custom)."""
    query = select(PosterTemplate).where(PosterTemplate.tenant_id == tenant.id)
    if category:
        query = query.where(PosterTemplate.category == category)
    rows = (await db.execute(query.order_by(PosterTemplate.sort_order))).scalars().all()

    # Always include system template slugs even if not in DB
    system_slugs = list(SYSTEM_TEMPLATES.keys())
    db_slugs = {r.slug for r in rows}
    builtin = [
        {
            "id": None,
            "slug": slug,
            "name": slug.replace("_", " ").title(),
            "is_system": True,
            "is_active": True,
            "layout_type": "square",
            "category": _infer_category(slug),
        }
        for slug in system_slugs
        if slug not in db_slugs
    ]

    return {"templates": builtin + [_template_dict(r) for r in rows]}


@router.post("/generate")
async def generate_poster(body: GeneratePosterRequest, tenant: CurrentTenant, db: DB):
    """
    Generate a structured poster JSON for a single social media platform.

    The response includes:
    - poster_json: structured layers for frontend PosterRenderer
    - bilingual_content: all English + regional text blocks
    - social_caption: ready-to-post caption
    - hashtags: relevant hashtags
    """
    brand = (await db.execute(
        select(BrandProfile).where(BrandProfile.tenant_id == tenant.id)
    )).scalar_one_or_none()

    campaign_input = _build_campaign_input(body, brand)

    poster_json = await PosterGenerator.generate_poster_json(
        campaign_input=campaign_input,
        brand=brand,
        template_slug=body.template_slug,
        platform=body.platform,
    )

    # Persist variant
    variant = PosterVariant(
        tenant_id=tenant.id,
        campaign_id=uuid.UUID(body.campaign_id) if body.campaign_id else None,
        brand_profile_id=brand.id if brand else None,
        platform=body.platform,
        width=str(poster_json["dimensions"]["width"]),
        height=str(poster_json["dimensions"]["height"]),
        campaign_data=body.model_dump(),
        language_primary=body.primary_language,
        language_secondary=body.secondary_language,
        bilingual_content=poster_json.get("bilingual_content"),
        poster_json=poster_json,
        social_caption=poster_json.get("bilingual_content", {}).get("social_caption_english"),
        hashtags=poster_json.get("bilingual_content", {}).get("hashtags"),
    )
    db.add(variant)
    await db.commit()
    await db.refresh(variant)

    return {
        "variant_id": str(variant.id),
        "platform": body.platform,
        "poster_json": poster_json,
        "social_caption": poster_json.get("bilingual_content", {}).get("social_caption_english"),
        "hashtags": poster_json.get("bilingual_content", {}).get("hashtags", []),
    }


@router.post("/generate-all-variants")
async def generate_all_variants(body: GenerateAllVariantsRequest, tenant: CurrentTenant, db: DB):
    """
    Generate poster JSON for ALL social media platforms in a single request.

    Efficient: calls AI only ONCE for bilingual content,
    then adapts layout for each platform (5 variants from 1 AI call).
    """
    brand = (await db.execute(
        select(BrandProfile).where(BrandProfile.tenant_id == tenant.id)
    )).scalar_one_or_none()

    campaign_input = _build_campaign_input(body, brand)

    result = await SocialVariantService.generate_all_variants(
        campaign_input=campaign_input,
        brand=brand,
        template_slug=body.template_slug,
        platforms=body.platforms,
    )

    # Persist all variants
    saved_ids = {}
    for platform, poster_json in result.get("variants", {}).items():
        if isinstance(poster_json, dict) and "error" not in poster_json:
            variant = PosterVariant(
                tenant_id=tenant.id,
                campaign_id=uuid.UUID(body.campaign_id) if body.campaign_id else None,
                brand_profile_id=brand.id if brand else None,
                platform=platform,
                width=str(poster_json.get("dimensions", {}).get("width", 1080)),
                height=str(poster_json.get("dimensions", {}).get("height", 1080)),
                campaign_data=body.model_dump(),
                language_primary=body.primary_language,
                language_secondary=body.secondary_language,
                bilingual_content=poster_json.get("bilingual_content"),
                poster_json=poster_json,
                social_caption=poster_json.get("social_caption"),
                hashtags=poster_json.get("hashtags"),
            )
            db.add(variant)
            await db.flush()
            saved_ids[platform] = str(variant.id)

    await db.commit()

    return {
        "variants": result["variants"],
        "summary": result["summary"],
        "saved_variant_ids": saved_ids,
    }


@router.get("/variants")
async def list_variants(
    tenant: CurrentTenant,
    db: DB,
    campaign_id: Optional[str] = Query(None),
    platform: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all generated poster variants for the tenant."""
    from sqlalchemy import func
    query = select(PosterVariant).where(PosterVariant.tenant_id == tenant.id)
    if campaign_id:
        query = query.where(PosterVariant.campaign_id == uuid.UUID(campaign_id))
    if platform:
        query = query.where(PosterVariant.platform == platform)

    query = query.order_by(PosterVariant.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(query)).scalars().all()
    return {"variants": [_variant_dict(r) for r in rows]}


@router.get("/variants/{variant_id}")
async def get_variant(variant_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Get a single poster variant by ID."""
    v = (await db.execute(
        select(PosterVariant).where(PosterVariant.id == variant_id, PosterVariant.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Variant not found")
    return _variant_dict(v)


@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant(variant_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Delete a poster variant."""
    v = (await db.execute(
        select(PosterVariant).where(PosterVariant.id == variant_id, PosterVariant.tenant_id == tenant.id)
    )).scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=404, detail="Variant not found")
    await db.delete(v)
    await db.commit()


@router.post("/translate")
async def translate_text(
    tenant: CurrentTenant,
    text: str = Query(..., description="Text to translate"),
    language: str = Query(..., description="Target language: telugu|hindi|tamil|kannada|malayalam"),
):
    """Translate a single text string to the target regional language."""
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}. Supported: {list(SUPPORTED_LANGUAGES.keys())}")
    translated = await LanguageService.translate_text(text, language)  # type: ignore[arg-type]
    return {"original": text, "translated": translated, "language": language}


# ── Serializers ────────────────────────────────────────────────────────

def _brand_dict(b: BrandProfile) -> dict:
    return {
        "id": str(b.id),
        "brand_name": b.brand_name,
        "tagline": b.tagline,
        "logo_url": b.logo_url,
        "primary_color": b.primary_color,
        "secondary_color": b.secondary_color,
        "accent_color": b.accent_color,
        "font_family": b.font_family,
        "regional_font_family": b.regional_font_family,
        "footer_text": b.footer_text,
        "phone_numbers": b.phone_numbers,
        "address": b.address,
        "email": b.email,
        "website": b.website,
        "social_links": b.social_links,
        "industry": b.industry,
        "default_languages": b.default_languages,
        "city": b.city,
        "state": b.state,
        "country": b.country,
        "accreditation_logos": b.accreditation_logos,
        "created_at": b.created_at.isoformat() if b.created_at else None,
    }


def _template_dict(t: PosterTemplate) -> dict:
    return {
        "id": str(t.id),
        "name": t.name,
        "slug": t.slug,
        "category": t.category,
        "layout_type": t.layout_type,
        "width": t.width,
        "height": t.height,
        "is_system": t.is_system,
        "is_active": t.is_active,
    }


def _variant_dict(v: PosterVariant) -> dict:
    return {
        "id": str(v.id),
        "platform": v.platform,
        "width": v.width,
        "height": v.height,
        "language_primary": v.language_primary,
        "language_secondary": v.language_secondary,
        "status": v.status,
        "social_caption": v.social_caption,
        "hashtags": v.hashtags,
        "image_url": v.image_url,
        "bilingual_content": v.bilingual_content,
        "poster_json": v.poster_json,
        "campaign_id": str(v.campaign_id) if v.campaign_id else None,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }


def _build_campaign_input(body, brand) -> CampaignContentInput:
    """Build CampaignContentInput from request body and brand profile."""
    phone = body.phone
    if not phone and brand and brand.phone_numbers:
        phone = brand.phone_numbers[0] if brand.phone_numbers else ""
    # Use form org_name first, fall back to brand profile name
    org_name = getattr(body, "org_name", None) or (brand.brand_name if brand else "") or ""

    return CampaignContentInput(
        template_slug=body.template_slug,
        industry=body.industry,
        city=body.city,
        locality=body.locality,
        state=getattr(body, "state", "Telangana"),
        department=body.department,
        doctor_name=body.doctor_name,
        doctor_qualification=body.doctor_qualification,
        date_range=body.date_range,
        event_time=body.event_time,
        offer_price=body.offer_price,
        original_price=body.original_price,
        services=body.services,
        job_title=body.job_title,
        vacancies=body.vacancies,
        salary_range=body.salary_range,
        experience=body.experience,
        org_name=org_name,
        phone=phone,
        primary_language=body.primary_language,
        secondary_language=body.secondary_language,
    )


def _infer_category(slug: str) -> str:
    if any(k in slug for k in ["health", "camp", "cardiac", "diabetes", "eye", "dental", "pharmacy", "orthopedic"]):
        return "health_camp"
    if any(k in slug for k in ["job", "walkin", "hiring", "recruitment"]):
        return "job_opening"
    if any(k in slug for k in ["restaurant", "bakery", "hotel", "food"]):
        return "food"
    if any(k in slug for k in ["sale", "furniture", "garment", "retail", "electronics", "discount"]):
        return "retail_sale"
    if any(k in slug for k in ["real_estate", "rental", "property", "flat"]):
        return "real_estate"
    if any(k in slug for k in ["coaching", "school", "skill", "training", "education"]):
        return "education"
    if any(k in slug for k in ["beauty", "salon", "gym", "spa", "wellness", "fitness"]):
        return "beauty_wellness"
    if any(k in slug for k in ["event", "wedding", "travel", "automobile", "tour"]):
        return "events"
    return "general"
