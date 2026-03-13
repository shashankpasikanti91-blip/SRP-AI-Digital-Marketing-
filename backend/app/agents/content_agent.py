"""Agent 2 — Content Agent
Generates social posts, ad copy, email copy, blog topics, CTAs.
Model is resolved dynamically via model_router (FeatureBucket.text_marketing).
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from pydantic import BaseModel

from app.services.model_router import FeatureBucket, get_model_router


class ContentVariant(BaseModel):
    platform: str
    content: str
    hashtags: list[str]
    cta: str
    character_count: int


class ContentOutput(BaseModel):
    primary_copy: str
    headline: str
    subheadline: str
    cta: str
    variants: list[ContentVariant]
    blog_topics: list[str]
    ad_copy_short: str          # ≤ 90 chars for paid ads
    ad_copy_long: str
    email_subject_lines: list[str]
    caption_variants: list[str]


CONTENT_SYSTEM_PROMPT = """You are an expert copywriter and content strategist for digital marketing.
You create compelling, platform-optimised content that drives engagement and conversions.
Always match the tone, platform character limits, and audience.
Return ONLY valid JSON matching the required schema."""


class ContentAgent:
    """Agent 2: Generates multichannel content from a brief."""

    def __init__(self):
        pass  # client resolved per-call via model_router

    async def run(
        self,
        topic: str,
        business_name: str,
        target_audience: str,
        tone: Literal["professional", "casual", "friendly", "urgent", "inspirational", "funny"] = "professional",
        platforms: Optional[list[str]] = None,
        campaign_objective: Optional[str] = None,
        language: str = "English",
        include_hashtags: bool = True,
        include_emoji: bool = True,
        brand_voice: Optional[str] = None,
        offer_details: Optional[str] = None,
    ) -> ContentOutput:
        platforms_str = ", ".join(platforms) if platforms else "Facebook, Instagram, LinkedIn"
        user_prompt = f"""
Topic/Campaign: {topic}
Business: {business_name}
Target Audience: {target_audience}
Tone: {tone}
Platforms: {platforms_str}
Campaign Objective: {campaign_objective or "Lead generation"}
Language: {language}
Include Hashtags: {include_hashtags}
Include Emoji: {include_emoji}
Brand Voice: {brand_voice or "Professional and engaging"}
Offer Details: {offer_details or "Not specified"}

Generate comprehensive content for all channels. Return JSON matching this schema:
{json.dumps(ContentOutput.model_json_schema(), indent=2)}
"""
        router = get_model_router()
        client, model_id = router.resolve(FeatureBucket.text_marketing)
        response = await client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": CONTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=2000,
            temperature=0.8,
        )
        data = json.loads(response.choices[0].message.content)
        return ContentOutput(**data)
