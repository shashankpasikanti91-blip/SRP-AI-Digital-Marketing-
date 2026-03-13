"""Agent 7 — Conversation Agent
Generates AI replies for Messenger, Instagram DMs, WhatsApp, chat, email.
Ultra-fast using gpt-4o-mini. Safety guardrails built in.
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class ConversationReply(BaseModel):
    reply: str
    tone_used: str
    detected_intent: str          # inquiry | complaint | appointment | purchase | spam | escalation
    should_escalate: bool
    escalation_reason: Optional[str] = None
    appointment_detected: bool
    suggested_next_step: str
    confidence: str               # high | medium | low


CONVERSATION_SYSTEM_PROMPT = """You are a professional customer communication specialist for the SRP AI Marketing Manager platform.
You generate contextual, empathetic, and conversion-focused replies for business communications.

STRICT RULES — you MUST follow:
1. Always be professional, courteous, and on-brand
2. Never discuss anything outside the business context
3. Flag conversations that need human escalation
4. Detect appointment booking intent and capture it
5. Keep replies concise and actionable
6. Support multiple languages — reply in the same language as the customer
7. Never make promises you can't keep
8. If a message seems like spam, mark it accordingly

Return ONLY valid JSON matching the required schema."""


class ConversationAgent:
    """Agent 7: Generates AI replies for customer conversations."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def run(
        self,
        customer_message: str,
        channel: Literal["facebook", "instagram", "whatsapp", "email", "website_chat"],
        business_name: str,
        business_type: str,
        customer_name: Optional[str] = None,
        tone: Literal["professional", "friendly", "casual"] = "friendly",
        faq_context: Optional[str] = None,
        previous_messages: Optional[list[dict]] = None,
        business_hours: Optional[str] = None,
        offer: Optional[str] = None,
    ) -> ConversationReply:
        context_parts = [
            f"Business: {business_name} ({business_type})",
            f"Channel: {channel}",
            f"Customer: {customer_name or 'Unknown'}",
            f"Tone: {tone}",
        ]
        if faq_context:
            context_parts.append(f"FAQ/Knowledge base: {faq_context}")
        if business_hours:
            context_parts.append(f"Business hours: {business_hours}")
        if offer:
            context_parts.append(f"Current offer: {offer}")

        messages_for_api: list[dict] = [
            {"role": "system", "content": CONVERSATION_SYSTEM_PROMPT},
        ]
        # Add conversation history
        if previous_messages:
            for msg in previous_messages[-6:]:  # last 6 messages for context
                messages_for_api.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", ""),
                })

        messages_for_api.append({
            "role": "user",
            "content": f"Context:\n{chr(10).join(context_parts)}\n\nCustomer message: {customer_message}\n\nGenerate a reply. Return JSON matching:\n{json.dumps(ConversationReply.model_json_schema(), indent=2)}",
        })

        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.6,
        )
        data = json.loads(response.choices[0].message.content)
        return ConversationReply(**data)
