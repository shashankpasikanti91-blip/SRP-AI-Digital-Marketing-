"""Agent 5 — Lead Capture Agent
Normalises and enriches raw lead data from any channel into a standard CRM record.
Very lightweight — uses gpt-4o-mini only if enrichment is needed.
"""
from __future__ import annotations

import json
import re
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class NormalisedLead(BaseModel):
    name: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    source: str
    campaign: Optional[str] = None
    medium: Optional[str] = None
    channel: str              # facebook | instagram | website | whatsapp | email | linkedin | direct
    intent_signals: list[str]
    urgency_level: str        # high | medium | low
    language_detected: str
    notes_cleaned: Optional[str] = None
    enrichment_notes: str


LEAD_CAPTURE_SYSTEM_PROMPT = """You are a CRM data specialist. Your job is to:
1. Normalise raw lead data from various sources into a clean, structured record
2. Detect intent signals from any text/notes
3. Estimate urgency level based on context
4. Detect the language of any message
5. Clean and standardise phone numbers and names
Return ONLY valid JSON matching the required schema."""


class LeadCaptureAgent:
    """Agent 5: Normalises raw lead data into standard CRM record."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def _quick_normalise(self, raw_name: str) -> tuple[str, str]:
        """Fast name splitting without AI."""
        parts = raw_name.strip().split()
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])
        return raw_name, ""

    async def run(
        self,
        raw_name: str,
        source: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        raw_message: Optional[str] = None,
        utm_params: Optional[dict] = None,
        form_data: Optional[dict] = None,
    ) -> NormalisedLead:
        """Normalise and enrich lead data."""
        first, last = self._quick_normalise(raw_name)
        channel = self._detect_channel(source)

        user_prompt = f"""
Raw Lead Data:
Name: {raw_name}
Email: {email or "Not provided"}
Phone: {phone or "Not provided"}
Company: {company or "Not provided"}
Source: {source}
Raw Message/Notes: {raw_message or "None"}
UTM Parameters: {json.dumps(utm_params or {})}
Form Data: {json.dumps(form_data or {})}

Detected channel: {channel}

Normalise this lead data, detect intent signals and urgency. Return JSON matching:
{json.dumps(NormalisedLead.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": LEAD_CAPTURE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.3,
        )
        data = json.loads(response.choices[0].message.content)
        return NormalisedLead(**data)

    def _detect_channel(self, source: str) -> str:
        source_lower = source.lower()
        channel_map = {
            "facebook": "facebook",
            "instagram": "instagram",
            "linkedin": "linkedin",
            "whatsapp": "whatsapp",
            "email": "email",
            "website": "website",
            "web": "website",
            "form": "website",
        }
        for key, val in channel_map.items():
            if key in source_lower:
                return val
        return "direct"
