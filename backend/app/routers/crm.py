"""CRM Pipeline Router"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.core.dependencies import DB, CurrentTenant
from app.models.crm import CRMStage
from app.schemas.crm import CRMCreate, CRMResponse, CRMStageUpdate, CRMUpdate, KanbanResponse
from app.services.crm_service import CRMService

router = APIRouter(prefix="/crm", tags=["CRM Pipeline"])


@router.post("/", response_model=CRMResponse, status_code=status.HTTP_201_CREATED)
async def create_pipeline(payload: CRMCreate, tenant: CurrentTenant, db: DB):
    return await CRMService.create(db, tenant.id, payload)


@router.get("/kanban", response_model=KanbanResponse)
async def get_kanban(tenant: CurrentTenant, db: DB):
    """Returns all pipeline records grouped by stage for Kanban view."""
    return await CRMService.get_kanban(db, tenant.id)


@router.get("/", response_model=list[CRMResponse])
async def list_pipelines(
    tenant: CurrentTenant,
    db: DB,
    stage: Optional[CRMStage] = None,
    assigned_to: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    return await CRMService.list(db, tenant.id, stage=stage, assigned_to=assigned_to, page=page, page_size=page_size)


@router.get("/{pipeline_id}", response_model=CRMResponse)
async def get_pipeline(pipeline_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    item = await CRMService.get(db, tenant.id, pipeline_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pipeline record not found")
    return item


@router.patch("/{pipeline_id}", response_model=CRMResponse)
async def update_pipeline(pipeline_id: uuid.UUID, payload: CRMUpdate, tenant: CurrentTenant, db: DB):
    item = await CRMService.update(db, tenant.id, pipeline_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Pipeline record not found")
    return item


@router.patch("/{pipeline_id}/stage", response_model=CRMResponse)
async def move_stage(pipeline_id: uuid.UUID, payload: CRMStageUpdate, tenant: CurrentTenant, db: DB):
    """Move a deal to a new CRM stage."""
    item = await CRMService.move_stage(db, tenant.id, pipeline_id, payload)
    if not item:
        raise HTTPException(status_code=404, detail="Pipeline record not found")
    return item


@router.delete("/{pipeline_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pipeline(pipeline_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    deleted = await CRMService.delete(db, tenant.id, pipeline_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pipeline record not found")
