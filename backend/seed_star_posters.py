#!/usr/bin/env python3
"""
Star Hospital Poster + WhatsApp Status Seeder
Seeds for bunty@srp.ai account:
  - 4 Poster variants (Orthopedic ₹500 x2, Diabetes x1, General Health x1)
  - 5 WhatsApp Status posts (health tips, camp promos)

No AI calls needed — uses pre-built data.

Usage:
    cd backend
    python seed_star_posters.py
"""
import asyncio, sys, os, uuid
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.config import settings
from app.models.tenant import Tenant
from app.models.poster_variant import PosterVariant
from app.models.social import SocialPost

# Import related models so SQLAlchemy can resolve string-based relationships
import app.models.brand_profile  # noqa - required for PosterVariant.brand_profile relationship
import app.models.poster_template  # noqa - required for PosterVariant.template relationship
import app.models.campaign  # noqa - required for PosterVariant FK

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

BUNTY_SLUG = "bunty-demo"

# ── Pre-built Poster JSON Templates ──────────────────────────────────────────

def make_ortho_poster_instagram(org_name: str, city: str, offer_price: str, doctor: str) -> dict:
    """Orthopedic health camp poster — Instagram Square 1080x1080"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {
                "type": "background",
                "gradient": "135deg, #1E3A8A 0%, #1E40AF 100%"
            },
            {
                "type": "shapes",
                "shapes": [
                    {"type": "circle", "size": 500, "x": -150, "y": -150, "color": "rgba(255,255,255,0.04)"},
                    {"type": "circle", "size": 350, "x": 830, "y": 750, "color": "rgba(245,158,11,0.12)"},
                    {"type": "circle", "border": True, "size": 280, "x": 820, "y": -80, "color": "rgba(255,255,255,0.08)"}
                ]
            },
            {
                "type": "accent_strip",
                "color": "#F59E0B",
                "height": 8
            },
            {
                "type": "logo",
                "value": org_name[:2].upper(),
                "x": 40, "y": 40, "w": 120, "h": 60
            },
            {
                "type": "badge",
                "value": "FREE CHECKUP",
                "x": 440, "y": 135,
                "bg": "#F59E0B", "text_color": "#000000", "font_size": 26, "bold": True
            },
            {
                "type": "title",
                "value": f"Orthopaedic Health Camp",
                "x": 40, "y": 220, "w": 1000,
                "font_size": 52, "bold": True, "color": "#FFFFFF", "align": "center"
            },
            {
                "type": "subtitle",
                "value": f"Bone, Joint & Spine Specialist Care — {city}",
                "x": 40, "y": 295, "w": 1000,
                "font_size": 26, "color": "#BFDBFE", "align": "center"
            },
            {
                "type": "text",
                "value": f"👨‍⚕️ {doctor}" if doctor else "👨‍⚕️ Expert Orthopaedic Surgeons",
                "x": 60, "y": 365,
                "font_size": 24, "color": "#FCD34D", "bold": True
            },
            {
                "type": "service_grid",
                "items": [
                    "Orthopaedic Consultation",
                    "X-Ray & Imaging",
                    "Physiotherapy Session",
                    "Bone Density Test",
                    "Joint Replacement Consult",
                    "Sports Injury Check"
                ],
                "columns": 2,
                "icon": "✓",
                "icon_color": "#F59E0B",
                "item_bg": "rgba(255,255,255,0.08)"
            },
            {
                "type": "price_block",
                "value": offer_price,
                "x": 40, "y": 740, "w": 1000,
                "font_size": 72, "color": "#F59E0B", "bold": True, "align": "center"
            },
            {
                "type": "original_price",
                "value": "₹1,000",
                "x": 40, "y": 825, "w": 1000,
                "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"
            },
            {
                "type": "date_block",
                "value": "📅 15–30 March 2026  |  9:00 AM – 5:00 PM",
                "x": 40, "y": 875, "w": 1000,
                "font_size": 24, "color": "#FFFFFF", "bold": True, "align": "center"
            },
            {
                "type": "cta",
                "value": "📞 Call Now to Register",
                "x": 40, "y": 920, "w": 1000, "h": 72,
                "bg": "#F59E0B", "text_color": "#000000", "font_size": 32, "bold": True, "border_radius": 12
            },
            {
                "type": "footer",
                "value": f"{org_name}  •  Star Hospital  •  Kothagudem",
                "x": 0, "y": 1005, "w": 1080, "h": 75,
                "bg": "#0F172A", "text_color": "#FFFFFF", "font_size": 20
            }
        ],
        "meta": {
            "template_slug": "orthopedic_health_camp",
            "org_name": org_name,
            "city": city
        }
    }


def make_ortho_poster_facebook(org_name: str, city: str, offer_price: str, doctor: str) -> dict:
    """Orthopedic health camp — Facebook Post 1200x630"""
    return {
        "platform": "facebook_post",
        "dimensions": {"width": 1200, "height": 630},
        "layers": [
            {
                "type": "background",
                "gradient": "135deg, #1E3A8A 0%, #1E40AF 100%"
            },
            {
                "type": "shapes",
                "shapes": [
                    {"type": "circle", "size": 400, "x": -100, "y": -100, "color": "rgba(255,255,255,0.05)"},
                    {"type": "circle", "size": 300, "x": 1000, "y": 350, "color": "rgba(245,158,11,0.1)"},
                ]
            },
            {
                "type": "accent_strip",
                "color": "#F59E0B",
                "height": 7
            },
            {
                "type": "badge",
                "value": "FREE CHECKUP",
                "x": 460, "y": 75,
                "bg": "#F59E0B", "text_color": "#000000", "font_size": 22, "bold": True
            },
            {
                "type": "title",
                "value": "Orthopaedic Health Camp",
                "x": 40, "y": 130, "w": 1120,
                "font_size": 48, "bold": True, "color": "#FFFFFF", "align": "center"
            },
            {
                "type": "subtitle",
                "value": f"Expert Bone, Joint & Spine Care — {city} | {offer_price} Only",
                "x": 40, "y": 195, "w": 1120,
                "font_size": 24, "color": "#BFDBFE", "align": "center"
            },
            {
                "type": "text",
                "value": f"👨‍⚕️ {doctor}" if doctor else "👨‍⚕️ Expert Orthopaedic Team",
                "x": 60, "y": 248,
                "font_size": 22, "color": "#FCD34D", "bold": True
            },
            {
                "type": "service_grid",
                "items": [
                    "Orthopaedic Consultation",
                    "X-Ray & MRI Review",
                    "Physiotherapy Session",
                    "Joint Replacement Advice",
                ],
                "columns": 2,
                "icon": "✓",
                "icon_color": "#F59E0B",
                "item_bg": "rgba(255,255,255,0.08)"
            },
            {
                "type": "stat_row",
                "items": [
                    {"value": "500+", "label": "Patients Treated"},
                    {"value": "15+", "label": "Years Experience"},
                    {"value": "98%", "label": "Success Rate"},
                ],
                "value_color": "#F59E0B"
            },
            {
                "type": "cta",
                "value": "📞 Register Now — Limited Slots!",
                "x": 40, "y": 560, "w": 1120, "h": 56,
                "bg": "#F59E0B", "text_color": "#000000", "font_size": 28, "bold": True, "border_radius": 10
            },
            {
                "type": "footer",
                "value": f"{org_name}  •  {city}  |  📅 15–30 March 2026",
                "x": 0, "y": 630, "w": 1200, "h": 0,
                "bg": "#0F172A", "text_color": "#FFFFFF", "font_size": 18
            }
        ],
        "meta": {
            "template_slug": "orthopedic_health_camp",
            "org_name": org_name,
            "city": city
        }
    }


def make_diabetes_poster_instagram(org_name: str, city: str) -> dict:
    """Diabetes health camp — Instagram Square 1080x1080"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {
                "type": "background",
                "gradient": "135deg, #065F46 0%, #047857 100%"
            },
            {
                "type": "shapes",
                "shapes": [
                    {"type": "circle", "size": 480, "x": -120, "y": -120, "color": "rgba(255,255,255,0.04)"},
                    {"type": "circle", "size": 320, "x": 840, "y": 800, "color": "rgba(16,185,129,0.15)"},
                ]
            },
            {
                "type": "accent_strip",
                "color": "#10B981",
                "height": 8
            },
            {
                "type": "badge",
                "value": "FREE SCREENING",
                "x": 420, "y": 135,
                "bg": "#10B981", "text_color": "#000000", "font_size": 26, "bold": True
            },
            {
                "type": "title",
                "value": "Diabetes Screening Camp",
                "x": 40, "y": 220, "w": 1000,
                "font_size": 52, "bold": True, "color": "#FFFFFF", "align": "center"
            },
            {
                "type": "subtitle",
                "value": f"Know Your Sugar Levels — Free Check in {city}",
                "x": 40, "y": 295, "w": 1000,
                "font_size": 26, "color": "#A7F3D0", "align": "center"
            },
            {
                "type": "service_grid",
                "items": [
                    "Blood Sugar Test (HbA1c)",
                    "Diet Consultation",
                    "Diabetes Education",
                    "Insulin Management",
                    "Foot Care Check",
                    "Eye Screening"
                ],
                "columns": 2,
                "icon": "✓",
                "icon_color": "#10B981",
                "item_bg": "rgba(255,255,255,0.08)"
            },
            {
                "type": "price_block",
                "value": "FREE",
                "x": 40, "y": 740, "w": 1000,
                "font_size": 72, "color": "#10B981", "bold": True, "align": "center"
            },
            {
                "type": "date_block",
                "value": "📅 Every Saturday  |  9:00 AM – 1:00 PM",
                "x": 40, "y": 830, "w": 1000,
                "font_size": 24, "color": "#FFFFFF", "bold": True, "align": "center"
            },
            {
                "type": "cta",
                "value": "📞 Book Your Free Screening",
                "x": 40, "y": 900, "w": 1000, "h": 72,
                "bg": "#10B981", "text_color": "#000000", "font_size": 32, "bold": True, "border_radius": 12
            },
            {
                "type": "footer",
                "value": f"{org_name}  •  Star Hospital  •  {city}",
                "x": 0, "y": 985, "w": 1080, "h": 75,
                "bg": "#022C22", "text_color": "#FFFFFF", "font_size": 20
            }
        ],
        "meta": {
            "template_slug": "diabetes_health_camp",
            "org_name": org_name,
            "city": city
        }
    }


def make_general_health_poster_whatsapp(org_name: str, city: str) -> dict:
    """General health camp — WhatsApp Share 1080x1080"""
    return {
        "platform": "whatsapp_share",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {
                "type": "background",
                "gradient": "135deg, #0C4A6E 0%, #0369A1 100%"
            },
            {
                "type": "shapes",
                "shapes": [
                    {"type": "circle", "size": 460, "x": -110, "y": -110, "color": "rgba(255,255,255,0.04)"},
                    {"type": "circle", "size": 300, "x": 860, "y": 820, "color": "rgba(56,189,248,0.12)"},
                ]
            },
            {
                "type": "accent_strip",
                "color": "#38BDF8",
                "height": 8
            },
            {
                "type": "badge",
                "value": "FREE HEALTH CHECK",
                "x": 400, "y": 135,
                "bg": "#38BDF8", "text_color": "#000000", "font_size": 24, "bold": True
            },
            {
                "type": "title",
                "value": "Multi-Speciality Health Camp",
                "x": 40, "y": 215, "w": 1000,
                "font_size": 50, "bold": True, "color": "#FFFFFF", "align": "center"
            },
            {
                "type": "subtitle",
                "value": f"Complete Health Screening — {city}",
                "x": 40, "y": 290, "w": 1000,
                "font_size": 26, "color": "#BAE6FD", "align": "center"
            },
            {
                "type": "service_grid",
                "items": [
                    "BP & Sugar Test",
                    "BMI Check",
                    "ECG",
                    "Doctor Consultation",
                    "Nutrition Advice",
                    "Eye Screening"
                ],
                "columns": 2,
                "icon": "✚",
                "icon_color": "#38BDF8",
                "item_bg": "rgba(255,255,255,0.08)"
            },
            {
                "type": "stat_row",
                "items": [
                    {"value": "1000+", "label": "Patients Served"},
                    {"value": "10+", "label": "Specialities"},
                    {"value": "24/7", "label": "Emergency Care"},
                ],
                "value_color": "#38BDF8"
            },
            {
                "type": "cta",
                "value": "📞 Register — Free Entry!",
                "x": 40, "y": 900, "w": 1000, "h": 72,
                "bg": "#38BDF8", "text_color": "#000000", "font_size": 32, "bold": True, "border_radius": 12
            },
            {
                "type": "footer",
                "value": f"{org_name}  •  Star Hospital  •  {city}  |  📅 20 March 2026",
                "x": 0, "y": 985, "w": 1080, "h": 75,
                "bg": "#082F49", "text_color": "#FFFFFF", "font_size": 20
            }
        ],
        "meta": {
            "template_slug": "general_health_camp",
            "org_name": org_name,
            "city": city
        }
    }


async def seed():
    async with async_session() as session:
        # Get bunty tenant
        result = await session.execute(
            select(Tenant).where(Tenant.slug == BUNTY_SLUG)
        )
        tenant = result.scalar_one_or_none()
        if not tenant:
            print(f"[ERROR] Tenant '{BUNTY_SLUG}' not found. Run seed_bunty.py first.")
            return

        print(f"[OK] Found tenant: {tenant.name} ({tenant.email})")

        # Check existing variants
        existing = await session.execute(
            select(PosterVariant).where(PosterVariant.tenant_id == tenant.id)
        )
        count = len(existing.scalars().all())
        print(f"[INFO] Existing poster variants: {count}")

        org_name = "Star Hospital"
        city = "Kothagudem"
        doctor = "Dr. Shashi (MBBS, MS Ortho)"

        variants_to_create = [
            # Orthopedic Poster 1 — Instagram Square ₹500
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="instagram_square",
                width="1080",
                height="1080",
                language_primary="english",
                language_secondary="telugu",
                status="ready",
                social_caption=(
                    f"🦴 FREE Orthopaedic Health Camp at {org_name}, {city}!\n\n"
                    "Don't let pain slow you down. Get expert bone, joint & spine check-up.\n\n"
                    f"✅ Only ₹500 Consultation | Original ₹1,000\n"
                    f"📅 15–30 March 2026 | 9 AM – 5 PM\n\n"
                    "#OrthopedicCamp #FreeHealthCheckup #StarHospital #Kothagudem #BoneHealth"
                ),
                hashtags=["OrthopedicCamp", "FreeCheckup", "StarHospital", "Kothagudem", "BoneHealth", "JointPain"],
                poster_json=make_ortho_poster_instagram(org_name, city, "₹500", doctor),
                campaign_data={
                    "template_slug": "orthopedic_health_camp",
                    "org_name": org_name,
                    "city": city,
                    "offer_price": "₹500",
                    "secondary_language": "telugu",
                },
                created_at=datetime.now(timezone.utc),
            ),
            # Orthopedic Poster 2 — Facebook ₹500
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="facebook_post",
                width="1200",
                height="630",
                language_primary="english",
                language_secondary="telugu",
                status="ready",
                social_caption=(
                    f"🏥 {org_name} presents FREE Orthopaedic Health Camp!\n\n"
                    "Get complete bone, joint & spine check-up by expert orthopaedic surgeons.\n"
                    f"💰 Only ₹500 (Worth ₹1,000+) | 📅 March 15–30, 2026\n\n"
                    "#StarHospital #OrthopaedicCamp #Kothagudem #BoneHealth #FreeCheckup"
                ),
                hashtags=["StarHospital", "Kothagudem", "OrthopaedicCamp", "BoneHealth"],
                poster_json=make_ortho_poster_facebook(org_name, city, "₹500", doctor),
                campaign_data={
                    "template_slug": "orthopedic_health_camp",
                    "org_name": org_name,
                    "city": city,
                    "offer_price": "₹500",
                    "secondary_language": "telugu",
                },
                created_at=datetime.now(timezone.utc),
            ),
            # Diabetes Poster — Instagram
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="instagram_square",
                width="1080",
                height="1080",
                language_primary="english",
                language_secondary="telugu",
                status="ready",
                social_caption=(
                    f"💉 FREE Diabetes Screening at {org_name}, {city}!\n\n"
                    "Know your sugar levels. Early detection saves lives.\n"
                    "Every Saturday | 9 AM – 1 PM | No appointment needed!\n\n"
                    "#DiabetesScreening #FreeCamp #StarHospital #Kothagudem #HealthFirst"
                ),
                hashtags=["DiabetesScreening", "FreeCamp", "StarHospital", "Kothagudem", "SugarTest"],
                poster_json=make_diabetes_poster_instagram(org_name, city),
                campaign_data={
                    "template_slug": "diabetes_health_camp",
                    "org_name": org_name,
                    "city": city,
                    "secondary_language": "telugu",
                },
                created_at=datetime.now(timezone.utc),
            ),
            # General Health — WhatsApp
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp_share",
                width="1080",
                height="1080",
                language_primary="english",
                language_secondary="telugu",
                status="ready",
                social_caption=(
                    f"🏥 Multi-Speciality Free Health Camp at {org_name}!\n\n"
                    "BP check, Sugar test, ECG, Doctor consultation — all FREE!\n"
                    "📅 20 March 2026 | 9 AM – 4 PM\n\n"
                    "Share this with your family! 🙏\n\n"
                    "#FreeHealthCamp #StarHospital #Kothagudem #HealthCare"
                ),
                hashtags=["FreeHealthCamp", "StarHospital", "Kothagudem", "MultiSpeciality", "HealthCheck"],
                poster_json=make_general_health_poster_whatsapp(org_name, city),
                campaign_data={
                    "template_slug": "general_health_camp",
                    "org_name": org_name,
                    "city": city,
                    "secondary_language": "telugu",
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

        for v in variants_to_create:
            session.add(v)

        # ── WhatsApp Status Posts ─────────────────────────────────────────────
        whatsapp_posts = [
            SocialPost(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp",
                campaign="Morning Health Tip",
                content=(
                    "🌅 *Good Morning from Star Hospital, Kothagudem!*\n\n"
                    "💊 *Today's Health Tip:*\n\n"
                    "Drink a glass of warm water every morning. It:\n"
                    "✅ Boosts immunity\n"
                    "✅ Aids digestion\n"
                    "✅ Improves metabolism\n\n"
                    "📞 Appointments: +91-98001-77001\n"
                    "Stay healthy! 🙏 *#StarHospital #HealthTip*"
                ),
                status="published",
                ai_generated=False,
                published_at=datetime.now(timezone.utc) - timedelta(hours=6),
            ),
            SocialPost(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp",
                campaign="Orthopaedic Camp ₹500",
                content=(
                    "🦴 *FREE Orthopaedic Camp — Star Hospital Kothagudem!*\n\n"
                    "Suffering from:\n"
                    "🔴 Knee Pain / Hip Pain\n"
                    "🔴 Back Pain / Slip Disc\n"
                    "🔴 Sports Injury / Fracture\n\n"
                    "📢 *Special Offer:*\n"
                    "💰 Only *₹500* (Original ₹1,000)\n"
                    "Includes X-Ray + Doctor Consultation\n\n"
                    "📅 15–30 March 2026 | 9 AM – 5 PM\n"
                    "📍 Star Hospital, Kothagudem\n\n"
                    "📞 Register: +91-98001-77001\n"
                    "⚠️ Limited slots — Book today!"
                ),
                status="scheduled",
                ai_generated=False,
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            ),
            SocialPost(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp",
                campaign="Diabetes Free Screening",
                content=(
                    "💉 *FREE Diabetes Screening — Every Saturday!*\n\n"
                    "Know your sugar levels. Early detection saves lives.\n\n"
                    "🔍 *Includes:*\n"
                    "✅ Blood Sugar Test (HbA1c)\n"
                    "✅ Diet Consultation\n"
                    "✅ Doctor Advice\n\n"
                    "⏰ Every Saturday | 9 AM – 1 PM\n"
                    "📍 Star Hospital, Kothagudem\n"
                    "📞 +91-98001-77001\n\n"
                    "*Bring a family member — it's FREE for all!* 🙏"
                ),
                status="published",
                ai_generated=False,
                published_at=datetime.now(timezone.utc) - timedelta(days=2),
            ),
            SocialPost(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp",
                campaign="Patient Testimonial",
                content=(
                    "⭐⭐⭐⭐⭐ *Patient Success Story*\n\n"
                    "_\"I had severe knee pain for 3 years. After treatment at Star Hospital, "
                    "I can walk 5 km daily without pain. Thank you Dr. Shashi!\"_\n\n"
                    "— *Ramaiah G., 58, Kothagudem*\n\n"
                    "📞 Book your consultation: +91-98001-77001\n"
                    "🏥 Star Hospital, Kothagudem — Your Health, Our Priority"
                ),
                status="published",
                ai_generated=False,
                published_at=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            SocialPost(
                id=uuid.uuid4(),
                tenant_id=tenant.id,
                platform="whatsapp",
                campaign="Multi-Speciality Free Camp",
                content=(
                    "🏥 *Free Multi-Speciality Health Camp*\n"
                    "📅 *20 March 2026 | 9 AM – 4 PM*\n\n"
                    "🎯 *All Tests FREE:*\n"
                    "• BP & Sugar Check\n"
                    "• BMI & Weight\n"
                    "• ECG\n"
                    "• Eye Screening\n"
                    "• Doctor Consultation\n\n"
                    "📍 Star Hospital, Kothagudem\n"
                    "📞 Pre-registration: +91-98001-77001\n\n"
                    "Share with family & friends! 🙏\n"
                    "*#FreeHealthCamp #StarHospital #Kothagudem*"
                ),
                status="draft",
                ai_generated=False,
            ),
        ]

        for wp in whatsapp_posts:
            session.add(wp)

        await session.commit()
        print(f"\n[SUCCESS] Created {len(variants_to_create)} poster variants for {org_name}:")
        for v in variants_to_create:
            print(f"  ✓ {v.platform} — {v.campaign_data.get('template_slug', 'unknown')} — {v.campaign_data.get('offer_price', 'FREE')}")

        print(f"\n[SUCCESS] Created {len(whatsapp_posts)} WhatsApp status posts:")
        for wp in whatsapp_posts:
            print(f"  ✓ [{wp.status}] {wp.campaign}")

        print("\n[INFO] Log in as bunty@srp.ai → Poster Gallery + WhatsApp Status to see them.")


if __name__ == "__main__":
    asyncio.run(seed())
