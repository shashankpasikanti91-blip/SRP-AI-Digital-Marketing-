"""Analytics Pydantic Schemas"""

from typing import Optional

from pydantic import BaseModel, Field


class AnalyticsOverview(BaseModel):
    total_leads: int
    new_leads_today: int
    total_pipeline_value: int  # cents
    conversion_rate: float
    active_campaigns: int
    posts_scheduled: int
    emails_sent_today: int


class LeadsAnalytics(BaseModel):
    date: str
    count: int
    source: Optional[str] = None
    campaign: Optional[str] = None


class ConversionFunnel(BaseModel):
    stage: str
    count: int
    percentage: float


class PlatformStats(BaseModel):
    platform: str
    posts_published: int
    posts_scheduled: int
    posts_failed: int


class EmailStats(BaseModel):
    campaign_id: str
    campaign_name: str
    sent: int
    opened: int
    clicked: int
    open_rate: float
    click_rate: float


class AnalyticsOverviewResponse(BaseModel):
    overview: AnalyticsOverview
    leads_trend: list[LeadsAnalytics]
    funnel: list[ConversionFunnel]
    platform_stats: list[PlatformStats]
    email_stats: list[EmailStats]
