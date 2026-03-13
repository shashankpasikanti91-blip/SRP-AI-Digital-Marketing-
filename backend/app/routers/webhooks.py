"""Webhooks Router — public endpoints for external lead capture"""

import hashlib
import hmac
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.lead import Lead, LeadStatus
from app.models.notification import Notification
from app.models.tenant import Tenant

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


# ── Schemas ────────────────────────────────────────────────────────────────

class WebhookLeadPayload(BaseModel):
    """Public webhook payload for capturing leads from external forms / landing pages."""
    name: str = Field(..., min_length=1, max_length=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    company: Optional[str] = Field(None, max_length=120)
    source: Optional[str] = Field(None, max_length=80)
    campaign: Optional[str] = Field(None, max_length=120)
    medium: Optional[str] = Field(None, max_length=80)
    notes: Optional[str] = None
    # UTM parameters
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_content: Optional[str] = None


async def _capture_lead_background(
    tenant_api_key: str,
    payload: WebhookLeadPayload,
    ip_address: Optional[str],
):
    """Background task: create lead & notification in a fresh DB session."""
    async with AsyncSessionLocal() as db:
        try:
            # Resolve tenant
            result = await db.execute(
                select(Tenant).where(Tenant.api_key == tenant_api_key, Tenant.is_active == True)
            )
            tenant = result.scalar_one_or_none()
            if not tenant:
                return

            source = payload.source or payload.utm_source or "webhook"
            campaign = payload.campaign or payload.utm_campaign

            lead = Lead(
                tenant_id=tenant.id,
                name=payload.name,
                email=str(payload.email) if payload.email else None,
                phone=payload.phone,
                company=payload.company,
                source=source,
                campaign=campaign,
                medium=payload.medium or payload.utm_medium,
                notes=payload.notes,
                status=LeadStatus.NEW,
            )
            db.add(lead)
            await db.flush()

            # Create notification
            notif = Notification(
                tenant_id=tenant.id,
                type="lead_captured",
                title=f"New lead from {source}",
                body=f"{payload.name} ({payload.email or 'no email'}) — {campaign or 'no campaign'}",
                link=f"/leads",
                is_read=False,
            )
            db.add(notif)

            await db.commit()

            # Fire AI scoring in background
            try:
                from app.workers.ai_worker import score_lead_task
                score_lead_task.delay(str(lead.id), str(tenant.id))
            except Exception:
                pass
        except Exception:
            await db.rollback()
            raise


@router.post("/lead/{api_key}", status_code=status.HTTP_202_ACCEPTED)
async def capture_lead_via_webhook(
    api_key: str,
    payload: WebhookLeadPayload,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """
    Public endpoint — embed in any website/form to capture leads.
    Authenticate with your tenant API key in the URL path.
    No JWT required. CORS-safe.

    Example:
      POST /api/v1/webhooks/lead/{your_api_key}
      { "name": "John Doe", "email": "john@example.com", "source": "homepage" }
    """
    ip = request.client.host if request.client else None
    background_tasks.add_task(_capture_lead_background, api_key, payload, ip)
    return {"status": "accepted", "message": "Lead will be processed shortly"}


@router.post("/lead/{api_key}/verify")
async def verify_webhook(api_key: str, request: Request):
    """Quick verification check for the webhook endpoint."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Tenant.id, Tenant.name).where(Tenant.api_key == api_key, Tenant.is_active == True)
        )
        row = result.one_or_none()
        if not row:
            raise HTTPException(status_code=404, detail="Invalid API key")
        return {
            "valid": True,
            "tenant": row.name,
            "endpoint": str(request.url),
        }
