"""Lead Service — business logic"""

import uuid
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadService:

    @staticmethod
    async def create(db: AsyncSession, tenant_id: uuid.UUID, payload: LeadCreate) -> Lead:
        lead = Lead(tenant_id=tenant_id, **payload.model_dump())
        db.add(lead)
        await db.flush()
        await db.refresh(lead)
        # Fire background AI scoring task
        try:
            from app.workers.ai_worker import score_lead_task
            score_lead_task.delay(str(lead.id), str(tenant_id))
        except Exception:
            pass  # Worker not available in test/dev without Celery running
        return lead

    @staticmethod
    async def get(db: AsyncSession, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> Lead | None:
        result = await db.execute(
            select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        status: Optional[LeadStatus] = None,
        source: Optional[str] = None,
        campaign: Optional[str] = None,
        ai_label: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Lead], int]:
        query = select(Lead).where(Lead.tenant_id == tenant_id)
        if status:
            query = query.where(Lead.status == status)
        if source:
            query = query.where(Lead.source == source)
        if campaign:
            query = query.where(Lead.campaign == campaign)
        if ai_label:
            query = query.where(Lead.ai_label == ai_label)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(Lead.name.ilike(pattern), Lead.email.ilike(pattern), Lead.phone.ilike(pattern))
            )

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar_one()

        query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        return list(result.scalars().all()), total

    @staticmethod
    async def update(db: AsyncSession, tenant_id: uuid.UUID, lead_id: uuid.UUID, payload: LeadUpdate) -> Lead | None:
        lead = await LeadService.get(db, tenant_id, lead_id)
        if not lead:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        await db.flush()
        await db.refresh(lead)
        return lead

    @staticmethod
    async def delete(db: AsyncSession, tenant_id: uuid.UUID, lead_id: uuid.UUID) -> bool:
        lead = await LeadService.get(db, tenant_id, lead_id)
        if not lead:
            return False
        await db.delete(lead)
        return True
