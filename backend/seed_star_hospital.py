#!/usr/bin/env python3
"""
Star Hospital — Real Project Seeder
SRP AI Marketing OS

Creates admin@starhospital.in / Star@12345 with full hospital marketing data.
Star Hospitals — Multi-specialty Hospital, Hyderabad.

Usage:
    cd backend
    python seed_star_hospital.py
"""
import asyncio, sys, os, json
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
from app.models.social import SocialPost, SocialPlatform, PostStatus
from app.models.conversation import (
    Conversation, ConversationMessage,
    ConversationChannel, ConversationStatus,
)
from app.models.followup import FollowupSequence, FollowupStep, SequenceStatus

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

STAR_EMAIL    = "admin@starhospital.in"
STAR_PASSWORD = "Star@12345"
STAR_SLUG     = "star-hospital"
STAR_NAME     = "Star Hospitals Hyderabad"

LEADS = [
    dict(name="Suresh Reddy",       email="suresh.reddy@gmail.com",     phone="+91-98480-11001", company="TATA Consultancy",        source="google_ads",      status=LeadStatus.QUALIFIED,  ai_score=91, ai_label="hot",  notes="Knee replacement inquiry. TATA employee. Budget flexible. Hyderabad."),
    dict(name="Priya Lakshmi",      email="priya.l@outlook.com",        phone="+91-98480-11002", company="Self",                    source="instagram_ad",    status=LeadStatus.CONTACTED,  ai_score=76, ai_label="warm", notes="Cardiac check-up inquiry. Female 45. Health insurance available."),
    dict(name="Mohammed Ibrahim",   email="ibrahim.m@yahoo.com",        phone="+91-98480-11003", company="Govt Servant",            source="whatsapp",        status=LeadStatus.QUALIFIED,  ai_score=88, ai_label="hot",  notes="Spine surgery inquiry. Referred by Dr. Venkat. CGHS patient."),
    dict(name="Nalini Sharma",      email="nalini.s@gmail.com",         phone="+91-98480-11004", company="Homemaker",               source="facebook_ad",     status=LeadStatus.CONTACTED,  ai_score=68, ai_label="warm", notes="Maternity package inquiry. 3rd month pregnant. Budget Rs 1.5L."),
    dict(name="Venkat Rao",         email="venkat.rao@infosys.com",     phone="+91-98480-11005", company="Infosys",                 source="website_form",    status=LeadStatus.NEW,        ai_score=52, ai_label="warm", notes="Corporate health packages for 200 employees. Decision maker."),
    dict(name="Anitha Krishnamurthy",email="anitha.k@gmail.com",        phone="+91-98480-11006", company="Lawyer",                  source="referral",        status=LeadStatus.QUALIFIED,  ai_score=93, ai_label="hot",  notes="Hip replacement. Referred by existing patient Suresh Reddy. Cash patient."),
    dict(name="Ravi Shankar",       email="ravi.s@wipro.com",           phone="+91-98480-11007", company="Wipro Technologies",      source="linkedin",        status=LeadStatus.CONTACTED,  ai_score=70, ai_label="warm", notes="Corporate deal — 500 employees health screening. Wipro Hyderabad."),
    dict(name="Kavitha Naidu",      email="kavitha.n@hotmail.com",      phone="+91-98480-11008", company="Teacher",                 source="instagram_ad",    status=LeadStatus.NEW,        ai_score=41, ai_label="cold", notes="Thyroid check-up inquiry. Government school teacher."),
    dict(name="Dr. Arjun Mehta",    email="arjun.m@gmail.com",          phone="+91-98480-11009", company="Retired",                 source="google_ads",      status=LeadStatus.QUALIFIED,  ai_score=84, ai_label="hot",  notes="Diabetes management package. Senior citizen 68yrs. Family referred."),
    dict(name="Swathi Iyer",        email="swathi.iyer@amazon.com",     phone="+91-98480-11010", company="Amazon India",            source="website_form",    status=LeadStatus.CONTACTED,  ai_score=73, ai_label="warm", notes="Women's health check-up package. Amazon employee benefits."),
    dict(name="Ramesh Babu",        email="ramesh.babu@gmail.com",      phone="+91-98480-11011", company="Business Owner",          source="facebook_ad",     status=LeadStatus.CONVERTED,  ai_score=97, ai_label="hot",  notes="CONVERTED - Knee replacement done. Rs 4.2L. Very satisfied. Will refer."),
    dict(name="Deepa Patel",        email="deepa.p@outlook.com",        phone="+91-98480-11012", company="Pharmacist",              source="whatsapp",        status=LeadStatus.NEW,        ai_score=36, ai_label="cold", notes="General OPD inquiry through WhatsApp campaign."),
    dict(name="Kishore Kumar",      email="kishore.k@hdfcbank.com",     phone="+91-98480-11013", company="HDFC Bank",               source="google_ads",      status=LeadStatus.QUALIFIED,  ai_score=89, ai_label="hot",  notes="LASIK surgery inquiry. HDFC employee. Insurance covers up to Rs 80K."),
    dict(name="Latha Venkatesh",    email="latha.v@gmail.com",          phone="+91-98480-11014", company="Homemaker",               source="referral",        status=LeadStatus.CONTACTED,  ai_score=65, ai_label="warm", notes="Maternity - C-section package. 6th month. Referred by Nalini."),
    dict(name="Srinivas Goud",      email="srinivas.g@gmail.com",       phone="+91-98480-11015", company="Real Estate",             source="instagram_ad",    status=LeadStatus.QUALIFIED,  ai_score=86, ai_label="hot",  notes="Complete body check-up. Business owner 55. High BP. Willing to pay premium."),
]

CAMPAIGNS = [
    dict(
        name="Star Hospitals — Orthopaedic Camp August 2026",
        objective="Patient Acquisition — Knee/Hip Replacement",
        channels=["instagram", "facebook", "whatsapp", "google_ads"],
        budget_total=150000,
        status=CampaignStatus.ACTIVE,
        target_audience="Adults 45-70, Hyderabad/Secunderabad, joint pain/mobility issues",
        leads_generated=89, impressions=215000, clicks=8400, conversions=31,
    ),
    dict(
        name="Free Cardiac Screening Camp — Heart Month",
        objective="Brand Awareness + OPD Conversion",
        channels=["facebook", "instagram", "whatsapp"],
        budget_total=80000,
        status=CampaignStatus.ACTIVE,
        target_audience="Adults 40+, urban Hyderabad, heart health concern",
        leads_generated=142, impressions=310000, clicks=11200, conversions=58,
    ),
    dict(
        name="Maternity Care — Delivery Package Promotion",
        objective="Lead Generation — Maternity OPD Bookings",
        channels=["instagram", "facebook", "whatsapp"],
        budget_total=60000,
        status=CampaignStatus.ACTIVE,
        target_audience="Women 22-38, pregnant/planning, Hyderabad",
        leads_generated=67, impressions=128000, clicks=5600, conversions=22,
    ),
    dict(
        name="Corporate Health Packages — B2B Drive",
        objective="Corporate Tie-ups B2B",
        channels=["linkedin", "email"],
        budget_total=40000,
        status=CampaignStatus.PAUSED,
        target_audience="HR Managers, Corporate Admins, IT companies Hyderabad 500+ employees",
        leads_generated=18, impressions=42000, clicks=1800, conversions=3,
    ),
    dict(
        name="LASIK Christmas Offer 2026",
        objective="Procedure Promotion — Eye Surgery",
        channels=["instagram", "facebook", "google_ads"],
        budget_total=75000,
        status=CampaignStatus.DRAFT,
        target_audience="Adults 22-40, spectacle/lens users, Hyderabad",
        leads_generated=0, impressions=0, clicks=0, conversions=0,
    ),
    dict(
        name="Diwali Wellness Package — Family Health Checkup",
        objective="Festive Promotion — Health Packages",
        channels=["whatsapp", "instagram", "facebook"],
        budget_total=55000,
        status=CampaignStatus.COMPLETED,
        target_audience="Families Hyderabad, health-conscious, income 8-25L",
        leads_generated=203, impressions=480000, clicks=19200, conversions=87,
    ),
]

SOCIAL_POSTS = [
    # Instagram posts
    dict(
        platform=SocialPlatform.INSTAGRAM,
        content="🦵 Joint Pain? Don't Ignore It!\n\nAt Star Hospitals Hyderabad, our expert orthopaedic team has performed 5,000+ successful knee and hip replacements.\n\n✅ Minimally Invasive Surgery\n✅ 3-Day Hospital Stay\n✅ Insurance Accepted\n✅ FREE Pre-Surgery Assessment\n\n📞 Book your Free Consultation: +91-40-4444-5555\n📍 Banjara Hills, Hyderabad\n\nDon't let joint pain hold you back! 💪\n\n#StarHospitals #KneeReplacement #HipReplacement #Hyderabad #Orthopaedic #JointPain #HealthCare",
        campaign="Orthopaedic Camp",
        status=PostStatus.PUBLISHED,
    ),
    dict(
        platform=SocialPlatform.INSTAGRAM,
        content="❤️ Love Your Heart!\n\nFree Cardiac Screening this Saturday at Star Hospitals!\n\n🔍 What's Included:\n• ECG\n• BP Check\n• Cholesterol Test\n• Cardiologist Consultation\n\nₒ All FREE of cost!\n⏰ Saturday 9 AM – 2 PM\n📍 Star Hospitals, Jubilee Hills\n\nLimited slots! Call NOW 📞\n+91-40-4444-5555\n\n#FreeHeartCheckup #StarHospitals #CardiacCare #Hyderabad #HeartHealth #FreeCamp",
        campaign="Cardiac Screening",
        status=PostStatus.SCHEDULED,
        scheduled_at=datetime.utcnow() + timedelta(days=3),
    ),
    dict(
        platform=SocialPlatform.INSTAGRAM,
        content="🤱 Welcome to Parenthood with Star Hospitals!\n\nOur Maternity package gives you everything you need for a safe, comfortable delivery.\n\n💜 Package Includes:\n✅ All Antenatal Check-ups\n✅ Delivery (Normal/C-Section)\n✅ Newborn Care\n✅ Post-Natal Support\n✅ Lactation Counselling\n\n💰 Starting from ₹45,000/-\n\nBook a FREE counselling session today!\n📞 +91-40-4444-5555\n\n#StarHospitals #Maternity #NormalDelivery #Hyderabad #MomLife #BabyShower",
        campaign="Maternity Package",
        status=PostStatus.DRAFT,
    ),
    # Facebook posts
    dict(
        platform=SocialPlatform.FACEBOOK,
        content="🏥 Star Hospitals Hyderabad — Your Health, Our Priority\n\nThis week only — Complete Body Health Checkup at 40% OFF!\n\n📋 35+ Tests Including:\n• Blood Sugar (Fasting + PP)\n• Lipid Profile\n• Liver & Kidney Function\n• Thyroid (T3, T4, TSH)\n• Chest X-Ray\n• Ultrasound Abdomen\n• Doctor Consultation\n\nRegular Price: ₹4,999/-\n🎯 Special Price: ₹2,999/- only!\n\n📞 Call Now: +91-40-4444-5555\n🌐 www.starhospitals.in\n\nOffer valid till Sunday midnight! Rush now 🚨",
        campaign="Diwali Wellness",
        status=PostStatus.PUBLISHED,
    ),
    dict(
        platform=SocialPlatform.FACEBOOK,
        content="👨‍💼 Corporate Health Packages — Designed for Your Team\n\nStar Hospitals offers customised corporate health plans for companies in Hyderabad.\n\n🏢 Benefits for Your Company:\n✅ Bulk Discounts (50+ employees)\n✅ Dedicated HR Coordinator\n✅ Priority Appointment Scheduling\n✅ Digital Health Records for Each Employee\n✅ Quarterly Health Reports\n\n📊 Packages starting from ₹2,500/employee\n\nSchedule a Demo for your HR team!\n📧 corporate@starhospitals.in\n📞 +91-40-4444-5556\n\n#CorporateHealth #StarHospitals #HyderabadCorporate #EmployeeWellness",
        campaign="Corporate B2B",
        status=PostStatus.PUBLISHED,
    ),
    # WhatsApp Status posts
    dict(
        platform=SocialPlatform.WHATSAPP,
        campaign="Monday Morning Health Tip",
        content="🌅 Good Morning from Star Hospitals!\n\n💊 Today's Health Tip:\n\nDrink a glass of warm water with lemon every morning. It:\n✅ Boosts immunity\n✅ Aids digestion\n✅ Kickstarts metabolism\n\n📞 For appointments: +91-40-4444-5555\n\nStay healthy! 🙏",
        status=PostStatus.PUBLISHED,
    ),
    dict(
        platform=SocialPlatform.WHATSAPP,
        campaign="Orthopaedic Camp Reminder",
        content="🦵 FREE Orthopaedic Consultation!\n\nAre you or someone you know suffering from:\n🔴 Knee Pain\n🔴 Hip Pain\n🔴 Back Pain\n\n📅 This Saturday ONLY\n⏰ 9 AM – 1 PM\n📍 Star Hospitals, Banjara Hills\n\n✅ FREE X-Ray\n✅ FREE Doctor Consultation\n✅ Same-Day Results\n\nBook your spot:\n📞 Reply BOOK to this message\nor Call: +91-40-4444-5555\n\nLimited slots! 🚨",
        status=PostStatus.SCHEDULED,
        scheduled_at=datetime.utcnow() + timedelta(days=2),
    ),
    dict(
        platform=SocialPlatform.WHATSAPP,
        campaign="New Year Health Resolution",
        content="🎉 Happy New Year from Star Hospitals!\n\nStart 2026 with a health resolution!\n\n💪 New Year Special:\nComplete Health Checkup @ ₹1,999/-\n(Worth ₹4,500/- Save 56%!)\n\n📋 Includes 40+ tests + Doctor Consult\n\n📞 Book Now: +91-40-4444-5555\n⏳ Offer valid for January only!\n\n#NewYear2026 #HealthResolution #StarHospitals",
        status=PostStatus.PUBLISHED,
    ),
    dict(
        platform=SocialPlatform.WHATSAPP,
        campaign="Heart Month Campaign",
        content="❤️ February = Heart Month!\n\nDid you know?\n📊 1 in 4 Indians over 40 has silent heart disease!\n\nStar Hospitals Hyderabad invites you for:\n\n🩺 FREE Cardiac Screening\n📅 Every Saturday this February\n⏰ 8 AM – 12 PM\n📍 Jubilee Hills Branch\n\nDon't wait for a warning sign!\nBook TODAY: +91-40-4444-5555\n\nShare this with someone you care about 🙏",
        status=PostStatus.DRAFT,
    ),
]

CONVS = [
    dict(
        ci="+91-98480-11001", cn="Suresh Reddy",
        ch=ConversationChannel.WHATSAPP, st=ConversationStatus.OPEN,
        lp="Can you confirm OT slot for 15th March?",
        msgs=[
            ("user", "Hello, I need to know the cost for knee replacement at Star Hospitals.", False),
            ("assistant", "Hello Suresh! Thank you for contacting Star Hospitals. Knee replacement at our centre costs between ₹2.8L – ₹4.5L depending on implant type. This includes surgery, 4 days hospitalization, physiotherapy, and follow-up. Do you have medical insurance?", True),
            ("user", "Yes I have CGHS. Will it be covered?", False),
            ("assistant", "Great! Star Hospitals is empanelled with CGHS. Knee replacement is fully covered under CGHS for government employees. I'll connect you with our Insurance Desk directly. Can I schedule a FREE consultation with Dr. Srikanth (Sr. Orthopaedic Surgeon) this week?", True),
            ("user", "Yes, Saturday works for me.", False),
            ("assistant", "Confirmed! Your FREE consultation with Dr. Srikanth is scheduled for this Saturday at 11 AM. Our team will send a reminder on Friday. Please bring your CGHS card and any existing X-rays. See you soon! 🙏", True),
            ("user", "Can you confirm OT slot for 15th March?", False),
        ],
    ),
    dict(
        ci="+91-98480-11004", cn="Nalini Sharma",
        ch=ConversationChannel.WHATSAPP, st=ConversationStatus.OPEN,
        lp="Please share the maternity package details PDF.",
        msgs=[
            ("user", "Hi, I'm 3 months pregnant. What maternity packages do you offer?", False),
            ("assistant", "Congratulations Nalini! 🎉 At Star Hospitals, our Maternity packages start from ₹45,000/- for normal delivery and ₹65,000/- for C-section. Both packages include all antenatal visits, delivery, new-born care, and 3-day stay for mom & baby. Shall I explain in detail?", True),
            ("user", "What is included in the antenatal visits?", False),
            ("assistant", "Our Antenatal package (4 visits) includes: Ultrasound scans, blood tests, BP monitoring, TIFFA scan, glucose tolerance test, and consultation with our gynaecologist Dr. Kavitha. All at no extra charge within the package. Would you like to book your first visit?", True),
            ("user", "Please share the maternity package details PDF.", False),
        ],
    ),
    dict(
        ci="venkat.rao@infosys.com", cn="Venkat Rao",
        ch=ConversationChannel.EMAIL, st=ConversationStatus.OPEN,
        lp="Can we schedule a corporate visit next Tuesday?",
        msgs=[
            ("user", "Hello, I'm the HR Manager at Infosys Hyderabad. We're looking for corporate health packages for 200 employees.", False),
            ("assistant", "Hello Venkat! Thank you for reaching out. Star Hospitals offers comprehensive corporate health packages starting from ₹2,500/employee for 100-300 employees. This includes annual health screening with 35+ tests, priority booking, dedicated HR coordinator, and digital health reports. I can arrange a detailed presentation for your leadership team. When would that be convenient?", True),
            ("user", "Can we schedule a corporate visit next Tuesday?", False),
        ],
    ),
]

SEQUENCES = [
    dict(
        name="New Patient Welcome — Orthopaedic",
        trigger="orthopaedic_inquiry",
        sequence_type="whatsapp",
        target_segment="Orthopaedic leads from Google/Instagram",
        status=SequenceStatus.ACTIVE,
        enrolled_count=67,
        completed_count=19,
        reply_count=28,
        ai_json={"goal": "book_consultation", "channel": "whatsapp", "hospital": "Star Hospitals"},
        steps=[
            dict(n=1, d=0, ch="whatsapp", sub=None,
                 body="Hello {{first_name}}! 👋\n\nThank you for enquiring at *Star Hospitals Hyderabad* about {{service}}.\n\nOur expert orthopaedic team has helped 5,000+ patients walk pain-free! 🦵\n\n✅ *FREE Consultation* available this week.\n📞 Reply *BOOK* to schedule.\n\nTeam Star Hospitals | +91-40-4444-5555",
                 cta="Reply BOOK", goal="book"),
            dict(n=2, d=2, ch="whatsapp", sub=None,
                 body="Hello {{first_name}},\n\nJust following up on your orthopaedic enquiry 🙏\n\nHere's what our patients say:\n⭐⭐⭐⭐⭐ ''Star Hospitals gave me my life back. Walking without pain for the first time in 5 years!'' — Ramesh, Hyderabad\n\nYour FREE consultation slot is still available.\n📞 Call: +91-40-4444-5555",
                 cta="Call Now", goal="convert"),
            dict(n=3, d=7, ch="whatsapp", sub=None,
                 body="Hi {{first_name}},\n\nThis week's tip for joint health:\n\n💧 Stay hydrated — cartilage is 65% water!\n🏃 Low-impact exercise like swimming helps more than rest.\n💊 Don't rely only on painkillers — treat the root cause.\n\nNeed expert advice? We're here.\n📞 +91-40-4444-5555 | Star Hospitals",
                 cta=None, goal="engage"),
        ],
    ),
    dict(
        name="Post-Surgery Recovery Follow-up",
        trigger="surgery_done",
        sequence_type="whatsapp",
        target_segment="All post-surgery patients",
        status=SequenceStatus.ACTIVE,
        enrolled_count=41,
        completed_count=34,
        reply_count=29,
        ai_json={"goal": "retention", "channel": "whatsapp"},
        steps=[
            dict(n=1, d=1, ch="whatsapp", sub=None,
                 body="Dear {{first_name}}, we hope you're recovering well after your procedure at Star Hospitals! 🙏\n\nPlease remember:\n✅ Take medicines on time\n✅ Keep the wound dry for 48 hours\n✅ Call us anytime if you feel discomfort\n\n📞 24/7 Emergency: +91-40-4444-5555",
                 cta="Call if needed", goal="retain"),
            dict(n=2, d=7, ch="whatsapp", sub=None,
                 body="Hi {{first_name}}, your 1-week follow-up is due! 📅\n\nBook your post-op review with Dr. {{doctor_name}}.\nReply *FOLLOWUP* and we'll arrange it.\n\nHoping you're feeling much better!\nTeam Star Hospitals 🌟",
                 cta="Reply FOLLOWUP", goal="retain"),
            dict(n=3, d=30, ch="whatsapp", sub=None,
                 body="Hello {{first_name}}, 1 month since your surgery — how are you feeling? 😊\n\nTime for your monthly review. This is crucial for best recovery results!\n\nBook: Reply or call +91-40-4444-5555\n\n— Dr. {{doctor_name}} & Team Star Hospitals",
                 cta="Book Review", goal="retain"),
        ],
    ),
]


async def seed() -> None:
    async with async_session() as db:
        # ── Upsert Tenant ────────────────────────────────────────────────
        existing = (await db.execute(select(Tenant).where(Tenant.email == STAR_EMAIL))).scalar_one_or_none()
        if existing:
            tenant = existing
            print(f"[INFO] Tenant {STAR_EMAIL} already exists — refreshing data.")
        else:
            tenant = Tenant(
                name=STAR_NAME,
                slug=STAR_SLUG,
                email=STAR_EMAIL,
                hashed_password=hash_password(STAR_PASSWORD),
                api_key=generate_api_key(),
                plan="growth",
                company_name="Star Hospitals Group",
                is_active=True,
            )
            db.add(tenant)
            await db.flush()
            print(f"[OK] Tenant created: {STAR_EMAIL}")

        tid = tenant.id

        # ── Business Profile ─────────────────────────────────────────────
        existing_bp = (await db.execute(select(BusinessProfile).where(BusinessProfile.tenant_id == tid))).scalar_one_or_none()
        if not existing_bp:
            bp = BusinessProfile(
                tenant_id=tid,
                business_name="Star Hospitals Hyderabad",
                business_type="Multi-Specialty Hospital",
                industry="Healthcare",
                location="Banjara Hills & Jubilee Hills, Hyderabad, Telangana",
                website="https://www.starhospitals.in",
                target_audience="Adults 35-70 with orthopaedic, cardiac, maternity, and general health needs in Hyderabad metro area",
                main_offer="World-class multi-specialty healthcare with NABH-accredited quality, advanced technology, and affordable packages",
                unique_selling_proposition="500+ specialist doctors, 24/7 emergency, CGHS/ECHS/TPA empanelled, 98.6% patient satisfaction, same-day appointments available",
                brand_voice="professional",
                brand_colors=["#1E3A6E", "#E8A020", "#FFFFFF"],
                competitors="Yashoda Hospitals, Apollo Hospitals, KIMS, Basavatarakam Cancer Institute",
                current_challenges="Standing out in crowded Hyderabad healthcare market, converting digital enquiries to OPD visits, corporate tie-ups",
                monthly_budget="200000",
                primary_goal="Increase OPD bookings by 40% through digital marketing. Establish Star Hospitals as top-of-mind for orthopaedic and cardiac care in Hyderabad.",
                channels=["instagram", "facebook", "whatsapp", "google_ads", "linkedin", "email", "seo"],
                contact_phone="+91-40-4444-5555",
                contact_email="marketing@starhospitals.in",
                business_hours="Mon–Sat 8AM–8PM, Sun 9AM–5PM, Emergency 24/7",
                onboarding_completed=True,
                strategy_json={
                    "phase_1": "Digital brand building — Instagram + Facebook awareness campaigns",
                    "phase_2": "WhatsApp lead nurture sequences for all OPD inquiries",
                    "phase_3": "SEO optimization for Hyderabad healthcare keywords",
                    "phase_4": "Corporate B2B tie-ups via LinkedIn + email campaigns",
                    "kpi": {"monthly_leads": 200, "conversion_rate": "15%", "cost_per_lead": 750},
                },
            )
            db.add(bp)
            print("[OK] Business profile created")

        # ── Leads ────────────────────────────────────────────────────────
        for ld in LEADS:
            has_lead = (await db.execute(
                select(Lead).where(Lead.tenant_id == tid, Lead.name == ld["name"])
            )).scalar_one_or_none()
            if not has_lead:
                db.add(Lead(tenant_id=tid, **ld))
        print(f"[OK] {len(LEADS)} leads seeded")

        # ── Campaigns ────────────────────────────────────────────────────
        for cd in CAMPAIGNS:
            has_camp = (await db.execute(
                select(Campaign).where(Campaign.tenant_id == tid, Campaign.name == cd["name"])
            )).scalar_one_or_none()
            if not has_camp:
                db.add(Campaign(
                    tenant_id=tid,
                    name=cd["name"],
                    objective=cd.get("objective", ""),
                    channels=cd.get("channels", []),
                    budget_total=cd.get("budget_total"),
                    status=cd["status"],
                    target_audience=cd.get("target_audience", ""),
                    leads_generated=cd.get("leads_generated", 0),
                    impressions=cd.get("impressions", 0),
                    clicks=cd.get("clicks", 0),
                    conversions=cd.get("conversions", 0),
                ))
        print(f"[OK] {len(CAMPAIGNS)} campaigns seeded")

        # ── Social Posts ─────────────────────────────────────────────────
        for sp in SOCIAL_POSTS:
            has_post = (await db.execute(
                select(SocialPost).where(
                    SocialPost.tenant_id == tid,
                    SocialPost.campaign == sp.get("campaign"),
                    SocialPost.platform == sp["platform"],
                )
            )).scalar_one_or_none()
            if not has_post:
                post_data = {k: v for k, v in sp.items()}
                db.add(SocialPost(tenant_id=tid, **post_data))
        print(f"[OK] {len(SOCIAL_POSTS)} social posts seeded")

        # ── Conversations ────────────────────────────────────────────────────
        for cv in CONVS:
            has_conv = (await db.execute(
                select(Conversation).where(
                    Conversation.tenant_id == tid,
                    Conversation.contact_name == cv["cn"],
                )
            )).scalar_one_or_none()
            if not has_conv:
                conv = Conversation(
                    tenant_id=tid,
                    contact_identifier=cv["ci"],
                    contact_name=cv["cn"],
                    channel=cv["ch"],
                    status=cv["st"],
                    last_message_preview=cv["lp"],
                )
                db.add(conv)
                await db.flush()
                for role, body, is_ai in cv["msgs"]:
                    db.add(ConversationMessage(
                        conversation_id=conv.id,
                        tenant_id=tid,
                        role=role,
                        content=body,
                        ai_generated=is_ai,
                    ))
        print(f"[OK] {len(CONVS)} conversations seeded")

        # ── Follow-up Sequences ───────────────────────────────────────────────
        for seq in SEQUENCES:
            has_seq = (await db.execute(
                select(FollowupSequence).where(
                    FollowupSequence.tenant_id == tid,
                    FollowupSequence.name == seq["name"],
                )
            )).scalar_one_or_none()
            if not has_seq:
                steps_data = seq.get("steps", [])
                s = FollowupSequence(
                    tenant_id=tid,
                    name=seq["name"],
                    trigger=seq.get("trigger"),
                    sequence_type=seq.get("sequence_type", "whatsapp"),
                    target_segment=seq.get("target_segment"),
                    status=seq["status"],
                    enrolled_count=seq.get("enrolled_count", 0),
                    completed_count=seq.get("completed_count", 0),
                    reply_count=seq.get("reply_count", 0),
                    ai_generated_json=seq.get("ai_json"),
                )
                db.add(s)
                await db.flush()
                for step in steps_data:
                    db.add(FollowupStep(
                        sequence_id=s.id,
                        tenant_id=tid,
                        step_number=step["n"],
                        delay_days=step["d"],
                        channel=step["ch"],
                        subject=step.get("sub"),
                        body=step["body"],
                        cta=step.get("cta"),
                        goal=step.get("goal"),
                    ))
        print(f"[OK] {len(SEQUENCES)} follow-up sequences seeded")

        await db.commit()
        print("\n" + "=" * 60)
        print("✅  STAR HOSPITAL SEEDING COMPLETE!")
        print("=" * 60)
        print(f"   Login Email   : {STAR_EMAIL}")
        print(f"   Password      : {STAR_PASSWORD}")
        print(f"   Business      : {STAR_NAME}")
        print(f"   Campaigns     : {len(CAMPAIGNS)}")
        print(f"   Leads         : {len(LEADS)}")
        print(f"   Social Posts  : {len(SOCIAL_POSTS)} (Instagram + Facebook + WhatsApp)")
        print(f"   Conversations : {len(CONVS)}")
        print(f"   Follow-ups    : {len(SEQUENCES)}")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed())
