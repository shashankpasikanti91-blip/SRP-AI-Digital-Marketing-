"""Agent 1 — Strategy Agent
Collects business profile and generates a full marketing strategy.
Model is resolved dynamically via model_router (FeatureBucket.campaign_strategy).
"""
from __future__ import annotations

import json
from typing import Optional

from pydantic import BaseModel, Field

from app.services.model_router import FeatureBucket, get_model_router


# ── Output schemas ────────────────────────────────────────────────────────

class AudienceSegment(BaseModel):
    name: str
    description: str
    age_range: str
    pain_points: list[str]
    messaging_angle: str


class CampaignObjective(BaseModel):
    phase: str           # awareness | consideration | conversion
    goal: str
    kpi: str
    suggested_channels: list[str]


class FunnelStage(BaseModel):
    stage: str
    action: str
    content_type: str
    channel: str


class StrategyOutput(BaseModel):
    executive_summary: str
    brand_positioning: str
    unique_selling_proposition: str
    audience_segments: list[AudienceSegment]
    campaign_objectives: list[CampaignObjective]
    funnel: list[FunnelStage]
    recommended_channels: list[str]
    monthly_content_plan: list[str]
    budget_allocation: dict[str, int]          # channel → % allocation
    quick_wins: list[str]
    risks: list[str]
    next_steps: list[str]


STRATEGY_SYSTEM_PROMPT = """You are an expert digital marketing strategist specializing in 
AI-powered marketing automation for businesses of all sizes. You have deep expertise in:
- Lead generation & conversion optimization
- Multi-channel marketing (social media, email, paid ads, content)
- Sales funnel design and CRM pipeline setup
- Performance analytics and optimization

Your task is to generate a comprehensive, actionable marketing strategy.
Always be specific, practical, and results-oriented.
Return ONLY valid JSON matching the required schema."""


class StrategyAgent:
    """Agent 1: Generates full marketing strategy from business profile."""

    def __init__(self):
        pass  # client resolved per-call via model_router

    async def run(
        self,
        business_name: str,
        business_type: str,
        industry: str,
        location: str,
        target_audience: str,
        main_offer: str,
        budget_monthly: Optional[str] = None,
        current_channels: Optional[list[str]] = None,
        goals: Optional[str] = None,
        competitors: Optional[str] = None,
        challenges: Optional[str] = None,
    ) -> StrategyOutput:
        """Generate a comprehensive marketing strategy."""
        user_prompt = f"""
Business Name: {business_name}
Business Type: {business_type}
Industry: {industry}
Location: {location}
Target Audience: {target_audience}
Main Offer/Product/Service: {main_offer}
Monthly Budget: {budget_monthly or "Not specified"}
Current Channels: {", ".join(current_channels) if current_channels else "None"}
Goals: {goals or "Grow business and generate more leads"}
Competitors: {competitors or "Not specified"}
Challenges: {challenges or "Not specified"}

Generate a detailed, actionable marketing strategy. Return JSON matching this schema:
{json.dumps(StrategyOutput.model_json_schema(), indent=2)}
"""
        router = get_model_router()
        client, model_id = router.resolve(FeatureBucket.campaign_strategy)
        response = await client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": STRATEGY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=3000,
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content)
        return StrategyOutput(**data)
