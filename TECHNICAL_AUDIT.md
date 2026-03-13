# SRP Marketing OS — Technical Audit Report

**Date:** 2025  
**Scope:** Full-stack audit of `ai-marketing-os` — all frontend pages, backend routers, services, models, schemas, and Alembic migrations.  
**Stack:** React 18 + TypeScript (Vite) · FastAPI + SQLAlchemy 2 (async) · PostgreSQL · Redis/Celery · pydantic-ai

---

## Summary Severity Table

| # | Severity | Module | Issue |
|---|----------|--------|-------|
| 1 | 🔴 CRITICAL | LinkedIn | Double `/api/v1` prefix — all LinkedIn calls are always 404 |
| 2 | 🔴 CRITICAL | Email | Backend returns plain list, frontend expects paginated — email list always empty |
| 3 | 🔴 CRITICAL | Analytics | Frontend and backend `AnalyticsOverview` fields completely mismatched — all KPIs show 0 |
| 4 | 🔴 CRITICAL | Analytics | `Analytics.tsx` reads `overview?.stats` but backend returns `overview.overview` — key does not exist |
| 5 | 🔴 CRITICAL | Settings router | `settings.py` router exists but is **never registered** in `main.py` — all `/settings/*` calls return 404 |
| 6 | 🟠 HIGH | Social Calendar | Frontend sends `{ year, month }`, backend expects `from_date` / `to_date` — calendar always fails |
| 7 | 🟠 HIGH | WhatsApp Status | Missing trailing slash on POST and GET to `/social` — FastAPI may 307-redirect POSTs causing data loss |
| 8 | 🟠 HIGH | CRM | "New Deal" button has no handler — deals cannot be created from the UI |
| 9 | 🟠 HIGH | Email | Send button always passes `recipients: []` — emails are always sent to zero recipients |
| 10 | 🟠 HIGH | Settings | "Change Password" and "Regenerate API Key" buttons have no `onClick` — dead UI |
| 11 | 🟠 HIGH | Settings | Settings page does not call `GET /settings/` — API key, plan, and preferences are never loaded |
| 12 | 🟠 HIGH | Business Profile | `POST /business/` returns 400 if profile exists — no upsert logic, frontend must detect and switch to PATCH |
| 13 | 🟡 MEDIUM | Email | Frontend `EmailCampaign` type uses `sent_count` / `opened_count` / `clicked_count` — backend model columns are `total_sent` / `total_opened` / `total_clicked` |
| 14 | 🟡 MEDIUM | Campaign Status | Frontend `CampaignStatus` contains `'archived'`, backend `campaign.py` `CampaignStatus` enum has `'cancelled'` not `'archived'` (email_campaign.py does have `ARCHIVED` — two different enums both named `CampaignStatus`) |
| 15 | 🟡 MEDIUM | `/auth/me` | Frontend `Tenant` type has 7 fields; backend `TenantProfile` returns 13 — extra fields silently dropped |
| 16 | 🟡 MEDIUM | BrandSettings | `BrandProfileForm` TypeScript interface is missing `background_color` and `text_color` fields that exist in backend schema and DB |
| 17 | 🟡 MEDIUM | SEO Tools | `auditMutation` and `localSEOMutation` return 100% hardcoded mock data — no real backend logic exists |
| 18 | 🟡 MEDIUM | Followups | `enrolled_count` field is never incremented anywhere in the backend — always shows 0 |
| 19 | 🟢 LOW | CRM | `crmApi.list()` expects `PaginatedResponse<CRMDeal>` but backend `GET /crm/` returns plain `list[CRMResponse]` — `data?.items` likely undefined in non-kanban views |
| 20 | 🟢 LOW | CampaignBuilder | `org_name` field UI is not auto-populated from BrandSettings — user must re-enter it every time |
| 21 | 🟢 LOW | Conversations | `conversationsApi.addMessage` passes `sender_role: 'assistant'` but backend `MessageCreate` schema expects field named `role` — confirmed mapped correctly in `api.ts`; not broken but fragile |
| 22 | 🟢 LOW | Config | `OPENAI_API_KEY: str = ""` — empty string default; all AI features silently fail instead of returning a clear error if the key is not set in environment |

---

## 1. Dashboard Module

**File:** `frontend/src/pages/Dashboard.tsx`  
**Backend:** `backend/app/services/analytics_service.py`, `backend/app/schemas/analytics.py`

### BUG 🔴 — KPI field names mismatch (all stats show 0 or undefined)

`Dashboard.tsx` reads:
```
overview.total_leads            → ✅ matches
overview.leads_this_month       → ❌ backend has NO such field
overview.revenue_this_month     → ❌ backend has NO such field
overview.revenue_growth_pct     → ❌ backend has NO such field
overview.active_deals           → ❌ backend has NO such field
overview.won_deals              → ❌ backend has NO such field
overview.posts_published        → ❌ backend returns posts_scheduled
overview.emails_sent            → ❌ backend returns emails_sent_today
overview.avg_open_rate          → ❌ backend has NO such field
```

Backend `AnalyticsOverview` schema (`schemas/analytics.py` lines 8–17):
```python
total_leads: int
new_leads_today: int
total_pipeline_value: int   # ← no revenue_this_month
conversion_rate: float
active_campaigns: int        # ← no active_deals
posts_scheduled: int         # ← not posts_published
emails_sent_today: int       # ← not emails_sent
```

Every KPI card on the Dashboard except `total_leads` and `conversion_rate` renders `undefined` / `NaN`.

---

## 2. Analytics Module

**File:** `frontend/src/pages/Analytics.tsx`  
**Backend:** `backend/app/routers/analytics.py`, `backend/app/services/analytics_service.py`

### BUG 🔴 — Wrong nested key access

`Analytics.tsx` calls `api.get('/analytics/overview')` and then reads:
```ts
overview?.stats?.total_leads        // line ~39
stats.qualified_leads
stats.pipeline_value
```

Backend `AnalyticsOverviewResponse` (schema line 50–57) structure is:
```json
{
  "overview": { "total_leads": ..., "new_leads_today": ..., ... },
  "leads_trend": [...],
  "funnel": [...],
  "platform_stats": [...],
  "email_stats": [...]
}
```

There is **no `stats` key** in the response. Correct access would be `overview?.overview?.total_leads`.  
Additionally, `Analytics.tsx` reads `leadsTrend?.trend` but backend key is `leads_trend`. Reads `funnel?.funnel` but backend key is `funnel` (a plain array). Reads `socialStats?.platforms` but backend key is `platform_stats`.

### BUG 🟡 — Using raw `api.get()` instead of typed `analyticsApi`

`Analytics.tsx` bypasses `analyticsApi.overview()` and calls `api.get('/analytics/overview')` directly, returning `any`. This loses all compile-time type safety.

---

## 3. Leads Module

**File:** `frontend/src/pages/Leads.tsx`  
**Backend:** `backend/app/routers/leads.py`

**Status: WORKING.** Full CRUD, AI scoring (`POST /leads/{id}/score`), CSV import/export, bulk update, stats summary — all endpoints exist and match frontend calls.  

Minor: `leadsApi.score(id)` calls `POST /leads/{id}/score` — endpoint exists at `leads.py` line ~165.

---

## 4. CRM Module

**File:** `frontend/src/pages/CRM.tsx`  
**Backend:** `backend/app/routers/crm.py`

### BUG 🔴 — "New Deal" button is dead

`CRM.tsx` renders a `<button>New Deal</button>` with no `onClick` handler. Clicking it does nothing. There is no modal, form, or mutation for creating a deal from the UI. The kanban board cannot be populated via the UI.

### BUG 🟡 — `crmApi.list()` expects pagination, backend returns plain list

`api.ts` `crmApi.list()` expects `PaginatedResponse<CRMDeal>` (accesses `.items`).  
Backend `GET /crm/` returns `list[CRMResponse]` (no wrapping object, no `items` key).  
Any list-view outside of kanban will show empty results.

### OK — Kanban works

`crmApi.kanban()` calls `GET /crm/kanban` which returns `{ columns: [...] }` — correctly consumed by `CRM.tsx` as `data?.columns ?? []`.

---

## 5. Social Scheduler

**File:** `frontend/src/pages/Social.tsx`  
**Backend:** `backend/app/routers/social.py`

### BUG 🟠 — Calendar parameter mismatch

`api.ts` `socialApi.calendar(year, month)` sends: `GET /social/calendar?year=2025&month=7`  
Backend `social.py` `GET /social/calendar` expects query params: `from_date: date` and `to_date: date`  
The backend will receive `year` and `month` as unknown params and use its defaults, returning wrong or empty data.

**Fix:** Either send `from_date=2025-07-01&to_date=2025-07-31` from the frontend, or update the backend to accept `year` and `month`.

### Minor — Social create modal missing platforms

The create modal only lists Facebook / Instagram / LinkedIn. The `SocialPost` type and backend model support `twitter`, `youtube`, `whatsapp` as valid platforms.

---

## 6. WhatsApp Status Module

**File:** `frontend/src/pages/WhatsAppStatus.tsx`  
**Backend:** `backend/app/routers/social.py`

### BUG 🟠 — Missing trailing slash on all API calls

`WhatsAppStatus.tsx` uses:
- `api.get('/social', ...)` — should be `/social/`
- `api.post('/social', ...)` — should be `/social/`

FastAPI returns `307 Temporary Redirect` for missing trailing slashes. Browsers/Axios will redirect GET requests but **will drop POST body** on redirect. Create post will fail silently or send empty payload.

**Affected lines:** approximately lines 108 and 120 of `WhatsAppStatus.tsx`.

### OK — `campaign` field used as title

`WhatsAppStatus.tsx` uses `post.campaign` as the display title. The `SocialPost` model (`models/social.py` line ~25) has `campaign: Mapped[str | None] = mapped_column(String(120))`. This is valid.

---

## 7. Email Campaigns Module

**File:** `frontend/src/pages/Email.tsx`  
**Backend:** `backend/app/routers/email_campaigns.py`

### BUG 🔴 — Email list always empty

`emailApi.list()` in `api.ts` calls `GET /email/campaigns/` and expects:
```ts
PaginatedResponse<EmailCampaign>  // { items: [...], total: N, page: 1, page_size: 20 }
```

Backend `GET /email/campaigns/` returns:
```python
list[EmailCampaignResponse]  # plain array, no wrapper object
```

`Email.tsx` accesses `data?.items ?? []` — because `.items` does not exist, the list is always an empty array. **The entire email campaigns page shows no campaigns at all.**

### BUG 🔴 — Send always delivers to zero recipients

`Email.tsx` calls `emailApi.send(c.id, [])` — hardcoded empty recipients array at every send invocation. No UI for selecting recipients. Emails are technically queued but sent to nobody.

### BUG 🟡 — Field name mismatch in EmailCampaign type

Frontend `types/index.ts` `EmailCampaign` interface (if it defines stat fields) uses `sent_count`, `opened_count`, `clicked_count`.  
Backend `EmailCampaign` model (`models/email_campaign.py` lines 40–43) columns are named `total_sent`, `total_opened`, `total_clicked`, `total_unsubscribed`.  
Any stats columns rendered from the list response will be `undefined`.

---

## 8. Content Generator

**File:** `frontend/src/pages/ContentGenerator.tsx`  
**Backend:** `backend/app/routers/content.py`

**Status: FUNCTIONALLY WORKING.**

`contentApi.generate(form)` → `POST /content/generate` → returns `{ content: {...}, saved_count: N }`.  
Frontend reads `res.content` then renders `result.headline`, `result.primary_copy`, `result.variants` — matches `ContentAgent` output shape.

No critical issues. Minor: no loading indicator for the time the AI agent takes to respond (can be 10–30s).

---

## 9. Campaign Builder (Poster Generation)

**File:** `frontend/src/pages/CampaignBuilder.tsx`  
**Backend:** `backend/app/routers/posters.py`, `backend/app/services/poster_generator.py`

**Status: FUNCTIONALLY WORKING** — core flow works end-to-end.

### Minor — `org_name` not auto-populated from BrandSettings

Step 1 of the wizard includes an `org_name` field. It is not pre-populated from the existing `BrandProfile`. User must type it manually every time, even if their brand is already configured.

### Minor — No error feedback on template step

If `GET /posters/templates` returns 0 templates (e.g. no brand profile exists yet), the template selection step renders an empty grid with no guidance.

---

## 10. Poster Preview / Gallery

**File:** `frontend/src/pages/PosterPreview.tsx`  
**Backend:** `backend/app/routers/posters.py`

**Status: WORKING.** Fetches `GET /posters/variants`, handles both response shapes (`r.data?.variants ?? r.data ?? []`). Delete via `DELETE /posters/variants/{id}` works.

---

## 11. Brand Settings

**File:** `frontend/src/pages/BrandSettings.tsx`  
**Backend:** `backend/app/routers/posters.py` (`POST /posters/brand-profile`)

### BUG 🟡 — Missing fields in TypeScript interface

The `BrandProfileForm` TypeScript interface in `BrandSettings.tsx` is missing:
- `background_color` (exists in `BrandProfile` DB model `models/brand_profile.py` line 36, and in migration 007)
- `text_color` (exists in `BrandProfile` DB model line 37)

Both fields are registered with `{...register('background_color')}` in the JSX (the form still works via `register` duck-typing), but TypeScript will complain and IntelliSense will miss them.

### Minor — No distinction between create (201) and update responses

`POST /posters/brand-profile` always runs — backend upserts and returns 200 or 201. Frontend treats both as success. Not broken, but the toast message always says "saved" even on initial creation.

---

## 12. SEO Tools

**File:** `frontend/src/pages/SEOTools.tsx`  
**Backend:** `backend/app/routers/ai_assistant.py`

### BUG 🟡 — SEO Audit is entirely hardcoded mock data

`auditMutation` (approximately lines 150–175 of `SEOTools.tsx`) never calls any backend endpoint — it calls `setTimeout` and returns a hardcoded JavaScript object with fake scores, issues, and recommendations. **There is no real SEO audit functionality.**

### BUG 🟡 — Local SEO is entirely hardcoded mock data

`localSEOMutation` (approximately lines 178–225) similarly returns a hardcoded list of directories and a static schema template. No backend call is made.

### Workaround in production

Keyword research (`keywordsMutation`), meta tags (`metaMutation`), and title suggestions (`titlesMutation`) all call `POST /ai/generate-post` with `platform: 'seo'` as a prompt workaround — these actually call the backend and work.

**No `/seo/*` backend routes exist.** The two mock tabs need real backend implementation or clear "coming soon" UI treatment.

---

## 13. LinkedIn Module

**File:** `frontend/src/pages/LinkedIn.tsx`  
**Backend:** `backend/app/routers/linkedin.py`

### BUG 🔴 — Double `/api/v1` prefix — all calls are 404

`LinkedIn.tsx` mutations call `api.post('/api/v1/linkedin/job-post', ...)`, `api.post('/api/v1/linkedin/outreach-message', ...)`, etc.

`api` axios instance has `baseURL = VITE_API_URL ?? '/api/v1'` — already contains the prefix.

Resulting actual URLs:
```
/api/v1/api/v1/linkedin/job-post           → 404
/api/v1/api/v1/linkedin/outreach-message   → 404
/api/v1/api/v1/linkedin/hiring-announcement → 404
/api/v1/api/v1/linkedin/company-post       → 404
```

Correct calls should be `api.post('/linkedin/job-post', ...)`.

**Every LinkedIn feature is permanently broken.** No error surfaced in UI because 404s are caught generically.

---

## 14. AI Assistant

**File:** `frontend/src/pages/AIAssistant.tsx`  
**Backend:** `backend/app/routers/ai_assistant.py`

**Status: WORKING.** All 5 tab operations use correct relative paths:
- `api.post('/ai/generate-post', ...)` ✅
- `api.post('/ai/classify-lead', ...)` ✅
- `api.post('/ai/reply-suggestion', ...)` ✅
- `api.post('/ai/write-email', ...)` ✅
- `api.post('/ai/campaign-ideas', ...)` ✅

Advanced endpoints (`/ai/chat`, `/ai/content-calendar`, `/ai/seo-keywords`, `/ai/ab-test`) exist in the backend but are not exposed in the UI.

---

## 15. Conversations Module

**File:** `frontend/src/pages/Conversations.tsx`  
**Backend:** `backend/app/routers/conversations.py`

**Status: WORKING.**

- `ConversationMessage` type in `types/index.ts` (lines ~330–340) correctly includes `ai_generated: boolean`.
- Backend `MessageCreate` schema (`conversations.py` line ~21) includes `ai_generated: bool = False`.
- `conversationsApi.addMessage` payload mapping in `api.ts` is consistent.
- Messages render check `msg.role === 'assistant' || msg.ai_generated` — both fields exist and are typed correctly.

---

## 16. Followups Module

**File:** `frontend/src/pages/Followups.tsx`  
**Backend:** `backend/app/routers/followups.py`

### BUG 🟡 — `enrolled_count` is never incremented

`FollowupSequence` type (`types/index.ts` lines ~358–372) includes `enrolled_count: number` and the backend model has this column (default 0). However, no code in any router or worker ever increments `enrolled_count` when a lead is enrolled in a sequence. It will always show 0.

### OK — `ai_generated_json` typing is correct

`FollowupSequence.ai_generated_json.steps` is properly typed as `AiFollowupStep[]` in `types/index.ts` lines ~362–368, matching the `output.model_dump()` saved in `followups.py` line ~87.

---

## 17. Settings

**File:** `frontend/src/pages/Settings.tsx`  
**Backend:** `backend/app/routers/settings.py`

### BUG 🔴 — Settings router never registered

`backend/app/routers/settings.py` exists (full `GET /settings/`, `PATCH /settings/`, `GET /settings/integrations`).  
`backend/app/main.py` does **not** import or register it. All `/settings/*` routes return `404 Not Found`.

### BUG 🟠 — Settings page makes no API calls

`Settings.tsx` does not call `GET /settings/` on mount. API key, plan, notification preferences, and integration toggles are never fetched. The page shows a static shell.

### BUG 🟠 — Dead buttons

- **"Change Password"** button (~line 85): no `onClick` handler
- **"Regenerate API Key"** button (~line 88): no `onClick` handler

Backend `GET /settings/` returns `{ settings, plan, api_key, webhook_url }` — the data exists but is never fetched or displayed.

---

## 18. Auth Module

**File:** `frontend/src/store/auth.ts`, `frontend/src/services/api.ts`  
**Backend:** `backend/app/routers/auth.py`

### BUG 🟡 — `/auth/me` response mismatch

Frontend `authApi.me()` is typed to return `Tenant` (7 fields: `id, name, slug, email, plan, api_key, created_at`).  
Backend `GET /auth/me` returns `TenantProfile` (13 fields including `company_name, website, phone, timezone, logo_url, settings`).  

Extra fields are present in the response but silently dropped. Not breaking but `company_name`, `timezone`, and `logo_url` are available for display and never used by the frontend.

---

## 19. Campaigns Module

**File:** `frontend/src/pages/Campaigns.tsx`  
**Backend:** `backend/app/routers/campaigns.py`

### BUG 🟡 — CampaignStatus value 'archived' vs 'cancelled'

Frontend `CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'archived'` (`types/index.ts` line ~290).  
Backend `Campaign.CampaignStatus` enum (`models/campaign.py`): `draft, active, paused, completed, cancelled`.  

There is no `archived` status in the campaign model. `Campaigns.tsx` `STATUS_COLORS` record has an `'archived'` key that will never match any backend value. The `'cancelled'` status from backend has no color entry.

Note: `EmailCampaign.CampaignStatus` in `models/email_campaign.py` DOES have `ARCHIVED` — these are two separate enums with the same Python name, causing confusion.

---

## 20. Business Profile Module

**File:** `frontend/src/pages/Business.tsx`  
**Backend:** `backend/app/routers/business.py`

### BUG 🟠 — POST returns 400 if profile exists

`POST /business/` (`business.py` line ~67): if a `BusinessProfile` record already exists for the tenant, it raises `HTTPException(status_code=400)`.  
Unless the frontend checks for existing profile first and routes to `PATCH /business/`, repeat visits to the onboarding flow will error.

---

## 21. Database / Migrations

**Files:** `backend/alembic/versions/001–007`

### OK — Migration 007 is complete

All `brand_profiles`, `poster_templates`, `poster_variants` tables are created with the correct columns matching the SQLAlchemy models.

### Gap — No `settings` column migration for `tenants`

Migration 001 creates the `tenants` table. The `settings.py` router reads/writes `tenant.settings` (a JSON text column). Confirm `tenants.settings` column exists in migration 001 — if it was added in a later ad-hoc migration or directly to the DB, a fresh deployment will fail with a column not found error on `GET /settings/`.

### Gap — `enrolled_count`, `completed_count`, `reply_count` on `followup_sequences`

These fields are accessed by the frontend. Verify they are present in the `followup_sequences` migration (004 or later) — they are not added by any migration visibly in 007.

---

## 22. Worker / Celery

**Directory:** `backend/app/workers/`

Not audited in full detail, but note:
- Email sending via workers is wired for background jobs, but the email campaigns router `POST /email/campaigns/{id}/send` receives recipients from the request body — the frontend always passes `[]`.
- Social scheduling workers exist in `social_worker.py` but scheduled posts are never triggered via the UI (only `publish` via `socialApi.publish(id)` exists in the frontend).

---

## 23. Config & Environment

**File:** `backend/app/config.py`

### Risk — `OPENAI_API_KEY` defaults to empty string

```python
OPENAI_API_KEY: str = ""  # line ~12
```

If the key is missing from `.env`, **all AI features fail silently** — pydantic-ai will raise an `AuthenticationError` at agent run time. No startup check or 503 early exit.

### Risk — Social platform tokens default to empty string

`FACEBOOK_ACCESS_TOKEN`, `INSTAGRAM_ACCESS_TOKEN`, `LINKEDIN_ACCESS_TOKEN` all default to `""`. Social publishing to real platforms will silently fail. The `GET /settings/integrations` endpoint correctly returns `connected: false` for these, but no UI warning is shown.

---

## Fixes Summary (Priority Order)

### Immediate — Fix in < 1 day

1. **LinkedIn double prefix** — Remove `/api/v1` from all `api.post()` calls in `LinkedIn.tsx`  
2. **Email list pagination** — Either wrap backend response in `{ items, total, page, page_size }` OR update frontend `emailApi.list()` to handle plain array  
3. **Settings router missing** — Add `from app.routers import settings` and `app.include_router(settings.router, prefix=api_prefix)` to `main.py`  
4. **Analytics field names** — Align `types/index.ts` `AnalyticsOverview` with backend schema fields (`new_leads_today`, `total_pipeline_value`, `active_campaigns`, `posts_scheduled`, `emails_sent_today`)  

### Short-term — Fix in < 3 days

5. **Analytics.tsx wrong key** — Change `overview?.stats` to `overview?.overview` throughout `Analytics.tsx`  
6. **Social calendar params** — Update `socialApi.calendar(year, month)` to compute `from_date` / `to_date` date strings before sending  
7. **WhatsApp trailing slash** — Add trailing slash to `/social` calls in `WhatsAppStatus.tsx`  
8. **CRM New Deal UI** — Implement create-deal modal with `crmApi.create()` wired to the button  
9. **Email recipients** — Add recipient email selector to Email.tsx send modal  
10. **Settings page** — Load data from `GET /settings/` on mount; implement Change Password and Regenerate API Key mutations  

### Medium-term — Fix in < 1 week

11. **EmailCampaign field names** — Rename frontend `sent_count` → `total_sent`, `opened_count` → `total_opened`, `clicked_count` → `total_clicked` in `types/index.ts`  
12. **CampaignStatus enum** — Add `'cancelled'` to frontend `CampaignStatus` type; remove `'archived'` from campaign STATUS_COLORS (keep for email campaigns)  
13. **SEO audit** — Replace hardcoded mock with a real `POST /ai/seo-audit` backend endpoint or display "coming soon"  
14. **Business profile upsert** — Change `Business.tsx` to detect existing profile (try `GET /business/`, use PATCH if 200, POST if 404)  
15. **`enrolled_count` tracking** — Increment `FollowupSequence.enrolled_count` in the followup enrollment logic  
16. **`BrandProfileForm` interface** — Add `background_color` and `text_color` to the TypeScript interface  
17. **OPENAI_API_KEY guard** — Add startup health check that warns if key is empty  
