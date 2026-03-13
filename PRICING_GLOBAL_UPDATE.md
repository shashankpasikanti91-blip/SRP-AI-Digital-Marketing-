# PRICING GLOBAL UPDATE — Phase 14
## SRP Marketing OS — USD Pricing Architecture

**Version:** 14.0.0  
**Date:** March 13, 2026  
**Status:** ✅ Implemented

---

## Summary of Changes

Phase 14 updates the marketing landing page from **INR-only pricing** to **global USD pricing**,
making the platform accessible and understandable to international audiences across 7 countries.

---

## Old vs New Pricing

### Old Pricing (Phase 13 — INR Only)

| Plan | Price (INR) | Positioning |
|------|------------|-------------|
| Starter | ₹0 | Free Forever |
| Growth | ₹1,499/month | Most Popular |
| Professional | ₹3,999/month | Best Value |
| Enterprise | ₹9,999/month | Full Power |

**Problems:**
- Confusing for international users in Malaysia, Indonesia, Thailand, etc.
- INR amounts look large/arbitrary to non-Indian users
- "Made for Indian businesses" tagline was exclusionary
- No indication of multi-country support

---

### New Pricing (Phase 14 — USD Global Default)

| Plan | Price (USD) | Annual (Save 20%) | Notes |
|------|-----------|-------------------|-------|
| Starter | $0 | $0 | Free Forever |
| Growth | $19/month | $15.20/month | Most Popular |
| Professional | $49/month | $39.20/month | Best Value |
| Enterprise | $99/month | $79.20/month | Full Power |

**Improvements:**
- Universal currency understood globally
- Clean, competitive pricing vs. international tools
- Clear note: *"Local taxes and currency conversion may apply depending on your country"*
- Annual billing toggle (save 20%) preserved

---

## Competitive Positioning (USD Comparison)

| Tool | Price | SRP AI Advantage |
|------|-------|-----------------|
| HubSpot | $90/user/month | SRP AI: Full platform for $19/month |
| Salesforce | $150/user/month | SRP AI: All features for $49/month |
| Hootsuite | $39/month | SRP AI: Includes AI + CRM + Analytics |
| Mailchimp | $35/month | SRP AI: 10 AI agents included |
| **Total (4 tools)** | **$314+/month** | **SRP AI replaces all: $19-$49/month** |

**Savings: $480+/year vs running separate tools**

---

## Price as USD — Database Convention

New tenant column `price_usd` stores the USD price for each plan tier.

```sql
-- Added to tenants table (Phase 14 migration)
ALTER TABLE tenants ADD COLUMN price_usd NUMERIC(10,2);
```

### Plan Tier → USD Price Mapping

```python
PLAN_USD_PRICES = {
    "starter": 0.00,
    "growth": 19.00,
    "professional": 49.00,
    "enterprise": 99.00,
}
```

---

## API Endpoint: Pricing in USD

```http
GET /api/v1/localization/pricing-usd
```

**Response:**
```json
{
  "currency": "USD",
  "currency_symbol": "$",
  "note": "Local taxes and currency conversion may apply depending on your country.",
  "plans": [
    { "name": "Starter", "price_usd": 0, "period": "forever", ... },
    { "name": "Growth", "price_usd": 19, "period": "/month", ... },
    { "name": "Professional", "price_usd": 49, "period": "/month", ... },
    { "name": "Enterprise", "price_usd": 99, "period": "/month", ... }
  ]
}
```

---

## Local Currency Reference (Informational)

The following shows approximate local equivalents (for reference only).
**The platform displays USD as the authoritative currency.**

| Plan | USD | INR (approx) | MYR (approx) | IDR (approx) | THB (approx) | SGD (approx) | AUD (approx) |
|------|-----|-------------|-------------|-------------|-------------|-------------|-------------|
| Starter | $0 | ₹0 | RM 0 | Rp 0 | ฿0 | S$0 | A$0 |
| Growth | $19 | ₹1,580 | RM 90 | Rp 300,000 | ฿680 | S$26 | A$29 |
| Professional | $49 | ₹4,075 | RM 231 | Rp 775,000 | ฿1,750 | S$66 | A$75 |
| Enterprise | $99 | ₹8,230 | RM 467 | Rp 1,565,000 | ฿3,550 | S$134 | A$151 |

*Exchange rates are approximate and change daily. Display USD on platform always.*

---

## Landing Page Changes

### Hero Section

**Before:**
```
India's #1 AI Marketing Operating System · Powered by GPT-4o
Built for Indian businesses at prices that make sense.
```

**After:**
```
AI Marketing OS for Local Businesses Worldwide · Powered by GPT-4o
Automate leads, campaigns, bilingual content, local posters & WhatsApp 
marketing — all in one OS. Built for local businesses across 7 countries.
```

### Pricing Section

**Before:**
```
Made for Indian Businesses
All prices in ₹ INR · GST-ready invoices · No dollar conversion
```

**After:**
```
Simple USD Pricing
All prices in USD · Local taxes and currency conversion may apply depending on your country.
```

### Savings Banner

**Before:**
```
You save ₹40,000+/year vs international tools
HubSpot ₹7,200/user/m · Salesforce ₹12,500/user/m...
```

**After:**
```
Save $480+/year vs international tools
HubSpot $90/user/m · Salesforce $150/user/m · SRP AI replaces them all for just $19/m
```

### Stats Bar

**Before:**
```
₹2.4 Cr+ Revenue Generated
```

**After:**
```
7 Countries Supported
```

---

## Footer Changes

**Before:** `Made with ❤️ in India 🇮🇳`  
**After:** `Made with ❤️ for businesses worldwide 🌍`

---

## Files Modified (Pricing Changes)

| File | Change Type |
|------|------------|
| `frontend/src/pages/LandingPage.tsx` | PLANS array → USD prices |
| `frontend/src/pages/LandingPage.tsx` | IndianRupee icon → DollarSign |
| `frontend/src/pages/LandingPage.tsx` | Hero text → global messaging |
| `frontend/src/pages/LandingPage.tsx` | Pricing section title/subtitle |
| `frontend/src/pages/LandingPage.tsx` | Savings banner → USD comparison |
| `frontend/src/pages/LandingPage.tsx` | Testimonials → "Worldwide" |
| `frontend/src/pages/LandingPage.tsx` | Footer → global messaging |
| `backend/app/routers/localization.py` | `/pricing-usd` API endpoint added |
| `backend/alembic/versions/008_global_localization.py` | `price_usd` column on tenants |

---

*Phase 14 — Global Pricing Update*  
*SRP Marketing OS — March 13, 2026*
