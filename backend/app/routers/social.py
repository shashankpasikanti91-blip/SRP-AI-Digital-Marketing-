"""Social Media Scheduler Router"""

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import DB, CurrentTenant
from app.models.social import PostStatus, SocialPlatform
from app.schemas.social import (
    CalendarResponse,
    SocialPostCreate,
    SocialPostListResponse,
    SocialPostResponse,
    SocialPostUpdate,
)
from app.services.social_service import SocialService

router = APIRouter(prefix="/social", tags=["Social Media Scheduler"])


@router.post("/posts/", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(payload: SocialPostCreate, tenant: CurrentTenant, db: DB):
    """Create and optionally schedule a social media post."""
    return await SocialService.create(db, tenant.id, payload)


@router.get("/posts/", response_model=SocialPostListResponse)
async def list_posts(
    tenant: CurrentTenant,
    db: DB,
    platform: Optional[SocialPlatform] = None,
    post_status: Optional[PostStatus] = Query(None, alias="status"),
    campaign: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = await SocialService.list(
        db, tenant.id,
        platform=platform, status=post_status, campaign=campaign,
        page=page, page_size=page_size,
    )
    return SocialPostListResponse(items=items, total=total)


@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    tenant: CurrentTenant,
    db: DB,
    from_date: date = Query(...),
    to_date: date = Query(...),
    platform: Optional[SocialPlatform] = None,
):
    """Returns all scheduled posts within a date range grouped by day."""
    return await SocialService.get_calendar(db, tenant.id, from_date, to_date, platform=platform)


@router.get("/posts/{post_id}", response_model=SocialPostResponse)
async def get_post(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    post = await SocialService.get(db, tenant.id, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/posts/{post_id}", response_model=SocialPostResponse)
async def update_post(post_id: uuid.UUID, payload: SocialPostUpdate, tenant: CurrentTenant, db: DB):
    post = await SocialService.update(db, tenant.id, post_id, payload)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts/{post_id}/publish", response_model=SocialPostResponse)
async def publish_now(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Immediately publish a post to the platform."""
    post = await SocialService.publish_now(db, tenant.id, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    deleted = await SocialService.delete(db, tenant.id, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")


# ── Alias routes (no /posts/ prefix) used by the frontend ──────────────────

@router.post("/", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post_alias(payload: SocialPostCreate, tenant: CurrentTenant, db: DB):
    return await SocialService.create(db, tenant.id, payload)


@router.get("/", response_model=SocialPostListResponse)
async def list_posts_alias(
    tenant: CurrentTenant,
    db: DB,
    platform: Optional[str] = None,
    post_status: Optional[PostStatus] = Query(None, alias="status"),
    campaign: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    # Accept any platform string (whatsapp, youtube, twitter etc.)
    plat = None
    if platform:
        try:
            plat = SocialPlatform(platform)
        except ValueError:
            plat = None  # unknown platform — still filter by raw string via service
    items, total = await SocialService.list(
        db, tenant.id,
        platform=plat, status=post_status, campaign=campaign,
        page=page, page_size=page_size,
    )
    return SocialPostListResponse(items=items, total=total)


@router.get("/{post_id}", response_model=SocialPostResponse)
async def get_post_alias(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    post = await SocialService.get(db, tenant.id, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/{post_id}", response_model=SocialPostResponse)
async def update_post_alias(post_id: uuid.UUID, payload: SocialPostUpdate, tenant: CurrentTenant, db: DB):
    post = await SocialService.update(db, tenant.id, post_id, payload)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/{post_id}/publish", response_model=SocialPostResponse)
async def publish_now_alias(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    post = await SocialService.publish_now(db, tenant.id, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post_alias(post_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    deleted = await SocialService.delete(db, tenant.id, post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")

