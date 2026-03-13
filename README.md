<div align="center">

# SRP Marketing OS

### by **SRP AI Digital Marketing**

> **The all-in-one AI-powered Marketing SaaS platform** — capture leads, manage your CRM pipeline, schedule social posts, automate email sequences, and generate multilingual creative content at scale.

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

**Live Production:** [app.srpailabs.com](https://app.srpailabs.com)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Core Product Positioning](#core-product-positioning)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [AI Routing Architecture](#ai-routing-architecture)
- [Creative Generation System](#creative-generation-system)
- [Multi-Country & Localization](#multi-country--localization-support)
- [Visual Creative System](#visual-creative-system)
- [Demo Accounts](#demo-accounts)
- [Pricing Plans](#pricing-plans)
- [Local Development Setup](#local-development-setup)
- [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [API Reference](#api-reference)
- [Production Deployment — Hetzner](#production-deployment--hetzner)
- [SSL & HTTPS](#ssl--https)
- [Project Structure](#project-structure)
- [Release Notes](#release-notes)
- [Future Improvements](#future-improvements)

---

## Overview

**SRP Marketing OS** is a production-ready, multi-tenant AI marketing automation platform built for agencies, hospitals, local businesses, and multi-industry clients across 7 countries.

It combines CRM, lead capture, social media scheduling, email automation, AI creative generation, and analytics into a single cost-controlled SaaS platform with full multi-tenancy and plan-based access control.

**What makes it different:**

- **AI cost control** — all AI calls route through a centralized `ModelRouter` that selects the cheapest suitable model per task (OpenRouter for content, OpenAI direct for translation)
- **Multilingual creative generation** — generates bilingual/trilingual marketing creatives in 14 languages including Indian scripts (Telugu, Hindi, Tamil) and SE Asian languages
- **Template-based visual output** — not just plain text — structured creative JSON drives a Canva-like poster renderer on the frontend
- **Plan-gated AI features** — every AI call is checked against tenant plan limits before execution (starter / pro / agency / enterprise)
- **Industry-aware content** — content adapts tone, vocabulary, and visual style based on industry (healthcare, education, real estate, restaurant, etc.)

---

## Core Product Positioning

| Dimension | Detail |
|-----------|--------|
| **Who it is for** | Digital agencies, hospitals, schools, restaurants, real estate — any business needing AI marketing |
| **Primary markets** | India, Australia, New Zealand, Malaysia, Singapore, Indonesia, Thailand |
| **Key value** | AI-first, cost-controlled, multilingual, template-driven creative output |
| **Deployment** | Self-hosted (Docker) or managed cloud |
| **Architecture** | Multi-tenant SaaS — one instance, many tenants, isolated workspaces |

---

## Key Features

| Module | Capabilities |
|--------|-------------|
| **Lead Capture** | REST API ingestion, UTM tracking, AI lead scoring (0-100), source attribution |
| **CRM Pipeline** | 6-stage Kanban (New to Won/Lost), bulk operations, notes, deal history |
| **Social Scheduler** | Multi-platform posting (Facebook, Instagram, LinkedIn), Celery workers, retry logic |
| **Email Automation** | Campaign builder, drip sequences, SMTP/TLS, open & click tracking |
| **AI Creative Generation** | Multilingual poster/social creatives with industry-aware templates |
| **AI Assistant** | GPT-4o / Claude-powered post generation, lead classification, reply suggestions |
| **Campaign Builder** | Full campaign strategy, funnel planning, bilingual creative output |
| **Analytics Dashboard** | Leads per campaign, conversion rates, platform performance, funnel metrics |
| **Multi-Tenancy** | Isolated tenant workspaces, JWT auth, per-plan feature gates |
| **Plan Limit Enforcement** | Monthly AI credit tracking, 402 upgrade prompts, usage dashboard |
| **AI Usage Tracking** | Per-tenant token usage, estimated cost in USD, billing category breakdown |
| **WhatsApp Export** | Export social creatives optimized for WhatsApp status |
| **LinkedIn AI** | LinkedIn-specific content with professional tone adaptation |
| **SEO Tools** | Keyword generation and SEO-optimized content per campaign |
| **Localization Engine** | Country + language aware content and template adaptation |
| **Security** | JWT auth, rate limiting, CORS, bcrypt passwords, Pydantic input validation |

---

## Architecture Overview

```
+--------------------------------------------------------------+
|                     SRP Marketing OS                         |
+--------------------------------------------------------------+
|                                                              |
|  [React SPA]   <-- HTTPS -->   [FastAPI /api/v1/*]           |
|  Vite + TypeScript              Async multi-tenant API       |
|  app.srpailabs.com              Nginx reverse proxy          |
|                                                              |
|  Service Layer:                                              |
|   LeadService  CRMService  SocialService  EmailService       |
|   CreativeService  ModelRouter  PlanLimitService             |
|   UsageTracker  LocalizationEngine  IndustryConfig           |
|                                                              |
|  [PostgreSQL 16]  [Redis 7]   [Celery Workers]               |
|  Async SQLAlchemy Queue/Cache  Social / Email / AI jobs      |
|                                                              |
|  [AI Providers]                                              |
|   OpenRouter (primary — content, campaigns, copywriting)     |
|   OpenAI direct (primary — translation, localization)        |
|                                                              |
+--------------------------------------------------------------+
```

**Design Principles:**

- **Async-first** — All I/O uses Python asyncio + SQLAlchemy async engine
- **Modular services** — Each domain is a self-contained service module
- **Multi-tenant isolation** — Every DB record is scoped by tenant_id; no cross-tenant leakage
- **Queue-backed workers** — Celery + Redis for publishing, email, and async AI jobs
- **Centralized AI routing** — ModelRouter governs all AI calls; no scattered provider imports

---

## AI Routing Architecture

All AI calls pass through the centralized `ModelRouter`. No service or agent imports `openai` directly.

### FeatureBucket System

Each task is classified into a `FeatureBucket` which determines model routing:

| Feature Bucket | Primary Model | Fallback | Rationale |
|---------------|---------------|----------|-----------|
| `text_basic` | Gemini Flash 1.5 (OpenRouter) | GPT-4o-mini (OpenAI) | Cheapest for short copy |
| `text_marketing` | GPT-4o-mini (OpenRouter) | GPT-4o-mini (OpenAI) | Reliable marketing copy |
| `translation` | GPT-4o-mini (OpenAI direct) | Gemini Flash (OpenRouter) | Best for Indian scripts |
| `localization` | GPT-4o-mini (OpenAI direct) | GPT-4o-mini (OpenRouter) | Locale accuracy |
| `seo_keywords` | Gemini Flash 1.5 (OpenRouter) | GPT-4o-mini (OpenAI) | Cost-efficient |
| `campaign_strategy` | GPT-4o (OpenRouter) | GPT-4o (OpenAI) | Deep reasoning |
| `email_copywriting` | GPT-4o-mini (OpenRouter) | GPT-4o-mini (OpenAI) | Reliable email copy |
| `chatbot` | Claude 3 Haiku (OpenRouter) | GPT-4o-mini (OpenAI) | Fast conversational |
| `image_generation` | GPT-4o (OpenAI) | GPT-4o (OpenAI) | Premium only, plan-gated |

### Cost Control

- **OpenRouter** — primary for most content tasks (significantly cheaper than OpenAI direct)
- **OpenAI direct** — primary for translation/localization (most reliable for non-Latin character sets)
- **Automatic fallback** — if primary provider key is missing or errors, router falls back seamlessly
- **Usage tracking** — every AI call logged with token counts and estimated USD cost per tenant
- **Plan limits** — `PlanLimitService` checks monthly limits before every call; HTTP 402 if exceeded

```python
# Standard usage pattern across all services
from app.services.model_router import ModelRouter, FeatureBucket

router = ModelRouter()
client, model = router.resolve(FeatureBucket.text_marketing)
cost = router.estimate_cost(FeatureBucket.text_marketing, input_tokens=500, output_tokens=300)
```

---

## Creative Generation System

The creative pipeline converts a business brief into structured, export-ready marketing output.

### Pipeline Steps

```
CreativeRequest (business_name, industry, country_code, language_mode, platform, ...)
      |
      v
[1] Locale Profile Resolution    (country -> language defaults, cultural context)
[2] Industry Config Resolution   (healthcare / restaurant / real estate / etc.)
[3] Cultural Style Selection     (formal / modern / community_trust / festive)
[4] AI Text Generation           (via ModelRouter: headline, CTA, caption, hashtags)
[5] Bilingual Translation        (secondary/tertiary language via localization bucket)
[6] Template Selection           (locale + industry + platform + output_type aware)
[7] Poster JSON Construction     (layers: background, text blocks, CTA, footer)
      |
      v
CreativeOutput
  - headline (primary + secondary language)
  - subheadline (localized)
  - cta (localized)
  - caption, hashtags
  - poster_json (template layer data for PosterRenderer)
  - ai_image_url (optional — premium plans only when IMAGE_GENERATION_ENABLED=true)
```

### Key Principles

- **AI generates TEXT only** — the template system handles all visual layout
- **AI image generation is OFF by default** — controlled by `IMAGE_GENERATION_ENABLED` flag + plan tier
- **Deterministic rendering** — same creative input always produces consistent visual output
- **Bilingual in one poster** — primary + translated secondary language in balanced visual hierarchy

---

## Multi-Country & Localization Support

| Country | Code | Default Languages | Key Industries |
|---------|------|------------------|----------------|
| India | `IN` | English + regional script | Healthcare, Education, Retail, Restaurant, Real Estate |
| Australia | `AU` | English | Healthcare, Real Estate, Education, Services |
| New Zealand | `NZ` | English | Healthcare, Real Estate, Tourism, Services |
| Malaysia | `MY` | English + Malay | Retail, Food & Beverage, Services |
| Singapore | `SG` | English + Chinese Simplified | Finance, Services, Retail |
| Indonesia | `ID` | Indonesian | Retail, Education, Services |
| Thailand | `TH` | Thai | Tourism, Retail, Healthcare |

### Supported Languages (14 total)

**Indian scripts:** Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, Odia

**SE Asian:** Malay, Indonesian, Thai, Chinese Simplified

Translation uses GPT-4o-mini direct (most reliable for Indian scripts and non-Latin character sets), with OpenRouter Gemini Flash as fallback.

---

## Visual Creative System

The platform generates **template-based structured creative output** — not raw text — designed for direct social media publishing.

### Template Industries

| Industry | Visual Style | Layout Features |
|----------|-------------|-----------------|
| Hospital / Clinic | Clean blue/white, formal | Doctor credentials, service list, consultation CTA |
| School / Education | Bright, trust-inspiring | Admission dates, course info, phone/address |
| Restaurant / Catering | Warm, food-first | Dish highlights, offers, festive specials |
| Digital Agency | Modern dark/gradient | Service list, results/stats, contact |
| Retail / Business | Bold offer-focused | Discount %, limited time, clear price |
| Real Estate | Premium, aspirational | Property details, location, agent contact |
| Salon / Beauty | Elegant, refined | Services, pricing, booking CTA |
| Gym / Fitness | Energetic, bold | Membership offer, class schedule |

### Output Platforms

- `instagram_square` — 1:1 ratio for Instagram feed
- `instagram_story` — 9:16 vertical for Stories
- `facebook_post` — 1.91:1 landscape
- `whatsapp_share` — optimized for WhatsApp status
- `linkedin_banner` — professional wide format

### PosterRenderer

`PosterRenderer.tsx` converts structured poster JSON (layers: background, text, badge, CTA, footer, checklist, divider) into a rendered visual HTML/CSS preview. The same JSON drives both in-app preview and exported download output — ensuring preview matches export.

---

## Demo Accounts

Five pre-seeded demo accounts across different industries. No setup required beyond running seed scripts.

| Industry | Email | Password | Business Name |
|----------|-------|----------|---------------|
| Digital Agency | `demo@srp.ai` | `Demo@12345` | SRP Digital Marketing Agency |
| Healthcare Marketing | `bunty@srp.ai` | `Bunty@12345` | Bunty Healthcare Marketing |
| Hospital | `bunty@hospital.demo` | `Bunty@2026` | Kothagudem General Hospital |
| Recruitment Agency | `bunty@recruitment.demo` | `Bunty@2026` | BuntyHire Pan India Staffing |
| Restaurant / Catering | `bunty@restaurant.demo` | `Bunty@2026` | Bunty Kitchen |

Each account includes 8-12 pre-seeded leads, 5 campaigns, brand profile, conversations, and follow-up sequences.

```bash
# Seed all demo accounts (run after alembic migrations)
docker compose exec backend python seed_demo.py
docker compose exec backend python seed_bunty.py
```

---

## Pricing Plans

| Plan | Price (INR/month) | Leads/mo | AI Credits | Social Accounts | Users |
|------|--------------------|----------|------------|-----------------|-------|
| **Starter** | Free | 100 | 50 | 1 | 1 |
| **Growth** | Rs 1,499 | 2,500 | 300 | 3 | 3 |
| **Professional** | Rs 3,999 | 10,000 | 1,000 | 10 | 10 |
| **Enterprise** | Rs 9,999 | Unlimited | Unlimited | Unlimited | Unlimited |

All prices exclude 18% GST. Annual billing saves 20%.

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (for Postgres + Redis)

### Backend

```bash
cd ai-marketing-os/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env: set DATABASE_URL, REDIS_URL, OPENAI_API_KEY, OPENROUTER_API_KEY

# Start Postgres + Redis
docker compose -f ../docker-compose.dev.yml up -d db redis

# Run migrations
cd ..
alembic -c backend/alembic.ini upgrade head

# Seed demo data
python backend/seed_demo.py

# Start API with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### Frontend

```bash
cd ai-marketing-os/frontend

npm install
echo "VITE_API_URL=http://localhost:8000" > .env.local
npm run dev
# Frontend: http://localhost:5173
```

---

## Docker Setup

```bash
cd ai-marketing-os

# Copy and configure environment
cp .env.example .env
# Edit .env with your values (SECRET_KEY, API keys, passwords)

# Build and start full stack
docker compose up --build -d

# Run migrations
docker compose exec backend alembic upgrade head

# Optional: seed demo accounts
docker compose exec backend python seed_demo.py

# View logs
docker compose logs -f backend
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `nginx` | 80, 443 | Reverse proxy + SSL termination |
| `frontend` | 80 (internal) | React SPA (Nginx-served static) |
| `backend` | 8000 (internal) | FastAPI application |
| `db` | 5432 | PostgreSQL 16 |
| `redis` | 6379 | Redis 7 |
| `celery-worker` | — | Background task worker (4 queues) |
| `celery-beat` | — | Scheduled task runner |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in values. All variables listed below.

### Required

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret — generate with `openssl rand -hex 32` |
| `DATABASE_URL` | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis URL (`redis://:password@host:6379/0`) |
| `OPENAI_API_KEY` | OpenAI API key — required for translation and localization |
| `OPENROUTER_API_KEY` | OpenRouter API key — required for content and campaigns |

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_ENV` | `development` | `development` / `production` / `testing` |
| `APP_NAME` | `AI Marketing OS` | Application display name |
| `APP_VERSION` | `1.0.0` | Version string |
| `DEBUG` | `true` | Set `false` in production |
| `ALLOWED_ORIGINS` | `http://localhost:5173,...` | CORS origins, comma-separated |
| `APP_URL` | `https://app.srpailabs.com` | Public URL (sent to OpenRouter as Referer) |

### AI Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PREFERRED_PROVIDER` | `openrouter` | `openrouter` or `openai` |
| `AI_MAX_TOKENS` | `2500` | Max tokens per AI call |
| `AI_TEMPERATURE` | `0.75` | Generation temperature (0.0-1.0) |
| `IMAGE_GENERATION_ENABLED` | `false` | Enable AI image generation (extra cost) |
| `IMAGE_GENERATION_PREMIUM_ONLY` | `true` | Restrict image gen to Pro/Agency/Enterprise |
| `USAGE_TRACKING_ENABLED` | `true` | Track per-tenant AI usage and costs |
| `USAGE_TRACKING_LOG_LEVEL` | `all` | `all` / `errors_only` / `none` |

### Docker / Production

| Variable | Description |
|----------|-------------|
| `POSTGRES_USER` | DB username (default: `srp`) |
| `POSTGRES_PASSWORD` | DB password — must be strong in production |
| `POSTGRES_DB` | DB name (default: `srp_marketing`) |
| `REDIS_PASSWORD` | Redis auth password |

### Email / SMTP

| Variable | Description |
|----------|-------------|
| `SMTP_HOST` | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (usually `587` for TLS) |
| `SMTP_USER` | SMTP login username |
| `SMTP_PASSWORD` | SMTP password or app password |
| `SMTP_FROM_EMAIL` | Sender address |

---

## Database Migrations

```bash
# Apply all pending migrations
docker compose exec backend alembic upgrade head

# Check current revision
docker compose exec backend alembic current

# View migration history
docker compose exec backend alembic history

# Create new migration (development)
docker compose exec backend alembic revision --autogenerate -m "your_description"

# Roll back one step
docker compose exec backend alembic downgrade -1
```

### Migration History

| Version | Description |
|---------|-------------|
| `001` | Initial schema — tenants, leads, CRM, social, email, analytics |
| `002` | Tenant profile columns — logo, brand, social handles |
| `003` | Missing tables — conversations, follow-ups, notifications |
| `004` | Support tables — webhooks, API keys |
| `005` | Missing columns — lead scoring, campaign metrics |
| `006` | Convert enums to varchar — flexible status values |
| `007` | Regional marketing tables — brands, campaign presets |
| `008` | Global localization — country/language config, locale profiles |
| `009` | AI usage tracking — per-tenant token/cost logging |

---

## API Reference

Base URL: `/api/v1` | Swagger UI: `/docs` | ReDoc: `/redoc`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new tenant account |
| `POST` | `/auth/login` | Login, returns JWT access token |
| `GET` | `/auth/me` | Get current authenticated tenant |

### Leads & CRM

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/leads/` | Create lead (form / webhook / API) |
| `GET` | `/leads/` | List leads with filter and pagination |
| `PATCH` | `/leads/{id}` | Update lead data |
| `GET` | `/crm/pipeline` | Full Kanban pipeline view |
| `PATCH` | `/crm/deals/{id}/stage` | Move deal to new pipeline stage |
| `POST` | `/crm/deals/{id}/notes` | Add note to deal |

### AI Creative Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/creatives/generate` | Generate multilingual creative + poster JSON |
| `GET` | `/creatives/usage` | Tenant AI usage stats and plan status |
| `GET` | `/creatives/templates` | List available templates |
| `POST` | `/posters/generate` | Generate bilingual poster JSON by industry |
| `GET` | `/posters/templates` | List poster templates by industry/platform |

### Social & Email

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/social/posts/` | Schedule social post |
| `GET` | `/social/posts/` | List scheduled and published posts |
| `POST` | `/social/posts/{id}/publish` | Publish immediately |
| `POST` | `/email-campaigns/` | Create email campaign |
| `POST` | `/email-campaigns/{id}/send` | Send campaign |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/overview` | Dashboard KPI stats |
| `GET` | `/analytics/leads/trend` | Lead count trend (last 30 days) |
| `GET` | `/analytics/campaigns` | Per-campaign performance metrics |

### Localization

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/localization/countries` | List supported countries |
| `GET` | `/localization/languages` | List supported languages |
| `GET` | `/localization/profile/{country_code}` | Get locale profile |

---

## Production Deployment — Hetzner

**Server IP:** `5.223.67.236` | **Domain:** `app.srpailabs.com`

### 1. SSH into server

```bash
ssh root@5.223.67.236
```

### 2. Install Docker (first time server setup)

```bash
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker
apt-get install -y docker-compose-plugin git certbot curl
```

### 3. Clone repository

```bash
cd /opt
git clone https://github.com/srp-ai-digital/srp-marketing-os.git
cd srp-marketing-os/ai-marketing-os
```

### 4. Configure environment

```bash
cp .env.example .env
nano .env
```

Minimum required for production:

```dotenv
APP_ENV=production
DEBUG=false
SECRET_KEY=<run: openssl rand -hex 32>
POSTGRES_PASSWORD=<strong-random-password>
REDIS_PASSWORD=<strong-random-password>
DATABASE_URL=postgresql+asyncpg://srp:<POSTGRES_PASSWORD>@db:5432/srp_marketing
REDIS_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
CELERY_BROKER_URL=redis://:<REDIS_PASSWORD>@redis:6379/0
CELERY_RESULT_BACKEND=redis://:<REDIS_PASSWORD>@redis:6379/1
ALLOWED_ORIGINS=https://app.srpailabs.com
APP_URL=https://app.srpailabs.com
OPENAI_API_KEY=sk-proj-...
OPENROUTER_API_KEY=sk-or-v1-...
```

### 5. Get SSL certificate

```bash
# Verify DNS A record: app.srpailabs.com -> 5.223.67.236
certbot certonly --standalone -d app.srpailabs.com \
  --non-interactive --agree-tos --email admin@srpailabs.com

mkdir -p nginx/ssl
cp /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/app.srpailabs.com/privkey.pem nginx/ssl/
chmod 600 nginx/ssl/privkey.pem
```

### 6. Build and start all services

```bash
docker compose up --build -d

# Verify all services are healthy
docker compose ps
```

### 7. Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### 8. Seed demo data (optional)

```bash
docker compose exec backend python seed_demo.py
docker compose exec backend python seed_bunty.py
```

### 9. Verify deployment

```bash
# Backend health check
curl https://app.srpailabs.com/health
# Expected: {"status":"ok","app":"AI Marketing OS","version":"1.0.0","env":"production"}

# Frontend check
curl -sI https://app.srpailabs.com | head -5
```

### 10. Verify creative generation

1. Open `https://app.srpailabs.com` in browser
2. Log in with demo account: `demo@srp.ai` / `Demo@12345`
3. Navigate to Campaign Builder
4. Generate a bilingual creative (e.g. English + Telugu, India, Healthcare)
5. Confirm poster preview renders with correct visual layers
6. Test export / download

### 11. Configure SSL auto-renewal

```bash
echo "0 3 * * * certbot renew --quiet && docker compose -f /opt/srp-marketing-os/ai-marketing-os/docker-compose.yml exec nginx nginx -s reload" | crontab -
```

### Updating production

```bash
cd /opt/srp-marketing-os/ai-marketing-os
git pull origin master
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

---

## SSL & HTTPS

`nginx/nginx.conf` is pre-configured for:

- HTTP to HTTPS redirect (301)
- Let's Encrypt / Certbot SSL certificates
- TLS 1.2 + 1.3 with strong cipher suites (ECDHE-RSA-AES256-GCM)
- HSTS (`max-age=31536000; includeSubDomains`)
- Security headers (X-Frame-Options DENY, X-Content-Type-Options, XSS protection)
- Rate limiting: 30 req/s for API, 5 req/min for auth endpoints
- Client max body size: 50MB

SSL certificates must be mounted at:
- `/etc/nginx/ssl/fullchain.pem`
- `/etc/nginx/ssl/privkey.pem`

These map from `./nginx/ssl/` on the host (see docker-compose.yml volumes section).

---

## Project Structure

```
ai-marketing-os/
|
+-- backend/
|   +-- app/
|   |   +-- main.py                     App factory, middleware, router registration
|   |   +-- config.py                   Pydantic-settings (all env vars with defaults)
|   |   +-- database.py                 Async SQLAlchemy engine + session factory
|   |   +-- models/                     SQLAlchemy ORM models
|   |   +-- schemas/                    Pydantic request/response schemas
|   |   +-- routers/                    FastAPI route handlers (22 router modules)
|   |   +-- services/
|   |   |   +-- model_router.py         Centralized AI routing -- ALL AI calls here
|   |   |   +-- creative_service.py     Full creative generation pipeline
|   |   |   +-- plan_limit_service.py   Plan-based AI credit enforcement
|   |   |   +-- usage_tracking_service.py  Per-tenant token/cost logging
|   |   |   +-- localization_engine.py  Locale + language content adaptation
|   |   |   +-- industry_config.py      20+ industry tone/template presets
|   |   |   +-- poster_generator.py     Structured poster JSON construction
|   |   |   +-- ai_service.py           AI assistant + lead classification
|   |   |   +-- crm_service.py          CRM pipeline business logic
|   |   |   +-- lead_service.py         Lead capture, scoring, attribution
|   |   |   +-- social_service.py       Social post scheduling + publishing
|   |   |   +-- social_variant_service.py  Multi-variant social content generation
|   |   |   +-- email_service.py        Email sending + campaign management
|   |   |   +-- analytics_service.py    Analytics aggregation queries
|   |   |   +-- language_service.py     Language detection + mapping
|   |   +-- workers/                    Celery async workers
|   |   +-- agents/                     AI agent modules (12 agents)
|   |   +-- core/                       Security, dependencies, exceptions, middleware
|   +-- alembic/                        9 migration versions
|   +-- seed_demo.py                    Demo account seed script
|   +-- seed_bunty.py                   Bunty demo accounts seed
|   +-- requirements.txt
|   +-- Dockerfile
|
+-- frontend/
|   +-- src/
|   |   +-- pages/                      24 route-level page components
|   |   +-- components/
|   |   |   +-- layout/                 Sidebar.tsx + Layout.tsx
|   |   |   +-- poster/                 PosterRenderer.tsx, VariantPreview.tsx, LanguageToggle.tsx
|   |   +-- services/                   Axios API client
|   |   +-- store/                      Zustand auth + global state
|   |   +-- types/                      TypeScript interfaces
|   |   +-- lib/                        Utilities (cn, formatCurrency, etc.)
|   +-- package.json
|   +-- vite.config.ts
|   +-- tailwind.config.js
|   +-- Dockerfile
|
+-- nginx/
|   +-- nginx.conf                      Production reverse proxy + SSL config
|   +-- ssl/                            SSL certs (not committed -- mount at deploy time)
|
+-- docker-compose.yml                  Production stack (7 services)
+-- docker-compose.dev.yml              Development override (hot-reload volumes)
+-- .env.example                        Complete environment variable template
+-- Makefile                            Development shortcuts (make dev, make migrate, etc.)
+-- README.md
```

---

## Release Notes

### v1.2.0 — 14 March 2026

**Bug Fixes**

- **Poster: translation error text no longer shown** — `[Translation failed: Error code: 401 ...]` messages that were stored in old poster JSON are now silently filtered in `PosterRenderer`. Posters fall back to English text instead of showing raw API errors.
- **Poster Gallery: delete now works from grid cards** — hover over any poster thumbnail to see a 🗑 quick-delete button without needing to open the detail view.
- **Poster Gallery: bulk delete added** — new "✅ Select" mode toggles checkboxes on all cards. Select individual posters or "Select all N", then "Delete Selected" with confirmation dialog.
- **Leads: bulk delete added** — header checkbox selects all filtered leads; row checkboxes allow individual selection; "Delete N" button in top toolbar with confirmation.
- **Model router: FLUX model IDs corrected** — previously used `black-forest-labs/FLUX.1-schnell` (capital letters, wrong format); fixed to `black-forest-labs/flux-1-schnell` which matches the OpenRouter API exactly.
- **Model router: GPT-4.1-mini added** — all text buckets updated from `gpt-4o-mini` to `gpt-4.1-mini` (better quality, 32K context, $0.40/1M input).
- **Model router: image_generation fixed** — was incorrectly mapped to `gpt-4o` (a text model); now correctly uses FLUX.1-schnell ($0.003/img) with FLUX.1.1-pro ($0.04/img) as quality fallback.
- **Google Fonts fixed** — `index.html` now preloads Inter + Noto Sans family (Telugu, Devanagari, Tamil, Kannada, Malayalam, Arabic); regional script poster text no longer renders as boxes.
- **CTA button rendering fixed** — `PosterRenderer` now respects `w`, `h`, and `border_radius` from poster JSON; CTA is full-width with coloured glow shadow.
- **celery-beat scheduler fixed** — was crashing with `django_celery_beat.schedulers:DatabaseScheduler` (package not installed); changed to `celery.beat.PersistentScheduler`.
- **HTTP-Referer header fixed** — model router was sending `app.srpmarketingos.com`; updated to `app.srpailabs.com`.

**New Templates**

- **🇲🇾 Malaysia category** added to Campaign Builder with 4 featured templates:
  - `malaysia_hospital_premium` — premium hospital health camp (BM/EN bilingual)
  - `malaysia_job_opening` — job vacancy poster (Jawatan Kosong, BM/EN)
  - `malaysia_walkin_drive` — walk-in interview (Temuduga Terbuka, BM/EN)
  - `malaysia_retail_sale` — retail sale (Jualan Mega, BM/EN)
- All Malaysia slugs map to `hospital_premium` / `job_opening` / `walkin_drive` visual templates with Malaysia-tuned AI prompts in `LanguageService.TEMPLATE_PROMPTS`.

**Image Generation Tiers**

| Model | Cost | Use case |
|---|---|---|
| `flux-1-schnell` | ~$0.003/img | Default — fast draft & testing |
| `flux-1.1-pro` | ~$0.040/img | Quality fallback |
| `flux-1-pro` | ~$0.055/img | In catalogue, available if configured |

**Language Toggle (previous release)**

- `getPosterForView()` in `VariantPreview` now actually swaps `_english` layers with `_regional` equivalents when user selects a regional language.
- Status badges: "✓ Showing telugu" / "⚠ Regional translation unavailable" shown on poster preview.

---

### v1.0.0 — March 2026

**Core Platform**

- Multi-tenant FastAPI backend with JWT authentication, CORS, GZip middleware
- React 18 + TypeScript + Vite frontend with Tailwind CSS + shadcn/ui components
- PostgreSQL 16 with async SQLAlchemy 2.0 and 9 Alembic migration versions
- Redis + Celery background workers for social publishing, email, and AI jobs
- bcrypt password hashing (bcrypt 3.x, passlib-compatible)

**AI Architecture**

- Centralized `ModelRouter` with `FeatureBucket` routing system (11 buckets)
- OpenRouter integration — cost-efficient content, campaign, and SEO generation
- OpenAI direct integration — translation and localization (most reliable for Indian scripts)
- `PlanLimitService` — monthly AI credit enforcement: starter / pro / agency / enterprise
- `UsageTrackingService` — per-tenant token usage logging with estimated USD cost

**Creative Generation**

- `CreativeService` — full 7-step pipeline from business brief to structured creative output
- `PosterGenerator` — industry + locale aware structured JSON poster generation
- `LocalizationEngine` — 14-language bilingual and trilingual content generation
- `IndustryConfig` — 20+ industry presets with tone, vocabulary, and template configuration
- `PosterRenderer` — React component rendering structured poster JSON visual layers
- `VariantPreview` — multi-variant poster comparison view
- `LanguageToggle` — bilingual poster language switching in preview

**Localization**

- 7-country multi-market support: IN, AU, NZ, MY, SG, ID, TH
- 14 languages: 10 Indian scripts + 4 SE Asian
- Country-aware locale profiles with default language routing
- Cultural style presets: formal, modern, premium, community_trust, festive, family_oriented

**Features**

- Lead capture, scoring, source attribution, and CRM pipeline
- 6-stage Kanban (New, Qualified, Proposal, Negotiation, Won, Lost)
- Social media scheduler with Celery publishing workers
- Email campaign builder with drip sequences and SMTP integration
- Analytics dashboard: leads trend, conversion funnel, per-campaign metrics
- AI assistant: copy generation, lead scoring, smart replies
- Campaign builder with audience targeting and bilingual creative output
- Follow-up sequence builder with AI flow suggestions
- WhatsApp status export
- LinkedIn AI content generation
- SEO keyword tools
- Global localization configuration panel
- Notifications system
- Webhook ingestion endpoints

---

## Future Improvements

- [ ] WhatsApp Business API live message sending
- [ ] Google Ads and Meta Ads campaign sync
- [ ] Advanced A/B testing for creative variants
- [ ] Real-time analytics with WebSocket push
- [ ] Mobile app (React Native) for on-the-go lead management
- [ ] AI image generation via DALL-E / Stable Diffusion (plan-gated, when enabled)
- [ ] Custom drag-and-drop template builder
- [ ] Multi-user per tenant with role-based permissions (admin / editor / viewer)
- [ ] Zapier / Make.com webhook integration for external CRM sync
- [ ] White-label deployment package for agency resellers
- [ ] Automated weekly performance report email digest
- [ ] OCR-based lead extraction from business cards

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Ensure all AI calls go through `ModelRouter` — no direct `openai` imports in services/routers
4. Add an Alembic migration if any schema change is involved
5. Test locally using Docker Compose
6. Submit a pull request with a clear description of the change

**Core Architecture Rules:**

- `ModelRouter` is the only place AI providers are imported — enforce this strictly
- All database records must carry `tenant_id` for multi-tenant isolation
- All AI endpoints must call `PlanLimitService.check_limit()` before generating
- Log every AI call with `UsageTracker.log()` after generation succeeds

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built by **SRP AI Digital Marketing**

[app.srpailabs.com](https://app.srpailabs.com)

</div>
