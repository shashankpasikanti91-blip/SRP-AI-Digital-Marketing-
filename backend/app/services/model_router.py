"""
Model Router — SRP Marketing OS
================================

Centralised, rule-based AI model routing.

All AI calls in the platform MUST route through this module.
No agent or service should import 'openai' or set a model string directly.

Architecture:
  - Feature buckets define which task category a request belongs to
  - Each bucket has a primary model + fallback model + cost tier
  - OpenRouter is the default provider; OpenAI direct is fallback
  - Cost per 1K tokens is tracked for billing estimation

Feature Buckets:
  text_basic          — hashtags, short captions, simple copy
  text_marketing      — ad copy, campaign copy, multi-section content
  translation         — translate text to regional/local language
  localization        — locale-aware content adaptation
  seo_keywords        — SEO keyword generation
  campaign_strategy   — full strategy, funnel planning, deep analysis
  image_prompting     — generate prompts for image creation
  image_generation    — actual AI image generation (premium / explicit only)
  lead_classification — CRM lead scoring
  email_copywriting   — email subject + body
  chatbot             — live chatbot responses

Usage:
    from app.services.model_router import ModelRouter, FeatureBucket

    router = ModelRouter()
    client, model = router.get_client_and_model(FeatureBucket.text_marketing)
    cost = router.estimate_cost(FeatureBucket.text_marketing, input_tokens=500, output_tokens=300)
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


# ── Feature Buckets ────────────────────────────────────────────────────────────

class FeatureBucket(str, Enum):
    text_basic = "text_basic"
    text_marketing = "text_marketing"
    translation = "translation"
    localization = "localization"
    seo_keywords = "seo_keywords"
    campaign_strategy = "campaign_strategy"
    image_prompting = "image_prompting"
    image_generation = "image_generation"
    lead_classification = "lead_classification"
    email_copywriting = "email_copywriting"
    chatbot = "chatbot"


# ── Model Definitions ──────────────────────────────────────────────────────────

# Provider prefixes for routing
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_OPENAI = "openai"


class ModelDef:
    """Definition of an AI model with routing metadata."""
    def __init__(
        self,
        model_id: str,
        provider: str,
        input_cost_per_1k: float,   # USD per 1K input tokens
        output_cost_per_1k: float,  # USD per 1K output tokens
        max_tokens: int = 4096,
        supports_json: bool = True,
    ):
        self.model_id = model_id
        self.provider = provider
        self.input_cost_per_1k = input_cost_per_1k
        self.output_cost_per_1k = output_cost_per_1k
        self.max_tokens = max_tokens
        self.supports_json = supports_json


# Model catalogue — costs approximate as of Q1 2026; update as needed
MODELS: dict[str, ModelDef] = {
    # ── OpenRouter via Claude/Mistral cheap models ──────────────────────
    "openrouter/mistral/mistral-7b-instruct": ModelDef(
        model_id="mistralai/mistral-7b-instruct",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.00007,
        output_cost_per_1k=0.00007,
        max_tokens=4096,
        supports_json=True,
    ),
    "openrouter/mistral/mistral-small": ModelDef(
        model_id="mistralai/mistral-small",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.001,
        output_cost_per_1k=0.003,
        max_tokens=8192,
        supports_json=True,
    ),
    "openrouter/google/gemini-flash-1.5": ModelDef(
        model_id="google/gemini-flash-1.5",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.000075,
        output_cost_per_1k=0.0003,
        max_tokens=8192,
        supports_json=True,
    ),
    "openrouter/meta-llama/llama-3.1-8b-instruct": ModelDef(
        model_id="meta-llama/llama-3.1-8b-instruct",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.0001,
        output_cost_per_1k=0.0001,
        max_tokens=8192,
        supports_json=True,
    ),
    "openrouter/openai/gpt-4o-mini": ModelDef(
        model_id="openai/gpt-4o-mini",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
        max_tokens=16384,
        supports_json=True,
    ),
    "openrouter/openai/gpt-4o": ModelDef(
        model_id="openai/gpt-4o",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.0025,
        output_cost_per_1k=0.01,
        max_tokens=16384,
        supports_json=True,
    ),
    "openrouter/anthropic/claude-3-haiku": ModelDef(
        model_id="anthropic/claude-3-haiku",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.00025,
        output_cost_per_1k=0.00125,
        max_tokens=8192,
        supports_json=True,
    ),
    "openrouter/anthropic/claude-3.5-sonnet": ModelDef(
        model_id="anthropic/claude-3.5-sonnet",
        provider=PROVIDER_OPENROUTER,
        input_cost_per_1k=0.003,
        output_cost_per_1k=0.015,
        max_tokens=8192,
        supports_json=True,
    ),
    # ── OpenAI Direct ───────────────────────────────────────────────────
    "openai/gpt-4o-mini": ModelDef(
        model_id="gpt-4o-mini",
        provider=PROVIDER_OPENAI,
        input_cost_per_1k=0.00015,
        output_cost_per_1k=0.0006,
        max_tokens=16384,
        supports_json=True,
    ),
    "openai/gpt-4o": ModelDef(
        model_id="gpt-4o",
        provider=PROVIDER_OPENAI,
        input_cost_per_1k=0.0025,
        output_cost_per_1k=0.01,
        max_tokens=16384,
        supports_json=True,
    ),
}


# ── Feature Bucket → Model Mapping ────────────────────────────────────────────

# Maps each feature bucket to (primary_model_key, fallback_model_key)
# Primary = cheapest suitable model
# Fallback = better model if primary fails
BUCKET_MODEL_MAP: dict[FeatureBucket, tuple[str, str]] = {
    # Primary = cheapest/best OpenRouter model
    # Fallback = OpenAI direct (ensures translation works even if OpenRouter key fails)
    FeatureBucket.text_basic: (
        "openrouter/google/gemini-flash-1.5",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.text_marketing: (
        "openrouter/openai/gpt-4o-mini",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.translation: (
        "openai/gpt-4o-mini",           # OpenAI direct as PRIMARY (most reliable for multilingual)
        "openrouter/google/gemini-flash-1.5",  # OpenRouter as secondary
    ),
    FeatureBucket.localization: (
        "openai/gpt-4o-mini",           # OpenAI direct as PRIMARY for locale accuracy
        "openrouter/openai/gpt-4o-mini",
    ),
    FeatureBucket.seo_keywords: (
        "openrouter/google/gemini-flash-1.5",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.campaign_strategy: (
        "openrouter/openai/gpt-4o",
        "openai/gpt-4o",                # Direct OpenAI fallback
    ),
    FeatureBucket.image_prompting: (
        "openrouter/openai/gpt-4o-mini",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.image_generation: (
        # Image generation is always premium/explicit — no cheap fallback
        "openai/gpt-4o",
        "openai/gpt-4o",
    ),
    FeatureBucket.lead_classification: (
        "openrouter/openai/gpt-4o-mini",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.email_copywriting: (
        "openrouter/openai/gpt-4o-mini",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
    FeatureBucket.chatbot: (
        "openrouter/anthropic/claude-3-haiku",
        "openai/gpt-4o-mini",           # Direct OpenAI fallback
    ),
}


# ── Model Router ───────────────────────────────────────────────────────────────

class ModelRouter:
    """
    Centralized AI model router.

    Usage:
        router = ModelRouter()
        # Get async openai-compatible client + resolved model string
        client, model_str = await router.resolve(FeatureBucket.text_marketing)
        # Or get cost estimate
        cost = router.estimate_cost(FeatureBucket.text_marketing, 500, 300)
    """

    def __init__(self):
        self._openrouter_available = bool(getattr(settings, "OPENROUTER_API_KEY", ""))
        self._openai_available = bool(getattr(settings, "OPENAI_API_KEY", ""))

    def _get_model_def(self, model_key: str) -> ModelDef:
        """Resolve model def from catalogue."""
        if model_key not in MODELS:
            # Fallback to gpt-4o-mini direct
            logger.warning(f"Model key '{model_key}' not in catalogue. Using gpt-4o-mini.")
            return MODELS["openai/gpt-4o-mini"]
        return MODELS[model_key]

    def _pick_model_key(self, bucket: FeatureBucket, use_fallback: bool = False) -> str:
        """Pick the right model key for a feature bucket."""
        primary_key, fallback_key = BUCKET_MODEL_MAP.get(
            bucket,
            ("openrouter/openai/gpt-4o-mini", "openai/gpt-4o-mini"),
        )
        if use_fallback:
            return fallback_key

        model_def = self._get_model_def(primary_key)
        # If primary model is openrouter and API key not set, use fallback
        if model_def.provider == PROVIDER_OPENROUTER and not self._openrouter_available:
            return fallback_key
        return primary_key

    def get_model_id_and_provider(
        self,
        bucket: FeatureBucket,
        use_fallback: bool = False,
    ) -> tuple[str, str]:
        """
        Returns (model_id, provider) for the given feature bucket.

        model_id: the raw model ID string for the API call
        provider: 'openrouter' or 'openai'
        """
        model_key = self._pick_model_key(bucket, use_fallback=use_fallback)
        model_def = self._get_model_def(model_key)
        return model_def.model_id, model_def.provider

    def get_async_client(self, provider: str):
        """
        Return an async OpenAI-compatible client for the given provider.

        Both OpenAI and OpenRouter use the same openai-compatible API.
        """
        import openai
        if provider == PROVIDER_OPENROUTER:
            if not self._openrouter_available:
                raise RuntimeError(
                    "OPENROUTER_API_KEY is not configured. "
                    "Set it in .env to use OpenRouter models."
                )
            return openai.AsyncOpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": getattr(settings, "APP_URL", "https://app.srpailabs.com"),
                    "X-Title": getattr(settings, "APP_NAME", "SRP Marketing OS"),
                },
            )
        else:
            # OpenAI direct
            if not self._openai_available:
                raise RuntimeError(
                    "OPENAI_API_KEY is not configured. "
                    "Set it in .env to use OpenAI models."
                )
            return openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def resolve(
        self,
        bucket: FeatureBucket,
        use_fallback: bool = False,
    ) -> tuple[object, str]:
        """
        Returns (async_client, model_id) ready for direct use in an API call.

        Example:
            client, model = router.resolve(FeatureBucket.text_marketing)
            response = await client.chat.completions.create(model=model, ...)
        """
        model_id, provider = self.get_model_id_and_provider(bucket, use_fallback=use_fallback)
        client = self.get_async_client(provider)
        return client, model_id

    def estimate_cost(
        self,
        bucket: FeatureBucket,
        input_tokens: int,
        output_tokens: int,
        use_fallback: bool = False,
    ) -> float:
        """
        Estimate the USD cost for a request.

        Returns float: estimated cost in USD.
        """
        model_key = self._pick_model_key(bucket, use_fallback=use_fallback)
        model_def = self._get_model_def(model_key)
        cost = (
            (input_tokens / 1000) * model_def.input_cost_per_1k
            + (output_tokens / 1000) * model_def.output_cost_per_1k
        )
        return round(cost, 8)

    def get_model_info(self, bucket: FeatureBucket) -> dict:
        """Return model metadata for a feature bucket (useful for admin/logging)."""
        model_key = self._pick_model_key(bucket)
        model_def = self._get_model_def(model_key)
        return {
            "bucket": bucket.value,
            "model_key": model_key,
            "model_id": model_def.model_id,
            "provider": model_def.provider,
            "input_cost_per_1k_usd": model_def.input_cost_per_1k,
            "output_cost_per_1k_usd": model_def.output_cost_per_1k,
            "max_tokens": model_def.max_tokens,
        }

    def list_buckets(self) -> list[dict]:
        """List all feature buckets with their assigned models."""
        return [self.get_model_info(bucket) for bucket in FeatureBucket]


# Singleton accessor
_router_instance: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get singleton ModelRouter instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
