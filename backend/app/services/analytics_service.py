"""Analytics Service"""

import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.crm import CRMPipeline, CRMStage
from app.models.email_campaign import EmailCampaign
from app.models.campaign import Campaign, CampaignStatus
from app.models.lead import Lead
from app.models.social import PostStatus, SocialPost
from app.schemas.analytics import (
    AnalyticsOverview,
    AnalyticsOverviewResponse,
    ConversionFunnel,
    EmailStats,
    LeadsAnalytics,
    PlatformStats,
)


class AnalyticsService:

    @staticmethod
    async def get_overview(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> AnalyticsOverviewResponse:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Total leads
        total_leads = (
            await db.execute(select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id))
        ).scalar_one()

        # New leads today
        new_leads_today = (
            await db.execute(
                select(func.count(Lead.id)).where(
                    Lead.tenant_id == tenant_id, Lead.created_at >= today_start
                )
            )
        ).scalar_one()

        # Pipeline value (sum of all won + active deals)
        pipeline_value = (
            await db.execute(
                select(func.coalesce(func.sum(CRMPipeline.value), 0)).where(
                    CRMPipeline.tenant_id == tenant_id, CRMPipeline.value.isnot(None)
                )
            )
        ).scalar_one()

        # Conversion rate: converted leads / total leads
        converted = (
            await db.execute(
                select(func.count(Lead.id)).where(
                    Lead.tenant_id == tenant_id, Lead.status == "converted"
                )
            )
        ).scalar_one()
        conversion_rate = round((converted / total_leads * 100) if total_leads > 0 else 0.0, 2)

        # Active campaigns — count from Campaign table (primary campaigns store)
        active_campaigns = (
            await db.execute(
                select(func.count(Campaign.id)).where(
                    Campaign.tenant_id == tenant_id,
                    Campaign.status == CampaignStatus.ACTIVE,
                )
            )
        ).scalar_one()

        # Scheduled posts
        posts_scheduled = (
            await db.execute(
                select(func.count(SocialPost.id)).where(
                    SocialPost.tenant_id == tenant_id, SocialPost.status == PostStatus.SCHEDULED
                )
            )
        ).scalar_one()

        overview = AnalyticsOverview(
            total_leads=total_leads,
            new_leads_today=new_leads_today,
            total_pipeline_value=int(pipeline_value or 0),
            conversion_rate=conversion_rate,
            active_campaigns=active_campaigns,
            posts_scheduled=posts_scheduled,
            emails_sent_today=0,
        )

        leads_trend = await AnalyticsService.get_leads_trend(db, tenant_id, from_date=from_date, to_date=to_date)
        funnel = await AnalyticsService.get_conversion_funnel(db, tenant_id)
        platform_stats = await AnalyticsService.get_social_stats(db, tenant_id, from_date=from_date, to_date=to_date)
        email_stats = await AnalyticsService.get_email_stats(db, tenant_id, from_date=from_date, to_date=to_date)

        return AnalyticsOverviewResponse(
            overview=overview,
            leads_trend=leads_trend,
            funnel=funnel,
            platform_stats=platform_stats,
            email_stats=email_stats,
        )

    @staticmethod
    async def get_leads_trend(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        campaign: Optional[str] = None,
        granularity: str = "day",
    ) -> list[LeadsAnalytics]:
        query = select(
            func.date_trunc(granularity, Lead.created_at).label("period"),
            func.count(Lead.id).label("count"),
            Lead.source,
            Lead.campaign,
        ).where(Lead.tenant_id == tenant_id)

        if from_date:
            query = query.where(Lead.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.where(Lead.created_at <= datetime.combine(to_date, datetime.max.time()))
        if campaign:
            query = query.where(Lead.campaign == campaign)

        query = query.group_by("period", Lead.source, Lead.campaign).order_by("period")
        rows = (await db.execute(query)).all()
        return [
            LeadsAnalytics(date=str(r.period)[:10], count=r.count, source=r.source, campaign=r.campaign)
            for r in rows if r.period is not None
        ]

    @staticmethod
    async def get_conversion_funnel(db: AsyncSession, tenant_id: uuid.UUID) -> list[ConversionFunnel]:
        from app.models.crm import CRMStage
        rows = (
            await db.execute(
                select(CRMPipeline.stage, func.count(CRMPipeline.id).label("count"))
                .where(CRMPipeline.tenant_id == tenant_id)
                .group_by(CRMPipeline.stage)
            )
        ).all()
        total = sum(r.count for r in rows) or 1
        return [
            ConversionFunnel(stage=r.stage.value if hasattr(r.stage, 'value') else str(r.stage), count=r.count, percentage=round(r.count / total * 100, 2))
            for r in rows
        ]

    @staticmethod
    async def get_social_stats(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[PlatformStats]:
        rows = (
            await db.execute(
                select(
                    SocialPost.platform,
                    func.count(case((SocialPost.status == PostStatus.PUBLISHED, 1))).label("published"),
                    func.count(case((SocialPost.status == PostStatus.SCHEDULED, 1))).label("scheduled"),
                    func.count(case((SocialPost.status == PostStatus.FAILED, 1))).label("failed"),
                )
                .where(SocialPost.tenant_id == tenant_id)
                .group_by(SocialPost.platform)
            )
        ).all()
        return [
            PlatformStats(
                platform=r.platform.value if hasattr(r.platform, 'value') else str(r.platform),
                posts_published=r.published,
                posts_scheduled=r.scheduled,
                posts_failed=r.failed,
            )
            for r in rows
        ]

    @staticmethod
    async def get_email_stats(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[EmailStats]:
        query = select(EmailCampaign).where(EmailCampaign.tenant_id == tenant_id)
        campaigns = list((await db.execute(query)).scalars().all())
        stats = []
        for c in campaigns:
            open_rate = round(c.total_opened / c.total_sent * 100, 2) if c.total_sent else 0.0
            click_rate = round(c.total_clicked / c.total_sent * 100, 2) if c.total_sent else 0.0
            stats.append(EmailStats(
                campaign_id=str(c.id),
                campaign_name=c.name,
                sent=c.total_sent,
                opened=c.total_opened,
                clicked=c.total_clicked,
                open_rate=open_rate,
                click_rate=click_rate,
            ))
        return stats

    @staticmethod
    async def get_revenue_stats(db: AsyncSession, tenant_id: uuid.UUID) -> dict:
        rows = (
            await db.execute(
                select(
                    CRMPipeline.stage,
                    func.count(CRMPipeline.id).label("count"),
                    func.coalesce(func.sum(CRMPipeline.value), 0).label("total_value"),
                )
                .where(CRMPipeline.tenant_id == tenant_id)
                .group_by(CRMPipeline.stage)
            )
        ).all()
        return {
            "by_stage": [
                {"stage": r.stage.value if hasattr(r.stage, 'value') else str(r.stage), "count": r.count, "total_value_cents": r.total_value}
                for r in rows
            ]
        }
