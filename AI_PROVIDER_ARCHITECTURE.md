# AI Provider Architecture — SRP AI Marketing OS

**Version**: 1.0  
**Date**: 2025-01-25

---

## Overview

The SRP AI Marketing OS uses a **multi-agent architecture** where specialized AI agents handle distinct business functions. All agents are powered by OpenAI's GPT models via a centralized `get_ai_client()` factory pattern.

---

## Agent Inventory

| Agent | File | Model | Purpose |
|-------|------|-------|---------|
| Strategy Agent | `strategy_agent.py` | GPT-4o | Marketing strategy generation, business analysis |
| Content Agent | `content_agent.py` | GPT-4o-mini | Copy generation, posts, captions |
| Analytics Agent | `analytics_agent.py` | GPT-4o | Performance analysis, insights |
| Campaign Agent | `campaign_agent.py` | GPT-4o-mini | Campaign planning and launch |
| Lead Capture | `lead_capture_agent.py` | GPT-4o-mini | Lead extraction from form data |
| Lead Qualification | `lead_qualification_agent.py` | GPT-4o-mini | Lead scoring and stage assignment |
| CRM Pipeline | `crm_pipeline_agent.py` | GPT-4o-mini | Deal stage recommendations |
| Followup Agent | `followup_agent.py` | GPT-4o-mini | Follow-up message generation |
| Chatbot Agent | `chatbot_agent.py` | GPT-4o-mini | Conversational responses |
| LinkedIn Agent | `linkedin_agent.py` | GPT-4o-mini | LinkedIn content and outreach |
| Design Brief Agent | `design_brief_agent.py` | GPT-4o-mini | Creative brief generation |
| Conversation Agent | `conversation_agent.py` | GPT-4o-mini | Multi-turn conversation management |
| Orchestrator | `orchestrator.py` | GPT-4o | Multi-agent workflow coordination |

---

## Configuration

### Environment Variables

```env
OPENAI_API_KEY=sk-...              # Primary AI provider key
OPENAI_MODEL=gpt-4o                # Default high-capability model
OPENAI_MINI_MODEL=gpt-4o-mini      # Default cost-optimized model
```

### Model Selection Strategy

```
High-Stakes Tasks → GPT-4o
  - Marketing strategy generation
  - Performance analytics and insights
  - Multi-agent orchestration decisions
  - Complex reasoning tasks

Cost-Optimized Tasks → GPT-4o-mini
  - Content generation (posts, captions)
  - Lead scoring (structured output)
  - CRM stage recommendations
  - Chat responses
  - LinkedIn copy
  - Follow-up messages
```

---

## Agent Implementation Pattern

All agents follow a consistent pattern:

```python
from openai import AsyncOpenAI
from app.config import settings

async def run_agent(input_data: dict) -> dict:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    response = await client.chat.completions.create(
        model=settings.openai_model,  # or openai_mini_model
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(input_data)},
        ],
        response_format={"type": "json_object"},  # where applicable
        temperature=0.7,
    )
    
    return parse_response(response.choices[0].message.content)
```

---

## Orchestrator Pattern

The `orchestrator.py` coordinates multi-agent workflows:

```
User Request
    ↓
Orchestrator (GPT-4o) — decides which agents to call
    ├── Strategy Agent → marketing strategy
    ├── Content Agent → generated copy
    ├── Campaign Agent → campaign structure
    └── Analytics Agent → performance context
         ↓
    Aggregated Response → Frontend
```

### Key Workflows

**New Lead Workflow** (`POST /agents/new-lead-workflow`):
1. Lead Capture Agent → extract structured lead data
2. Lead Qualification Agent → score 0-100, assign stage
3. CRM Pipeline Agent → recommend initial actions
4. Followup Agent → generate first follow-up message

**Campaign Launch Workflow** (`POST /agents/campaign-launch`):
1. Strategy Agent → campaign strategy
2. Content Agent → 5-platform content (bilingual)
3. Campaign Agent → timeline and budget allocation
4. Poster Generator → visual content for all platforms

---

## Poster Generation Architecture

The poster generator uses a unique **bilingual single-pass** architecture:

```
POST /posters/generate
    ↓
PosterGeneratorService.generate_platform_variants()
    ├── Single AI call with bilingual prompt
    │   ├── English content
    │   └── Hindi/Regional content  
    ├── Build 5 platform variants from bilingual content
    │       ├── Instagram (1080×1080)
    │       ├── Facebook (1200×630)
    │       ├── WhatsApp (800×800)  
    │       ├── LinkedIn (1200×627)
    │       └── Twitter/X (1200×675)
    └── Each variant → JSON layer structure → PosterRenderer
```

### Layer Structure

```json
{
  "width": 1080,
  "height": 1080,
  "background_color": "#1a1a2e",
  "layers": [
    {
      "id": "bg",
      "type": "background",
      "bg": "linear-gradient(135deg, #1a1a2e, #16213e)",
      "w": 1080,
      "h": 1080
    },
    {
      "id": "headline",
      "type": "text",
      "content": "Your Headline Here",
      "x": 40,
      "y": 120,
      "w": 1000,
      "h": 120,
      "font_size": 64,
      "bold": true,
      "text_color": "#ffffff",
      "align": "center"
    },
    {
      "id": "footer",
      "type": "footer",
      "brand_name": "Brand Name",
      "phone": "+91-XXXXX",
      "x": 0,
      "y": 1000,
      "w": 1080,
      "h": 80
    }
  ]
}
```

### Frontend Normalization

`PosterRenderer.tsx` applies `normalizeLayer()` to bridge backend flat properties to the nested `styling` object expected by the renderer. This allows the backend to generate clean JSON without worrying about the frontend's internal structure.

---

## Extending with New AI Providers

To add a new AI provider (e.g., Anthropic Claude, Google Gemini):

1. **Add environment variable** in `backend/app/config.py`:
```python
anthropic_api_key: str = ""
preferred_provider: str = "openai"  # "openai" | "anthropic" | "gemini"
```

2. **Create provider factory** in `backend/app/services/ai_client.py`:
```python
def get_ai_client(provider: str = None):
    p = provider or settings.preferred_provider
    if p == "anthropic":
        from anthropic import AsyncAnthropic
        return AsyncAnthropic(api_key=settings.anthropic_api_key)
    # default: OpenAI
    return AsyncOpenAI(api_key=settings.openai_api_key)
```

3. **Update agents** to use factory instead of inline client instantiation

---

## Cost Optimization

| Task Type | Monthly Volume (est.) | Model | Est. Cost |
|-----------|----------------------|-------|-----------|
| Strategy generation | ~200 calls | GPT-4o | ~$8 |
| Content generation | ~2,000 calls | GPT-4o-mini | ~$4 |
| Lead scoring | ~500 calls | GPT-4o-mini | ~$1 |
| Poster generation | ~300 calls | GPT-4o-mini | ~$2 |
| Chat/Chatbot | ~5,000 calls | GPT-4o-mini | ~$5 |
| **Total estimate** | | | **~$20/month** |

---

*SRP AI Digital Marketing OS — AI Architecture Document*
