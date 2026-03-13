"""AI Assistant Router — powered by Pydantic AI"""

import json
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.core.dependencies import CurrentTenant
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
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


# ── Chat Schemas ────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = True
    context: Optional[str] = Field(
        None,
        description="Extra context: 'marketing', 'leads', 'crm', 'social', 'email'",
    )


class ContentCalendarRequest(BaseModel):
    business_type: str
    target_audience: str
    platforms: List[str] = ["instagram", "linkedin", "facebook"]
    weeks: int = Field(2, ge=1, le=4)
    tone: str = "professional"


class SEORequest(BaseModel):
    topic: str
    industry: str
    target_audience: str
    intent: str = "informational"  # informational | transactional | navigational


class ABTestRequest(BaseModel):
    original_content: str
    content_type: str = "email_subject"  # email_subject | ad_copy | cta | headline
    variants: int = Field(3, ge=2, le=5)


# ── Core AI Endpoints ───────────────────────────────────────────────────────

@router.post("/generate-post", response_model=GeneratePostResponse)
async def generate_post(payload: GeneratePostRequest, tenant: CurrentTenant):
    """Generate a social media post using AI."""
    return await AIService.generate_social_post(payload)


@router.post("/classify-lead", response_model=ClassifyLeadResponse)
async def classify_lead(payload: ClassifyLeadRequest, tenant: CurrentTenant):
    """Score and classify a lead using AI (0-100 score + hot/warm/cold label)."""
    return await AIService.classify_lead_raw(payload)


@router.post("/reply-suggestion", response_model=ReplySuggestionResponse)
async def reply_suggestion(payload: ReplySuggestionRequest, tenant: CurrentTenant):
    """Suggest smart replies for a lead message."""
    return await AIService.suggest_reply(payload)


@router.post("/write-email", response_model=WriteEmailResponse)
async def write_email(payload: WriteEmailRequest, tenant: CurrentTenant):
    """Generate email campaign content with subject and body."""
    return await AIService.write_email(payload)


@router.post("/campaign-ideas", response_model=CampaignIdeasResponse)
async def campaign_ideas(payload: CampaignIdeasRequest, tenant: CurrentTenant):
    """Brainstorm marketing campaign ideas for a business."""
    return await AIService.generate_campaign_ideas(payload)


# ── Advanced AI Endpoints ───────────────────────────────────────────────────

@router.post("/chat")
async def ai_chat(payload: ChatRequest, tenant: CurrentTenant):
    """
    Conversational AI chat with streaming support.
    Returns a streamed text/event-stream when stream=True, or JSON otherwise.
    """
    system_instructions = (
        "You are an expert AI marketing assistant for SRP AI Digital Marketing. "
        "You help with leads, CRM, social media, email campaigns, analytics, and marketing strategy. "
        "Be concise, actionable, and data-driven. Format with markdown when helpful."
    )
    if payload.context:
        ctx_map = {
            "leads": "Focus on lead capture, qualification, and nurturing strategies.",
            "crm": "Focus on CRM pipeline management, deal progression, and sales tactics.",
            "social": "Focus on social media content, scheduling, and platform best practices.",
            "email": "Focus on email marketing, deliverability, open rates, and conversion.",
            "marketing": "Focus on overall digital marketing strategy, ROI, and growth tactics.",
        }
        system_instructions += f"\n{ctx_map.get(payload.context, '')}"

    if payload.stream:
        return StreamingResponse(
            _stream_chat(system_instructions, payload.messages),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        # Non-streaming fallback
        result = await AIService.chat(system_instructions, payload.messages)
        return {"content": result}


async def _stream_chat(system: str, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
    """Yield SSE chunks from OpenAI streaming."""
    try:
        import openai
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        msgs = [{"role": "system", "content": system}]
        msgs += [{"role": m.role, "content": m.content} for m in messages]

        stream = await client.chat.completions.create(
            model="gpt-4o",
            messages=msgs,
            stream=True,
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                yield f"data: {json.dumps({'content': delta})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/content-calendar")
async def generate_content_calendar(payload: ContentCalendarRequest, tenant: CurrentTenant):
    """Generate a social media content calendar for multiple weeks."""
    return await AIService.generate_content_calendar(payload)


@router.post("/seo-keywords")
async def seo_keywords(payload: SEORequest, tenant: CurrentTenant):
    """Generate SEO keywords & meta content for a topic."""
    return await AIService.generate_seo_content(payload)


@router.post("/ab-test")
async def ab_test_variants(payload: ABTestRequest, tenant: CurrentTenant):
    """Generate A/B test variants for email subjects, headlines, CTAs, or ad copy."""
    return await AIService.generate_ab_variants(payload)


@router.get("/usage")
async def ai_usage_stats(tenant: CurrentTenant):
    """Return AI usage statistics for the tenant (placeholder — implement with token tracking)."""
    return {
        "model": settings.AI_MODEL,
        "status": "active" if settings.OPENAI_API_KEY else "no_api_key",
        "features": [
            "social_post_generation",
            "lead_scoring",
            "reply_suggestions",
            "email_writing",
            "campaign_ideas",
            "conversational_chat",
            "content_calendar",
            "seo_keywords",
            "ab_testing",
        ],
    }
