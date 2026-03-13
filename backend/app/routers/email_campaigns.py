"""Email Campaign Router"""

import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import DB, CurrentTenant
from app.schemas.email_campaign import (
    EmailCampaignCreate,
    EmailCampaignResponse,
    EmailCampaignUpdate,
    EmailSendRequest,
    EmailSequenceCreate,
    EmailSequenceResponse,
    EmailStatsResponse,
)
from app.services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["Email Automation"])


@router.post("/campaigns/", response_model=EmailCampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(payload: EmailCampaignCreate, tenant: CurrentTenant, db: DB):
    return await EmailService.create_campaign(db, tenant.id, payload)


@router.get("/campaigns/", response_model=list[EmailCampaignResponse])
async def list_campaigns(tenant: CurrentTenant, db: DB):
    return await EmailService.list_campaigns(db, tenant.id)


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def get_campaign(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    campaign = await EmailService.get_campaign(db, tenant.id, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
async def update_campaign(campaign_id: uuid.UUID, payload: EmailCampaignUpdate, tenant: CurrentTenant, db: DB):
    campaign = await EmailService.update_campaign(db, tenant.id, campaign_id, payload)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.delete("/campaigns/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    deleted = await EmailService.delete_campaign(db, tenant.id, campaign_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Campaign not found")


@router.post("/campaigns/{campaign_id}/sequences/", response_model=EmailSequenceResponse, status_code=status.HTTP_201_CREATED)
async def add_sequence(campaign_id: uuid.UUID, payload: EmailSequenceCreate, tenant: CurrentTenant, db: DB):
    seq = await EmailService.add_sequence(db, tenant.id, campaign_id, payload)
    if not seq:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return seq


@router.get("/campaigns/{campaign_id}/sequences/", response_model=list[EmailSequenceResponse])
async def list_sequences(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    return await EmailService.list_sequences(db, tenant.id, campaign_id)


@router.post("/campaigns/{campaign_id}/send", status_code=status.HTTP_202_ACCEPTED)
async def send_campaign(campaign_id: uuid.UUID, payload: EmailSendRequest, tenant: CurrentTenant, db: DB):
    """Trigger campaign send — enqueues Celery task."""
    await EmailService.trigger_send(db, tenant.id, campaign_id, payload)
    return {"message": "Campaign send enqueued", "campaign_id": str(campaign_id)}


@router.get("/campaigns/{campaign_id}/stats", response_model=EmailStatsResponse)
async def campaign_stats(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    stats = await EmailService.get_stats(db, tenant.id, campaign_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return stats
