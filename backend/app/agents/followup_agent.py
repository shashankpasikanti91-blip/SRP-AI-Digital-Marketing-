"""Agent 8 — Follow-up Agent
Builds automated follow-up sequences: email drips, reminders, nurture flows.
Uses gpt-4o-mini.
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class FollowupStep(BaseModel):
    step_number: int
    delay_days: int              # 0 = immediately, 1 = Day 1, 3 = Day 3, etc.
    channel: str                 # email | whatsapp | sms | call_reminder
    subject: Optional[str] = None   # for email
    body: str
    cta: str
    goal: str                    # what this step aims to achieve
    if_no_reply_action: str      # what happens if lead doesn't respond
    personalisation_tokens: list[str]  # e.g. ["{{name}}", "{{company}}"]


class FollowupSequenceOutput(BaseModel):
    sequence_name: str
    trigger: str                 # what triggers this sequence
    total_steps: int
    total_duration_days: int
    target_segment: str
    goal: str
    steps: list[FollowupStep]
    exit_conditions: list[str]   # when to stop the sequence
    success_metric: str


FOLLOWUP_SYSTEM_PROMPT = """You are an expert marketing automation specialist.
You design effective follow-up sequences that nurture leads through the funnel.
Each sequence must be:
- Timed strategically (not too aggressive, not too passive)
- Personalised with tokens
- Channel-appropriate
- Value-first (give value before asking)
- Clear exit conditions (don't spam people who said no)
Return ONLY valid JSON matching the required schema."""


class FollowupAgent:
    """Agent 8: Creates automated follow-up sequences."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def run(
        self,
        lead_status: str,
        business_name: str,
        offer: str,
        num_steps: int = 5,
        sequence_type: Literal[
            "new_lead", "missed_inquiry", "post_demo", "re_engagement",
            "post_purchase", "upsell", "event_reminder"
        ] = "new_lead",
        channels: Optional[list[str]] = None,
        lead_name_token: str = "{{name}}",
        urgency: str = "medium",
    ) -> FollowupSequenceOutput:
        channels_str = ", ".join(channels) if channels else "email"
        user_prompt = f"""
Build a follow-up sequence:
Business: {business_name}
Sequence Type: {sequence_type}
Lead Status: {lead_status}
Offer: {offer}
Number of Steps: {num_steps}
Channels: {channels_str}
Urgency: {urgency}

Standard delays: Day 0 (immediately), Day 1, Day 3, Day 7, Day 14, Day 30
Use personalisation tokens like {{{{name}}}}, {{{{company}}}}, {{{{offer}}}}.

Return JSON matching:
{json.dumps(FollowupSequenceOutput.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content)
        return FollowupSequenceOutput(**data)
