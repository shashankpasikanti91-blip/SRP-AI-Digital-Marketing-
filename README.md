<div align="center">

# âš¡ SRP Marketing OS

### by **SRP AI Digital Marketing**

> **The all-in-one AI-powered Marketing SaaS platform** â€” capture leads, manage your CRM pipeline, schedule social posts, automate email sequences and let AI do the heavy lifting.

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Pydantic AI](https://img.shields.io/badge/Pydantic_AI-1.67-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://ai.pydantic.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

![SRP Marketing OS Dashboard Preview](https://via.placeholder.com/1200x600/0f172a/6366f1?text=SRP+Marketing+OS+%E2%80%94+Dashboard+Preview)

</div>

---

## ðŸŽ® Demo Accounts

> **5 ready-to-use demo accounts across different industries â€” no setup needed.**

| Industry | Email | Password | Company | Data |
|----------|-------|----------|---------|------|
| Digital Agency | `demo@srp.ai` | `Demo@12345` | SRP Digital Marketing Agency | 12 leads, 5 campaigns |
| Healthcare Marketing | `bunty@srp.ai` | `Bunty@12345` | Bunty Healthcare Marketing | 12 leads, 5 campaigns |
| Hospital (Basic) | `bunty@hospital.demo` | `Bunty@2026` | Kothagudem General Hospital | 12 leads |
| Recruitment Agency | `bunty@recruitment.demo` | `Bunty@2026` | BuntyHire Pan India Staffing | 12 leads |
| FB/Google Ads Agency | `bunty@ads.demo` | `Bunty@2026` | BuntyAds Lead Generation | 12 leads |
| Restaurant / Catering | `bunty@restaurant.demo` | `Bunty@2026` | Bunty's Kitchen | 8 leads |

**Each demo account includes pre-seeded:**
- 8-12 leads (hot/warm/cold across multiple sources)
- 5 campaigns (awareness, conversion, social, email, nurture)
- Brand profile (for Regional Marketing / Campaign Builder)
- Conversations and AI follow-up sequences

```bash
# Seed demo accounts (run after alembic migrations)
python backend/seed_demo.py
python backend/seed_bunty.py   # bunty@srp.ai healthcare account
```


---

## ðŸ’° India Pricing Plans

> All prices in Indian Rupees (INR) + 18% GST. Annual billing saves 20%.

| Plan | Price | Leads/mo | AI Credits | Social Accounts | Users |
|------|-------|----------|------------|-----------------|-------|
| ðŸ†“ **Starter** | â‚¹0 / forever | 100 | 50 AI posts | 1 | 1 |
| ðŸš€ **Growth** â­ | â‚¹1,499 / month | 2,500 | 300 AI posts | 3 | 3 |
| ðŸ’¼ **Professional** | â‚¹3,999 / month | 10,000 | 1,000 AI posts | 10 | 10 |
| ðŸ¢ **Enterprise** | â‚¹9,999 / month | Unlimited | Unlimited | Unlimited | Unlimited |

**Growth plan = ~Rs 50 per day** â€” less than a cup of chai â˜•

Compared to international alternatives:
- HubSpot Professional: $800/month (~â‚¹66,000)
- GoHighLevel: $97/month (~â‚¹8,000)
- **SRP Growth: â‚¹1,499/month** ðŸ‡®ðŸ‡³

---

## Table of Contents

- [Demo Access](#-demo-access)
- [India Pricing](#-india-pricing-plans)
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Docker Setup (Recommended)](#docker-setup-recommended)
  - [Local Development Setup](#local-development-setup)
- [Environment Configuration](#-environment-configuration)
- [Database Models](#-database-models)
- [API Endpoints](#-api-endpoints)
  - [Authentication](#authentication)
  - [Lead Capture](#lead-capture)
  - [CRM Pipeline](#crm-pipeline)
  - [Social Media Scheduler](#social-media-scheduler)
  - [Email Automation](#email-automation)
  - [AI Assistant](#ai-assistant)
  - [Analytics](#analytics)
- [Background Workers](#-background-workers)
- [Frontend Pages](#-frontend-pages)
- [AI Agents](#-ai-agents)
- [Multi-Tenancy](#-multi-tenancy)
- [Security](#-security)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## ðŸŒŸ Overview

**SRP Marketing OS** is a production-ready, **multi-tenant AI marketing automation platform** built by **SRP AI Digital Marketing**. It enables businesses of all sizes to:

- **Capture and qualify leads** automatically from any web form, landing page, or ad platform
- **Manage their sales pipeline** through a visual CRM with Kanban-style stages
- **Schedule and publish social media content** across Facebook, Instagram, and LinkedIn from one place
- **Run automated email sequences** with SMTP integration and engagement tracking
- **Leverage AI** (via [Pydantic AI](https://ai.pydantic.dev)) to generate posts, classify leads, and suggest smart replies
- **Analyze performance** across campaigns, platforms, and conversion funnels in real-time

Built on a **modular, service-oriented architecture** â€” every module is independently scalable and testable.

---

## âœ¨ Key Features

| Module | Capabilities |
|--------|-------------|
| ðŸŽ¯ **Lead Capture** | REST API ingestion, UTM tracking, AI lead scoring (0â€“100), source attribution |
| ðŸ—‚ **CRM Pipeline** | 6-stage Kanban (New â†’ Won/Lost), CRUD API, bulk operations, notes & history |
| ðŸ“… **Social Scheduler** | Multi-platform posting (FB / IG / LinkedIn), queue-based worker, retry logic |
| ðŸ“§ **Email Automation** | Campaign builder, drip sequences, SMTP/TLS, open & click tracking |
| ðŸ¤– **AI Assistant** | GPT-4o / Claude-powered post generation, lead classification, reply suggestions |
| ðŸ“Š **Analytics** | Leads per campaign, conversion rates, platform performance, funnel metrics |
| ðŸ¢ **Multi-Tenancy** | Isolated tenant workspaces, API key auth, per-plan feature gates |
| ðŸ”’ **Security** | JWT auth, rate limiting, row-level security, input validation via Pydantic |

---

## ðŸ— Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                        SRP Marketing OS                              â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚                                                                       â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    HTTPS     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   â”‚   React SPA  â”‚â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚    FastAPI  (async)             â”‚  â”‚
â”‚   â”‚  (Vite/TS)   â”‚              â”‚    /api/v1/*                    â”‚  â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                            â”‚                          â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚   â”‚  Lead Forms  â”‚â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚    Service Layer                â”‚  â”‚
â”‚   â”‚  (External)  â”‚   REST API   â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚  â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚  â”‚ Leads  â”‚  â”‚  CRM         â”‚  â”‚  â”‚
â”‚                                 â”‚  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”¤  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤  â”‚  â”‚
â”‚   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”‚  â”‚ Social â”‚  â”‚  Email       â”‚  â”‚  â”‚
â”‚   â”‚  AI Models   â”‚â—„â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”¤  â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤  â”‚  â”‚
â”‚   â”‚ (OpenAI/     â”‚  Pydantic-AI â”‚  â”‚  AI    â”‚  â”‚  Analytics   â”‚  â”‚  â”‚
â”‚   â”‚  Anthropic)  â”‚              â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚  â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                            â”‚                          â”‚
â”‚        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”      â”‚
â”‚        â”‚                                   â”‚                  â”‚      â”‚
â”‚   â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”                     â”Œâ”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â” â”‚
â”‚   â”‚PostgreSQLâ”‚                     â”‚    Redis     â”‚   â”‚  Celery   â”‚ â”‚
â”‚   â”‚  (async) â”‚                     â”‚  (Queue /    â”‚   â”‚  Workers  â”‚ â”‚
â”‚   â”‚SQLAlchemyâ”‚                     â”‚   Cache)     â”‚   â”‚(scheduler)â”‚ â”‚
â”‚   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â”‚                                                                       â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Design Principles

- **Async-first** â€” All I/O uses Python `asyncio` + SQLAlchemy async engine for maximum throughput
- **Modular services** â€” Each domain (leads, CRM, social, email, AI, analytics) is a self-contained service module
- **Multi-tenant isolation** â€” Every database record is scoped by `tenant_id`; no cross-tenant data leakage
- **Queue-backed workers** â€” Celery + Redis handles social publishing, email sending, and AI tasks asynchronously
- **Type-safe AI** â€” [Pydantic AI](https://ai.pydantic.dev) wraps all LLM interactions with validated, typed outputs

---

## ðŸ“ Project Structure

```
ai-marketing-os/
â”‚
â”œâ”€â”€ backend/                        # FastAPI application
â”‚   â”œâ”€â”€ app/
â”‚   â”‚   â”œâ”€â”€ __init__.py
â”‚   â”‚   â”œâ”€â”€ main.py                 # App factory, middleware, router registration
â”‚   â”‚   â”œâ”€â”€ config.py               # Pydantic-settings config (env vars)
â”‚   â”‚   â”œâ”€â”€ database.py             # Async SQLAlchemy engine & session
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ models/                 # SQLAlchemy ORM models
â”‚   â”‚   â”‚   â”œâ”€â”€ tenant.py           # Multi-tenant accounts
â”‚   â”‚   â”‚   â”œâ”€â”€ lead.py             # Lead capture & scoring
â”‚   â”‚   â”‚   â”œâ”€â”€ crm.py              # CRM pipeline & stages
â”‚   â”‚   â”‚   â”œâ”€â”€ social.py           # Social media posts/schedules
â”‚   â”‚   â”‚   â”œâ”€â”€ email_campaign.py   # Email campaigns & sequences
â”‚   â”‚   â”‚   â””â”€â”€ analytics.py        # Analytics events
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ schemas/                # Pydantic request/response schemas
â”‚   â”‚   â”‚   â”œâ”€â”€ lead.py
â”‚   â”‚   â”‚   â”œâ”€â”€ crm.py
â”‚   â”‚   â”‚   â”œâ”€â”€ social.py
â”‚   â”‚   â”‚   â”œâ”€â”€ email_campaign.py
â”‚   â”‚   â”‚   â”œâ”€â”€ ai_assistant.py
â”‚   â”‚   â”‚   â””â”€â”€ analytics.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ routers/                # FastAPI route handlers
â”‚   â”‚   â”‚   â”œâ”€â”€ leads.py
â”‚   â”‚   â”‚   â”œâ”€â”€ crm.py
â”‚   â”‚   â”‚   â”œâ”€â”€ social.py
â”‚   â”‚   â”‚   â”œâ”€â”€ email_campaigns.py
â”‚   â”‚   â”‚   â”œâ”€â”€ ai_assistant.py
â”‚   â”‚   â”‚   â””â”€â”€ analytics.py
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ services/               # Business logic layer
â”‚   â”‚   â”‚   â”œâ”€â”€ lead_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ crm_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ social_service.py
â”‚   â”‚   â”‚   â”œâ”€â”€ email_service.py
â”‚   â”‚   â”‚   â””â”€â”€ ai_service.py       # Pydantic AI agents
â”‚   â”‚   â”‚
â”‚   â”‚   â”œâ”€â”€ workers/                # Celery async workers
â”‚   â”‚   â”‚   â”œâ”€â”€ celery_app.py
â”‚   â”‚   â”‚   â”œâ”€â”€ social_worker.py    # Social post publisher
â”‚   â”‚   â”‚   â”œâ”€â”€ email_worker.py     # Email sequence sender
â”‚   â”‚   â”‚   â””â”€â”€ ai_worker.py        # Async AI tasks
â”‚   â”‚   â”‚
â”‚   â”‚   â””â”€â”€ core/                   # Shared utilities
â”‚   â”‚       â”œâ”€â”€ security.py         # JWT, API key auth
â”‚   â”‚       â”œâ”€â”€ dependencies.py     # FastAPI dependencies
â”‚   â”‚       â”œâ”€â”€ middleware.py        # Tenant context, rate-limit
â”‚   â”‚       â””â”€â”€ exceptions.py       # Custom exception handlers
â”‚   â”‚
â”‚   â”œâ”€â”€ alembic/                    # Database migrations
â”‚   â”‚   â”œâ”€â”€ versions/
â”‚   â”‚   â””â”€â”€ env.py
â”‚   â”œâ”€â”€ tests/                      # Pytest test suite
â”‚   â”œâ”€â”€ requirements.txt
â”‚   â””â”€â”€ Dockerfile
â”‚
â”œâ”€â”€ frontend/                       # React 18 + Vite + TypeScript
â”‚   â”œâ”€â”€ src/
â”‚   â”‚   â”œâ”€â”€ components/             # Reusable UI components
â”‚   â”‚   â”‚   â”œâ”€â”€ Layout/
â”‚   â”‚   â”‚   â”œâ”€â”€ LeadCapture/
â”‚   â”‚   â”‚   â”œâ”€â”€ CRMKanban/
â”‚   â”‚   â”‚   â”œâ”€â”€ SocialCalendar/
â”‚   â”‚   â”‚   â”œâ”€â”€ EmailBuilder/
â”‚   â”‚   â”‚   â”œâ”€â”€ AIAssistant/
â”‚   â”‚   â”‚   â””â”€â”€ AnalyticsDashboard/
â”‚   â”‚   â”œâ”€â”€ pages/                  # Route-level page components
â”‚   â”‚   â”œâ”€â”€ hooks/                  # Custom React hooks
â”‚   â”‚   â”œâ”€â”€ services/               # API client (Axios)
â”‚   â”‚   â”œâ”€â”€ store/                  # Zustand state management
â”‚   â”‚   â””â”€â”€ types/                  # TypeScript interfaces
â”‚   â”œâ”€â”€ package.json
â”‚   â”œâ”€â”€ vite.config.ts
â”‚   â””â”€â”€ Dockerfile
â”‚
â”œâ”€â”€ nginx/                          # Reverse proxy config
â”‚   â””â”€â”€ nginx.conf
â”‚
â”œâ”€â”€ docker-compose.yml              # Full-stack orchestration
â”œâ”€â”€ docker-compose.dev.yml          # Dev override (hot-reload)
â”œâ”€â”€ .env.example                    # Environment variable template
â”œâ”€â”€ Makefile                        # Dev shortcuts (make dev, make test, etc.)
â””â”€â”€ README.md                       # YOU ARE HERE
```

---

## ðŸ›  Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Core language |
| **FastAPI** | 0.115 | Async REST API framework |
| **Pydantic AI** | 1.67 | AI agent framework (OpenAI, Anthropic, Gemini) |
| **SQLAlchemy** | 2.0 (async) | ORM + async database engine |
| **Alembic** | 1.13 | Database migrations |
| **Celery** | 5.4 | Distributed task queue |
| **Redis** | 7 | Message broker + caching |
| **PostgreSQL** | 16 | Primary relational database |
| **asyncpg** | 0.30 | Async PostgreSQL driver |
| **Pydantic Settings** | 2.x | Env config management |
| **Python-Jose** | 3.3 | JWT token handling |
| **aiosmtplib** | 3.x | Async SMTP email sending |
| **httpx** | 0.27 | Async HTTP client (social APIs) |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18 | UI framework |
| **TypeScript** | 5.x | Type safety |
| **Vite** | 5.x | Build tool & dev server |
| **TailwindCSS** | 3.x | Utility-first styling |
| **shadcn/ui** | Latest | Component library |
| **Zustand** | 4.x | Lightweight state management |
| **React Query** | 5.x | Server-state & caching |
| **Axios** | 1.x | HTTP API client |
| **Recharts** | 2.x | Analytics charts |
| **React DnD** | 16.x | Kanban drag-and-drop |
| **Framer Motion** | 11.x | Smooth UI animations |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| **Docker + Compose** | Containerisation & local orchestration |
| **Nginx** | Reverse proxy, SSL termination |
| **GitHub Actions** | CI/CD pipelines |

---

## ðŸš€ Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) â‰¥ 4.x
- [Git](https://git-scm.com/)
- (Optional for local dev) Python 3.12+ & Node.js 20+

### Docker Setup (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/srp-ai-digital/srp-marketing-os.git
cd srp-marketing-os

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys (OpenAI, SMTP, social media tokens)
# At minimum set:  SECRET_KEY, OPENAI_API_KEY, SMTP_USER, SMTP_PASSWORD

# 3. Start the entire stack (API + DB + Redis + Frontend + Nginx)
docker compose up --build

# 4. Run database migrations
docker compose exec backend alembic upgrade head

# 5. Seed demo data (optional)
docker compose exec backend python -m app.scripts.seed_demo

# 6. Open the dashboard
open http://localhost:3000
# API docs (Swagger UI)
open http://localhost:8002/docs
# API docs (ReDoc)
open http://localhost:8002/redoc
```

### Local Development Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp ../.env.example ../.env
# Edit .env as needed

# Start dependencies (Postgres + Redis only)
docker compose -f ../docker-compose.dev.yml up -d postgres redis

# Run migrations
alembic upgrade head

# Start FastAPI with hot-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Start Celery worker (separate terminal)
celery -A app.workers.celery_app worker --loglevel=info

# Start Celery Beat scheduler (separate terminal)
celery -A app.workers.celery_app beat --loglevel=info
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server with hot-reload
npm run dev
# â†’ http://localhost:5173
```

---

## âš™ï¸ Environment Configuration

Copy `.env.example` to `.env` and fill in the values:

```env
# â”€â”€ Application â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
APP_NAME="SRP Marketing OS"
APP_ENV=development
DEBUG=true
SECRET_KEY=your-super-secret-key-change-in-production

# â”€â”€ Database â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/srp_marketing_os

# â”€â”€ Redis / Celery â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# â”€â”€ AI (Pydantic AI supports multiple providers) â”€â”€â”€â”€â”€â”€â”€â”€â”€
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
AI_MODEL=openai:gpt-4o          # or anthropic:claude-sonnet-4-6

# â”€â”€ SMTP / Email â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME="SRP Marketing OS"
SMTP_FROM_EMAIL=noreply@srp-marketing.com

# â”€â”€ Social Media APIs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
FACEBOOK_ACCESS_TOKEN=EAA...
FACEBOOK_PAGE_ID=123456789
INSTAGRAM_ACCESS_TOKEN=EAA...
INSTAGRAM_ACCOUNT_ID=987654321
LINKEDIN_ACCESS_TOKEN=AQX...
LINKEDIN_ORG_ID=urn:li:organization:...

# â”€â”€ CORS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ALLOWED_ORIGINS=["http://localhost:3000","https://app.srp-marketing.com"]
```

---

## ðŸ—„ Database Models

### Entity Relationship Overview

```
Tenant
  â”œâ”€â”€ Lead (name, email, phone, source, campaign, ai_score, status)
  â”‚     â””â”€â”€ CRMPipeline (stage: newâ†’won/lost, notes, history)
  â”œâ”€â”€ SocialPost (platform, content, scheduled_at, status, media_url)
  â”œâ”€â”€ EmailCampaign (name, subject, body_html)
  â”‚     â”œâ”€â”€ EmailSequence (step, delay_days, subject, body)
  â”‚     â””â”€â”€ EmailLog (lead_id, sent_at, opened_at, clicked_at)
  â””â”€â”€ AnalyticsEvent (event_type, source, campaign, metadata)
```

### CRM Pipeline Stages

```
NEW â†’ CONTACTED â†’ QUALIFIED â†’ PROPOSAL â†’ WON
                                        â†˜ LOST
```

### Lead Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | UUID | Owning tenant |
| `name` | String | Full name |
| `email` | String | Email address |
| `phone` | String | Phone number |
| `source` | String | Traffic source (e.g. `facebook_ad`) |
| `campaign` | String | Campaign name / UTM campaign |
| `medium` | String | UTM medium |
| `notes` | Text | Free-form notes |
| `ai_score` | Int (0â€“100) | AI-generated lead quality score |
| `ai_label` | Enum | `hot` / `warm` / `cold` |
| `status` | Enum | `new` / `contacted` / `qualified` / `disqualified` / `converted` |

---

## ðŸ“¡ API Endpoints

Interactive docs available at **`/docs`** (Swagger UI) or **`/redoc`** (ReDoc) when the server is running.

Base URL: `http://localhost:8002/api/v1`

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new tenant account |
| `POST` | `/auth/login` | Login, get JWT access token |
| `POST` | `/auth/refresh` | Refresh access token |
| `GET` | `/auth/me` | Get current tenant profile |

### Lead Capture

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/leads/` | **Create lead** (from form / integration) |
| `GET` | `/leads/` | List all leads (filterable by source, campaign, status) |
| `GET` | `/leads/{id}` | Get single lead |
| `PATCH` | `/leads/{id}` | Update lead fields |
| `DELETE` | `/leads/{id}` | Delete lead |
| `POST` | `/leads/{id}/score` | **Trigger AI lead scoring** |
| `GET` | `/leads/export` | Export leads as CSV |

**Example â€” Create Lead:**
```bash
curl -X POST http://localhost:8002/api/v1/leads/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+1-555-0100",
    "source": "facebook_ad",
    "campaign": "summer_sale_2026"
  }'
```

**Example Response:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1-555-0100",
  "source": "facebook_ad",
  "campaign": "summer_sale_2026",
  "status": "new",
  "ai_score": null,
  "ai_label": null,
  "created_at": "2026-03-12T10:00:00Z"
}
```

### CRM Pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/crm/` | Create pipeline record for a lead |
| `GET` | `/crm/` | List all pipeline records (filterable by stage) |
| `GET` | `/crm/{id}` | Get pipeline details |
| `PATCH` | `/crm/{id}/stage` | **Move lead to new stage** |
| `PATCH` | `/crm/{id}` | Update pipeline record |
| `DELETE` | `/crm/{id}` | Delete pipeline record |
| `GET` | `/crm/kanban` | Get all records grouped by stage (Kanban view) |

**Stage values:** `new` | `contacted` | `qualified` | `proposal` | `won` | `lost`

### Social Media Scheduler

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/social/posts/` | Create & schedule a post |
| `GET` | `/social/posts/` | List all posts (filterable by platform, status) |
| `GET` | `/social/posts/{id}` | Get post details |
| `PATCH` | `/social/posts/{id}` | Edit scheduled post |
| `DELETE` | `/social/posts/{id}` | Cancel / delete post |
| `POST` | `/social/posts/{id}/publish` | Publish immediately |
| `GET` | `/social/calendar` | Get posts in calendar view (by date range) |
| `GET` | `/social/analytics` | Platform performance metrics |

**Supported platforms:** `facebook` | `instagram` | `linkedin`

**Example â€” Schedule a Post:**
```bash
curl -X POST http://localhost:8002/api/v1/social/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "content": "ðŸš€ Excited to announce our Summer Sale is LIVE! ...",
    "media_url": "https://cdn.srp.com/images/summer-sale.jpg",
    "scheduled_at": "2026-03-15T09:00:00Z",
    "campaign": "summer_sale_2026"
  }'
```

### Email Automation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/email/campaigns/` | Create email campaign |
| `GET` | `/email/campaigns/` | List all campaigns |
| `GET` | `/email/campaigns/{id}` | Get campaign details |
| `PATCH` | `/email/campaigns/{id}` | Update campaign |
| `DELETE` | `/email/campaigns/{id}` | Delete campaign |
| `POST` | `/email/campaigns/{id}/sequences/` | Add sequence step |
| `GET` | `/email/campaigns/{id}/sequences/` | List sequence steps |
| `POST` | `/email/campaigns/{id}/send` | **Trigger campaign send** |
| `GET` | `/email/campaigns/{id}/stats` | Open / click rates |
| `GET` | `/email/logs/` | Full send log |

### AI Assistant

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/ai/generate-post` | **Generate social media post** |
| `POST` | `/ai/classify-lead` | **Score & classify a lead** |
| `POST` | `/ai/reply-suggestion` | **Suggest reply to lead message** |
| `POST` | `/ai/write-email` | **Generate email campaign content** |
| `POST` | `/ai/campaign-ideas` | **Brainstorm campaign ideas** |

**Example â€” Generate Social Post:**
```bash
curl -X POST http://localhost:8002/api/v1/ai/generate-post \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "topic": "Benefits of AI in digital marketing",
    "tone": "professional",
    "include_hashtags": true,
    "include_cta": true
  }'
```

**Example Response:**
```json
{
  "content": "ðŸ¤– AI is no longer a future trend â€” it's today's competitive advantage...\n\n#AIMarketing #DigitalMarketing #SRPMarketingOS",
  "character_count": 420,
  "suggested_platforms": ["linkedin", "facebook"],
  "tokens_used": 312
}
```

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/analytics/overview` | Platform-wide KPI summary |
| `GET` | `/analytics/leads` | Leads per campaign, source, date |
| `GET` | `/analytics/conversion` | Funnel conversion rates |
| `GET` | `/analytics/social` | Reach, engagement by platform |
| `GET` | `/analytics/email` | Open rate, CTR by campaign |
| `GET` | `/analytics/revenue` | Won deals & pipeline value |

**Query Parameters for all analytics endpoints:**
```
?from=2026-01-01&to=2026-03-12&campaign=summer_sale_2026&granularity=day
```

---

## âš™ï¸ Background Workers

SRP Marketing OS uses **Celery** backed by **Redis** for all async operations:

### Social Post Publisher (`social_worker.py`)
- Runs every minute to check for due posts
- Calls Facebook Graph API, Instagram API, LinkedIn API
- Handles retries with exponential backoff (max 3 attempts)
- Updates post status: `scheduled â†’ published | failed`

### Email Sequence Sender (`email_worker.py`)
- Evaluates drip sequence schedules daily
- Sends via `aiosmtplib` (async SMTP)
- Tracks delivery, opens (pixel tracking), and click-throughs
- Respects unsubscribe lists

### AI Background Tasks (`ai_worker.py`)
- Asynchronous lead scoring triggered on new lead creation
- Batch classification for bulk imports
- Scheduled content ideas generation (weekly)

### Running Workers

```bash
# All workers
celery -A app.workers.celery_app worker -B --loglevel=info

# Monitor tasks (Flower UI at :5555)
celery -A app.workers.celery_app flower
```

---

## ðŸ–¥ Frontend Pages

### Public Routes
| Route | Component | Description |
|-------|-----------|-------------|
| `/` | `LandingPage` | Marketing landing page with India pricing |
| `/login` | `Login` | Login with demo credentials auto-fill |
| `/register` | `Register` | Free account registration |

### Protected Routes (`/app/*`)
| Route | Component | Description |
|-------|-----------|-------------|
| `/app/dashboard` | `Dashboard` | KPI overview + AI summary |
| `/app/leads` | `Leads` | Lead list + AI scoring |
| `/app/crm` | `CRM` | Kanban pipeline |
| `/app/business` | `Business` | Strategy wizard + AI plan |
| `/app/campaigns` | `Campaigns` | Campaign management |
| `/app/content` | `Content` | AI content generation |
| `/app/conversations` | `Conversations` | Inbox (Email/WhatsApp/IG/LinkedIn) |
| `/app/followups` | `Followups` | Drip sequence builder |
| `/app/chatbot` | `Chatbot` | AI marketing assistant chat |
| `/app/social` | `Social` | Social media scheduler |
| `/app/email` | `Email` | Email campaign builder |
| `/app/ai` | `AIAssistant` | AI tools & generation |
| `/app/analytics` | `Analytics` | Performance dashboards |
| `/app/settings` | `Settings` | Account & integrations |

The React dashboard includes **14 pages across public + protected routes**:

---

## ðŸ¤– AI Agents

SRP Marketing OS includes **10 specialised AI agents** powered by OpenAI GPT-4o / GPT-4o-mini:

| Agent | Model | Purpose |
|-------|-------|---------|
| **Strategy Agent** | GPT-4o | Full go-to-market strategy from business profile |
| **Content Agent** | GPT-4o-mini | Social posts, captions, ad copy, hashtags |
| **Lead Scoring Agent** | GPT-4o-mini | 0â€“100 score + hot/warm/cold classification |
| **Reply Agent** | GPT-4o-mini | Smart reply suggestions for conversations |
| **Email Agent** | GPT-4o-mini | Email subjects, body, drip sequences |
| **Follow-up Agent** | GPT-4o-mini | Automated follow-up sequence generation |
| **Campaign Agent** | GPT-4o-mini | Campaign plan + targeting recommendations |
| **Analytics Agent** | GPT-4o | Insight summaries + performance diagnosis |
| **Chatbot Agent** | GPT-4o-mini | Marketing Q&A + task automation via chat |
| **SEO Agent** | GPT-4o-mini | Blog outlines, meta descriptions, keyword clusters |

---

### 1. ðŸŽ¯ Leads Dashboard
- Live feed of incoming leads
- Filter/search by source, campaign, status, date
- One-click AI scoring trigger
- Bulk import via CSV

### 2. ðŸ—‚ CRM Kanban Board
- Drag-and-drop lead cards between stages
- Stage-by-stage pipeline value
- Lead detail side panel with full history
- Notes and follow-up reminders

### 3. ðŸ“… Social Media Calendar
- Monthly/weekly calendar view of scheduled posts
- Platform filter (Facebook / Instagram / LinkedIn)
- AI post composition assistant
- Media upload + preview

### 4. ðŸ“§ Email Campaign Builder
- Drag-and-drop email sequence builder
- HTML rich-text email editor
- A/B test subject lines
- Real-time performance stats (open rate, CTR)

### 5. ðŸ¤– AI Assistant Chat
- Chat interface to generate posts, classify leads, draft emails
- Powered by Pydantic AI (OpenAI GPT-4o / Anthropic Claude)
- Save generated content directly to scheduler

### 6. ðŸ“Š Analytics Dashboard
- Recharts-powered interactive charts
- KPI cards: total leads, conversion rate, ROI
- Platform comparison bar charts
- Funnel visualisation
- Custom date range picker

---

## ðŸ¢ Multi-Tenancy

SRP Marketing OS is built for **multiple clients / businesses** on a single platform:

- Every API request identifies the tenant via **JWT token** or **API key** header (`X-API-Key`)
- All database queries automatically filter by `tenant_id` via SQLAlchemy middleware
- Tenants are fully **data-isolated** â€” no cross-tenant queries are possible
- Plan-based **feature gating** (Starter / Pro / Enterprise) controls AI token limits, post volumes, etc.

```
Header: X-API-Key: <tenant-api-key>
# OR
Header: Authorization: Bearer <jwt-token>
```

---

## ðŸ”’ Security

| Concern | Implementation |
|---------|---------------|
| **Authentication** | JWT (HS256) with refresh tokens |
| **API Key Auth** | Per-tenant API keys for form integrations |
| **Rate Limiting** | 60 req/min per tenant (configurable) |
| **Input Validation** | Pydantic v2 schema validation on all endpoints |
| **SQL Injection** | SQLAlchemy parameterised queries |
| **CORS** | Allowlist-based, configurable per environment |
| **Secrets** | Env vars / Docker secrets â€” never committed |
| **HTTPS** | Nginx SSL termination in production |

---

## ðŸ§ª Testing

```bash
# Run all tests
cd backend
pytest tests/ -v --cov=app --cov-report=html

# Run specific module tests
pytest tests/test_leads.py -v
pytest tests/test_ai_service.py -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

Tests cover:
- Unit tests for all service layer functions
- Integration tests for all API endpoints
- AI service mock tests (no real API calls in CI)
- Worker task tests with Celery eager mode

---

## ðŸš¢ Deployment

### Docker Compose (Recommended for VPS / Self-hosted)

```bash
# Production build
docker compose -f docker-compose.yml up -d --build

# Scale workers
docker compose up -d --scale celery-worker=3
```

### Environment-Specific Config

| Variable | Dev | Prod |
|----------|-----|------|
| `DEBUG` | `true` | `false` |
| `APP_ENV` | `development` | `production` |
| `DATABASE_URL` | local postgres | managed DB (RDS, Supabase) |
| `REDIS_URL` | local redis | managed Redis (ElastiCache, Upstash) |

### Hetzner VPS Deployment — srp-ai-server (5.223.67.236)

> Production deployment for **SRP Marketing OS** on Hetzner + Ubuntu 22.04 + Docker Compose.  
> Domain: **https://app.srpailabs.com** (Cloudflare DNS → 5.223.67.236)  
> All services run in containers — no manual installs beyond Docker.

---

#### Step 0 — Cloudflare DNS Record

In your Cloudflare dashboard, add:

| Type | Name | Content | TTL |
|------|------|---------|-----|
| **A** | **app** | **5.223.67.236** | Auto |

> This points `app.srpailabs.com` → your Hetzner server IP.  
> Set Proxy status to **DNS only** (grey cloud) during first SSL setup, then enable Proxy after.

---

#### Step 0b — Choose Your Hetzner Plan

| Plan | RAM | CPU | Storage | Price/mo | Use Case |
|------|-----|-----|---------|---------|----------|
| **CX21** | 4 GB | 2 vCPU | 40 GB SSD | ~€5.83 | Dev / Demo |
| **CX31** | 8 GB | 2 vCPU | 80 GB SSD | ~€14.63 | Small Production |
| **CX41** | 16 GB | 4 vCPU | 160 GB SSD | ~€28.74 | Production (Recommended) |
| **CX51** | 32 GB | 8 vCPU | 240 GB SSD | ~€57.49 | High-traffic / Multi-agency |

> **Minimum recommended**: CX31 (8GB RAM) — runs backend + DB + Redis + Nginx comfortably.

---

#### Step 1 — Provision Server

1. Go to [Hetzner Cloud Console](https://console.hetzner.cloud)
2. Existing server: **srp-ai-server** (IP: `5.223.67.236`)
   - **Image**: Ubuntu 22.04 LTS
   - **SSH Key**: Add your public key (`~/.ssh/id_rsa.pub`)
   - **Firewall**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)
3. Server IP: `5.223.67.236`

---

#### Step 2 — Initial Server Setup

```bash
# Connect to server
ssh root@5.223.67.236

# Update system
apt update && apt upgrade -y

# Install essentials
apt install -y git curl wget unzip ufw fail2ban

# Configure firewall
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create non-root user (optional but recommended)
adduser srp
usermod -aG sudo srp
usermod -aG docker srp
```

---

#### Step 3 — Install Docker & Docker Compose

```bash
# Install Docker Engine
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin (v2)
apt install -y docker-compose-plugin

# Verify
docker --version           # Docker version 26.x.x
docker compose version     # Docker Compose version v2.x.x

# Start and enable Docker
systemctl start docker
systemctl enable docker
```

---

#### Step 4 — Clone Repository & Configure Environment

```bash
# Clone the project
git clone https://github.com/shashankpasikanti91-blip/srp-marketing-os.git
cd srp-marketing-os

# Generate a strong SECRET_KEY
openssl rand -hex 32
# Example output: 6d15dab061abc0da8ab9ac736a7c0b9b...

# Create backend environment file
cp backend/.env.example backend/.env   # or create from scratch
nano backend/.env
```

**Production `.env` contents** (`backend/.env`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://ats_user:STRONG_DB_PASS@db:5432/srp_marketing

# Security (CHANGE THESE!)
SECRET_KEY=your-openssl-generated-64-char-hex-string
ACCESS_TOKEN_EXPIRE_MINUTES=10080        # 7 days

# AI
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE   # optional

# App
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://app.srpailabs.com

# Email (SMTP - for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your-app-password

# Redis
REDIS_URL=redis://redis:6379/0

# PostgreSQL (used by docker-compose.yml)
POSTGRES_USER=ats_user
POSTGRES_PASSWORD=STRONG_DB_PASS
POSTGRES_DB=srp_marketing
```

---

#### Step 5 — Configure Nginx for Your Domain

Edit `nginx/nginx.conf` and replace `localhost` with your domain:

```nginx
server {
    listen 80;
    server_name app.srpailabs.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name app.srpailabs.com;

    ssl_certificate     /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.srpailabs.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # Frontend (React SPA)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }

    # API Docs
    location /docs {
        proxy_pass http://backend:8002/docs;
    }
}
```

---

#### Step 6 — Build & Launch All Services

```bash
# Build all Docker images and start in background
docker compose -f docker-compose.yml up -d --build

# Watch logs during startup (Ctrl+C to stop watching)
docker compose logs -f

# Verify all containers are running
docker compose ps
# Expected: backend, frontend (nginx), db, redis all "Up"

# Check backend health
curl http://localhost:8002/api/v1/health
# Expected: {"status": "ok", "database": "connected"}
```

---

#### Step 7 — Run Database Migrations & Seed Data

```bash
# Run all Alembic migrations (creates all 22 tables)
docker compose exec backend alembic upgrade head

# Seed demo accounts (digital agency + healthcare + restaurant etc.)
docker compose exec backend python seed_demo.py
docker compose exec backend python seed_bunty.py   # Healthcare demo (bunty@srp.ai)

# Verify DB has all tables
docker compose exec db psql -U ats_user -d srp_marketing -c "\dt"
# Expected: 22 tables listed

# Verify tenant accounts
docker compose exec db psql -U ats_user -d srp_marketing \
  -c "SELECT name, email FROM tenants;"
```

---

#### Step 8 — SSL Certificate with Let's Encrypt (HTTPS)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Temporarily stop nginx container to free port 80
docker compose stop nginx

# Get SSL certificate for app.srpailabs.com
certbot certonly --standalone -d app.srpailabs.com \
  --email admin@srpailabs.com --agree-tos --non-interactive

# Certificates are at:
# /etc/letsencrypt/live/app.srpailabs.com/fullchain.pem
# /etc/letsencrypt/live/app.srpailabs.com/privkey.pem

# Restart nginx (now with SSL)
docker compose up -d nginx

# Auto-renew (add to crontab)
echo "0 12 * * * root certbot renew --quiet && docker compose -f /root/srp-marketing-os/docker-compose.yml restart nginx" >> /etc/crontab
```

---

#### Step 9 — GitHub → Hetzner Auto-Deploy (CI/CD)

Create `.github/workflows/deploy.yml` in your repo:

```yaml
name: Deploy to Hetzner

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.HETZNER_IP }}   # 5.223.67.236
          username: root
          key: ${{ secrets.HETZNER_SSH_KEY }}
          script: |
            cd /root/srp-marketing-os
            git pull origin main
            docker compose -f docker-compose.yml up -d --build backend frontend
            docker compose exec -T backend alembic upgrade head
            echo "Deployment complete: $(date)"
```

**GitHub Secrets to add** (`Settings → Secrets → Actions`):
- `HETZNER_IP` — `5.223.67.236`
- `HETZNER_SSH_KEY` — contents of your `~/.ssh/id_rsa` private key

---

#### Step 10 — Monitoring & Maintenance

```bash
# Live resource usage
docker stats

# View backend logs (last 100 lines)
docker compose logs backend --tail=100 -f

# View DB logs
docker compose logs db --tail=50

# Restart a single service without downtime
docker compose restart backend

# Full system restart
docker compose down && docker compose up -d

# Backup PostgreSQL database
docker compose exec db pg_dump -U ats_user srp_marketing > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260101.sql | docker compose exec -T db psql -U ats_user -d srp_marketing

# Check disk usage
df -h
docker system df

# Prune old images (free disk space)
docker image prune -f
```

---

#### Quick Reference — Production URLs

| Service | Internal | External |
|---------|----------|---------|
| Frontend | `http://frontend:80` | `https://yourdomain.com` |
| Backend API | `http://backend:8002` | `https://yourdomain.com/api/v1/` |
| Swagger UI | `http://backend:8002/docs` | `https://yourdomain.com/docs` |
| PostgreSQL | `db:5432` | Internal only |
| Redis | `redis:6379` | Internal only |

#### Common Troubleshooting

```bash
# Backend won't start — check for migration errors
docker compose logs backend | grep -i error

# DB connection refused — check postgres is healthy
docker compose exec db pg_isready -U ats_user

# Frontend 404 after refresh — nginx SPA config issue
# Ensure nginx.conf has: try_files $uri $uri/ /index.html;

# Permission denied on .env — fix file permissions
chmod 600 backend/.env

# Out of memory — check container limits
docker stats --no-stream | sort -k4 -rh
```

### Regional Marketing / Campaign Builder

The platform includes a full **multi-language campaign poster generator** supporting all industries:
- Hospital, Clinic, Healthcare
- Recruitment Agency
- Restaurant / Catering
- FB/Google Ads Agency
- Real Estate, Education, Retail, and more

Navigate to **Regional Marketing → Brand Settings** to set up your brand, then **Campaign Builder** to generate AI-powered bilingual social media posters.

### Cloud Deployment Options

| Platform | Guide |
|----------|-------|
| **Railway** | Push to main â†’ auto-deploy via Dockerfile |
| **Render** | Connect repo â†’ auto-detect Docker Compose |
| **AWS ECS** | Use `docker-compose --context ecs` |
| **DigitalOcean App Platform** | Dockerfile + managed Postgres + Redis |
| **Heroku** | `heroku.yml` + Postgres add-on |

---

## ðŸ—º Future Roadmap

### Phase 1 â€” v1.0 âœ… COMPLETE
- [x] Multi-tenant FastAPI backend with JWT + API key auth
- [x] Lead capture, scoring, and CRM pipeline
- [x] Social media scheduler (Facebook/Instagram/LinkedIn)
- [x] Email campaign builder with drip sequences
- [x] Follow-up sequence builder with AI generation
- [x] Business profile + AI strategy generation
- [x] 10 specialised AI agents (GPT-4o / GPT-4o-mini)
- [x] Analytics dashboard with Recharts
- [x] Marketing landing page with India pricing (â‚¹1,499â€“â‚¹9,999)
- [x] Free registration + demo account seeder
- [x] Full Docker Compose orchestration

### Phase 2 â€” v1.1 (Q2 2026) â€” Integrations
- [ ] **WhatsApp Business API** â€” 2-way lead conversations
- [ ] **Google Ads** lead form sync
- [ ] **RazorPay / PayU** payment gateway for India billing
- [ ] **Indiamart / JustDial** lead import connectors
- [ ] **Webhook system** â€” outbound webhooks on lead events
- [ ] **Zapier / Make** integration connector
- [ ] **Twilio SMS** campaigns for Indian numbers

### Phase 3 â€” v1.2 (Q3 2026) â€” Advanced AI
- [ ] **AI Content Calendar** â€” auto-plan 30 days of content
- [ ] **Predictive lead scoring** with custom training data
- [ ] **Vernacular AI** â€” generate content in Hindi, Tamil, Telugu
- [ ] **Landing page builder** (drag-and-drop)
- [ ] **White-label** â€” custom branding per agency tenant
- [ ] **Mobile app** (React Native)

### Phase 4 â€” v2.0 (2027) â€” Autonomous
- [ ] **Fully autonomous AI campaigns** â€” set goal, AI executes end-to-end
- [ ] **Multi-language** i18n (Hindi, Tamil, Marathi, Gujarati)
- [ ] **AI Marketplace** of prompt templates & playbooks
- [ ] **Enterprise SSO** (SAML / OAuth2)
- [ ] **Agentic outbound** â€” AI finds leads, writes emails, follows up

---

## ðŸ¤ Contributing

We welcome contributions from the community!

```bash
# Fork and clone
git clone https://github.com/your-fork/srp-marketing-os.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes, add tests, then:
git commit -m "feat: add your feature"
git push origin feature/your-feature-name

# Open a Pull Request
```

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and ensure all tests pass before submitting a PR.

### Commit Message Convention

```
feat:     New feature
fix:      Bug fix
docs:     Documentation change
refactor: Code refactoring
test:     Adding/updating tests
chore:    Tooling or config changes
```


---

## Phase 15 - AI Creative Generation Architecture

> Multi-country, multi-language, culturally-aware marketing creative generation with cost controls, template visuals, and SaaS billing readiness.

### Architecture Overview

`
CreativeRequest (API)  ->  CreativeService.generate()
  |-> PlanLimitService        (Enforce plan quotas - HTTP 402 if exceeded)
  |-> LocalizationEngine      (Country/state/language resolution)
  |-> IndustryConfig          (Industry strategy + tone + CTA style)
  |-> CulturalStyle           (Design context for AI prompt)
  |-> ModelRouter             (Select cheapest model per feature bucket)
  |       -> OpenRouter       (200+ models: Gemini Flash, Mistral, GPT-4o-mini)
  |-> AI call (JSON output)   (headline, cta, caption, hashtags, ad copy)
  |-> PosterGenerator         (Template JSON for frontend renderer)
  -> UsageTracker             (Log tokens + cost per tenant)
`

### Supported Countries

| Code | Country | Bilingual Default |
|------|---------|-------------------|
| IN | India | Yes (English + regional language) |
| AU | Australia | English only |
| NZ | New Zealand | English / Te Reo Maori |
| MY | Malaysia | English + Bahasa Malaysia / Chinese |
| SG | Singapore | English + Chinese |
| ID | Indonesia | Bahasa Indonesia |
| TH | Thailand | Thai + English |

India state profiles: Maharashtra, Tamil Nadu, Gujarat, Karnataka, Kerala, West Bengal, Punjab, Rajasthan, Telangana, Delhi, Uttar Pradesh.

### Supported Industries (12)

hospital_clinic, school_education, restaurant_cafe, retail_shop, real_estate, salon_beauty, gym_fitness, digital_agency, pharmacy, coaching_institute, event_management, general_business

### Model Routing (Cost Control)

All agents and services route AI calls through ModelRouter - no more hardcoded gpt-4o:

| Feature Bucket | Default Model (OpenRouter) | vs GPT-4o |
|---------------|--------------------------|-----------|
| text_basic | Gemini Flash 1.5 | ~66x cheaper |
| text_marketing | Gemini Flash 1.5 | ~66x cheaper |
| translation | Mistral 7B Instruct | ~16x cheaper |
| campaign_strategy | GPT-4o-mini | ~7x cheaper |
| chatbot | Gemini Flash 1.5 | ~66x cheaper |

Set OPENROUTER_API_KEY to activate OpenRouter. Falls back to OpenAI direct if not set.

### Creative API Endpoints

`http
POST /api/v1/creatives/generate        - Generate full creative set (locale-aware)
GET  /api/v1/creatives/industries      - 12 industry configs
GET  /api/v1/creatives/locales         - 7 country + state profiles
GET  /api/v1/creatives/cultural-styles - 8 cultural design styles
GET  /api/v1/creatives/plans           - SaaS plan tiers + limits
GET  /api/v1/creatives/usage           - Tenant usage this month
GET  /api/v1/creatives/models          - Model routing assignments (admin)
`

### SaaS Plan Limits

| Plan | Text Gen/mo | Translations/mo | AI Images/mo |
|------|------------|----------------|-------------|
| Starter | 50 | 20 | 0 |
| Pro | 500 | 200 | 20 |
| Agency | 2,000 | 1,000 | 100 |
| Enterprise | Unlimited | Unlimited | Unlimited |

Limits enforced via PlanLimitService. Returns HTTP 402 with clear message when exceeded.

### New Services

| File | Purpose |
|------|---------|
| app/services/model_router.py | Centralized AI model routing |
| app/services/industry_config.py | Industry + locale + cultural style config |
| app/services/creative_service.py | Unified creative generation pipeline |
| app/services/usage_tracking_service.py | Per-tenant AI usage logging |
| app/services/plan_limit_service.py | SaaS plan quota enforcement |
| alembic/versions/009_ai_usage_tracking.py | DB migration: ai_usage_log + tenant_plan_credits |
---

## ðŸ“„ License

This project is licensed under the **MIT License** â€” see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with â¤ï¸ by [SRP AI Digital Marketing](https://srp-ai-digital.com)**

> From an IT recruiter who experienced every pain of manual lead gen, cold outreach, missed follow-ups, and siloed tools â€” SRP Marketing OS was built to solve it all with agentic AI.

> Empowering Indian businesses to market smarter, not harder. ðŸ‡®ðŸ‡³

[Website](https://srp-ai-digital.com) Â· [Documentation](https://docs.srp-marketing.com) Â· [Support](mailto:support@srp-ai-digital.com) Â· [Twitter](https://twitter.com/srp_ai_digital)

---

*SRP Marketing OS â€” Version 1.0.0 Â· March 2026*

</div>
