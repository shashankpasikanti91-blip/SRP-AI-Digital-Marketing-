#!/usr/bin/env python3
"""
Bunty Demo Account Seeder — SRP AI Marketing OS
Creates bunty@srp.ai / Bunty@12345 with healthcare/medical industry data.

Usage:
    cd backend
    python seed_bunty.py
"""
import asyncio, sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password, generate_api_key
from app.models.tenant import Tenant
from app.models.lead import Lead, LeadStatus
from app.models.business_profile import BusinessProfile
from app.models.campaign import Campaign, CampaignStatus
from app.models.conversation import (Conversation, ConversationMessage,
                                     ConversationChannel, ConversationStatus)
from app.models.followup import FollowupSequence, FollowupStep, SequenceStatus

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

BUNTY_EMAIL    = "bunty@srp.ai"
BUNTY_PASSWORD = "Bunty@12345"
BUNTY_SLUG     = "bunty-demo"

LEADS = [
    dict(name="Dr. Ramesh Verma",    email="ramesh@cityhospital.in",   phone="+91-98001-11001", company="City Multi-Specialty Hospital",  source="google_ads",    status=LeadStatus.QUALIFIED, ai_score=93, ai_label="hot",  notes="50-bed hospital. Marketing budget Rs 3L/yr. Interested in patient acquisition. Lucknow."),
    dict(name="Sunita Agarwal",      email="sunita@smiledentalclinic.in", phone="+91-98001-11002", company="Smile Dental Clinic",         source="instagram_ad",  status=LeadStatus.CONTACTED, ai_score=78, ai_label="warm", notes="5 clinics across Jaipur. Rs 1.5L/yr budget. Wants appointment reminders + ads."),
    dict(name="Dr. Kavitha Pillai",  email="kavitha@visioneye.in",     phone="+91-98001-11003", company="Vision Eye Care Centre",         source="referral",      status=LeadStatus.QUALIFIED, ai_score=87, ai_label="hot",  notes="Eye specialist. 3 locations. LASIK promotion. Chennai."),
    dict(name="Pooja Shah",          email="pooja@heartplus.in",       phone="+91-98001-11004", company="Heart Plus Cardiology",          source="linkedin",      status=LeadStatus.CONTACTED, ai_score=72, ai_label="warm", notes="Cardiac centre. Digital OPD promotion. Surat."),
    dict(name="Suresh Nair",         email="suresh@lifepharmacy.com",  phone="+91-98001-11005", company="Life Pharmacy Chain",            source="facebook_ad",   status=LeadStatus.NEW,       ai_score=55, ai_label="warm", notes="15 pharmacy stores. Wants festive offer posters. Kochi."),
    dict(name="Dr. Amrita Bose",     email="amrita@motherhoodcare.in", phone="+91-98001-11006", company="Motherhood Care Hospital",       source="website_form",  status=LeadStatus.QUALIFIED, ai_score=90, ai_label="hot",  notes="Maternity hospital. Rs 2L/yr. Instagram + Google campaigns. Kolkata."),
    dict(name="Rakesh Tiwari",       email="rakesh@fitnesspulse.in",   phone="+91-98001-11007", company="Fitness Pulse Gym",              source="instagram_ad",  status=LeadStatus.CONTACTED, ai_score=62, ai_label="warm", notes="Chain of 3 gyms. Membership drive. Rs 80K/yr. Bhopal."),
    dict(name="Ananya Krishnan",     email="ananya@ayurvitacare.com",  phone="+91-98001-11008", company="AyurVita Wellness",              source="whatsapp",      status=LeadStatus.NEW,       ai_score=44, ai_label="cold", notes="Ayurveda & yoga centre. Small budget. Wants WhatsApp campaigns. Trivandrum."),
    dict(name="Vikram Joshi",        email="vikram@dentalfirst.in",    phone="+91-98001-11009", company="Dental First Super Speciality",  source="google_ads",    status=LeadStatus.QUALIFIED, ai_score=85, ai_label="hot",  notes="Super-speciality dental. Rs 2.5L/yr. Implant promotion. Hyderabad."),
    dict(name="Meena Desai",         email="meena@skincareclinic.in",  phone="+91-98001-11010", company="Glow Skin & Hair Clinic",        source="instagram_ad",  status=LeadStatus.CONTACTED, ai_score=70, ai_label="warm", notes="Dermatology + cosmetic treatments. Summer package. Ahmedabad."),
    dict(name="Dr. Sunil Kapoor",    email="sunil@orthocare.in",       phone="+91-98001-11011", company="OrthoCare Orthopaedic Hospital", source="referral",      status=LeadStatus.CONVERTED, ai_score=96, ai_label="hot",  notes="Paying Growth plan. Joint replacement specialist. Mumbai."),
    dict(name="Preethi Sundaram",    email="preethi@petclinicplus.in", phone="+91-98001-11012", company="PetClinic Plus",                 source="facebook_ad",   status=LeadStatus.NEW,       ai_score=38, ai_label="cold", notes="Veterinary clinic. New to digital marketing. Coimbatore."),
]

CAMPAIGNS = [
    dict(name="Monsoon Health Check-up Drive",        objective="Patient Acquisition",    channels=["instagram","facebook","whatsapp"], budget_total=45000, status=CampaignStatus.ACTIVE,   target_audience="Adults 30-60, urban, health-conscious", leads_generated=67, impressions=42000, clicks=3100, conversions=28),
    dict(name="Free Eye Camp – August",               objective="Brand Awareness + OPD",  channels=["facebook","google_ads"],          budget_total=30000, status=CampaignStatus.ACTIVE,   target_audience="Senior citizens 55+, suburbs", leads_generated=41, impressions=28000, clicks=1900, conversions=19),
    dict(name="Dental Implant Awareness Month",       objective="Procedure Promotion",     channels=["instagram","email"],              budget_total=55000, status=CampaignStatus.PAUSED,   target_audience="Adults 25-55 with dental concerns", leads_generated=33, impressions=19500, clicks=2200, conversions=14),
    dict(name="Fitness Membership – New Year Push",   objective="Lead Generation",         channels=["instagram","facebook"],           budget_total=20000, status=CampaignStatus.DRAFT,    target_audience="Youth 18-35, urban gyms", leads_generated=0, impressions=0, clicks=0, conversions=0),
    dict(name="Pharmacy Festive Offer – Diwali",      objective="Retail Sales",            channels=["whatsapp","facebook"],            budget_total=15000, status=CampaignStatus.COMPLETED,target_audience="Existing patients & walk-ins", leads_generated=210, impressions=51000, clicks=4800, conversions=195),
]

CONVS = [
    dict(ci="+91-98001-11001", cn="Dr. Ramesh Verma",   ch=ConversationChannel.WHATSAPP, st=ConversationStatus.OPEN,     lp="When can we schedule the onboarding call?",
         msgs=[("user","Hello, I want to market my hospital on Instagram and Google.", False),
               ("assistant","Hi Dr. Ramesh! Great choice. Let me create a tailored campaign plan for City Multi-Specialty Hospital focusing on patient acquisition. Shall I start with an Instagram health awareness campaign?", True),
               ("user","Yes, also need help with appointment reminders.", False),
               ("assistant","Perfect! I will set up an AI-powered WhatsApp reminder sequence for your patients. This typically reduces no-shows by 35%. Want me to draft the message flows now?", True),
               ("user","When can we schedule the onboarding call?", False)]),
    dict(ci="sunita@smiledentalclinic.in", cn="Sunita Agarwal", ch=ConversationChannel.EMAIL, st=ConversationStatus.OPEN,   lp="Please send the poster designs for all 5 clinics.",
         msgs=[("user","We need festive dental posters for Diwali. Each clinic has a different name.", False),
               ("assistant","Absolutely! I can generate customised Diwali dental posters for each of your 5 clinics with their individual branding. Can you share the clinic names and preferred color themes?", True),
               ("user","Please send the poster designs for all 5 clinics.", False)]),
    dict(ci="+91-98001-11006", cn="Dr. Amrita Bose", ch=ConversationChannel.WHATSAPP, st=ConversationStatus.RESOLVED, lp="Thanks! Campaign results are great.",
         msgs=[("user","How do I create a maternity package promotion?", False),
               ("assistant","For a maternity package campaign, I recommend Instagram Reels + Facebook carousel ads targeting women aged 22-35. I can generate bilingual (Hindi + English) ad copy in 30 seconds. Want to see samples?", True),
               ("user","Yes please! Also in Bengali for Kolkata audience.", False),
               ("assistant","Generated! Here are 3 Instagram caption variations and 2 Facebook ad headlines in English, Hindi, and Bengali. The CTR benchmark for healthcare in Kolkata is 2.4%. Shall I schedule the posts?", True),
               ("user","Thanks! Campaign results are great.", False)]),
]

SEQUENCES = [
    dict(name="New Patient Welcome Series", trigger="new_lead", sequence_type="whatsapp",
         target_segment="All new patient leads", status=SequenceStatus.ACTIVE,
         enrolled_count=45, completed_count=12, reply_count=18,
         ai_json={"goal":"convert","channel":"whatsapp"},
         steps=[
             dict(n=1, d=0,  ch="whatsapp", sub=None, body="Hi {{first_name}}! Welcome to {{org_name}}. We are excited to help you with your healthcare journey. Book your first appointment at a special 20% discount. Reply BOOK to proceed!", cta="Reply BOOK", goal="convert"),
             dict(n=2, d=3,  ch="whatsapp", sub=None, body="Hi {{first_name}}, just a reminder — your 20% new patient discount expires in 2 days! Our doctors are available Mon–Sat 9am–7pm. Call us: {{phone}}", cta="Call Now", goal="convert"),
             dict(n=3, d=7,  ch="email",    sub="Health Tip from {{org_name}}", body="Hi {{first_name}},\n\nHere is your personalised health tip this week:\n[AI-generated health tip based on patient profile]\n\nStay healthy!\nTeam {{org_name}}", cta=None, goal="engage"),
         ]),
    dict(name="Post-Appointment Follow-up", trigger="appointment_done", sequence_type="whatsapp",
         target_segment="Patients after consultation", status=SequenceStatus.ACTIVE,
         enrolled_count=89, completed_count=67, reply_count=34,
         ai_json={"goal":"retain","channel":"whatsapp"},
         steps=[
             dict(n=1, d=1,  ch="whatsapp", sub=None, body="Hi {{first_name}}, hope you are feeling better after your visit at {{org_name}}! Please share your feedback: [link]. Your review helps us serve more patients.", cta="Rate Us", goal="retain"),
             dict(n=2, d=30, ch="whatsapp", sub=None, body="Hi {{first_name}}, it has been a month since your last visit. Time for a routine check-up? Book easily: {{booking_link}}", cta="Book Now", goal="retain"),
         ]),
]


async def seed():
    async with async_session() as db:
        existing = await db.execute(select(Tenant).where(Tenant.email == BUNTY_EMAIL))
        tenant = existing.scalar_one_or_none()

        if not tenant:
            print("Creating bunty demo tenant...")
            tenant = Tenant(
                name="Bunty Healthcare Marketing",
                slug=BUNTY_SLUG,
                email=BUNTY_EMAIL,
                hashed_password=hash_password(BUNTY_PASSWORD),
                api_key=generate_api_key(),
                plan="professional",
                company_name="Bunty Healthcare Marketing Solutions",
                website="https://bunty.srp.ai",
                phone="+91-98001-00000",
                timezone="Asia/Kolkata",
                is_active=True,
                settings={"industry": "Healthcare", "location": "Mumbai"},
            )
            db.add(tenant)
            await db.flush()
            print(f"  Tenant: {tenant.id}")
        else:
            print(f"Bunty tenant exists: {tenant.id} — refreshing password")
            tenant.hashed_password = hash_password(BUNTY_PASSWORD)
            await db.flush()

        tid = tenant.id

        # Business profile
        bp_r = await db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tid))
        if not bp_r.scalar_one_or_none():
            db.add(BusinessProfile(
                tenant_id=tid,
                business_name="Bunty Healthcare Marketing Solutions",
                business_type="Healthcare Marketing Agency",
                industry="Healthcare & Medical Services",
                location="Mumbai, Maharashtra, India",
                website="https://bunty.srp.ai",
                target_audience="Hospitals, clinics, pharmacies, and wellness centres across India",
                main_offer="AI-powered patient acquisition and healthcare brand building",
                unique_selling_proposition="Bilingual healthcare marketing — Hindi + English + regional languages",
                brand_voice="professional",
                monthly_budget="200000",
                primary_goal="lead_generation",
                channels=["instagram", "facebook", "whatsapp", "google_ads", "email"],
                current_challenges="Low digital presence, missed appointments, high patient acquisition cost",
                contact_phone="+91-98001-00000",
                contact_email=BUNTY_EMAIL,
                onboarding_completed=True,
                strategy_json={
                    "summary": "Build healthcare authority content, run targeted local ads, automate patient follow-ups.",
                    "kpis": {"monthly_leads": 150, "cpl_inr": 600}
                }
            ))
            await db.flush()
            print("  Business profile done")

        # Leads
        lr = await db.execute(select(Lead).where(Lead.tenant_id == tid))
        if not lr.scalars().all():
            for i, ld in enumerate(LEADS):
                db.add(Lead(
                    tenant_id=tid, name=ld["name"], email=ld.get("email"),
                    phone=ld.get("phone"), company=ld.get("company"),
                    source=ld.get("source"), status=ld["status"],
                    ai_score=ld.get("ai_score"), ai_label=ld.get("ai_label"),
                    notes=ld.get("notes"),
                    created_at=datetime.utcnow() - timedelta(days=30 - i * 2)
                ))
            await db.flush()
            print(f"  {len(LEADS)} leads done")

        # Campaigns
        cr = await db.execute(select(Campaign).where(Campaign.tenant_id == tid))
        if not cr.scalars().all():
            for i, cd in enumerate(CAMPAIGNS):
                db.add(Campaign(
                    tenant_id=tid, name=cd["name"], objective=cd["objective"],
                    channels=cd["channels"], budget_total=cd["budget_total"],
                    currency="INR", status=cd["status"],
                    target_audience=cd.get("target_audience"),
                    leads_generated=cd.get("leads_generated", 0),
                    impressions=cd.get("impressions", 0),
                    clicks=cd.get("clicks", 0), conversions=cd.get("conversions", 0),
                    start_date=datetime.utcnow() - timedelta(days=15 - i * 4),
                    end_date=datetime.utcnow() + timedelta(days=30 + i * 7),
                    ai_plan_json={"target_audience": cd.get("target_audience")}
                ))
            await db.flush()
            print(f"  {len(CAMPAIGNS)} campaigns done")

        # Conversations
        cvr = await db.execute(select(Conversation).where(Conversation.tenant_id == tid))
        if not cvr.scalars().all():
            for i, cd in enumerate(CONVS):
                conv = Conversation(
                    tenant_id=tid, contact_identifier=cd["ci"],
                    contact_name=cd.get("cn"), channel=cd["ch"],
                    status=cd["st"], last_message_preview=cd.get("lp"),
                    last_message_at=datetime.utcnow() - timedelta(hours=24 - i * 3),
                    created_at=datetime.utcnow() - timedelta(hours=48 - i * 4)
                )
                db.add(conv)
                await db.flush()
                base = datetime.utcnow() - timedelta(hours=24)
                for j, (role, content, ai_gen) in enumerate(cd.get("msgs", [])):
                    db.add(ConversationMessage(
                        conversation_id=conv.id, tenant_id=tid,
                        role=role, content=content, ai_generated=ai_gen,
                        created_at=base + timedelta(minutes=j * 7)
                    ))
            await db.flush()
            print(f"  {len(CONVS)} conversations done")

        # Sequences
        sr = await db.execute(select(FollowupSequence).where(FollowupSequence.tenant_id == tid))
        if not sr.scalars().all():
            for sd in SEQUENCES:
                seq = FollowupSequence(
                    tenant_id=tid, name=sd["name"], trigger=sd["trigger"],
                    sequence_type=sd["sequence_type"],
                    target_segment=sd.get("target_segment"),
                    status=sd["status"],
                    enrolled_count=sd.get("enrolled_count", 0),
                    completed_count=sd.get("completed_count", 0),
                    reply_count=sd.get("reply_count", 0),
                    ai_generated_json=sd.get("ai_json")
                )
                db.add(seq)
                await db.flush()
                for s in sd.get("steps", []):
                    db.add(FollowupStep(
                        sequence_id=seq.id, tenant_id=tid,
                        step_number=s["n"], delay_days=s["d"], channel=s["ch"],
                        subject=s.get("sub"), body=s["body"],
                        cta=s.get("cta"), goal=s.get("goal"), is_active=True
                    ))
            await db.flush()
            print(f"  {len(SEQUENCES)} follow-up sequences done")

        await db.commit()

    print("\n" + "=" * 60)
    print("BUNTY DEMO ACCOUNT READY")
    print("=" * 60)
    print(f"  Email    : {BUNTY_EMAIL}")
    print(f"  Password : {BUNTY_PASSWORD}")
    print(f"  Slug     : {BUNTY_SLUG}")
    print(f"  Plan     : professional")
    print("  Industry : Healthcare & Medical Services")
    print("  Data: 12 leads | 5 campaigns | 3 conversations | 2 sequences")
    print("  Frontend : http://localhost:5173")
    print("  API docs : http://localhost:8002/docs")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
