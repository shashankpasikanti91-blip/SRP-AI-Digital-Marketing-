"""Email Campaign Pydantic Schemas"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.email_campaign import CampaignStatus


class EmailSequenceCreate(BaseModel):
    step_order: int = Field(..., ge=1)
    subject: str = Field(..., min_length=1, max_length=300)
    body_html: str = Field(..., min_length=1)
    body_text: Optional[str] = None
    delay_days: int = Field(0, ge=0)


class EmailSequenceResponse(BaseModel):
    id: uuid.UUID
    campaign_id: uuid.UUID
    step_order: int
    subject: str
    body_html: str
    body_text: Optional[str] = None
    delay_days: int
    created_at: datetime

    model_config = {"from_attributes": True}


class EmailCampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    from_name: Optional[str] = Field(None, max_length=120)
    from_email: Optional[EmailStr] = None
    campaign_tag: Optional[str] = Field(None, max_length=80)


class EmailCampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    from_name: Optional[str] = Field(None, max_length=120)
    from_email: Optional[EmailStr] = None
    campaign_tag: Optional[str] = Field(None, max_length=80)
    status: Optional[CampaignStatus] = None


class EmailCampaignResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    from_name: Optional[str] = None
    from_email: Optional[str] = None
    campaign_tag: Optional[str] = None
    status: CampaignStatus
    total_sent: int
    total_opened: int
    total_clicked: int
    total_unsubscribed: int
    sequences: list[EmailSequenceResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailSendRequest(BaseModel):
    recipient_emails: Optional[list[EmailStr]] = None  # if None, targets leads in campaign_tag
    lead_ids: Optional[list[uuid.UUID]] = None


class EmailStatsResponse(BaseModel):
    campaign_id: uuid.UUID
    total_sent: int
    total_opened: int
    total_clicked: int
    total_unsubscribed: int
    open_rate: float
    click_rate: float
