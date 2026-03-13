"""Agent 4 — Campaign Agent
Builds full campaign plans: objectives, schedule, budget allocation, funnel.
Uses gpt-4o-mini.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class PostScheduleItem(BaseModel):
    week: int
    day: str
    time: str
    platform: str
    content_type: str
    topic: str


class BudgetItem(BaseModel):
    channel: str
    amount: int           # in user's currency
    percentage: int
    purpose: str


class CampaignPlanOutput(BaseModel):
    campaign_name: str
    campaign_objective: str
    duration_weeks: int
    target_audience: str
    channels: list[str]
    funnel_stages: list[dict]     # awareness→interest→desire→action
    posting_schedule: list[PostScheduleItem]
    budget_breakdown: list[BudgetItem]
    total_budget: int
    expected_reach: str
    expected_leads: str
    kpis: list[str]
    success_metrics: dict[str, str]
    ab_test_ideas: list[str]
    content_themes: list[str]
    call_to_actions: list[str]
    landing_page_requirements: list[str]


CAMPAIGN_SYSTEM_PROMPT = """You are an expert performance marketing strategist.
You create detailed, realistic, and ROI-focused campaign plans.
Always include specific schedules, budget breakdowns, and measurable KPIs.
Return ONLY valid JSON matching the required schema."""


class CampaignAgent:
    """Agent 4: Creates full campaign plans."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def run(
        self,
        business_name: str,
        campaign_goal: str,
        budget: int,
        currency: str = "USD",
        duration_weeks: int = 4,
        channels: Optional[list[str]] = None,
        target_audience: str = "General audience",
        industry: str = "General",
        offer: Optional[str] = None,
        start_date: Optional[str] = None,
    ) -> CampaignPlanOutput:
        channels_str = ", ".join(channels) if channels else "Facebook, Instagram, email"
        user_prompt = f"""
Business: {business_name}
Campaign Goal: {campaign_goal}
Total Budget: {currency} {budget}
Duration: {duration_weeks} weeks
Channels: {channels_str}
Target Audience: {target_audience}
Industry: {industry}
Offer/Product: {offer or "Not specified"}
Start Date: {start_date or "As soon as possible"}

Create a detailed, actionable campaign plan. Return JSON matching this schema:
{json.dumps(CampaignPlanOutput.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CAMPAIGN_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content)
        return CampaignPlanOutput(**data)
