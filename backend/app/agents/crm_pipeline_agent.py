"""Agent 9 — CRM Pipeline Agent
Manages deal stages, auto-updates based on events, maintains notes & activity.
Uses gpt-4o-mini.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class PipelineDecision(BaseModel):
    recommended_stage: str   # new|contacted|qualified|interested|appointment_booked|proposal_sent|won|lost
    confidence: str          # high|medium|low
    reasoning: str
    next_action: str
    next_action_deadline: str   # e.g. "within 2 hours", "by EOD", "this week"
    reminder_message: str
    deal_health: str            # healthy|at_risk|stalled|hot
    estimated_close_probability: int   # 0-100%
    recommended_follow_up_channel: str
    notes_to_add: str
    red_flags: list[str]
    opportunities: list[str]


CRM_PIPELINE_SYSTEM_PROMPT = """You are an expert CRM pipeline manager and sales coach.
Given a lead's current state and recent activity, you recommend:
1. The most appropriate pipeline stage
2. The next best action with a specific deadline
3. Deal health assessment
4. Closing probability

Pipeline stages:
- new: Just captured, not yet contacted
- contacted: First contact made
- qualified: Confirmed they are a potential buyer
- interested: Showed clear buying interest
- appointment_booked: Meeting/demo scheduled
- proposal_sent: Proposal or quote sent
- won: Deal closed successfully
- lost: Deal lost

Always be specific and time-bound with recommendations. Return ONLY valid JSON."""


class CRMPipelineAgent:
    """Agent 9: Manages CRM stages and provides pipeline decisions."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def run(
        self,
        lead_name: str,
        current_stage: str,
        lead_score: int,
        lead_label: str,
        source: str,
        days_in_current_stage: int,
        last_interaction: Optional[str] = None,
        last_message: Optional[str] = None,
        deal_value: Optional[int] = None,
        notes_history: Optional[list[str]] = None,
        num_follow_ups_sent: int = 0,
        appointment_date: Optional[str] = None,
    ) -> PipelineDecision:
        notes_text = "\n".join(f"- {n}" for n in notes_history) if notes_history else "No notes"
        user_prompt = f"""
CRM Decision for:
Name: {lead_name}
Current Stage: {current_stage}
AI Score: {lead_score}/100 ({lead_label})
Source: {source}
Days in Current Stage: {days_in_current_stage}
Last Interaction: {last_interaction or "Unknown"}
Last Message: {last_message or "None"}
Deal Value: {deal_value or "Unknown"}
Follow-ups Sent: {num_follow_ups_sent}
Appointment Date: {appointment_date or "None scheduled"}
Notes History:
{notes_text}

Analyse this deal and provide a pipeline decision. Return JSON matching:
{json.dumps(PipelineDecision.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": CRM_PIPELINE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.4,
        )
        data = json.loads(response.choices[0].message.content)
        return PipelineDecision(**data)
