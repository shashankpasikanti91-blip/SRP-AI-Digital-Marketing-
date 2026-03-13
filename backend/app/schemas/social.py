"""Social Media Pydantic Schemas"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl

from app.models.social import PostStatus, SocialPlatform


class SocialPostCreate(BaseModel):
    platform: SocialPlatform
    content: str = Field(..., min_length=1, max_length=3000)
    media_url: Optional[str] = Field(None, max_length=512)
    campaign: Optional[str] = Field(None, max_length=120)
    scheduled_at: Optional[datetime] = None
    ai_generated: bool = False


class SocialPostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=3000)
    media_url: Optional[str] = Field(None, max_length=512)
    campaign: Optional[str] = Field(None, max_length=120)
    scheduled_at: Optional[datetime] = None
    status: Optional[PostStatus] = None


class SocialPostResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    platform: SocialPlatform
    content: str
    media_url: Optional[str] = None
    campaign: Optional[str] = None
    status: PostStatus
    scheduled_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    external_post_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int
    ai_generated: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SocialPostListResponse(BaseModel):
    items: list[SocialPostResponse]
    total: int


class CalendarDay(BaseModel):
    date: str  # YYYY-MM-DD
    posts: list[SocialPostResponse]


class CalendarResponse(BaseModel):
    days: list[CalendarDay]
    from_date: str
    to_date: str
