"""Analytics Router"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.core.dependencies import DB, CurrentTenant
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=AnalyticsOverviewResponse)
async def overview(
    tenant: CurrentTenant,
    db: DB,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    """Platform-wide KPI summary with trends, funnel, and platform stats."""
    return await AnalyticsService.get_overview(db, tenant.id, from_date=from_date, to_date=to_date)


@router.get("/leads")
async def leads_analytics(
    tenant: CurrentTenant,
    db: DB,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    campaign: Optional[str] = Query(None),
    granularity: str = Query("day", regex="^(day|week|month)$"),
):
    """Leads count over time, grouped by campaign/source."""
    return await AnalyticsService.get_leads_trend(
        db, tenant.id, from_date=from_date, to_date=to_date, campaign=campaign, granularity=granularity
    )


@router.get("/conversion")
async def conversion_funnel(tenant: CurrentTenant, db: DB):
    """CRM funnel conversion rates across all stages."""
    return await AnalyticsService.get_conversion_funnel(db, tenant.id)


@router.get("/social")
async def social_analytics(
    tenant: CurrentTenant,
    db: DB,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    """Social media post performance by platform."""
    return await AnalyticsService.get_social_stats(db, tenant.id, from_date=from_date, to_date=to_date)


@router.get("/email")
async def email_analytics(
    tenant: CurrentTenant,
    db: DB,
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
):
    """Email campaign open rates and CTR."""
    return await AnalyticsService.get_email_stats(db, tenant.id, from_date=from_date, to_date=to_date)


@router.get("/revenue")
async def revenue_analytics(tenant: CurrentTenant, db: DB):
    """Won deals and pipeline value by stage."""
    return await AnalyticsService.get_revenue_stats(db, tenant.id)
