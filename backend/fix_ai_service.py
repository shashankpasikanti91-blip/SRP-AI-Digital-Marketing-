"""Script to rewrite ai_service.py without pydantic_ai dependency."""
import textwrap, os

NEW_CONTENT = textwrap.dedent('''
"""AI Service — OpenAI-powered agents for all AI capabilities (no pydantic_ai dependency)"""

import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

from app.config import settings
from app.schemas.ai_assistant import (
    CampaignIdeasRequest,
    CampaignIdeasResponse,
    ClassifyLeadRequest,
    ClassifyLeadResponse,
    GeneratePostRequest,
    GeneratePostResponse,
    ReplySuggestionRequest,
    ReplySuggestionResponse,
    WriteEmailRequest,
    WriteEmailResponse,
)

if TYPE_CHECKING:
    import uuid
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.models.lead import Lead


# ── Pydantic Structured Output Models ────────────────────────────────

class PostOutput(BaseModel):
    content: str
    suggested_platforms: list[str]


class LeadClassificationOutput(BaseModel):
    score: int = Field(..., ge=0, le=100)
    label: str
    reasoning: str
    recommended_action: str


class ReplyOutput(BaseModel):
    suggestions: list[str]


class EmailOutput(BaseModel):
    subject: str
    body_html: str
    body_text: str


class CampaignIdeasOutput(BaseModel):
    ideas: list[dict]


# ── OpenAI helper ─────────────────────────────────────────────────────

async def _ai_call(system: str, user: str, output_model: type[BaseModel]) -> tuple[Any, int]:
    """Call OpenAI with JSON mode and parse into the given Pydantic model."""
    import openai
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    schema = output_model.model_json_schema()
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system + "\\n\\nReturn ONLY valid JSON matching: " + json.dumps(schema)},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
        max_tokens=getattr(settings, "AI_MAX_TOKENS", 2000),
        temperature=getattr(settings, "AI_TEMPERATURE", 0.7),
    )
    raw = response.choices[0].message.content or "{}"
    if raw.startswith("```"):
        raw = raw.split("```")[-2].lstrip("json").strip()
    return output_model.model_validate(json.loads(raw)), (response.usage.total_tokens if response.usage else 0)


async def _ai_text(system: str, prompt: str) -> str:
    """Plain text AI call."""
    import openai
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        max_tokens=getattr(settings, "AI_MAX_TOKENS", 2000),
        temperature=getattr(settings, "AI_TEMPERATURE", 0.7),
    )
    return response.choices[0].message.content or ""


# ── System prompts ────────────────────────────────────────────────────
_POST_SYSTEM = "You are an expert social media copywriter. Generate engaging, platform-optimised posts. Return JSON."
_LEAD_SYSTEM = "You are a sales expert. Return score 0-100, label (hot/warm/cold), reasoning, recommended_action as JSON."
_REPLY_SYSTEM = "You are a customer success expert. Generate 3 reply suggestions under 150 words each. Return JSON."
_EMAIL_SYSTEM = "You are an expert email copywriter. Return subject, body_html, body_text as JSON."
_IDEAS_SYSTEM = "You are a marketing strategist. Return JSON with 'ideas' array: title, description, platforms, estimated_budget, kpi."


# ── AIService ─────────────────────────────────────────────────────────

class AIService:

    @staticmethod
    async def generate_social_post(payload: GeneratePostRequest) -> GeneratePostResponse:
        prompt = (
            f"Platform: {payload.platform.value}\\n"
            f"Topic: {payload.topic}\\nTone: {payload.tone}\\n"
            f"Include hashtags: {payload.include_hashtags}\\nInclude CTA: {payload.include_cta}\\n"
            f"Max length: {payload.max_length or 'platform default'}\\n"
            f"Brand voice: {payload.brand_voice or 'professional and engaging'}"
        )
        output, tokens = await _ai_call(_POST_SYSTEM, prompt, PostOutput)
        return GeneratePostResponse(
            content=output.content, character_count=len(output.content),
            suggested_platforms=output.suggested_platforms, tokens_used=tokens,
        )

    @staticmethod
    async def classify_lead_raw(payload: ClassifyLeadRequest) -> ClassifyLeadResponse:
        prompt = (
            f"Lead Name: {payload.name}\\nEmail: {payload.email or 'N/A'}\\n"
            f"Phone: {payload.phone or 'N/A'}\\nCompany: {payload.company or 'N/A'}\\n"
            f"Source: {payload.source or 'N/A'}\\nCampaign: {payload.campaign or 'N/A'}\\n"
            f"Notes: {payload.notes or 'N/A'}"
        )
        output, tokens = await _ai_call(_LEAD_SYSTEM, prompt, LeadClassificationOutput)
        return ClassifyLeadResponse(
            score=output.score, label=output.label, reasoning=output.reasoning,
            recommended_action=output.recommended_action, tokens_used=tokens,
        )

    @staticmethod
    async def classify_lead(db: "AsyncSession", tenant_id: "uuid.UUID", lead: "Lead") -> "Lead":
        from app.schemas.ai_assistant import ClassifyLeadRequest as Req
        payload = Req(lead_id=str(lead.id), name=lead.name, email=lead.email,
                      phone=lead.phone, source=lead.source, campaign=lead.campaign, notes=lead.notes)
        result = await AIService.classify_lead_raw(payload)
        lead.ai_score = result.score
        lead.ai_label = result.label
        await db.flush()
        await db.refresh(lead)
        return lead

    @staticmethod
    async def suggest_reply(payload: ReplySuggestionRequest) -> ReplySuggestionResponse:
        prompt = (
            f"Lead: {payload.lead_name}\\nMessage: {payload.lead_message}\\n"
            f"Context: {payload.context or 'General enquiry'}\\nTone: {payload.tone}"
        )
        output, tokens = await _ai_call(_REPLY_SYSTEM, prompt, ReplyOutput)
        return ReplySuggestionResponse(suggestions=output.suggestions, tokens_used=tokens)

    @staticmethod
    async def write_email(payload: WriteEmailRequest) -> WriteEmailResponse:
        prompt = (
            f"Campaign: {payload.campaign_name}\\nAudience: {payload.target_audience}\\n"
            f"Goal: {payload.goal}\\nTone: {payload.tone}"
        )
        output, tokens = await _ai_call(_EMAIL_SYSTEM, prompt, EmailOutput)
        return WriteEmailResponse(
            subject=output.subject, body_html=output.body_html, body_text=output.body_text, tokens_used=tokens,
        )

    @staticmethod
    async def generate_campaign_ideas(payload: CampaignIdeasRequest) -> CampaignIdeasResponse:
        platforms_str = ", ".join(p.value for p in payload.platforms) if payload.platforms else "any"
        prompt = (
            f"Business type: {payload.business_type}\\nAudience: {payload.target_audience}\\n"
            f"Goal: {payload.goal}\\nBudget: {payload.budget or 'flexible'}\\nPlatforms: {platforms_str}\\n"
            "Generate 5 creative, actionable campaign ideas."
        )
        output, tokens = await _ai_call(_IDEAS_SYSTEM, prompt, CampaignIdeasOutput)
        return CampaignIdeasResponse(ideas=output.ideas, tokens_used=tokens)

    @staticmethod
    async def chat(system: str, messages: list) -> str:
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            msgs = [{"role": "system", "content": system}]
            msgs += [{"role": m.role, "content": m.content} for m in messages]
            response = await client.chat.completions.create(
                model="gpt-4o", messages=msgs,
                max_tokens=getattr(settings, "AI_MAX_TOKENS", 2000),
                temperature=getattr(settings, "AI_TEMPERATURE", 0.7),
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            return f"AI response unavailable: {str(e)}"

    @staticmethod
    async def generate_content_calendar(payload) -> dict:
        class CalendarOutput(BaseModel):
            weeks: list[dict]
        prompt = (
            f"Business: {payload.business_type}\\nAudience: {payload.target_audience}\\n"
            f"Platforms: {', '.join(payload.platforms)}\\nWeeks: {payload.weeks}\\nTone: {payload.tone}"
        )
        try:
            output, _ = await _ai_call(
                "Generate a content calendar as JSON with 'weeks' array. Each week has posts with content, time, hashtags.",
                prompt, CalendarOutput,
            )
            return {"weeks": output.weeks, "platforms": payload.platforms}
        except Exception as e:
            return {"weeks": [], "error": str(e)}

    @staticmethod
    async def generate_seo_content(payload) -> dict:
        class SEOOutput(BaseModel):
            primary_keywords: list[str]
            secondary_keywords: list[str]
            long_tail_keywords: list[str]
            meta_title: str
            meta_description: str
            content_outline: list[str]
        prompt = (
            f"Topic: {payload.topic}\\nIndustry: {payload.industry}\\n"
            f"Target audience: {payload.target_audience}\\nSearch intent: {payload.intent}"
        )
        try:
            output, _ = await _ai_call("You are an SEO expert. Generate keyword research and meta content.", prompt, SEOOutput)
            return output.model_dump()
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    async def generate_ab_variants(payload) -> dict:
        class ABOutput(BaseModel):
            variants: list[dict]
            recommendation: str
        prompt = (
            f"Content type: {payload.content_type}\\nOriginal: {payload.original_content}\\n"
            f"Generate {payload.variants} distinct A/B variants with content, trigger, score."
        )
        try:
            output, _ = await _ai_call("Generate A/B test variants as JSON with 'variants' array and 'recommendation'.", prompt, ABOutput)
            return {"original": payload.original_content, "variants": output.variants, "recommendation": output.recommendation}
        except Exception as e:
            return {"error": str(e)}
''').lstrip('\n')

path = os.path.join(os.path.dirname(__file__), 'app', 'services', 'ai_service.py')
with open(path, 'w', encoding='utf-8') as f:
    f.write(NEW_CONTENT)
print(f"Written {len(NEW_CONTENT)} chars to {path}")
print(f"pydantic_ai occurrences: {NEW_CONTENT.count('pydantic_ai')}")
