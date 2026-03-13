#!/usr/bin/env python3
"""
Global Demo Poster Seeder — SRP AI Marketing OS
Seeds extra poster variants for client demo purposes:

  • Bengaluru IT Agency  — Hindi bilingual job opening (→ demo@srp.ai)
  • Bunty Cloth Store    — Hindi bilingual discount offer (→ bunty@srp.ai)
  • Australia demo       — English retail poster (→ demo@srp.ai)
  • New Zealand demo     — English event poster (→ demo@srp.ai)

Usage:
    cd backend
    python seed_global_demo.py
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

# Load related models so FK relationships resolve
import app.models.brand_profile   # noqa
import app.models.poster_template  # noqa
import app.models.campaign         # noqa

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ─────────────────────────────────────────────────────────────────────────────
# Poster JSON builder helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_it_job_poster_instagram(company: str, city: str, role: str, salary: str) -> dict:
    """Bengaluru IT agency — job opening — Instagram square 1080×1080 (Hindi/English bilingual)"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {"type": "background", "gradient": "135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 600, "x": -200, "y": -200, "color": "rgba(99,102,241,0.08)"},
                {"type": "circle", "size": 400, "x": 900, "y": 800, "color": "rgba(99,102,241,0.06)"},
                {"type": "rect", "x": 0, "y": 0, "w": 8, "h": 1080, "color": "#6366F1"},
            ]},
            {"type": "badge", "value": "नौकरी उपलब्ध / HIRING NOW",
             "x": 200, "y": 80, "bg": "#6366F1", "text_color": "#FFFFFF",
             "font_size": 22, "bold": True},
            {"type": "title", "value": role,
             "x": 40, "y": 160, "w": 1000,
             "font_size": 52, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": f"{company}  •  {city}",
             "x": 40, "y": 230, "w": 1000,
             "font_size": 28, "color": "#A5B4FC", "align": "center"},
            {"type": "text", "value": "आईटी / सॉफ्टवेयर इंडस्ट्री  |  IT / Software Industry",
             "x": 40, "y": 285, "w": 1000,
             "font_size": 22, "color": "#94A3B8", "align": "center"},
            {"type": "service_grid",
             "items": [
                 "React / Angular / Vue.js",
                 "Python / Django / FastAPI",
                 "Node.js / TypeScript",
                 "AWS / Azure / DevOps",
                 "Full Stack Development",
                 "AI / ML Integration",
             ],
             "columns": 2, "icon": "💻", "icon_color": "#6366F1",
             "item_bg": "rgba(99,102,241,0.10)"},
            {"type": "stat_row", "items": [
                {"value": salary, "label": "वेतन / Salary"},
                {"value": "50+", "label": "Opening"},
                {"value": "Hybrid", "label": "Work Mode"},
            ], "value_color": "#818CF8"},
            {"type": "text", "value": "📧 careers@" + company.lower().replace(" ", "") + ".com",
             "x": 40, "y": 820, "w": 1000,
             "font_size": 24, "color": "#A5B4FC", "align": "center", "bold": True},
            {"type": "cta", "value": "📩 अभी Apply करें / Apply Now",
             "x": 40, "y": 880, "w": 1000, "h": 72,
             "bg": "#6366F1", "text_color": "#FFFFFF", "font_size": 30, "bold": True, "border_radius": 12},
            {"type": "footer", "value": f"{company}  •  {city}  |  We're Hiring!",
             "x": 0, "y": 1005, "w": 1080, "h": 75,
             "bg": "#1E1B4B", "text_color": "#FFFFFF", "font_size": 20},
        ],
        "meta": {"template_slug": "job_opening", "org_name": company, "city": city},
    }


def make_it_job_poster_linkedin(company: str, city: str, role: str, salary: str) -> dict:
    """Bengaluru IT agency — LinkedIn banner 1200×628"""
    return {
        "platform": "linkedin_banner",
        "dimensions": {"width": 1200, "height": 628},
        "layers": [
            {"type": "background", "gradient": "120deg, #0F172A 0%, #1E3A8A 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 500, "x": -150, "y": -150, "color": "rgba(99,102,241,0.08)"},
                {"type": "circle", "size": 350, "x": 1050, "y": 400, "color": "rgba(99,102,241,0.06)"},
            ]},
            {"type": "badge", "value": "WE'RE HIRING",
             "x": 30, "y": 50, "bg": "#6366F1", "text_color": "#FFFFFF",
             "font_size": 22, "bold": True},
            {"type": "title", "value": f"{role}",
             "x": 40, "y": 110, "w": 1120,
             "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "left"},
            {"type": "subtitle", "value": f"{company}  •  {city}  |  IT / हिंदी-English Workspace",
             "x": 40, "y": 185, "w": 1120,
             "font_size": 26, "color": "#BFDBFE", "align": "left"},
            {"type": "service_grid",
             "items": ["Full Stack Development", "AI/ML Projects", "Agile Sprints", "Hybrid Work"],
             "columns": 4, "icon": "✓", "icon_color": "#818CF8",
             "item_bg": "rgba(99,102,241,0.10)"},
            {"type": "stat_row", "items": [
                {"value": salary, "label": "Package"},
                {"value": city, "label": "Location"},
                {"value": "Immediate", "label": "Joining"},
            ], "value_color": "#818CF8"},
            {"type": "cta", "value": "Apply at linkedin.com/company/" + company.lower().replace(" ", "-"),
             "x": 40, "y": 560, "w": 1120, "h": 50,
             "bg": "#6366F1", "text_color": "#FFFFFF", "font_size": 24, "bold": True, "border_radius": 8},
        ],
        "meta": {"template_slug": "job_opening", "org_name": company, "city": city},
    }


def make_cloth_discount_instagram(org_name: str, city: str, discount: str) -> dict:
    """Bunty Cloth Store — Hindi discount offer — Instagram 1080×1080"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {"type": "background", "gradient": "135deg, #7F1D1D 0%, #DC2626 50%, #B91C1C 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 700, "x": -250, "y": -250, "color": "rgba(255,255,255,0.04)"},
                {"type": "circle", "size": 500, "x": 900, "y": 700, "color": "rgba(251,191,36,0.12)"},
                {"type": "circle", "border": True, "size": 320, "x": 840, "y": -80,
                 "color": "rgba(251,191,36,0.2)"},
            ]},
            {"type": "accent_strip", "color": "#FCD34D", "height": 10},
            {"type": "logo", "value": org_name[:2].upper(), "x": 40, "y": 40, "w": 120, "h": 60},
            {"type": "badge", "value": f"SALE • {discount} OFF",
             "x": 340, "y": 125,
             "bg": "#FCD34D", "text_color": "#7F1D1D", "font_size": 32, "bold": True},
            {"type": "title", "value": "महा सेल / MEGA SALE",
             "x": 40, "y": 220, "w": 1000,
             "font_size": 72, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": "कपड़ों पर बड़ी छूट / Big Discount on All Clothes",
             "x": 40, "y": 310, "w": 1000,
             "font_size": 30, "color": "#FEF3C7", "align": "center"},
            {"type": "service_grid",
             "items": [
                 "सूट & साड़ी / Suits & Sarees",
                 "शर्ट & पैंट / Shirts & Pants",
                 "लेहंगा & कुर्ती / Lehenga & Kurti",
                 "जींस & टी-शर्ट / Jeans & T-shirts",
                 "किड्स वियर / Kids Wear",
                 "वेडिंग कलेक्शन / Wedding",
             ],
             "columns": 2, "icon": "🎁", "icon_color": "#FCD34D",
             "item_bg": "rgba(0,0,0,0.15)"},
            {"type": "price_block", "value": discount + " OFF",
             "x": 40, "y": 730, "w": 1000,
             "font_size": 90, "color": "#FCD34D", "bold": True, "align": "center"},
            {"type": "text", "value": "सभी ब्रांड्स पर / On All Brands  |  Limited Time Offer!",
             "x": 40, "y": 840, "w": 1000,
             "font_size": 26, "color": "#FEF3C7", "align": "center"},
            {"type": "cta", "value": "🛍️ आज ही खरीदें / Shop Today",
             "x": 40, "y": 900, "w": 1000, "h": 72,
             "bg": "#FCD34D", "text_color": "#7F1D1D", "font_size": 32, "bold": True,
             "border_radius": 12},
            {"type": "footer", "value": f"{org_name}  •  {city}  |  📞 Call for more info",
             "x": 0, "y": 1005, "w": 1080, "h": 75,
             "bg": "#450A0A", "text_color": "#FFFFFF", "font_size": 20},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": org_name, "city": city},
    }


def make_cloth_discount_whatsapp(org_name: str, city: str, discount: str) -> dict:
    """Bunty Cloth Store — WhatsApp share 1080×1080 compact"""
    return {
        "platform": "whatsapp_share",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {"type": "background", "gradient": "160deg, #7C2D12 0%, #EA580C 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 600, "x": -150, "y": -150, "color": "rgba(255,255,255,0.05)"},
                {"type": "circle", "size": 400, "x": 900, "y": 750, "color": "rgba(251,191,36,0.1)"},
            ]},
            {"type": "accent_strip", "color": "#FCD34D", "height": 8},
            {"type": "badge", "value": "सीमित समय / LIMITED TIME",
             "x": 320, "y": 100,
             "bg": "#FCD34D", "text_color": "#7C2D12", "font_size": 24, "bold": True},
            {"type": "title", "value": f"🎉 {discount} की छूट!",
             "x": 40, "y": 190, "w": 1000,
             "font_size": 80, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": "हर कपड़े पर / On Every Item",
             "x": 40, "y": 285, "w": 1000,
             "font_size": 34, "color": "#FEF3C7", "align": "center"},
            {"type": "text", "value": org_name,
             "x": 40, "y": 360, "w": 1000,
             "font_size": 40, "bold": True, "color": "#FCD34D", "align": "center"},
            {"type": "text", "value": city,
             "x": 40, "y": 420, "w": 1000,
             "font_size": 28, "color": "#FED7AA", "align": "center"},
            {"type": "service_grid",
             "items": [
                 "साड़ी / Saree", "सूट / Suits", "कुर्ती / Kurti",
                 "शर्ट / Shirts", "जींस / Jeans", "Kids Wear",
             ],
             "columns": 3, "icon": "✂️", "icon_color": "#FCD34D",
             "item_bg": "rgba(0,0,0,0.2)"},
            {"type": "cta", "value": "📞 अभी Call करें — जल्दी करें!",
             "x": 40, "y": 880, "w": 1000, "h": 72,
             "bg": "#FCD34D", "text_color": "#7C2D12", "font_size": 32, "bold": True,
             "border_radius": 12},
            {"type": "footer", "value": f"{org_name}  •  आज ही आएं — Don't Miss!",
             "x": 0, "y": 1005, "w": 1080, "h": 75,
             "bg": "#431407", "text_color": "#FFFFFF", "font_size": 18},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": org_name, "city": city},
    }


def make_australia_poster_instagram(company: str, city: str, category: str) -> dict:
    """Australia retail/service poster — Instagram 1080×1080 (English)"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {"type": "background", "gradient": "140deg, #00284F 0%, #003D75 50%, #00284F 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 600, "x": -200, "y": -200, "color": "rgba(255,215,0,0.06)"},
                {"type": "circle", "size": 400, "x": 900, "y": 800, "color": "rgba(255,0,0,0.06)"},
                {"type": "rect", "x": 0, "y": 0, "w": 1080, "h": 12, "color": "#FFCD00"},
                {"type": "rect", "x": 0, "y": 1068, "w": 1080, "h": 12, "color": "#FF0000"},
            ]},
            {"type": "badge", "value": "🇦🇺 AUSTRALIA",
             "x": 390, "y": 80,
             "bg": "#FFCD00", "text_color": "#00284F", "font_size": 26, "bold": True},
            {"type": "title", "value": company,
             "x": 40, "y": 170, "w": 1000,
             "font_size": 58, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": f"{category}  |  {city}, Australia",
             "x": 40, "y": 250, "w": 1000,
             "font_size": 28, "color": "#93C5FD", "align": "center"},
            {"type": "service_grid",
             "items": [
                 "Premium Quality Products",
                 "Australian Owned & Operated",
                 "Fast Delivery Nationwide",
                 "100% Satisfaction Guarantee",
                 "Competitive Pricing",
                 "Expert Customer Support",
             ],
             "columns": 2, "icon": "⭐", "icon_color": "#FFCD00",
             "item_bg": "rgba(255,255,255,0.07)"},
            {"type": "stat_row", "items": [
                {"value": "10K+", "label": "Customers"},
                {"value": "4.9★", "label": "Rating"},
                {"value": "15yr", "label": "Experience"},
            ], "value_color": "#FFCD00"},
            {"type": "text", "value": f"📍 {city}, Australia  |  🌐 srpailabs.com",
             "x": 40, "y": 840, "w": 1000,
             "font_size": 24, "color": "#BFDBFE", "align": "center"},
            {"type": "cta", "value": "📞 Get a Free Quote Today!",
             "x": 40, "y": 895, "w": 1000, "h": 72,
             "bg": "#FFCD00", "text_color": "#00284F", "font_size": 32, "bold": True,
             "border_radius": 12},
            {"type": "footer", "value": f"{company}  •  {city}, Australia",
             "x": 0, "y": 1005, "w": 1080, "h": 75,
             "bg": "#001F3F", "text_color": "#FFFFFF", "font_size": 20},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": company, "city": city},
    }


def make_australia_poster_facebook(company: str, city: str, category: str) -> dict:
    """Australia — Facebook post 1200×630"""
    return {
        "platform": "facebook_post",
        "dimensions": {"width": 1200, "height": 630},
        "layers": [
            {"type": "background", "gradient": "140deg, #00284F 0%, #00498F 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 450, "x": -100, "y": -100, "color": "rgba(255,215,0,0.06)"},
                {"type": "circle", "size": 300, "x": 1100, "y": 450, "color": "rgba(255,0,0,0.05)"},
            ]},
            {"type": "badge", "value": "🇦🇺 AUSTRALIA — TRUSTED BRAND",
             "x": 330, "y": 50,
             "bg": "#FFCD00", "text_color": "#00284F", "font_size": 20, "bold": True},
            {"type": "title", "value": company,
             "x": 40, "y": 105, "w": 1120,
             "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": f"{category}  •  {city}, Australia",
             "x": 40, "y": 172, "w": 1120,
             "font_size": 26, "color": "#BFDBFE", "align": "center"},
            {"type": "service_grid",
             "items": ["Premium Quality", "Nationwide Delivery", "Satisfaction Guaranteed", "Expert Support"],
             "columns": 4, "icon": "✓", "icon_color": "#FFCD00",
             "item_bg": "rgba(255,255,255,0.07)"},
            {"type": "stat_row", "items": [
                {"value": "10K+", "label": "Happy Customers"},
                {"value": "4.9★", "label": "Google Rating"},
                {"value": city, "label": "Location"},
            ], "value_color": "#FFCD00"},
            {"type": "cta", "value": "📞 Call Now for a Free Consultation!",
             "x": 40, "y": 563, "w": 1120, "h": 55,
             "bg": "#FFCD00", "text_color": "#00284F", "font_size": 28, "bold": True, "border_radius": 10},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": company, "city": city},
    }


def make_nz_poster_instagram(company: str, city: str, category: str) -> dict:
    """New Zealand poster — Instagram 1080×1080 (English)"""
    return {
        "platform": "instagram_square",
        "dimensions": {"width": 1080, "height": 1080},
        "layers": [
            {"type": "background", "gradient": "140deg, #0C2340 0%, #003366 50%, #0C2340 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 650, "x": -220, "y": -220, "color": "rgba(255,255,255,0.04)"},
                {"type": "circle", "size": 420, "x": 920, "y": 820, "color": "rgba(255,255,255,0.04)"},
                {"type": "rect", "x": 0, "y": 0, "w": 1080, "h": 12, "color": "#FFFFFF"},
                {"type": "rect", "x": 0, "y": 1068, "w": 1080, "h": 12, "color": "#CC0000"},
            ]},
            {"type": "badge", "value": "🇳🇿 NEW ZEALAND",
             "x": 380, "y": 80,
             "bg": "#CC0000", "text_color": "#FFFFFF", "font_size": 26, "bold": True},
            {"type": "title", "value": company,
             "x": 40, "y": 170, "w": 1000,
             "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": f"{category}  |  {city}, New Zealand",
             "x": 40, "y": 248, "w": 1000,
             "font_size": 28, "color": "#93C5FD", "align": "center"},
            {"type": "service_grid",
             "items": [
                 "NZ Owned & Operated",
                 "Eco-Friendly Products",
                 "Free Kiwi Delivery",
                 "5-Star Rated Service",
                 "Expert Local Team",
                 "Best Price Promise",
             ],
             "columns": 2, "icon": "🥝", "icon_color": "#86EFAC",
             "item_bg": "rgba(255,255,255,0.07)"},
            {"type": "stat_row", "items": [
                {"value": "5K+", "label": "Kiwi Customers"},
                {"value": "5.0★", "label": "Rating"},
                {"value": "NZ-Made", "label": "Products"},
            ], "value_color": "#86EFAC"},
            {"type": "text", "value": f"📍 {city}, Aotearoa New Zealand",
             "x": 40, "y": 840, "w": 1000,
             "font_size": 26, "color": "#BFDBFE", "align": "center"},
            {"type": "cta", "value": "🛒 Shop Now — Free NZ Delivery!",
             "x": 40, "y": 895, "w": 1000, "h": 72,
             "bg": "#CC0000", "text_color": "#FFFFFF", "font_size": 32, "bold": True,
             "border_radius": 12},
            {"type": "footer", "value": f"{company}  •  {city}, New Zealand  |  Kia Ora! 🤙",
             "x": 0, "y": 1005, "w": 1080, "h": 75,
             "bg": "#060F1F", "text_color": "#FFFFFF", "font_size": 20},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": company, "city": city},
    }


def make_nz_poster_facebook(company: str, city: str, category: str) -> dict:
    """New Zealand — Facebook post 1200×630"""
    return {
        "platform": "facebook_post",
        "dimensions": {"width": 1200, "height": 630},
        "layers": [
            {"type": "background", "gradient": "140deg, #0C2340 0%, #003366 100%"},
            {"type": "shapes", "shapes": [
                {"type": "circle", "size": 400, "x": -100, "y": -100, "color": "rgba(255,255,255,0.04)"},
                {"type": "circle", "size": 280, "x": 1100, "y": 450, "color": "rgba(204,0,0,0.06)"},
            ]},
            {"type": "badge", "value": "🇳🇿 NEW ZEALAND — KIWI OWNED",
             "x": 330, "y": 50,
             "bg": "#CC0000", "text_color": "#FFFFFF", "font_size": 20, "bold": True},
            {"type": "title", "value": company,
             "x": 40, "y": 105, "w": 1120,
             "font_size": 52, "bold": True, "color": "#FFFFFF", "align": "center"},
            {"type": "subtitle", "value": f"{category}  •  {city}, New Zealand",
             "x": 40, "y": 172, "w": 1120,
             "font_size": 26, "color": "#BAE6FD", "align": "center"},
            {"type": "service_grid",
             "items": ["NZ Owned", "Eco-Friendly", "Free Delivery", "5-Star Rated"],
             "columns": 4, "icon": "🥝", "icon_color": "#86EFAC",
             "item_bg": "rgba(255,255,255,0.07)"},
            {"type": "stat_row", "items": [
                {"value": "5K+", "label": "NZ Customers"},
                {"value": "5.0★", "label": "Google Rating"},
                {"value": city, "label": "Headquarters"},
            ], "value_color": "#86EFAC"},
            {"type": "cta", "value": "🛒 Shop Online — Free NZ Delivery!",
             "x": 40, "y": 563, "w": 1120, "h": 55,
             "bg": "#CC0000", "text_color": "#FFFFFF", "font_size": 28, "bold": True,
             "border_radius": 10},
        ],
        "meta": {"template_slug": "retail_discount", "org_name": company, "city": city},
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main seed function
# ─────────────────────────────────────────────────────────────────────────────

async def seed():
    async with async_session() as session:

        # ── Resolve tenant accounts ───────────────────────────────────────────
        result = await session.execute(select(Tenant).where(Tenant.email == "demo@srp.ai"))
        demo_tenant = result.scalars().first()

        result = await session.execute(select(Tenant).where(Tenant.email == "bunty@srp.ai"))
        bunty_tenant = result.scalars().first()

        if not demo_tenant:
            print("[ERROR] demo@srp.ai not found — run seed_demo.py first")
            return
        if not bunty_tenant:
            print("[ERROR] bunty@srp.ai not found — run seed_bunty.py first")
            return

        print(f"[OK] demo@srp.ai  → tenant id: {demo_tenant.id}")
        print(f"[OK] bunty@srp.ai → tenant id: {bunty_tenant.id}")

        all_variants: list[PosterVariant] = []
        all_posts: list[SocialPost] = []

        # ====================================================================
        # 1. Bengaluru IT Agency — Hindi bilingual job opening (demo@srp.ai)
        # ====================================================================
        IT_COMPANY = "TechNova Solutions"
        IT_CITY    = "Bengaluru"
        IT_ROLE    = "Senior Software Engineer"
        IT_SALARY  = "₹18–35 LPA"

        all_variants += [
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="instagram_square",
                width="1080", height="1080",
                language_primary="english", language_secondary="hindi",
                status="ready",
                social_caption=(
                    f"💻 We're Hiring! {IT_COMPANY}, {IT_CITY}\n\n"
                    f"🚀 {IT_ROLE} | {IT_SALARY} CTC\n\n"
                    "⚡ हिंदी + English Friendly Workplace\n"
                    "🌐 React | Python | Node.js | AI/ML\n\n"
                    "DM us or visit the link in bio!\n\n"
                    "#Hiring #BengaluruJobs #SoftwareEngineer #ITJobs #ReactDeveloper"
                ),
                hashtags=["Hiring", "BengaluruJobs", "SoftwareEngineer", "ITJobs", "TechNova"],
                poster_json=make_it_job_poster_instagram(IT_COMPANY, IT_CITY, IT_ROLE, IT_SALARY),
                campaign_data={
                    "template_slug": "job_opening",
                    "org_name": IT_COMPANY, "city": IT_CITY,
                    "secondary_language": "hindi",
                },
                created_at=datetime.now(timezone.utc),
            ),
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="linkedin_banner",
                width="1200", height="628",
                language_primary="english", language_secondary="hindi",
                status="ready",
                social_caption=(
                    f"🏢 {IT_COMPANY} is hiring!\n\n"
                    f"Role: {IT_ROLE}\n"
                    f"Location: {IT_CITY}, India\n"
                    f"Package: {IT_SALARY}\n\n"
                    "Skills: React / Python / FastAPI / AWS / AI\n"
                    "Hybrid work | Immediate joining\n\n"
                    "Apply via LinkedIn or DM! #Hiring #ITJobs #Bengaluru"
                ),
                hashtags=["Hiring", "ITJobs", "Bengaluru", "SoftwareEngineer", "TechNova"],
                poster_json=make_it_job_poster_linkedin(IT_COMPANY, IT_CITY, IT_ROLE, IT_SALARY),
                campaign_data={
                    "template_slug": "job_opening",
                    "org_name": IT_COMPANY, "city": IT_CITY,
                    "secondary_language": "hindi",
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

        all_posts.append(SocialPost(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            platform="whatsapp",
            campaign="TechNova Hiring Drive",
            content=(
                "💻 *नौकरी का मौका! / JOB OPENING!*\n\n"
                f"🏢 {IT_COMPANY}, {IT_CITY}\n\n"
                f"💼 Post: *{IT_ROLE}*\n"
                f"💰 Salary: *{IT_SALARY} CTC*\n\n"
                "✅ Skills Required:\n"
                "• React / Angular / Vue\n"
                "• Python / Django / FastAPI\n"
                "• Node.js / TypeScript\n"
                "• AWS / DevOps\n\n"
                "⚡ हिंदी + English Friendly Workplace\n"
                "🏠 Hybrid Work from Bengaluru\n\n"
                "📧 careers@technovasolutions.com\n"
                "🔗 Apply: linkedin.com/company/technova\n\n"
                "*अभी Apply करें — Seats Limited!*"
            ),
            status="published",
            ai_generated=False,
            published_at=datetime.now(timezone.utc) - timedelta(hours=3),
        ))

        # ====================================================================
        # 2. Bunty Cloth Store — Hindi discount offer (bunty@srp.ai)
        # ====================================================================
        CLOTH_ORG     = "Bunty Cloth Store"
        CLOTH_CITY    = "Nagpur"
        CLOTH_DISCOUNT = "40%"

        all_variants += [
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=bunty_tenant.id,
                platform="instagram_square",
                width="1080", height="1080",
                language_primary="hindi", language_secondary="english",
                status="ready",
                social_caption=(
                    f"🎉 {CLOTH_DISCOUNT} की महा छूट — {CLOTH_ORG}, {CLOTH_CITY}!\n\n"
                    "साड़ी, सूट, कुर्ती, जींस — सभी पर बड़ी सेल!\n"
                    "सीमित समय / Limited Time Offer!\n\n"
                    "#BuntyClothStore #MegaSale #Discount #HindiSale #Nagpur #Kapde"
                ),
                hashtags=["BuntyClothStore", "MegaSale", "Discount", "HindiSale", "Nagpur", "Kapde"],
                poster_json=make_cloth_discount_instagram(CLOTH_ORG, CLOTH_CITY, CLOTH_DISCOUNT),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": CLOTH_ORG, "city": CLOTH_CITY,
                    "secondary_language": "hindi",
                },
                created_at=datetime.now(timezone.utc),
            ),
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=bunty_tenant.id,
                platform="whatsapp_share",
                width="1080", height="1080",
                language_primary="hindi", language_secondary="english",
                status="ready",
                social_caption=(
                    f"🛍️ {CLOTH_DISCOUNT} छूट — {CLOTH_ORG}!\n\n"
                    "सभी कपड़ों पर भारी छूट।\n"
                    "आज ही Visit करें!\n\n"
                    "#BuntyClothStore #Nagpur #Sale"
                ),
                hashtags=["BuntyClothStore", "Nagpur", "HindiSale", "MegaSale"],
                poster_json=make_cloth_discount_whatsapp(CLOTH_ORG, CLOTH_CITY, CLOTH_DISCOUNT),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": CLOTH_ORG, "city": CLOTH_CITY,
                    "secondary_language": "hindi",
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

        all_posts.append(SocialPost(
            id=uuid.uuid4(),
            tenant_id=bunty_tenant.id,
            platform="whatsapp",
            campaign="Bunty Cloth Mega Sale",
            content=(
                f"🛍️ *{CLOTH_ORG} — महा सेल!*\n\n"
                f"*{CLOTH_DISCOUNT} की छूट — सभी कपड़ों पर!*\n\n"
                "🎁 क्या मिलेगा:\n"
                "✅ साड़ी / Saree\n"
                "✅ सूट / Suits\n"
                "✅ कुर्ती / Kurti\n"
                "✅ जींस / Jeans\n"
                "✅ बच्चों के कपड़े / Kids Wear\n"
                "✅ वेडिंग कलेक्शन\n\n"
                "⏰ *सीमित समय / Limited Time Only!*\n\n"
                f"📍 {CLOTH_ORG}, {CLOTH_CITY}\n"
                "📞 जल्दी Call करें — Stock Limited!\n\n"
                "*अपने दोस्तों को Share करें! 🙏*"
            ),
            status="published",
            ai_generated=False,
            published_at=datetime.now(timezone.utc) - timedelta(hours=1),
        ))

        # ====================================================================
        # 3. Australia Demo — SRP Digital Agency (demo@srp.ai)
        # ====================================================================
        AU_COMPANY  = "PrimeEdge Digital"
        AU_CITY     = "Sydney"
        AU_CATEGORY = "Digital Marketing Agency"

        all_variants += [
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="instagram_square",
                width="1080", height="1080",
                language_primary="english",
                status="ready",
                social_caption=(
                    f"🇦🇺 {AU_COMPANY} — {AU_CITY}'s Leading Digital Marketing Agency!\n\n"
                    "🚀 We grow Australian businesses with AI-powered marketing.\n"
                    "📈 SEO | Social Media | Google Ads | AI Automation\n\n"
                    "📞 Free consultation — no commitment!\n\n"
                    "#DigitalMarketing #SydneyBusiness #AustraliaMarketing #AIMarketing"
                ),
                hashtags=["DigitalMarketing", "SydneyBusiness", "AustraliaMarketing", "AIMarketing", "PrimeEdge"],
                poster_json=make_australia_poster_instagram(AU_COMPANY, AU_CITY, AU_CATEGORY),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": AU_COMPANY, "city": AU_CITY,
                },
                created_at=datetime.now(timezone.utc),
            ),
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="facebook_post",
                width="1200", height="630",
                language_primary="english",
                status="ready",
                social_caption=(
                    f"🇦🇺 Ready to grow your business in Australia?\n\n"
                    f"{AU_COMPANY} helps Australian SMEs dominate their market with:\n"
                    "✅ AI-powered social media marketing\n"
                    "✅ Google Ads management\n"
                    "✅ SEO & content strategy\n\n"
                    "📞 Call us for a FREE 30-min strategy session!\n\n"
                    "#AustraliaBusiness #DigitalMarketing #SydneyMarketing"
                ),
                hashtags=["AustraliaBusiness", "DigitalMarketing", "SydneyMarketing", "PrimeEdge"],
                poster_json=make_australia_poster_facebook(AU_COMPANY, AU_CITY, AU_CATEGORY),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": AU_COMPANY, "city": AU_CITY,
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

        all_posts.append(SocialPost(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            platform="whatsapp",
            campaign="Australia Brand Launch",
            content=(
                "🇦🇺 *PrimeEdge Digital — Sydney, Australia*\n\n"
                "🚀 *Grow Your Business with AI Marketing!*\n\n"
                "✅ Social Media Management\n"
                "✅ Google Ads & SEO\n"
                "✅ AI-Powered Content\n"
                "✅ Lead Generation\n\n"
                "📞 Free 30-min consultation!\n"
                "🌐 Visit: srpailabs.com\n\n"
                "_Australia's most innovative digital marketing platform_ 🤖"
            ),
            status="published",
            ai_generated=False,
            published_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ))

        # ====================================================================
        # 4. New Zealand Demo (demo@srp.ai)
        # ====================================================================
        NZ_COMPANY  = "KiwiGrow Marketing"
        NZ_CITY     = "Auckland"
        NZ_CATEGORY = "Digital Marketing & AI Solutions"

        all_variants += [
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="instagram_square",
                width="1080", height="1080",
                language_primary="english",
                status="ready",
                social_caption=(
                    f"🇳🇿 {NZ_COMPANY} — {NZ_CITY}, New Zealand!\n\n"
                    "🥝 Kiwi-owned digital marketing for NZ businesses.\n"
                    "🌿 Eco-conscious | AI-powered | NZ-first approach\n\n"
                    "📞 Free strategy session — no obligation!\n\n"
                    "#NewZealand #AucklandBusiness #NZMarketing #KiwiGrow #AIMarketing"
                ),
                hashtags=["NewZealand", "AucklandBusiness", "NZMarketing", "KiwiGrow", "AIMarketing"],
                poster_json=make_nz_poster_instagram(NZ_COMPANY, NZ_CITY, NZ_CATEGORY),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": NZ_COMPANY, "city": NZ_CITY,
                },
                created_at=datetime.now(timezone.utc),
            ),
            PosterVariant(
                id=uuid.uuid4(),
                tenant_id=demo_tenant.id,
                platform="facebook_post",
                width="1200", height="630",
                language_primary="english",
                status="ready",
                social_caption=(
                    f"🇳🇿 Kia Ora, New Zealand!\n\n"
                    f"{NZ_COMPANY} helps Kiwi businesses grow with AI-powered marketing.\n"
                    "✅ Social media management\n"
                    "✅ Google Ads & SEO\n"
                    "✅ NZ-focused content strategy\n\n"
                    "📞 Free consultation — Kia Kaha!\n\n"
                    "#NZBusiness #AucklandMarketing #KiwiOwned"
                ),
                hashtags=["NZBusiness", "AucklandMarketing", "KiwiOwned", "KiwiGrow"],
                poster_json=make_nz_poster_facebook(NZ_COMPANY, NZ_CITY, NZ_CATEGORY),
                campaign_data={
                    "template_slug": "retail_discount",
                    "org_name": NZ_COMPANY, "city": NZ_CITY,
                },
                created_at=datetime.now(timezone.utc),
            ),
        ]

        all_posts.append(SocialPost(
            id=uuid.uuid4(),
            tenant_id=demo_tenant.id,
            platform="whatsapp",
            campaign="New Zealand Brand Launch",
            content=(
                "🇳🇿 *KiwiGrow Marketing — Auckland, NZ*\n\n"
                "🥝 *Kia Ora! Grow Your NZ Business with AI!*\n\n"
                "✅ Social Media Management\n"
                "✅ Google Ads & SEO Optimisation\n"
                "✅ AI-Powered Content Creation\n"
                "✅ 100% NZ-owned Agency\n\n"
                "📞 Book a FREE consultation today!\n"
                "🌐 srpailabs.com\n\n"
                "_Kia Kaha — Be Strong, Grow Strong!_ 🌿"
            ),
            status="published",
            ai_generated=False,
            published_at=datetime.now(timezone.utc) - timedelta(hours=4),
        ))

        # ── Save everything ──────────────────────────────────────────────────
        for v in all_variants:
            session.add(v)
        for p in all_posts:
            session.add(p)

        await session.commit()

        print(f"\n[SUCCESS] Created {len(all_variants)} poster variants:")
        for v in all_variants:
            label = v.campaign_data.get("org_name", "?") if v.campaign_data else "?"
            print(f"  ✓ [{v.platform}] {label} — {v.campaign_data.get('city', '')} ({v.language_primary or 'en'})")

        print(f"\n[SUCCESS] Created {len(all_posts)} WhatsApp/social posts:")
        for p in all_posts:
            print(f"  ✓ [{p.platform}] {p.campaign}")

        print("\n[INFO] Log in to:")
        print("  • demo@srp.ai  / Demo@12345  → IT Agency, Australia, NZ posters")
        print("  • bunty@srp.ai / Bunty@12345 → Cloth store + Star Hospital posters")


if __name__ == "__main__":
    asyncio.run(seed())
