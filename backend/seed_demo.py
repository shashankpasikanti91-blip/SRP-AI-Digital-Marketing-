#!/usr/bin/env python3
"""
Demo Account Seeder -- SRP AI Marketing OS  (field-verified)
Creates demo@srp.ai / Demo@12345 with rich Indian agency data.

Usage:
    cd backend
    python seed_demo.py
"""
import asyncio, json, sys, os
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

DEMO_EMAIL = "demo@srp.ai"
DEMO_PASSWORD = "Demo@12345"
DEMO_SLUG = "srp-demo"

LEADS = [
    dict(name="Anjali Sharma",   email="anjali@startup.in",      phone="+91-98765-43210", company="TechMinds India",         source="instagram_ad",   status=LeadStatus.QUALIFIED,    ai_score=92, ai_label="hot",  notes="Budget Rs 1.5L/yr. Full AI stack. Mumbai."),
    dict(name="Ravi Patel",      email="ravi@growfast.co",        phone="+91-97654-32109", company="GrowFast Solutions",       source="website_form",   status=LeadStatus.CONTACTED,    ai_score=74, ai_label="warm", notes="E-commerce brand. Rs 80K/yr. Ahmedabad."),
    dict(name="Priya Nair",      email="priya@brandbuilder.in",   phone="+91-96543-21098", company="Brand Builder Agency",     source="referral",       status=LeadStatus.QUALIFIED,    ai_score=88, ai_label="hot",  notes="Manages 20+ client accounts. Bengaluru."),
    dict(name="Mohit Gupta",     email="mohit@realestatepro.com", phone="+91-95432-10987", company="RealEstate Pro",           source="facebook_ad",    status=LeadStatus.CONTACTED,    ai_score=65, ai_label="warm", notes="Real estate developer. Rs 5L/yr. Delhi NCR."),
    dict(name="Sneha Reddy",     email="sneha@fashionhub.in",     phone="+91-94321-09876", company="FashionHub",               source="whatsapp",       status=LeadStatus.NEW,          ai_score=40, ai_label="cold", notes="Fashion startup. Rs 50K/yr. Hyderabad."),
    dict(name="Amit Singh",      email="amit@edutech.org",        phone="+91-93210-98765", company="EduTech Academy",          source="linkedin",       status=LeadStatus.QUALIFIED,    ai_score=95, ai_label="hot",  notes="Ed-tech founder. Rs 3L/yr. Pune."),
    dict(name="Kavya Menon",     email="kavya@finpulse.io",       phone="+91-92109-87654", company="FinPulse India",           source="website_form",   status=LeadStatus.CONTACTED,    ai_score=71, ai_label="warm", notes="FinTech startup. Rs 1.2L/yr. Chennai."),
    dict(name="Suresh Kumar",    email="suresh@spicelane.com",    phone="+91-91098-76543", company="SpiceLane Restaurants",    source="instagram_ad",   status=LeadStatus.NEW,          ai_score=35, ai_label="cold", notes="Restaurant chain. Tight budget. Coimbatore."),
    dict(name="Deepika Joshi",   email="deepika@carefirst.in",    phone="+91-90987-65432", company="CareFirst Clinics",        source="google_ads",     status=LeadStatus.QUALIFIED,    ai_score=89, ai_label="hot",  notes="12 clinics. Rs 2.5L/yr. Jaipur."),
    dict(name="Arjun Nambiar",   email="arjun@quickship.co",      phone="+91-89876-54321", company="QuickShip Logistics",      source="referral",       status=LeadStatus.CONTACTED,    ai_score=68, ai_label="warm", notes="Logistics startup. Rs 1.8L/yr. Kochi."),
    dict(name="Rohit Verma",     email="rohit@digitalwave.in",    phone="+91-88765-43210", company="Digital Wave Agency",      source="website_form",   status=LeadStatus.CONVERTED,    ai_score=97, ai_label="hot",  notes="Paying Growth plan customer."),
    dict(name="Anita Desai",     email="anita@jewelshoppe.com",   phone="+91-87654-32109", company="Jewel Shoppe",             source="instagram_ad",   status=LeadStatus.NEW,          ai_score=28, ai_label="cold", notes="Jewellery retail. Exploring. Surat."),
]

CAMPAIGNS = [
    dict(name="Diwali 2026 -- Social Media Blitz",        objective="brand_awareness",  channels=["instagram","facebook"],  budget_total=500000,  status=CampaignStatus.ACTIVE,    leads_generated=127, impressions=180000, clicks=4200, conversions=34, target_audience="25-45, Tier 1 cities, interest: gifting, home decor"),
    dict(name="Lead Gen -- Real Estate NCR Investors",    objective="lead_generation",  channels=["facebook","linkedin"],   budget_total=300000,  status=CampaignStatus.ACTIVE,    leads_generated=48,  impressions=95000,  clicks=1800, conversions=12, target_audience="HNI investors 35-55, Delhi NCR, Rs 50L+ capacity"),
    dict(name="Email Nurture -- B2B SaaS 7-Step",         objective="lead_nurture",     channels=["email"],                 budget_total=80000,   status=CampaignStatus.PAUSED,    leads_generated=22,  impressions=0,      clicks=890,  conversions=5,  target_audience="SaaS founders and marketing managers, India"),
    dict(name="LinkedIn B2B -- IT Decision Makers",       objective="lead_generation",  channels=["linkedin"],              budget_total=200000,  status=CampaignStatus.DRAFT,     leads_generated=0,   impressions=0,      clicks=0,    conversions=0,  target_audience="CTOs, CMOs at IT companies 100+ employees"),
    dict(name="Brand Story Video -- Pan India YouTube",   objective="brand_awareness",  channels=["youtube"],               budget_total=1000000, status=CampaignStatus.COMPLETED, leads_generated=89,  impressions=2100000,clicks=62000,conversions=18, target_audience="Business owners 28-50, all India"),
]

CONVS = [
    dict(ci="anjali@startup.in",          cn="Anjali Sharma",  ch=ConversationChannel.EMAIL,     st=ConversationStatus.OPEN,     lp="Thursday 4 PM works perfectly!",
         msgs=[("user","Hi! I saw your LinkedIn post about AI marketing tools. Can we schedule a call this week?",False),
               ("assistant","Hello Anjali! We have slots Thursday 3-5 PM and Friday 10 AM-12 PM. Which works?",True),
               ("user","Thursday 4 PM works perfectly!",False)]),
    dict(ci="+91-97654-32109",            cn="Ravi Patel",     ch=ConversationChannel.WHATSAPP,  st=ConversationStatus.WAITING,  lp="What is your pricing for Growth plan?",
         msgs=[("user","What is your pricing for Growth plan? Do you have GST invoice?",False),
               ("assistant","Hi Ravi! Growth plan is Rs 1,499/month + 18% GST. Yes, GST invoices provided. Want the full comparison?",True)]),
    dict(ci="priya@brandbuilder.in",      cn="Priya Nair",     ch=ConversationChannel.EMAIL,     st=ConversationStatus.OPEN,     lp="Yes, please book a demo for next week!",
         msgs=[("user","We run 20+ client accounts. Do you have agency pricing?",False),
               ("assistant","Hi Priya! Professional plan Rs 3,999/month supports 15 users + multi-brand workspaces. Want a quick call?",True),
               ("user","Yes, please book a demo for next week!",False)]),
    dict(ci="mohit.gupta.delhi",          cn="Mohit Gupta",    ch=ConversationChannel.INSTAGRAM, st=ConversationStatus.OPEN,     lp="How does your AI qualify real estate leads?",
         msgs=[("user","Saw your ad. How does your AI qualify real estate leads?",False),
               ("assistant","Hi Mohit! Our Lead Qualification Agent scores leads 0-100 on budget, location, urgency. Flags serious buyers instantly. Demo?",True)]),
    dict(ci="amit@edutech.org",           cn="Amit Singh",     ch=ConversationChannel.LINKEDIN,  st=ConversationStatus.RESOLVED, lp="Great, sending the contract now.",
         msgs=[("user","We want to automate all our ed-tech lead follow-ups. Can you do that?",False),
               ("assistant","Absolutely! Follow-up Agent builds Day 0/1/3/7 sequences automatically via email & WhatsApp. Demo?",True),
               ("user","Yes! Please send a proposal.",False),
               ("assistant","Great, sending the contract now.",False)]),
]

SEQUENCES = [
    dict(name="New Lead Nurture -- 7-Day Email Flow", trigger="new_lead", sequence_type="email",
         target_segment="B2B SaaS & Agency Prospects", status=SequenceStatus.ACTIVE,
         enrolled_count=47, completed_count=23, reply_count=12,
         ai_json={"goal":"convert","channel":"email","strategy_note":"Value first, pitch Day 5"},
         steps=[
             dict(n=1,d=0, ch="email", sub="Quick question about your marketing goals",
                  body="Hi {{first_name}},\n\nWhat is the #1 marketing challenge you face right now?\n\nWe help 500+ Indian businesses solve this.\n\nBest,\nSRP AI Team", cta="Reply here", goal="engage"),
             dict(n=2,d=1, ch="email", sub="3 AI marketing hacks Indian businesses use in 2026",
                  body="Hi {{first_name}},\n\nHere is what is working:\n- AI lead scoring (saves 5+ hrs/week)\n- WhatsApp auto-replies (3x reply rate)\n- Omnichannel inbox for 6 platforms\n\nWant a 15-min demo?", cta="Book demo", goal="book_meeting"),
             dict(n=3,d=3, ch="email", sub="Case study: GrowFast went from 12 to 38 sales calls/month",
                  body="Hi {{first_name}},\n\nGrowFast Ahmedabad 3x their sales conversations using SRP AI -- AI replies on WhatsApp within 2 minutes, 24/7.\n\nWant the full case study?", cta="Send case study", goal="engage"),
             dict(n=4,d=5, ch="email", sub="You are leaving money on the table -- here is how to fix it",
                  body="Hi {{first_name}},\n\nMost businesses lose 70% of leads because they follow up too slow.\n\nSRP AI fixes this:\n- Instant reply within 60 seconds\n- Personalised by lead source\n- Smart human escalation\n\nReady to see it?", cta="Start free trial", goal="convert"),
             dict(n=5,d=7, ch="email", sub="Last chance -- 2 months free offer expires tomorrow",
                  body="Hi {{first_name}},\n\nWe are offering 2 months free on annual plans + a dedicated onboarding call worth Rs 5,000.\n\nOffer expires tomorrow 11:59 PM IST.", cta="Claim 2 months free", goal="convert"),
         ]),
    dict(name="No-Reply Recovery -- WhatsApp Re-engagement", trigger="no_reply", sequence_type="whatsapp",
         target_segment="Cold leads, no response 3+ days", status=SequenceStatus.ACTIVE,
         enrolled_count=31, completed_count=8, reply_count=9,
         ai_json={"goal":"reactivate","channel":"whatsapp"},
         steps=[
             dict(n=1,d=3, ch="whatsapp", sub=None, body="Hi {{first_name}} - just checking in! Did you get a chance to look at SRP AI Marketing? Happy to answer any questions. No pressure.", cta="Reply YES for demo", goal="reactivate"),
             dict(n=2,d=7, ch="whatsapp", sub=None, body="Hi {{first_name}}, our AI content generator creates Instagram captions, ad copy and emails in seconds. Free to try: srp.ai/demo", cta="Try free", goal="engage"),
             dict(n=3,d=14, ch="email",   sub="Last message from us", body="Hi {{first_name}},\n\nWe will not message you again after this.\n\nIf you ever need AI marketing automation, we are here at srp.ai\n\nWishing you great success!", cta=None, goal="reactivate"),
         ]),
    dict(name="Won Deal Upsell -- Upgrade to Professional", trigger="won", sequence_type="email",
         target_segment="New Growth plan customers", status=SequenceStatus.DRAFT,
         enrolled_count=0, completed_count=0, reply_count=0,
         ai_json={"goal":"upsell","channel":"email"},
         steps=[
             dict(n=1,d=14, ch="email", sub="How are your first 2 weeks with SRP AI?", body="Hi {{first_name}},\n\nHope you are loving SRP AI! Are you using the Campaign Planner and AI Follow-up Builder yet?\n\nThose two features alone 3x results for most businesses.", cta="Book onboarding", goal="engage"),
             dict(n=2,d=30, ch="email", sub="Ready for the next level? Professional plan features inside", body="Hi {{first_name}},\n\nYou have been rocking SRP AI for a month! Teams on Professional at Rs 3,999/month see 2x more leads via multi-brand workspaces + advanced AI.", cta="See Professional features", goal="upsell"),
         ]),
]


async def seed():
    async with async_session() as db:
        existing = await db.execute(select(Tenant).where(Tenant.email == DEMO_EMAIL))
        tenant = existing.scalar_one_or_none()

        if not tenant:
            print("Creating demo tenant...")
            tenant = Tenant(
                name="SRP Demo Agency", slug=DEMO_SLUG, email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
                api_key=generate_api_key(), plan="professional",
                company_name="SRP Digital Marketing Agency",
                website="https://srp.ai", phone="+91-98765-00000",
                timezone="Asia/Kolkata", is_active=True,
                settings={"industry": "Digital Marketing", "location": "Mumbai"},
            )
            db.add(tenant); await db.flush()
            print(f"  Tenant: {tenant.id}")
        else:
            print(f"Demo tenant exists: {tenant.id} -- refreshing password")
            tenant.hashed_password = hash_password(DEMO_PASSWORD)
            await db.flush()

        tid = tenant.id

        # Business profile
        bp_r = await db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tid))
        if not bp_r.scalar_one_or_none():
            db.add(BusinessProfile(
                tenant_id=tid, business_name="SRP Digital Marketing Agency",
                business_type="Digital Marketing Agency", industry="Digital Marketing & Advertising",
                location="Mumbai, Maharashtra, India", website="https://srp.ai",
                target_audience="SMBs and agencies across India scaling their digital marketing",
                main_offer="AI-powered marketing automation -- 10 agents working 24/7",
                unique_selling_proposition="10 AI agents cheaper than one junior hire",
                brand_voice="professional", monthly_budget="150000", primary_goal="lead_generation",
                channels=["facebook","instagram","linkedin","email","whatsapp"],
                current_challenges="Manual follow-up, slow response, expensive agency retainers",
                contact_phone="+91-98765-00000", contact_email=DEMO_EMAIL, onboarding_completed=True,
                strategy_json={"summary":"Build authority, gen leads via paid, nurture email/WA, convert via demo.","kpis":{"monthly_leads":200,"cpl_inr":750}}
            ))
            await db.flush(); print("  Business profile done")

        # Leads
        lr = await db.execute(select(Lead).where(Lead.tenant_id == tid))
        if not lr.scalars().all():
            for i, ld in enumerate(LEADS):
                db.add(Lead(tenant_id=tid, name=ld["name"], email=ld.get("email"),
                            phone=ld.get("phone"), company=ld.get("company"),
                            source=ld.get("source"), status=ld["status"],
                            ai_score=ld.get("ai_score"), ai_label=ld.get("ai_label"),
                            notes=ld.get("notes"),
                            created_at=datetime.utcnow()-timedelta(days=30-i*2)))
            await db.flush(); print(f"  {len(LEADS)} leads done")

        # Campaigns
        cr = await db.execute(select(Campaign).where(Campaign.tenant_id == tid))
        if not cr.scalars().all():
            for i, cd in enumerate(CAMPAIGNS):
                db.add(Campaign(tenant_id=tid, name=cd["name"], objective=cd["objective"],
                                channels=cd["channels"], budget_total=cd["budget_total"],
                                currency="INR", status=cd["status"],
                                target_audience=cd.get("target_audience"),
                                leads_generated=cd.get("leads_generated",0),
                                impressions=cd.get("impressions",0),
                                clicks=cd.get("clicks",0), conversions=cd.get("conversions",0),
                                start_date=datetime.utcnow()-timedelta(days=15-i*4),
                                end_date=datetime.utcnow()+timedelta(days=30+i*7),
                                ai_plan_json={"target_audience":cd.get("target_audience")}))
            await db.flush(); print(f"  {len(CAMPAIGNS)} campaigns done")

        # Conversations
        cvr = await db.execute(select(Conversation).where(Conversation.tenant_id == tid))
        if not cvr.scalars().all():
            for i, cd in enumerate(CONVS):
                conv = Conversation(tenant_id=tid, contact_identifier=cd["ci"],
                                    contact_name=cd.get("cn"), channel=cd["ch"],
                                    status=cd["st"], last_message_preview=cd.get("lp"),
                                    last_message_at=datetime.utcnow()-timedelta(hours=24-i*3),
                                    created_at=datetime.utcnow()-timedelta(hours=48-i*4))
                db.add(conv); await db.flush()
                base = datetime.utcnow()-timedelta(hours=24)
                for j, (role, content, ai_gen) in enumerate(cd.get("msgs", [])):
                    db.add(ConversationMessage(conversation_id=conv.id, tenant_id=tid,
                                               role=role, content=content, ai_generated=ai_gen,
                                               created_at=base+timedelta(minutes=j*7)))
            await db.flush(); print(f"  {len(CONVS)} conversations done")

        # Sequences
        sr = await db.execute(select(FollowupSequence).where(FollowupSequence.tenant_id == tid))
        if not sr.scalars().all():
            for sd in SEQUENCES:
                seq = FollowupSequence(
                    tenant_id=tid, name=sd["name"], trigger=sd["trigger"],
                    sequence_type=sd["sequence_type"], target_segment=sd.get("target_segment"),
                    status=sd["status"], enrolled_count=sd.get("enrolled_count",0),
                    completed_count=sd.get("completed_count",0), reply_count=sd.get("reply_count",0),
                    ai_generated_json=sd.get("ai_json"))
                db.add(seq); await db.flush()
                for s in sd.get("steps",[]):
                    db.add(FollowupStep(sequence_id=seq.id, tenant_id=tid,
                                        step_number=s["n"], delay_days=s["d"], channel=s["ch"],
                                        subject=s.get("sub"), body=s["body"],
                                        cta=s.get("cta"), goal=s.get("goal"), is_active=True))
            await db.flush(); print(f"  {len(SEQUENCES)} follow-up sequences done")

        await db.commit()

    print("\n" + "="*60)
    print("DEMO ACCOUNT READY")
    print("="*60)
    print(f"  Email    : {DEMO_EMAIL}")
    print(f"  Password : {DEMO_PASSWORD}")
    print(f"  Plan     : professional")
    print("  Data: 12 leads | 5 campaigns | 5 conversations | 3 sequences")
    print("  Frontend : http://localhost:5173")
    print("  API docs : http://localhost:8000/docs")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(seed())
