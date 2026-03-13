"""Agent 10 — Analytics & Optimization Agent
Analyses performance data and generates actionable optimization recommendations.
Uses gpt-4o for deep analysis quality.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class ChannelPerformance(BaseModel):
    channel: str
    leads_generated: int
    conversion_rate: float
    cost_per_lead: Optional[float] = None
    engagement_rate: Optional[float] = None
    assessment: str    # excellent | good | average | poor
    recommendation: str


class FunnelBottleneck(BaseModel):
    stage: str
    drop_off_rate: float
    root_cause: str
    fix_recommendation: str
    priority: str    # high | medium | low


class OptimizationOutput(BaseModel):
    overall_health_score: int     # 0-100
    performance_summary: str
    top_performing_channel: str
    worst_performing_channel: str
    channel_performance: list[ChannelPerformance]
    funnel_bottlenecks: list[FunnelBottleneck]
    quick_wins: list[str]
    strategic_recommendations: list[str]
    content_recommendations: list[str]
    budget_reallocation: dict[str, str]
    predicted_revenue_impact: str
    next_30_day_priorities: list[str]
    ab_test_suggestions: list[str]
    risk_alerts: list[str]


ANALYTICS_SYSTEM_PROMPT = """You are an expert data-driven marketing analyst and growth strategist.
You analyse marketing performance data and provide specific, actionable recommendations.
Always:
- Be data-specific (refer to actual numbers)
- Prioritise by impact and effort
- Identify the highest-leverage opportunities
- Spot trends and patterns
- Give ROI estimates where possible
Return ONLY valid JSON matching the required schema."""


class AnalyticsAgent:
    """Agent 10: Analyses performance and generates optimization recommendations."""

    def __init__(self):
        from app.services.model_router import get_model_router, FeatureBucket
        router = get_model_router()
        self._client, self._model = router.resolve(FeatureBucket.campaign_strategy)

    async def run(
        self,
        total_leads: int,
        leads_by_source: dict[str, int],
        conversion_rate: float,
        pipeline_value: int,
        campaigns_data: list[dict],
        email_open_rate: float = 0.0,
        email_click_rate: float = 0.0,
        social_engagement: dict[str, float] = None,
        time_period: str = "last 30 days",
        revenue_won: int = 0,
        avg_deal_size: int = 0,
        lead_response_time_hours: float = 0,
        follow_up_success_rate: float = 0,
    ) -> OptimizationOutput:
        user_prompt = f"""
Analytics Report — {time_period}:

Overview:
- Total Leads: {total_leads}
- Conversion Rate: {conversion_rate:.1f}%
- Pipeline Value: ${pipeline_value:,}
- Revenue Won: ${revenue_won:,}
- Average Deal Size: ${avg_deal_size:,}
- Lead Response Time: {lead_response_time_hours:.1f} hours avg
- Follow-up Success Rate: {follow_up_success_rate:.1f}%

Leads by Source: {json.dumps(leads_by_source)}
Email Performance: Open rate {email_open_rate:.1f}%, Click rate {email_click_rate:.1f}%
Social Engagement: {json.dumps(social_engagement or {})}
Campaigns: {json.dumps(campaigns_data)}

Provide a comprehensive analytics and optimization report. Return JSON matching:
{json.dumps(OptimizationOutput.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": ANALYTICS_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=2500,
            temperature=0.5,
        )
        data = json.loads(response.choices[0].message.content)
        return OptimizationOutput(**data)
