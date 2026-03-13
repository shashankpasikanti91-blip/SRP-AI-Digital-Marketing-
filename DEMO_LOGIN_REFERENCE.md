# Demo Login Reference — SRP AI Marketing OS

**Version**: 1.0  
**Date**: 2025-01-25

---

## Quick Access

| Environment | URL |
|-------------|-----|
| Frontend (Dev) | http://localhost:5173/ |
| Backend API | http://localhost:8000/ |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

---

## Demo Accounts

### Account 1 — SRP Marketing Agency (General)
> Multi-industry marketing agency demo with rich campaign data

| Field | Value |
|-------|-------|
| **Email** | `demo@srp.ai` |
| **Password** | `Demo@12345` |
| **Slug** | `srp-demo` |
| **Business Type** | Marketing Agency |
| **Industry** | Multi-industry |

**Sample Data Includes:**
- 12 leads across all stages (hot/warm/cold) with AI scores
- 5 campaigns (Active, Paused, Draft, Completed)
- Industries: Tech, Real Estate, E-commerce, FinTech, Restaurants, Education
- Locations: Mumbai, Delhi, Bengaluru, Hyderabad, Pune, Chennai, Ahmedabad

**Seed Script:** `cd backend && python seed_demo.py`

---

### Account 2 — Bunty Healthcare Marketing
> Healthcare-specific demo for medical industry vertical

| Field | Value |
|-------|-------|
| **Email** | `bunty@srp.ai` |
| **Password** | `Bunty@12345` |
| **Slug** | `bunty-demo` |
| **Business Type** | Healthcare Marketing Agency |
| **Industry** | Healthcare / Medical |

**Sample Data Includes:**
- 12 healthcare leads (doctors, hospitals, clinics, pharmacies)
- 5 healthcare campaigns (Patient Acquisition, Brand Awareness, Procedure Promotion)
- Industries: Multi-specialty Hospital, Dental, Eye Care, Cardiology, Pharmacy, Fitness, Ayurveda
- Locations: Mumbai, Chennai, Hyderabad, Kolkata, Lucknow, Kochi, Ahmedabad

**Seed Script:** `cd backend && python seed_bunty.py`

---

### Account 3 — Star Hospitals (Real Project Demo)
> Full hospital marketing department demo

| Field | Value |
|-------|-------|
| **Email** | `admin@starhospital.in` |
| **Password** | `Star@12345` |
| **Slug** | `star-hospital` |
| **Business Type** | Multi-specialty Hospital |
| **Industry** | Healthcare |
| **Location** | Hyderabad, India |

**Sample Data Includes:**
- Complete hospital marketing setup
- Department-specific campaigns
- Doctor profiles and appointment promotions
- WhatsApp status templates for healthcare
- Social media content calendar

**Seed Script:** `cd backend && python seed_star_hospital.py`

---

## How to Seed Demo Data

### Prerequisites
- Backend container must be running OR backend Python environment configured
- Database must be up and migrated

### Option A — With Docker (Recommended)
```bash
# Seed demo@srp.ai account
docker exec -it ai-marketing-os-backend-1 python seed_demo.py

# Seed bunty@srp.ai account
docker exec -it ai-marketing-os-backend-1 python seed_bunty.py

# Seed Star Hospital account
docker exec -it ai-marketing-os-backend-1 python seed_star_hospital.py
```

### Option B — Direct Python
```bash
cd backend
pip install -r requirements.txt
python seed_demo.py
python seed_bunty.py
python seed_star_hospital.py
```

---

## Feature Coverage by Account

| Feature | demo@srp.ai | bunty@srp.ai | admin@starhospital.in |
|---------|-------------|----------|---------------------|
| Dashboard KPIs | ✅ | ✅ | ✅ |
| Lead Pipeline | ✅ 12 leads | ✅ 12 leads | ✅ |
| CRM Kanban | ✅ | ✅ | ✅ |
| Campaigns | ✅ 5 campaigns | ✅ 5 campaigns | ✅ |
| Social Posts | ✅ | ✅ | ✅ |
| WhatsApp Templates | ✅ General | ✅ Healthcare | ✅ Medical |
| Email Campaigns | ✅ | ✅ | ✅ |
| AI Poster Gen | ✅ | ✅ Healthcare | ✅ |
| Analytics Charts | ✅ | ✅ | ✅ |
| LinkedIn Tools | ✅ | ✅ | ✅ |

---

## Login Flow

1. Navigate to http://localhost:5173/
2. You will be redirected to `/login`
3. Enter email and password from above
4. Click "Sign In"
5. JWTaccess token is stored in localStorage and Zustand store
6. Auto-redirected to Dashboard

### Session Management
- JWT expires after the configured `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60 minutes)
- On expiry, user is automatically redirected to login with "Session expired" message
- No persistent refresh token in current implementation — users must re-login after expiry

---

## API Authentication (for Postman / curl)

```bash
# Step 1: Login → get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@srp.ai", "password": "Demo@12345"}'

# Response:
# { "access_token": "eyJ...", "token_type": "bearer", "tenant": {...} }

# Step 2: Use token in all subsequent calls
curl http://localhost:8000/api/v1/leads/ \
  -H "Authorization: Bearer eyJ..."
```

---

## Resetting Demo Data

To wipe and re-seed a demo account:
```bash
# Connect to PostgreSQL
psql -h localhost -p 5434 -U ats_user -d srp_marketing

# Delete tenant (cascades to all data)
DELETE FROM tenants WHERE email = 'demo@srp.ai';

# Re-seed
python backend/seed_demo.py
```

---

*Demo Login Reference — SRP AI Digital Marketing OS*
