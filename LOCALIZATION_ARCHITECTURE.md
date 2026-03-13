# LOCALIZATION ARCHITECTURE — Phase 14
## SRP Marketing OS — Global Localization & Multi-Country Support

**Version:** 14.0.0  
**Date:** March 13, 2026  
**Status:** ✅ Implemented & Active

---

## Overview

Phase 14 introduces a fully additive Global Localization layer to SRP Marketing OS.
The system now supports marketing automation across **7 countries**, **13 languages**,
and auto-generates **bilingual marketing assets** based on country, state, city, industry,
and selected language mode.

> **IMPORTANT:** Phase 14 is purely additive. No existing Phase-13 modules were modified.
> All new functionality wraps and extends existing services.

---

## Architecture Overview

```
SRP Marketing OS (Phase 14)
│
├── Backend
│   ├── app/services/localization_engine.py   ← CORE (NEW - Phase 14)
│   ├── app/routers/localization.py           ← API Router (NEW)
│   ├── app/models/localization.py            ← ORM Models (NEW)
│   └── alembic/versions/008_global_localization.py  ← DB Migration (NEW)
│
├── Frontend
│   ├── src/pages/GlobalLocalization.tsx      ← UI Page (NEW)
│   ├── src/pages/LandingPage.tsx             ← Updated (Global Positioning)
│   └── src/components/layout/Sidebar.tsx     ← Updated (Nav Link Added)
│
└── Documentation
    ├── LOCALIZATION_ARCHITECTURE.md          ← This file
    ├── COUNTRY_LANGUAGE_MAPPING.md
    ├── PRICING_GLOBAL_UPDATE.md
    └── LOCALIZATION_TEST_REPORT.md
```

---

## Core Module: LocalizationEngine

**File:** `backend/app/services/localization_engine.py`

The `LocalizationEngine` class is the central brain of Phase 14. It handles:

| Method | Purpose |
|--------|---------|
| `get_country_config(code)` | Returns country metadata by ISO code |
| `resolve_languages(country, state)` | Resolves primary + secondary language |
| `build_localization_context(...)` | Builds full `LocalizationContext` model |
| `build_campaign_prompt(context, ...)` | Generates AI-ready bilingual campaign prompt |
| `generate_seo_keywords(...)` | Generates localized SEO keyword set |
| `build_whatsapp_status_prompt(...)` | Generates bilingual WhatsApp status prompt |
| `get_poster_layout_spec(context)` | Returns poster layout spec for country/language |
| `get_festival_suggestions(...)` | Returns regional festival campaign suggestions |
| `get_regional_template_suggestions(...)` | Returns template slugs for country/industry |
| `format_currency(amount, code)` | Formats currency in local notation |

---

## Supported Countries

| Code | Country | Currency | Bilingual | Language Modes |
|------|---------|----------|-----------|----------------|
| IN | India | ₹ INR | ✅ | english, local, bilingual |
| MY | Malaysia | RM MYR | ✅ | english, local, bilingual |
| ID | Indonesia | Rp IDR | ✅ | english, local, bilingual |
| TH | Thailand | ฿ THB | ✅ | english, local, bilingual |
| SG | Singapore | S$ SGD | ❌ | english only |
| AU | Australia | A$ AUD | ❌ | english only |
| NZ | New Zealand | NZ$ NZD | ❌ | english only |

---

## Language Mode System

| Mode | Description | Example |
|------|-------------|---------|
| `english` | English-only content | "Free Health Camp" |
| `local` | Local language only | "ఉచిత ఆరోగ్య శిబిరం" |
| `bilingual` | Both languages | "Free Health Camp / ఉచిత ఆరోగ్య శిబిరం" |

---

## Database Schema (Migration 008)

### New Tables

**`countries`** — Country metadata, currency, language config  
**`languages`** — Language registry with ISO codes and scripts  
**`states`** — State-language mapping (critical for India)  
**`localization_rules`** — Configurable rules by country/state/industry  

### Additive Tenant Columns

```sql
ALTER TABLE tenants ADD COLUMN country VARCHAR(5);
ALTER TABLE tenants ADD COLUMN state VARCHAR(100);
ALTER TABLE tenants ADD COLUMN city VARCHAR(100);
ALTER TABLE tenants ADD COLUMN primary_language VARCHAR(40) DEFAULT 'english';
ALTER TABLE tenants ADD COLUMN language_mode VARCHAR(20) DEFAULT 'english';
ALTER TABLE tenants ADD COLUMN price_usd NUMERIC(10,2);
```

---

## API Endpoints (Phase 14)

All endpoints are under prefix: `/api/v1/localization/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/countries` | List all supported countries |
| GET | `/languages` | List all supported languages |
| GET | `/states/{country_code}` | States for a country |
| POST | `/context` | Build full localization context |
| POST | `/seo-keywords` | Generate localized SEO keywords |
| POST | `/campaign-prompt` | Generate bilingual campaign AI prompt |
| POST | `/whatsapp-prompt` | Generate bilingual WhatsApp prompt |
| GET | `/festivals` | Festival campaign suggestions |
| GET | `/poster-layout` | Poster layout specifications |
| GET | `/template-suggestions` | Regional template suggestions |
| POST | `/format-currency` | Currency formatting |
| GET | `/detect-language` | Detect language for country/state |
| GET | `/pricing-usd` | Global USD pricing tiers |
| GET | `/supported-markets` | Full supported markets overview |

---

## Poster Layout System

The poster layout adapts based on country and language mode:

| Layout Style | Condition | Description |
|--------------|-----------|-------------|
| `standard` | English only | Standard single-language layout |
| `bilingual_stack` | Bilingual mode | English on top, local language below |
| `local_primary` | Local-only mode | Local language as primary element |

### Bilingual Poster Structure Example

```
┌─────────────────────────────────────┐
│  [BRAND LOGO]            [BADGE]    │
│                                     │
│  Free Orthopedic Health Camp        │  ← English Headline
│  ఉచిత ఆర్థోపెడిక్ ఆరోగ్య శిబిరం    │  ← Telugu Headline
│                                     │
│  • X-Ray  • Consultation            │  ← Services
│  • ఎక్స్-రే  • సంప్రదింపు          │  ← Services (Telugu)
│                                     │
│  📅 15th - 20th March 2026          │
│  🕐 9 AM - 5 PM                     │
│                                     │
│       [BOOK NOW / ఇప్పుడే బుక్ చేయండి] │  ← Bilingual CTA
│                                     │
│  📞 +91-XXXXXXXXXX  📍 Hyderabad    │
└─────────────────────────────────────┘
```

---

## SEO Localization Example

**Input:** `country=MY, city=Kuala Lumpur, industry=restaurant, mode=bilingual`

**Output:**
```
English Keywords:
- best restaurant in Kuala Lumpur
- top restaurant Kuala Lumpur
- restaurant services Kuala Lumpur
- affordable restaurant Kuala Lumpur

Near-Me Keywords:
- restaurant near me
- best restaurant near me
- restaurant near Kuala Lumpur

Malay Keywords:
- restaurant terbaik di Kuala Lumpur
- kedai makan Kuala Lumpur
- restoran berhampiran Kuala Lumpur
```

---

## WhatsApp Status Bilingual Format

**India (Bilingual — English + Telugu):**
```
🎯 Special Offer Today!

📍 Star Hospital, Hyderabad

💊 Free Health Checkup Camp
✅ Blood Sugar · Cholesterol · ECG

ఈ రోజు ప్రత్యేక ఆఫర్!
⭐ స్టార్ హాస్పిటల్, హైదరాబాద్
🏥 ఉచిత ఆరోగ్య తనిఖీ శిబిరం

📞 Book Now — [phone]
```

---

## Existing Modules — Unchanged

The following Phase-13 modules remain completely unchanged:

- ✅ `language_service.py` — Original bilingual India service
- ✅ `poster_generator.py` — Original poster generation
- ✅ `social_variant_service.py` — Social platform variants
- ✅ All routers: posters, campaigns, content, SEO, WhatsApp
- ✅ All database tables (except additive tenant columns)
- ✅ All AI agents: strategy, content, campaign, etc.
- ✅ Campaign builder
- ✅ Template system

---

## Integration Pattern

Phase 14 uses a **context injection pattern**:

```python
# 1. Build context (auto-resolves language, currency, style)
ctx = LocalizationEngine.build_localization_context(
    country_code="IN",
    state="Telangana",
    city="Hyderabad",
    industry="hospital",
    language_mode="bilingual",
)

# 2. Build AI prompt (feeds into existing AI service)
prompt = LocalizationEngine.build_campaign_prompt(
    context=ctx,
    campaign_type="Free Health Camp",
    org_name="Star Hospital",
)

# 3. Pass to existing AI service (no changes needed)
result = ai_service.generate(prompt)
```

---

*Phase 14 — SRP Marketing OS — Global Localization Architecture*  
*Generated: March 13, 2026*
