"""Email Sequence Worker — sends email campaign sequences via SMTP"""

import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.email_worker.send_campaign_task", bind=True, max_retries=3)
def send_campaign_task(self, campaign_id: str, tenant_id: str, lead_ids: list[str], recipient_emails: list[str]):
    """Send first sequence step to a list of recipients."""
    asyncio.run(_send_campaign(campaign_id, tenant_id, lead_ids, recipient_emails))


@celery_app.task(name="app.workers.email_worker.process_email_sequences")
def process_email_sequences():
    """Hourly: check for pending drip sequence sends and dispatch them."""
    asyncio.run(_process_sequences())


async def _send_campaign(campaign_id: str, tenant_id: str, lead_ids: list[str], recipient_emails: list[str]):
    import uuid
    import aiosmtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from sqlalchemy import select
    from app.config import settings
    from app.database import AsyncSessionLocal
    from app.models.email_campaign import EmailCampaign, EmailLog, EmailSequence
    from app.models.lead import Lead

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(EmailCampaign).where(EmailCampaign.id == campaign_id)
        )
        campaign = result.scalar_one_or_none()
        if not campaign:
            logger.error("Campaign %s not found", campaign_id)
            return

        # Get first sequence step
        seq_result = await db.execute(
            select(EmailSequence)
            .where(EmailSequence.campaign_id == campaign.id)
            .order_by(EmailSequence.step_order.asc())
            .limit(1)
        )
        sequence = seq_result.scalar_one_or_none()
        if not sequence:
            logger.warning("Campaign %s has no sequence steps", campaign_id)
            return

        # Collect recipient emails from leads
        if lead_ids:
            leads_result = await db.execute(
                select(Lead).where(Lead.id.in_([uuid.UUID(lid) for lid in lead_ids]))
            )
            leads = list(leads_result.scalars().all())
            recipient_emails.extend([l.email for l in leads if l.email])

        recipient_emails = list(set(recipient_emails))  # deduplicate

        smtp = aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=False,
            start_tls=settings.SMTP_TLS,
        )
        await smtp.connect()
        if settings.SMTP_USER:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        for email_addr in recipient_emails:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = sequence.subject
                msg["From"] = f"{campaign.from_name or settings.SMTP_FROM_NAME} <{campaign.from_email or settings.SMTP_FROM_EMAIL}>"
                msg["To"] = email_addr
                msg.attach(MIMEText(sequence.body_text or "", "plain"))
                msg.attach(MIMEText(sequence.body_html, "html"))
                await smtp.send_message(msg)

                log = EmailLog(
                    campaign_id=campaign.id,
                    sequence_id=sequence.id,
                    recipient_email=email_addr,
                )
                from datetime import datetime, timezone
                log.sent_at = datetime.now(timezone.utc)
                db.add(log)
                campaign.total_sent = (campaign.total_sent or 0) + 1
                logger.info("Email sent to %s for campaign %s", email_addr, campaign_id)
            except Exception as exc:
                logger.error("Failed to send to %s: %s", email_addr, exc)
                db_log = EmailLog(
                    campaign_id=campaign.id,
                    sequence_id=sequence.id,
                    recipient_email=email_addr,
                    error_message=str(exc),
                    bounced=True,
                )
                db.add(db_log)

        await smtp.quit()
        await db.commit()


async def _process_sequences():
    """
    Evaluate drip sequences: for each lead enrolled in an active campaign,
    check if the next scheduled step is due and send it.
    Full drip logic would be implemented here in production.
    """
    logger.info("Processing email drip sequences...")
    # Implementation: query EmailLog, find enrolled leads, check delay_days, send next step
    # This is a placeholder for the full drip engine
