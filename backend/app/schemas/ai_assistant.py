"""AI Assistant Pydantic Schemas"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.social import SocialPlatform


class GeneratePostRequest(BaseModel):
    platform: SocialPlatform
    topic: str = Field(..., min_length=3, max_length=300)
    tone: str = Field("professional", examples=["professional", "casual", "funny", "inspirational"])
    include_hashtags: bool = True
    include_cta: bool = True
    max_length: Optional[int] = Field(None, ge=50, le=3000)
    brand_voice: Optional[str] = Field(None, max_length=500)


class GeneratePostResponse(BaseModel):
    content: str
    character_count: int
    suggested_platforms: list[str]
    tokens_used: int


class ClassifyLeadRequest(BaseModel):
    lead_id: Optional[str] = None
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    campaign: Optional[str] = None
    notes: Optional[str] = None
    company: Optional[str] = None


class ClassifyLeadResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    label: str  # hot | warm | cold
    reasoning: str
    recommended_action: str
    tokens_used: int


class ReplySuggestionRequest(BaseModel):
    lead_name: str
    lead_message: str
    context: Optional[str] = Field(None, max_length=500)
    tone: str = Field("professional", examples=["professional", "friendly", "urgent"])


class ReplySuggestionResponse(BaseModel):
    suggestions: list[str]
    tokens_used: int


class WriteEmailRequest(BaseModel):
    campaign_name: str
    target_audience: str
    goal: str = Field(..., examples=["book a demo", "sign up for free trial", "learn more"])
    tone: str = Field("professional", examples=["professional", "casual", "urgent"])
    include_subject: bool = True


class WriteEmailResponse(BaseModel):
    subject: str
    body_html: str
    body_text: str
    tokens_used: int


class CampaignIdeasRequest(BaseModel):
    business_type: str = Field(..., max_length=200)
    target_audience: str = Field(..., max_length=200)
    goal: str = Field(..., max_length=200)
    budget: Optional[str] = Field(None, max_length=100)
    platforms: list[SocialPlatform] = []


class CampaignIdeasResponse(BaseModel):
    ideas: list[dict]
    tokens_used: int
