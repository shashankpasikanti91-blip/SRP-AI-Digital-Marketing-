"""CRM Pydantic Schemas"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.crm import CRMStage


class CRMCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    stage: CRMStage = CRMStage.NEW
    value: Optional[int] = Field(None, ge=0, description="Deal value in cents")
    notes: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=120)
    expected_close: Optional[datetime] = None
    lead_id: Optional[uuid.UUID] = None


class CRMUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    stage: Optional[CRMStage] = None
    value: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    assigned_to: Optional[str] = Field(None, max_length=120)
    expected_close: Optional[datetime] = None
    lost_reason: Optional[str] = Field(None, max_length=255)


class CRMStageUpdate(BaseModel):
    stage: CRMStage
    lost_reason: Optional[str] = Field(None, max_length=255)


class CRMResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    title: str
    stage: CRMStage
    value: Optional[int] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    expected_close: Optional[datetime] = None
    lost_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KanbanColumn(BaseModel):
    stage: CRMStage
    items: list[CRMResponse]
    total_value: int


class KanbanResponse(BaseModel):
    columns: list[KanbanColumn]
