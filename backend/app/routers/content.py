"""Content Router — AI content generation and management"""
import uuid
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.content_piece import ContentPiece, ContentStatus, ContentType

router = APIRouter(prefix="/content", tags=["Content"])


class GenerateContentRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    target_audience: str = "General audience"
    tone: Literal["professional", "casual", "friendly", "urgent", "inspirational", "funny"] = "professional"
    platforms: Optional[list[str]] = None
    campaign_objective: Optional[str] = None
    language: str = "English"
    include_hashtags: bool = True
    include_emoji: bool = True
    brand_voice: Optional[str] = None
    offer_details: Optional[str] = None
    campaign_id: Optional[uuid.UUID] = None


class ContentPieceCreate(BaseModel):
    type: ContentType
    headline: Optional[str] = None
    body: str
    cta: Optional[str] = None
    platform: Optional[str] = None
    tone: Optional[str] = None
    hashtags: Optional[list[str]] = None
    campaign_id: Optional[uuid.UUID] = None


class ContentPieceUpdate(BaseModel):
    status: Optional[ContentStatus] = None
    headline: Optional[str] = None
    body: Optional[str] = None
    cta: Optional[str] = None
    hashtags: Optional[list[str]] = None


@router.get("/")
async def list_content(
    tenant: CurrentTenant,
    db: DB,
    type_filter: Optional[ContentType] = Query(None, alias="type"),
    status_filter: Optional[ContentStatus] = Query(None, alias="status"),
    campaign_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(ContentPiece).where(ContentPiece.tenant_id == tenant.id)
    if type_filter:
        query = query.where(ContentPiece.type == type_filter)
    if status_filter:
        query = query.where(ContentPiece.status == status_filter)
    if campaign_id:
        query = query.where(ContentPiece.campaign_id == campaign_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(ContentPiece.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/generate")
async def generate_content(payload: GenerateContentRequest, tenant: CurrentTenant, db: DB):
    """Use Content Agent to generate multi-platform content. Auto-saves to database."""
    from app.models.business_profile import BusinessProfile
    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()

    from app.agents.content_agent import ContentAgent
    agent = ContentAgent()
    try:
        output = await agent.run(
            topic=payload.topic,
            business_name=bp.business_name if bp else tenant.name,
            target_audience=payload.target_audience,
            tone=payload.tone,
            platforms=payload.platforms,
            campaign_objective=payload.campaign_objective,
            language=payload.language,
            include_hashtags=payload.include_hashtags,
            include_emoji=payload.include_emoji,
            brand_voice=payload.brand_voice or (bp.brand_voice if bp else None),
            offer_details=payload.offer_details or (bp.main_offer if bp else None),
        )

        # Save each variant as a content piece
        saved_pieces = []
        for variant in output.variants:
            piece = ContentPiece(
                tenant_id=tenant.id,
                campaign_id=payload.campaign_id,
                type=ContentType.SOCIAL_POST,
                headline=output.headline,
                body=variant.content,
                cta=variant.cta,
                platform=variant.platform,
                tone=payload.tone,
                hashtags=variant.hashtags,
                ai_generated=True,
                ai_full_output=output.model_dump(),
            )
            db.add(piece)
            saved_pieces.append(piece)

        # Save email content
        email_piece = ContentPiece(
            tenant_id=tenant.id,
            campaign_id=payload.campaign_id,
            type=ContentType.EMAIL,
            headline=output.email_subject_lines[0] if output.email_subject_lines else output.headline,
            body=output.primary_copy,
            cta=output.cta,
            ai_generated=True,
            ai_full_output=output.model_dump(),
        )
        db.add(email_piece)

        await db.flush()
        return {
            "content": output.model_dump(),
            "saved_count": len(saved_pieces) + 1,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_content_piece(payload: ContentPieceCreate, tenant: CurrentTenant, db: DB):
    piece = ContentPiece(tenant_id=tenant.id, ai_generated=False, **payload.model_dump())
    db.add(piece)
    await db.flush()
    await db.refresh(piece)
    return piece


@router.get("/{piece_id}")
async def get_content_piece(piece_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(ContentPiece).where(ContentPiece.id == piece_id, ContentPiece.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content piece not found")
    return item


@router.patch("/{piece_id}")
async def update_content_piece(piece_id: uuid.UUID, payload: ContentPieceUpdate, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(ContentPiece).where(ContentPiece.id == piece_id, ContentPiece.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content piece not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{piece_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content_piece(piece_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(ContentPiece).where(ContentPiece.id == piece_id, ContentPiece.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Content piece not found")
    await db.delete(item)


@router.post("/design-brief")
async def generate_design_brief(
    campaign_name: str,
    platform: str,
    headline: str,
    format_type: Literal["image_ad", "reel", "carousel", "banner", "story"] = "image_ad",
    campaign_id: Optional[uuid.UUID] = None,
    tenant: CurrentTenant = None,
    db: DB = None,
):
    """Use Design Brief Agent to generate a creative brief."""
    from app.models.business_profile import BusinessProfile
    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()

    from app.agents.design_brief_agent import DesignBriefAgent
    from app.models.design_brief import DesignBrief
    agent = DesignBriefAgent()
    try:
        brief = await agent.run(
            campaign_name=campaign_name,
            format_type=format_type,
            platform=platform,
            headline=headline,
            brand_colors=bp.brand_colors if bp else None,
            target_audience=bp.target_audience if bp else "General audience",
        )

        # Save brief
        db_brief = DesignBrief(
            tenant_id=tenant.id,
            campaign_id=campaign_id,
            campaign_name=campaign_name,
            format_type=format_type,
            platform=platform,
            headline=brief.headline,
            subheadline=brief.subheadline,
            cta_text=brief.cta_text,
            color_palette=brief.color_palette,
            mood=brief.mood,
            imagery_description=brief.imagery_description,
            full_brief_json=brief.model_dump(),
        )
        db.add(db_brief)
        await db.flush()
        return brief.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Design brief failed: {str(e)}")
