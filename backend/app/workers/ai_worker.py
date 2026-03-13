"""AI Background Worker — async lead scoring and batch AI tasks"""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.ai_worker.score_lead_task", bind=True, max_retries=2)
def score_lead_task(self, lead_id: str, tenant_id: str):
    """Asynchronously score a single lead using AI after creation."""
    asyncio.run(_score_lead(lead_id, tenant_id))


@celery_app.task(name="app.workers.ai_worker.batch_score_leads", bind=True)
def batch_score_leads(self, tenant_id: str):
    """Score all unscored leads for a tenant."""
    asyncio.run(_batch_score(tenant_id))


async def _score_lead(lead_id: str, tenant_id: str):
    import uuid
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.lead import Lead
    from app.services.ai_service import AIService

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lead).where(
                Lead.id == uuid.UUID(lead_id),
                Lead.tenant_id == uuid.UUID(tenant_id)
            )
        )
        lead = result.scalar_one_or_none()
        if not lead:
            logger.warning("Lead %s not found for scoring", lead_id)
            return
        try:
            await AIService.classify_lead(db, uuid.UUID(tenant_id), lead)
            await db.commit()
            logger.info("Lead %s scored: %s (%s)", lead_id, lead.ai_score, lead.ai_label)
        except Exception as exc:
            logger.error("Failed to score lead %s: %s", lead_id, exc)


async def _batch_score(tenant_id: str):
    import uuid
    from sqlalchemy import select
    from app.database import AsyncSessionLocal
    from app.models.lead import Lead
    from app.services.ai_service import AIService

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lead).where(
                Lead.tenant_id == uuid.UUID(tenant_id),
                Lead.ai_score.is_(None),
            ).limit(100)
        )
        leads = list(result.scalars().all())
        logger.info("Batch scoring %d leads for tenant %s", len(leads), tenant_id)
        for lead in leads:
            try:
                await AIService.classify_lead(db, uuid.UUID(tenant_id), lead)
            except Exception as exc:
                logger.error("Batch score failed for lead %s: %s", lead.id, exc)
        await db.commit()
