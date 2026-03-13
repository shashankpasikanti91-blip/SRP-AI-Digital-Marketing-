"""System Chatbot Agent
A focused customer-support chatbot that ONLY discusses the SRP AI Marketing Manager platform.
Uses gpt-4o-mini for cost efficiency.
Strict safety rules: no harmful, political, sexual, or off-topic content.
"""
from __future__ import annotations

from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI

from app.config import settings

CHATBOT_SYSTEM_PROMPT = """You are "SRP Assistant", the official AI support chatbot for SRP AI Marketing Manager — a multi-tenant AI marketing automation platform.

YOUR PURPOSE:
Help users understand and use the SRP AI Marketing Manager platform.

WHAT YOU CAN DISCUSS:
1. How to use the platform (leads, CRM, campaigns, analytics, AI agents)
2. Setting up business profiles and onboarding
3. Understanding the 10 AI agents (Strategy, Content, Design Brief, Campaign, Lead Capture, Lead Qualification, Conversation, Follow-up, CRM Pipeline, Analytics)
4. Marketing best practices relevant to using this platform
5. Troubleshooting features within the platform
6. Understanding lead scoring, campaign planning, and follow-up automation
7. API keys, webhooks, and integrations
8. How to read analytics and dashboards

WHAT YOU ABSOLUTELY CANNOT DO:
- Discuss topics completely unrelated to the platform or digital marketing
- Generate harmful, hateful, violent, racist, sexist, or discriminatory content
- Discuss politics, religion, or controversial personal topics
- Engage with sexual, explicit, or inappropriate content
- Impersonate other systems or people
- Provide legal, medical, or financial advice
- Discuss competitors in a negative way

IF SOMEONE ASKS OFF-TOPIC:
Politely redirect: "I'm specifically designed to help with SRP AI Marketing Manager. I can help you with [list relevant topics]. Is there something about the platform I can help with?"

TONE: Friendly, professional, helpful, concise.
Always ask clarifying questions if a request is unclear.
Keep responses concise — 2-4 paragraphs max unless a detailed how-to is needed."""


class ChatbotAgent:
    """Focused platform support chatbot using gpt-4o-mini."""

    SAFE_MODEL = "gpt-4o-mini"

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        user_context: Optional[dict] = None,
    ) -> str:
        """Single-turn or multi-turn chat response."""
        messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]

        # Add user context if available
        if user_context:
            ctx_parts = []
            if user_context.get("tenant_name"):
                ctx_parts.append(f"User's business: {user_context['tenant_name']}")
            if user_context.get("plan"):
                ctx_parts.append(f"Plan: {user_context['plan']}")
            if ctx_parts:
                messages.append({
                    "role": "system",
                    "content": f"User context: {', '.join(ctx_parts)}",
                })

        # Add conversation history (last 10 messages)
        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        response = await self._client.chat.completions.create(
            model=self.SAFE_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.6,
        )
        return response.choices[0].message.content

    async def chat_stream(
        self,
        user_message: str,
        conversation_history: Optional[list[dict]] = None,
        user_context: Optional[dict] = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat response — yields text chunks."""
        messages = [{"role": "system", "content": CHATBOT_SYSTEM_PROMPT}]

        if user_context:
            ctx_parts = []
            if user_context.get("tenant_name"):
                ctx_parts.append(f"User's business: {user_context['tenant_name']}")
            if user_context.get("plan"):
                ctx_parts.append(f"Plan: {user_context['plan']}")
            if ctx_parts:
                messages.append({
                    "role": "system",
                    "content": f"User context: {', '.join(ctx_parts)}",
                })

        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg.get("role") in ("user", "assistant") and msg.get("content"):
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        stream = await self._client.chat.completions.create(
            model=self.SAFE_MODEL,
            messages=messages,
            max_tokens=1000,
            temperature=0.6,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
