"""Email Campaign Service"""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.email_campaign import CampaignStatus, EmailCampaign, EmailSequence
from app.schemas.email_campaign import (
    EmailCampaignCreate,
    EmailCampaignUpdate,
    EmailSendRequest,
    EmailSequenceCreate,
    EmailStatsResponse,
)


class EmailService:

    @staticmethod
    async def create_campaign(db: AsyncSession, tenant_id: uuid.UUID, payload: EmailCampaignCreate) -> EmailCampaign:
        campaign = EmailCampaign(tenant_id=tenant_id, **payload.model_dump())
        db.add(campaign)
        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def _get_with_sequences(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID) -> EmailCampaign | None:
        result = await db.execute(
            select(EmailCampaign)
            .options(selectinload(EmailCampaign.sequences))
            .where(EmailCampaign.id == campaign_id, EmailCampaign.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_campaign(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID) -> EmailCampaign | None:
        return await EmailService._get_with_sequences(db, tenant_id, campaign_id)

    @staticmethod
    async def list_campaigns(db: AsyncSession, tenant_id: uuid.UUID) -> list[EmailCampaign]:
        result = await db.execute(
            select(EmailCampaign)
            .options(selectinload(EmailCampaign.sequences))
            .where(EmailCampaign.tenant_id == tenant_id)
            .order_by(EmailCampaign.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_campaign(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID, payload: EmailCampaignUpdate) -> EmailCampaign | None:
        campaign = await EmailService._get_with_sequences(db, tenant_id, campaign_id)
        if not campaign:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(campaign, field, value)
        await db.flush()
        await db.refresh(campaign)
        return campaign

    @staticmethod
    async def delete_campaign(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID) -> bool:
        campaign = await EmailService.get_campaign(db, tenant_id, campaign_id)
        if not campaign:
            return False
        await db.delete(campaign)
        return True

    @staticmethod
    async def add_sequence(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        campaign_id: uuid.UUID,
        payload: EmailSequenceCreate,
    ) -> EmailSequence | None:
        campaign = await EmailService.get_campaign(db, tenant_id, campaign_id)
        if not campaign:
            return None
        seq = EmailSequence(campaign_id=campaign_id, **payload.model_dump())
        db.add(seq)
        await db.flush()
        await db.refresh(seq)
        return seq

    @staticmethod
    async def list_sequences(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID) -> list[EmailSequence]:
        campaign = await EmailService.get_campaign(db, tenant_id, campaign_id)
        if not campaign:
            return []
        result = await db.execute(
            select(EmailSequence)
            .where(EmailSequence.campaign_id == campaign_id)
            .order_by(EmailSequence.step_order.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def trigger_send(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID, payload: EmailSendRequest) -> None:
        """Enqueue Celery task for campaign send."""
        try:
            from app.workers.email_worker import send_campaign_task
            send_campaign_task.delay(
                str(campaign_id),
                str(tenant_id),
                [str(e) for e in (payload.lead_ids or [])],
                payload.recipient_emails or [],
            )
        except Exception:
            pass

    @staticmethod
    async def get_stats(db: AsyncSession, tenant_id: uuid.UUID, campaign_id: uuid.UUID) -> EmailStatsResponse | None:
        campaign = await EmailService.get_campaign(db, tenant_id, campaign_id)
        if not campaign:
            return None
        open_rate = (campaign.total_opened / campaign.total_sent * 100) if campaign.total_sent > 0 else 0.0
        click_rate = (campaign.total_clicked / campaign.total_sent * 100) if campaign.total_sent > 0 else 0.0
        return EmailStatsResponse(
            campaign_id=str(campaign.id),
            total_sent=campaign.total_sent,
            total_opened=campaign.total_opened,
            total_clicked=campaign.total_clicked,
            total_unsubscribed=campaign.total_unsubscribed,
            open_rate=round(open_rate, 2),
            click_rate=round(click_rate, 2),
        )
