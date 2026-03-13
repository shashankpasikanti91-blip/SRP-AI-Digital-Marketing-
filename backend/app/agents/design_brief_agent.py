"""Agent 3 — Design Brief Agent
Generates creative briefs for image ads, reels, carousels, banners.
Uses gpt-4o-mini.
"""
from __future__ import annotations

import json
from typing import Literal, Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings


class DesignDirective(BaseModel):
    element: str          # background | typography | imagery | cta_button | overlay
    description: str
    color_suggestion: Optional[str] = None


class DesignBriefOutput(BaseModel):
    format_type: str           # image_ad | reel | carousel | banner | story
    headline: str
    subheadline: str
    body_copy: str
    cta_text: str
    cta_color: str
    background_direction: str
    typography_style: str
    imagery_description: str
    color_palette: list[str]   # hex codes or descriptive colors
    mood: str
    visual_hierarchy: list[str]  # ordered elements top → bottom
    design_directives: list[DesignDirective]
    sizes_required: list[str]    # 1080x1080, 1920x1080, 1080x1920 etc.
    do_list: list[str]
    dont_list: list[str]
    reference_style: str


DESIGN_BRIEF_SYSTEM_PROMPT = """You are a senior creative director and visual branding expert.
You create detailed, production-ready design briefs that any designer can execute.
Be specific with colors (hex codes preferred), typography, layout, and visual direction.
Return ONLY valid JSON matching the required schema."""


class DesignBriefAgent:
    """Agent 3: Creates creative briefs for ad creatives."""

    def __init__(self):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def run(
        self,
        campaign_name: str,
        format_type: Literal["image_ad", "reel", "carousel", "banner", "story"],
        platform: str,
        headline: str,
        brand_colors: Optional[list[str]] = None,
        target_audience: str = "General audience",
        campaign_objective: str = "Lead generation",
        tone: str = "Professional",
        existing_brand_guide: Optional[str] = None,
        content_copy: Optional[str] = None,
    ) -> DesignBriefOutput:
        user_prompt = f"""
Campaign: {campaign_name}
Format: {format_type}
Platform: {platform}
Headline: {headline}
Brand Colors: {", ".join(brand_colors) if brand_colors else "Not specified – suggest appropriate colors"}
Target Audience: {target_audience}
Campaign Objective: {campaign_objective}
Tone/Mood: {tone}
Content Copy: {content_copy or "Not provided"}
Brand Guide Notes: {existing_brand_guide or "No brand guide – create compelling defaults"}

Create a detailed, production-ready design brief. Return JSON matching this schema:
{json.dumps(DesignBriefOutput.model_json_schema(), indent=2)}
"""
        response = await self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": DESIGN_BRIEF_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=1500,
            temperature=0.7,
        )
        data = json.loads(response.choices[0].message.content)
        return DesignBriefOutput(**data)
