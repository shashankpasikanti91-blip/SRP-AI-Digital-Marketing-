"""CRM Pipeline Service"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CRMPipeline, CRMStage
from app.schemas.crm import CRMCreate, CRMStageUpdate, CRMUpdate, KanbanColumn, KanbanResponse


class CRMService:

    @staticmethod
    async def create(db: AsyncSession, tenant_id: uuid.UUID, payload: CRMCreate) -> CRMPipeline:
        data = payload.model_dump(exclude={"lead_id"})
        pipeline = CRMPipeline(tenant_id=tenant_id, **data)
        if payload.lead_id:
            from app.models.lead import Lead
            result = await db.execute(select(Lead).where(Lead.id == payload.lead_id, Lead.tenant_id == tenant_id))
            lead = result.scalar_one_or_none()
            if lead:
                lead.pipeline_id = pipeline.id
        db.add(pipeline)
        await db.flush()
        await db.refresh(pipeline)
        return pipeline

    @staticmethod
    async def get(db: AsyncSession, tenant_id: uuid.UUID, pipeline_id: uuid.UUID) -> CRMPipeline | None:
        result = await db.execute(
            select(CRMPipeline).where(CRMPipeline.id == pipeline_id, CRMPipeline.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        stage: Optional[CRMStage] = None,
        assigned_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> list[CRMPipeline]:
        query = select(CRMPipeline).where(CRMPipeline.tenant_id == tenant_id)
        if stage:
            query = query.where(CRMPipeline.stage == stage)
        if assigned_to:
            query = query.where(CRMPipeline.assigned_to == assigned_to)
        query = query.order_by(CRMPipeline.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_kanban(db: AsyncSession, tenant_id: uuid.UUID) -> KanbanResponse:
        result = await db.execute(
            select(CRMPipeline).where(CRMPipeline.tenant_id == tenant_id).order_by(CRMPipeline.created_at.asc())
        )
        all_items = list(result.scalars().all())
        columns = []
        for stage in CRMStage:
            stage_items = [i for i in all_items if i.stage == stage]
            total_value = sum(i.value or 0 for i in stage_items)
            columns.append(KanbanColumn(stage=stage, items=stage_items, total_value=total_value))
        return KanbanResponse(columns=columns)

    @staticmethod
    async def update(db: AsyncSession, tenant_id: uuid.UUID, pipeline_id: uuid.UUID, payload: CRMUpdate) -> CRMPipeline | None:
        item = await CRMService.get(db, tenant_id, pipeline_id)
        if not item:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def move_stage(db: AsyncSession, tenant_id: uuid.UUID, pipeline_id: uuid.UUID, payload: CRMStageUpdate) -> CRMPipeline | None:
        item = await CRMService.get(db, tenant_id, pipeline_id)
        if not item:
            return None
        item.stage = payload.stage
        if payload.lost_reason:
            item.lost_reason = payload.lost_reason
        await db.flush()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete(db: AsyncSession, tenant_id: uuid.UUID, pipeline_id: uuid.UUID) -> bool:
        item = await CRMService.get(db, tenant_id, pipeline_id)
        if not item:
            return False
        await db.delete(item)
        return True
