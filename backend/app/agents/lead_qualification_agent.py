"""Agent 6 — Lead Qualification Agent
Scores leads 0-100, labels hot/warm/cold/spam, provides detailed reasoning.
Uses gpt-4o-mini for cost efficiency at scale.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings


class QualificationOutput(BaseModel):
    score: int = Field(..., ge=0, le=100)
    label: str = Field(..., pattern="^(hot|warm|cold|spam)$")
    confidence: str = Field(..., pattern="^(high|medium|low)$")

    # Score breakdown dimensions
    urgency_score: int = Field(..., ge=0, le=25)
    intent_score: int = Field(..., ge=0, le=25)
    fit_score: int = Field(..., ge=0, le=25)
    engagement_score: int = Field(..., ge=0, le=25)

    reasoning: str
    key_buying_signals: list[str]
    red_flags: list[str]
    recommended_action: str
    recommended_response_channel: str   # email | call | whatsapp | dm
    ideal_follow_up_time: str           # e.g. "within 1 hour", "within 24 hours"
    estimated_deal_value: Optional[str] = None
    objection_prediction: list[str]


QUALIFICATION_SYSTEM_PROMPT = """You are an expert B2B/B2C sales qualification specialist.
You analyse lead data and score them based on:
- Urgency (0-25): How quickly do they need a solution?
- Intent (0-25): How likely are they to buy?
- Fit (0-25): How well does the offer match their needs?
- Engagement (0-25): How engaged are they with the brand?

Labels:
- hot (80-100): Ready to buy, contact immediately
- warm (50-79): Interested, needs nurturing
- cold (20-49): Early stage, add to automation
- spam (0-19): Not a real prospect

Always provide specific, actionable reasoning. Return ONLY valid JSON."""


class LeadQualificationAgent:
    """Agent 6: Scores and qualifies leads with detailed reasoning."""

    def __init__(self):
        from app.services.model_router import get_model_router, FeatureBucket
        router = get_model_router()
        self._client, self._model = router.resolve(FeatureBucket.lead_classification)

    async def run(
        self,
        name: str,
        source: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        job_title: Optional[str] = None,
        message: Optional[str] = None,
        campaign: Optional[str] = None,
        industry: Optional[str] = None,
        target_customer_profile: Optional[str] = None,
        previous_interactions: Optional[int] = 0,
        time_since_first_contact: Optional[str] = None,
    ) -> QualificationOutput:
        user_prompt = f"""
Lead to qualify:
Name: {name}
Email: {email or "Unknown"}
Phone: {phone or "Unknown"}
Company: {company or "Unknown"}
Job Title: {job_title or "Unknown"}
Source: {source}
Campaign: {campaign or "Unknown"}
Message/Notes: {message or "No message provided"}
Industry: {industry or "Unknown"}
Ideal Customer Profile: {target_customer_profile or "Not specified"}
Previous Interactions: {previous_interactions}
Time Since First Contact: {time_since_first_contact or "First contact now"}

Qualify this lead thoroughly. Return JSON matching:
{json.dumps(QualificationOutput.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": QUALIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=1000,
            temperature=0.4,
        )
        data = json.loads(response.choices[0].message.content)
        return QualificationOutput(**data)
