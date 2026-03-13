"""Lead Pydantic Schemas"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Jane Smith"])
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company: Optional[str] = Field(None, max_length=120)
    source: Optional[str] = Field(None, max_length=80, examples=["facebook_ad"])
    campaign: Optional[str] = Field(None, max_length=120, examples=["summer_sale_2026"])
    medium: Optional[str] = Field(None, max_length=80)
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company: Optional[str] = Field(None, max_length=120)
    source: Optional[str] = Field(None, max_length=80)
    campaign: Optional[str] = Field(None, max_length=120)
    medium: Optional[str] = Field(None, max_length=80)
    notes: Optional[str] = None
    status: Optional[LeadStatus] = None
    ai_score: Optional[int] = Field(None, ge=0, le=100)
    ai_label: Optional[str] = Field(None, max_length=30)


class LeadResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    campaign: Optional[str] = None
    medium: Optional[str] = None
    notes: Optional[str] = None
    ai_score: Optional[int] = None
    ai_label: Optional[str] = None
    status: LeadStatus
    pipeline_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    page_size: int
