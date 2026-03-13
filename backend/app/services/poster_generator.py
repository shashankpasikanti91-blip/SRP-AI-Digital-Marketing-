"""
Poster Generator Service — template-driven structured poster JSON generation.

Architecture principle:
  - Brand template (BrandProfile) provides: colors, fonts, logo, footer
  - Campaign template (PosterTemplate) provides: layout blocks, positions, sizes
  - Dynamic content (CampaignContentInput) provides: city, dates, prices, services
  - Language content (BilingualCampaignContent) provides: bilingual text blocks
  - OUTPUT: Structured poster_json for frontend PosterRenderer

AI is NOT used for visual design. AI generates text only.
Visual consistency comes 100% from templates.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.services.language_service import (
    BilingualCampaignContent,
    CampaignContentInput,
    LanguageService,
)

if TYPE_CHECKING:
    from app.models.brand_profile import BrandProfile
    from app.models.poster_template import PosterTemplate


# ── Poster dimension presets ──────────────────────────────────────────

PLATFORM_DIMENSIONS = {
    "instagram_square": {"width": 1080, "height": 1080},
    "instagram_story": {"width": 1080, "height": 1920},
    "facebook_post": {"width": 1200, "height": 630},
    "whatsapp_share": {"width": 1080, "height": 1080},
    "linkedin_banner": {"width": 1200, "height": 628},
    "twitter_post": {"width": 1200, "height": 675},
    "youtube_thumbnail": {"width": 1280, "height": 720},
}

# ── Built-in system template definitions ─────────────────────────────

SYSTEM_TEMPLATES: dict[str, dict] = {
    "orthopedic_health_camp": {
        "background": {"type": "gradient", "colors": ["#1E3A8A", "#1E40AF"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#F59E0B", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "accreditation": {"position": "top-right", "x": 900, "y": 40, "w": 100, "h": 50},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#F59E0B", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#FCD34D", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#BFDBFE", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#BFDBFE", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#FCD34D", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "✓", "icon_color": "#F59E0B", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#F59E0B", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#F59E0B", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#0F172A", "text_color": "#FFFFFF", "font_size": 20},
    },
    "diabetes_health_camp": {
        "background": {"type": "gradient", "colors": ["#065F46", "#047857"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#10B981", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#10B981", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#A7F3D0", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#D1FAE5", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#D1FAE5", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#A7F3D0", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "✓", "icon_color": "#10B981", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#10B981", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#10B981", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#022C22", "text_color": "#FFFFFF", "font_size": 20},
    },
    "job_opening": {
        "background": {"type": "solid", "color": "#F8FAFC"},
        "accent_strip": {"enabled": True, "color": "#4F46E5", "height": 10},
        "logo": {"position": "top-left", "x": 40, "y": 50, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 145, "type": "pill", "bg": "#4F46E5", "text_color": "#FFF", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#1E293B", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 36, "bold": True, "color": "#4F46E5", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 28, "color": "#475569", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 415, "w": 1000, "font_size": 22, "color": "#475569", "align": "center"},
        "checklist": {"x": 60, "y": 480, "font_size": 24, "icon": "→", "icon_color": "#4F46E5", "color": "#1E293B", "columns": 1, "line_height": 52},
        "date_block": {"x": 40, "y": 800, "font_size": 26, "color": "#EF4444", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 880, "w": 1000, "h": 72, "bg": "#4F46E5", "text_color": "#FFF", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 980, "w": 1080, "h": 100, "bg": "#1E293B", "text_color": "#FFFFFF", "font_size": 20},
    },
    "walkin_drive": {
        "background": {"type": "gradient", "colors": ["#7C3AED", "#5B21B6"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FDE68A", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#FDE68A", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#FDE68A", "align": "center"},
        "subtitle": {"x": 40, "y": 360, "w": 1000, "font_size": 28, "color": "#DDD6FE", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 400, "w": 1000, "font_size": 22, "color": "#DDD6FE", "align": "center"},
        "checklist": {"x": 60, "y": 460, "font_size": 22, "icon": "✦", "icon_color": "#FDE68A", "color": "#FFFFFF", "columns": 1, "line_height": 50},
        "date_block": {"x": 40, "y": 800, "font_size": 28, "color": "#FDE68A", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 870, "w": 1000, "h": 72, "bg": "#FDE68A", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 975, "w": 1080, "h": 105, "bg": "#2E1065", "text_color": "#FFFFFF", "font_size": 20},
    },
    "restaurant_offer": {
        "background": {"type": "gradient", "colors": ["#7F1D1D", "#991B1B"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FBBF24", "height": 8},
        "logo": {"position": "top-center", "x": 465, "y": 40, "w": 150, "h": 75},
        "badge": {"x": 380, "y": 145, "type": "pill", "bg": "#FBBF24", "text_color": "#000", "font_size": 28, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 60, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FDE68A", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 28, "color": "#FECACA", "align": "center"},
        "price_block": {"x": 40, "y": 500, "font_size": 80, "color": "#FBBF24", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 600, "font_size": 32, "color": "#FCA5A5", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 660, "font_size": 24, "icon": "★", "icon_color": "#FBBF24", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 830, "font_size": 26, "color": "#FDE68A", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#FBBF24", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#450A0A", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Cardiac / Heart Camp ──────────────────────────────────────────
    "cardiac_checkup_camp": {
        "background": {"type": "gradient", "colors": ["#7F1D1D", "#BE123C"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FB7185", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#FB7185", "text_color": "#FFF", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#FECDD3", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#FCA5A5", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#FCA5A5", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#FECDD3", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "❤", "icon_color": "#FB7185", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#FB7185", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#FB7185", "text_color": "#FFF", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#4C0519", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Eye Camp ─────────────────────────────────────────────────────
    "eye_camp": {
        "background": {"type": "gradient", "colors": ["#0F766E", "#0D9488"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#2DD4BF", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#2DD4BF", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#CCFBF1", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#99F6E4", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#99F6E4", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#CCFBF1", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "👁", "icon_color": "#2DD4BF", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#2DD4BF", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#2DD4BF", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#042F2E", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Dental Camp ──────────────────────────────────────────────────
    "dental_camp": {
        "background": {"type": "gradient", "colors": ["#0369A1", "#0284C7"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#7DD3FC", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#7DD3FC", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#E0F2FE", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#BAE6FD", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#BAE6FD", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#E0F2FE", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "✓", "icon_color": "#7DD3FC", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#7DD3FC", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#7DD3FC", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#082F49", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── General Health Camp ──────────────────────────────────────────
    "general_health_camp": {
        "background": {"type": "gradient", "colors": ["#1E3A8A", "#2563EB"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#60A5FA", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 440, "y": 135, "type": "pill", "bg": "#60A5FA", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 220, "w": 1000, "font_size": 54, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 38, "bold": True, "color": "#BFDBFE", "align": "center"},
        "subtitle": {"x": 40, "y": 355, "w": 1000, "font_size": 26, "color": "#93C5FD", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#93C5FD", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#BFDBFE", "bold": True},
        "checklist": {"x": 60, "y": 510, "font_size": 22, "icon": "✓", "icon_color": "#60A5FA", "color": "#FFFFFF", "columns": 2, "line_height": 44},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#60A5FA", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#60A5FA", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#0F172A", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Pharmacy / Medicine Sale ──────────────────────────────────────
    "pharmacy_sale": {
        "background": {"type": "gradient", "colors": ["#14532D", "#15803D"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#4ADE80", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#4ADE80", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#BBF7D0", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#86EFAC", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 80, "color": "#4ADE80", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 590, "font_size": 32, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 650, "font_size": 24, "icon": "💊", "icon_color": "#4ADE80", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 840, "font_size": 26, "color": "#BBF7D0", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#4ADE80", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#052E16", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Retail / Shop Discount ────────────────────────────────────────
    "retail_discount": {
        "background": {"type": "gradient", "colors": ["#C2410C", "#EA580C"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FED7AA", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#FED7AA", "text_color": "#000", "font_size": 28, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 58, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FED7AA", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#FDBA74", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 84, "color": "#FED7AA", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 596, "font_size": 32, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 650, "font_size": 24, "icon": "✦", "icon_color": "#FED7AA", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 840, "font_size": 26, "color": "#FED7AA", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#FED7AA", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#431407", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Real Estate Launch ────────────────────────────────────────────
    "real_estate_launch": {
        "background": {"type": "gradient", "colors": ["#78350F", "#92400E"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FCD34D", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#FCD34D", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FDE68A", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 28, "color": "#FEF3C7", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 72, "color": "#FCD34D", "bold": True, "align": "center"},
        "checklist": {"x": 60, "y": 600, "font_size": 24, "icon": "🏠", "icon_color": "#FCD34D", "color": "#FFFFFF", "columns": 2, "line_height": 50},
        "date_block": {"x": 40, "y": 830, "font_size": 26, "color": "#FDE68A", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 890, "w": 1000, "h": 72, "bg": "#FCD34D", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 990, "w": 1080, "h": 90, "bg": "#451A03", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Coaching Institute ─────────────────────────────────────────────
    "coaching_institute": {
        "background": {"type": "gradient", "colors": ["#0C4A6E", "#0369A1"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#38BDF8", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#38BDF8", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#E0F2FE", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#BAE6FD", "align": "center"},
        "checklist": {"x": 60, "y": 460, "font_size": 24, "icon": "📖", "icon_color": "#38BDF8", "color": "#FFFFFF", "columns": 2, "line_height": 50},
        "price_block": {"x": 40, "y": 730, "font_size": 68, "color": "#38BDF8", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 812, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 858, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 920, "w": 1000, "h": 72, "bg": "#38BDF8", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#082F49", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Beauty Salon / Parlour ────────────────────────────────────────
    "beauty_salon": {
        "background": {"type": "gradient", "colors": ["#9D174D", "#BE185D"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#F9A8D4", "height": 8},
        "logo": {"position": "top-center", "x": 465, "y": 40, "w": 150, "h": 75},
        "badge": {"x": 380, "y": 145, "type": "pill", "bg": "#F9A8D4", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FCE7F3", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#FBCFE8", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 78, "color": "#F9A8D4", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 590, "font_size": 30, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 650, "font_size": 24, "icon": "✿", "icon_color": "#F9A8D4", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 840, "font_size": 26, "color": "#FCE7F3", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#F9A8D4", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#500724", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Gym / Fitness ─────────────────────────────────────────────────
    "gym_offer": {
        "background": {"type": "gradient", "colors": ["#111827", "#1F2937"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#F97316", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#F97316", "text_color": "#FFF", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 58, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FED7AA", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#D1D5DB", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 80, "color": "#F97316", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 590, "font_size": 30, "color": "#6B7280", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 650, "font_size": 24, "icon": "💪", "icon_color": "#F97316", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 840, "font_size": 26, "color": "#FED7AA", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#F97316", "text_color": "#FFF", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#030712", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Event / Programme ─────────────────────────────────────────────
    "event_announcement": {
        "background": {"type": "gradient", "colors": ["#4C1D95", "#6D28D9"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#C4B5FD", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#C4B5FD", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 58, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#EDE9FE", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#DDD6FE", "align": "center"},
        "checklist": {"x": 60, "y": 460, "font_size": 24, "icon": "★", "icon_color": "#C4B5FD", "color": "#FFFFFF", "columns": 1, "line_height": 54},
        "date_block": {"x": 40, "y": 790, "font_size": 30, "color": "#C4B5FD", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 870, "w": 1000, "h": 72, "bg": "#C4B5FD", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 975, "w": 1080, "h": 105, "bg": "#2E1065", "text_color": "#FFFFFF", "font_size": 20},
    },
    # ── Generic fallback for new industry slugs ───────────────────────
    "bakery_offer": {
        "background": {"type": "gradient", "colors": ["#C2410C", "#EA580C"], "direction": "135deg"},
        "accent_strip": {"enabled": True, "color": "#FED7AA", "height": 8},
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 380, "y": 135, "type": "pill", "bg": "#FED7AA", "text_color": "#000", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 240, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 315, "w": 1000, "font_size": 38, "bold": True, "color": "#FED7AA", "align": "center"},
        "subtitle": {"x": 40, "y": 375, "w": 1000, "font_size": 26, "color": "#FDBA74", "align": "center"},
        "price_block": {"x": 40, "y": 490, "font_size": 80, "color": "#FED7AA", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 590, "font_size": 30, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "checklist": {"x": 60, "y": 650, "font_size": 24, "icon": "★", "icon_color": "#FED7AA", "color": "#FFFFFF", "columns": 2, "line_height": 46},
        "date_block": {"x": 40, "y": 840, "font_size": 26, "color": "#FED7AA", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#FED7AA", "text_color": "#000", "font_size": 32, "bold": True, "border_radius": 12},
        "footer": {"x": 0, "y": 1000, "w": 1080, "h": 80, "bg": "#431407", "text_color": "#FFFFFF", "font_size": 20},
    },

    # ════════════════════════════════════════════════════════════════════
    # PREMIUM AGENCY / BUSINESS TEMPLATES  (with shapes + service_grid)
    # ════════════════════════════════════════════════════════════════════

    "digital_agency_promo": {
        # Deep navy background with decorative circles + service grid layout
        # Looks like professional Canva/Freepik agency posters
        "background": {"type": "gradient", "colors": ["#0F172A", "#1E293B"], "direction": "180deg"},
        "shapes": {
            "shapes": [
                {"type": "circle", "size": 500, "x": -160, "y": -160,
                 "color": "rgba(99,102,241,0.10)"},
                {"type": "circle", "size": 350, "right": -100, "y": 300,
                 "color": "rgba(245,158,11,0.08)"},
                {"type": "circle", "size": 240, "right": -60, "bottom": -60,
                 "border": True, "border_color": "rgba(245,158,11,0.20)", "border_width": 4},
                {"type": "rect", "w": 120, "h": 600, "right": 0, "y": 0,
                 "color": "rgba(245,158,11,0.12)", "rotate": 0, "radius": 0},
                {"type": "rect", "w": 1080, "h": 6, "x": 0, "y": 0,
                 "color": "#F59E0B", "rotate": 0},
            ]
        },
        "badge": {"x": 300, "y": 80, "type": "pill", "bg": "#F59E0B", "text_color": "#0F172A", "font_size": 24, "bold": True},
        "title": {"x": 40, "y": 160, "w": 900, "font_size": 62, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 240, "w": 900, "font_size": 42, "bold": True, "color": "#F59E0B", "align": "center"},
        "subtitle": {"x": 40, "y": 310, "w": 1000, "font_size": 26, "color": "#CBD5E1", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 350, "w": 1000, "font_size": 22, "color": "#94A3B8", "align": "center"},
        # Service grid instead of checklist
        "service_grid": {"columns": 3, "icon": "◆", "icon_color": "#F59E0B",
                         "item_bg": "rgba(255,255,255,0.08)", "font_size": 21},
        # Stats bar: clients, projects, success
        "stat_block": {
            "items": [
                {"value": "500+", "label": "Clients Served"},
                {"value": "1200+", "label": "Campaigns"},
                {"value": "98%", "label": "Success Rate"},
            ],
            "font_size": 22, "value_color": "#F59E0B",
            "bg": "rgba(245,158,11,0.10)",
            "divider_color": "rgba(245,158,11,0.30)",
        },
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#F59E0B", "text_color": "#0F172A", "font_size": 30, "bold": True, "border_radius": 16},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#020617", "text_color": "#FFFFFF", "font_size": 20},
    },

    "business_services_pro": {
        # Dark purple-to-slate with decorative geometry + service grid
        "background": {"type": "gradient", "colors": ["#1E1B4B", "#312E81"], "direction": "135deg"},
        "shapes": {
            "shapes": [
                {"type": "circle", "size": 420, "right": -120, "y": -100,
                 "color": "rgba(167,139,250,0.10)"},
                {"type": "circle", "size": 280, "x": -80, "bottom": 200,
                 "color": "rgba(167,139,250,0.07)"},
                {"type": "circle", "size": 180, "x": 80, "bottom": 80,
                 "border": True, "border_color": "rgba(167,139,250,0.25)", "border_width": 3},
                {"type": "rect", "w": 1080, "h": 8, "x": 0, "y": 0,
                 "color": "#A78BFA", "rotate": 0},
                {"type": "rect", "w": 300, "h": 300, "right": 60, "bottom": 200,
                 "color": "rgba(167,139,250,0.05)", "rotate": 45, "radius": 24},
            ]
        },
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 360, "y": 130, "type": "pill", "bg": "#A78BFA", "text_color": "#1E1B4B", "font_size": 24, "bold": True},
        "title": {"x": 40, "y": 210, "w": 1000, "font_size": 58, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 285, "w": 1000, "font_size": 40, "bold": True, "color": "#C4B5FD", "align": "center"},
        "subtitle": {"x": 40, "y": 345, "w": 1000, "font_size": 26, "color": "#DDD6FE", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 385, "w": 1000, "font_size": 22, "color": "#C4B5FD", "align": "center"},
        "service_grid": {"columns": 2, "icon": "✦", "icon_color": "#A78BFA",
                         "item_bg": "rgba(255,255,255,0.09)", "font_size": 22},
        "cta": {"x": 40, "y": 900, "w": 1000, "h": 72, "bg": "#A78BFA", "text_color": "#1E1B4B", "font_size": 30, "bold": True, "border_radius": 16},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#0F0A2E", "text_color": "#FFFFFF", "font_size": 20},
    },

    "agency_hero_bold": {
        # Black + vibrant yellow — bold two-tone agency hero (like Freepik DM agency posters)
        "background": {"type": "gradient", "colors": ["#111827", "#1F2937"], "direction": "180deg"},
        "shapes": {
            "shapes": [
                # Top-right filled circle — "we are digital marketing" style
                {"type": "circle", "size": 340, "right": -80, "y": -80,
                 "color": "rgba(234,179,8,0.15)"},
                # Bottom-left outline circle
                {"type": "circle", "size": 260, "x": -60, "bottom": 150,
                 "border": True, "border_color": "rgba(234,179,8,0.25)", "border_width": 3},
                # Top accent bar
                {"type": "rect", "w": 1080, "h": 8, "x": 0, "y": 0,
                 "color": "#EAB308", "rotate": 0},
                # Diagonal accent slab bottom-right
                {"type": "rect", "w": 400, "h": 400, "right": -150, "bottom": -150,
                 "color": "rgba(234,179,8,0.07)", "rotate": 30, "radius": 0},
            ]
        },
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 340, "y": 128, "type": "pill", "bg": "#EAB308", "text_color": "#111827", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 205, "w": 1000, "font_size": 64, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 285, "w": 1000, "font_size": 44, "bold": True, "color": "#FDE047", "align": "center"},
        "subtitle": {"x": 40, "y": 350, "w": 1000, "font_size": 27, "color": "#9CA3AF", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#6B7280", "align": "center"},
        "service_grid": {"columns": 3, "icon": "→",
                         "icon_color": "#EAB308",
                         "item_bg": "rgba(234,179,8,0.12)", "font_size": 20},
        "stat_block": {
            "items": [
                {"value": "10+", "label": "Years Experience"},
                {"value": "800+", "label": "Happy Clients"},
                {"value": "24/7", "label": "Support"},
            ],
            "font_size": 22,
            "value_color": "#EAB308",
            "bg": "rgba(234,179,8,0.10)",
            "divider_color": "rgba(234,179,8,0.30)",
        },
        "cta": {"x": 40, "y": 898, "w": 1000, "h": 74, "bg": "#EAB308", "text_color": "#111827", "font_size": 30, "bold": True, "border_radius": 16},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#030712", "text_color": "#FFFFFF", "font_size": 20},
    },

    "hospital_premium": {
        # Clean white-on-blue hospital / healthcare with decorative circles
        "background": {"type": "gradient", "colors": ["#0C4A6E", "#0369A1"], "direction": "135deg"},
        "shapes": {
            "shapes": [
                {"type": "circle", "size": 460, "right": -130, "y": -130,
                 "color": "rgba(186,230,253,0.08)"},
                {"type": "circle", "size": 300, "x": -80, "bottom": 200,
                 "border": True, "border_color": "rgba(186,230,253,0.18)", "border_width": 3},
                {"type": "rect", "w": 1080, "h": 8, "x": 0, "y": 0,
                 "color": "#38BDF8", "rotate": 0},
                {"type": "circle", "size": 140, "right": 100, "bottom": 280,
                 "color": "rgba(56,189,248,0.08)"},
            ]
        },
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "accreditation": {"position": "top-right", "x": 900, "y": 40, "w": 100, "h": 50},
        "badge": {"x": 380, "y": 130, "type": "pill", "bg": "#38BDF8", "text_color": "#0C4A6E", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 215, "w": 1000, "font_size": 56, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 290, "w": 1000, "font_size": 38, "bold": True, "color": "#BAE6FD", "align": "center"},
        "subtitle": {"x": 40, "y": 350, "w": 1000, "font_size": 26, "color": "#E0F2FE", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 390, "w": 1000, "font_size": 22, "color": "#BAE6FD", "align": "center"},
        "doctor_block": {"x": 60, "y": 430, "font_size": 24, "color": "#7DD3FC", "bold": True},
        "service_grid": {"columns": 3, "icon": "✚", "icon_color": "#38BDF8",
                         "item_bg": "rgba(255,255,255,0.10)", "font_size": 20},
        "price_block": {"x": 40, "y": 730, "font_size": 70, "color": "#38BDF8", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 815, "font_size": 28, "color": "#9CA3AF", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 860, "font_size": 26, "color": "#FFFFFF", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 918, "w": 1000, "h": 72, "bg": "#38BDF8", "text_color": "#0C4A6E", "font_size": 30, "bold": True, "border_radius": 16},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#082040", "text_color": "#FFFFFF", "font_size": 20},
    },

    "real_estate_luxury": {
        # Deep slate + gold — luxury property / real estate
        "background": {"type": "gradient", "colors": ["#1C1917", "#292524"], "direction": "180deg"},
        "shapes": {
            "shapes": [
                {"type": "rect", "w": 1080, "h": 8, "x": 0, "y": 0,
                 "color": "#D97706", "rotate": 0},
                {"type": "rect", "w": 8, "h": 1080, "x": 0, "y": 0,
                 "color": "#D97706", "rotate": 0},
                {"type": "circle", "size": 400, "right": -100, "y": -100,
                 "color": "rgba(217,119,6,0.07)"},
                {"type": "rect", "w": 300, "h": 300, "right": 40, "bottom": 340,
                 "color": "rgba(217,119,6,0.07)", "rotate": 45},
                {"type": "circle", "size": 200, "x": -60, "bottom": 300,
                 "border": True, "border_color": "rgba(217,119,6,0.20)", "border_width": 2},
            ]
        },
        "logo": {"position": "top-left", "x": 40, "y": 40, "w": 140, "h": 70},
        "badge": {"x": 360, "y": 130, "type": "pill", "bg": "#D97706", "text_color": "#FFF", "font_size": 26, "bold": True},
        "title": {"x": 40, "y": 215, "w": 1000, "font_size": 62, "bold": True, "color": "#FFFFFF", "align": "center"},
        "regional_title": {"x": 40, "y": 295, "w": 1000, "font_size": 42, "bold": True, "color": "#FCD34D", "align": "center"},
        "subtitle": {"x": 40, "y": 360, "w": 1000, "font_size": 26, "color": "#D6D3D1", "align": "center"},
        "regional_subtitle": {"x": 40, "y": 400, "w": 1000, "font_size": 22, "color": "#A8A29E", "align": "center"},
        "checklist": {"x": 60, "y": 460, "font_size": 24, "icon": "◈", "icon_color": "#D97706", "color": "#FFFFFF", "columns": 2, "line_height": 48},
        "price_block": {"x": 40, "y": 720, "font_size": 72, "color": "#D97706", "bold": True, "align": "center"},
        "original_price": {"x": 40, "y": 810, "font_size": 28, "color": "#78716C", "strikethrough": True, "align": "center"},
        "date_block": {"x": 40, "y": 860, "font_size": 26, "color": "#FCD34D", "bold": True, "align": "center"},
        "cta": {"x": 40, "y": 918, "w": 1000, "h": 72, "bg": "#D97706", "text_color": "#FFF", "font_size": 30, "bold": True, "border_radius": 16},
        "footer": {"x": 0, "y": 1005, "w": 1080, "h": 75, "bg": "#0C0A09", "text_color": "#FFFFFF", "font_size": 20},
    },
}

# Map slugs that share a layout with an existing template
SLUG_LAYOUT_MAP: dict[str, str] = {
    "hotel_event":         "restaurant_offer",
    "garment_sale":        "retail_discount",
    "electronics_sale":    "retail_discount",
    "rental_property":     "real_estate_launch",
    "school_admission":    "coaching_institute",
    "skill_training":      "coaching_institute",
    "spa_wellness":        "beauty_salon",
    "wedding_services":    "event_announcement",
    "automobile_service":  "retail_discount",
    "travel_tour":         "event_announcement",
    "furniture_sale":      "retail_discount",
    # new agency / business mapping
    "digital_marketing":   "digital_agency_promo",
    "content_marketing":   "digital_agency_promo",
    "social_media_agency": "digital_agency_promo",
    "seo_agency":          "digital_agency_promo",
    "web_design":          "business_services_pro",
    "it_services":         "business_services_pro",
    "consulting":          "business_services_pro",
    "law_firm":            "business_services_pro",
}


def _resolve_template_layout(template_slug: str) -> dict:
    """Resolve layout config for a slug, falling back to the closest match."""
    if template_slug in SYSTEM_TEMPLATES:
        return SYSTEM_TEMPLATES[template_slug]
    fallback_slug = SLUG_LAYOUT_MAP.get(template_slug, "orthopedic_health_camp")
    return SYSTEM_TEMPLATES.get(fallback_slug, SYSTEM_TEMPLATES["orthopedic_health_camp"])


class PosterGenerator:
    """
    Template-driven poster JSON generator.

    Flow:
      generate_poster_json(campaign_input, brand_profile, template_slug, platform)
        → calls LanguageService.generate_bilingual_content()  [AI: text only]
        → merges with brand_profile (colors, logo, fonts, footer)
        → merges with SYSTEM_TEMPLATES[template_slug] (layout positions)
        → adapts dimensions for target platform
        → returns structured poster_json
    """

    @staticmethod
    async def generate_poster_json(
        campaign_input: CampaignContentInput,
        brand: "BrandProfile | None",
        template_slug: str = "orthopedic_health_camp",
        platform: str = "instagram_square",
    ) -> dict:
        """
        Generate a complete structured poster JSON.
        This is the main method — call this to create a poster.
        """
        # 1. Generate bilingual content via AI
        bilingual = await LanguageService.generate_bilingual_content(campaign_input)

        # 2. Resolve template layout blocks
        layout = _resolve_template_layout(template_slug)

        # 3. Resolve dimensions
        dims = PLATFORM_DIMENSIONS.get(platform, PLATFORM_DIMENSIONS["instagram_square"])
        w, h = dims["width"], dims["height"]

        # Scale factor from 1080x1080 base
        scale_x = w / 1080
        scale_y = h / 1080

        # 4. Resolve brand colors & fonts
        primary = brand.primary_color if brand else "#1E40AF"
        secondary = brand.secondary_color if brand else "#FFFFFF"
        accent = brand.accent_color if brand else "#F59E0B"
        font = brand.font_family if brand else "Inter"
        regional_font = brand.regional_font_family if brand else "Noto Sans"
        logo_url = brand.logo_url if brand else None
        brand_name = brand.brand_name if brand else campaign_input.org_name
        footer_phones = brand.phone_numbers if brand else [campaign_input.phone]
        footer_address = brand.address if brand else ""
        footer_text = brand.footer_text if brand else brand_name

        # Check if we should use brand colors or template default
        # For now, we overlay brand primary/accent over the template
        bg = layout.get("background", {})
        if brand and brand.primary_color:
            # Override template background with brand colors
            bg = {
                "type": "gradient",
                "colors": [brand.primary_color, _darken_hex(brand.primary_color)],
                "direction": "135deg",
            }

        # 5. Build layers list
        layers = []

        # Background
        layers.append({"type": "background", **_scale_block(bg, scale_x, scale_y)})

        # Accent strip
        if layout.get("accent_strip", {}).get("enabled"):
            strip = layout["accent_strip"]
            layers.append({
                "type": "rect",
                "role": "accent_strip",
                "x": 0, "y": 0,
                "w": w,
                "h": int(strip["height"] * scale_y),
                "fill": accent if brand else strip["color"],
            })

        # Decorative shapes overlay (circles, diagonals) — new premium templates
        if "shapes" in layout:
            shapes_def = layout["shapes"]
            # Scale shape positions relative to 1080×1080 base
            scaled_shapes = []
            for sh in shapes_def.get("shapes", []):
                s = dict(sh)
                for key in ("size", "w", "h", "width", "height"):
                    if key in s:
                        s[key] = int(s[key] * scale_x)
                for key in ("x", "right"):
                    if key in s:
                        s[key] = int(s[key] * scale_x)
                for key in ("y", "bottom"):
                    if key in s:
                        s[key] = int(s[key] * scale_y)
                scaled_shapes.append(s)
            layers.append({
                "type": "shapes",
                "shapes": scaled_shapes,
            })

        # Logo
        if logo_url and "logo" in layout:
            lb = layout["logo"]
            layers.append({
                "type": "image",
                "role": "logo",
                "src": logo_url,
                "x": int(lb["x"] * scale_x),
                "y": int(lb["y"] * scale_y),
                "w": int(lb["w"] * scale_x),
                "h": int(lb["h"] * scale_y),
            })

        # Badge
        if "badge" in layout:
            bb = layout["badge"]
            badge_text = bilingual.english_badge
            regional_badge = bilingual.regional_badge
            layers.append({
                "type": "badge",
                "role": "badge_english",
                "text": badge_text,
                "x": int(bb["x"] * scale_x),
                "y": int(bb["y"] * scale_y),
                "bg": accent if brand else bb["bg"],
                "text_color": bb.get("text_color", "#000"),
                "font_size": int(bb["font_size"] * scale_x),
                "bold": bb.get("bold", True),
                "font_family": font,
            })
            if regional_badge and regional_badge != badge_text:
                layers.append({
                    "type": "badge",
                    "role": "badge_regional",
                    "text": f"{badge_text} | {regional_badge}",
                    "x": int(bb["x"] * scale_x),
                    "y": int((bb["y"] + 40) * scale_y),
                    "bg": "transparent",
                    "text_color": accent if brand else bb["bg"],
                    "font_size": int((bb["font_size"] - 4) * scale_x),
                    "font_family": regional_font,
                })

        # English title
        if "title" in layout:
            tb = layout["title"]
            layers.append({
                "type": "text",
                "role": "title_english",
                "text": bilingual.english_title,
                "x": int(tb["x"] * scale_x),
                "y": int(tb["y"] * scale_y),
                "w": int(tb["w"] * scale_x),
                "font_size": int(tb["font_size"] * scale_x),
                "bold": tb.get("bold", True),
                "color": secondary if brand else tb["color"],
                "align": tb.get("align", "center"),
                "font_family": font,
            })

        # Regional title
        if "regional_title" in layout and bilingual.regional_title:
            rb = layout["regional_title"]
            layers.append({
                "type": "text",
                "role": "title_regional",
                "text": bilingual.regional_title,
                "x": int(rb["x"] * scale_x),
                "y": int(rb["y"] * scale_y),
                "w": int(rb["w"] * scale_x),
                "font_size": int(rb["font_size"] * scale_x),
                "bold": rb.get("bold", True),
                "color": accent if brand else rb["color"],
                "align": rb.get("align", "center"),
                "font_family": regional_font,
            })

        # Subtitle
        if "subtitle" in layout and bilingual.english_subtitle:
            sb = layout["subtitle"]
            layers.append({
                "type": "text",
                "role": "subtitle_english",
                "text": bilingual.english_subtitle,
                "x": int(sb["x"] * scale_x),
                "y": int(sb["y"] * scale_y),
                "w": int(sb["w"] * scale_x),
                "font_size": int(sb["font_size"] * scale_x),
                "color": sb.get("color", "#BFDBFE"),
                "align": sb.get("align", "center"),
                "font_family": font,
            })

        if "regional_subtitle" in layout and bilingual.regional_subtitle:
            rsb = layout["regional_subtitle"]
            layers.append({
                "type": "text",
                "role": "subtitle_regional",
                "text": bilingual.regional_subtitle,
                "x": int(rsb["x"] * scale_x),
                "y": int(rsb["y"] * scale_y),
                "w": int(rsb["w"] * scale_x),
                "font_size": int(rsb["font_size"] * scale_x),
                "color": rsb.get("color", "#BFDBFE"),
                "align": rsb.get("align", "center"),
                "font_family": regional_font,
            })

        # Doctor block (hospital campaigns)
        if "doctor_block" in layout and campaign_input.doctor_name:
            db_ = layout["doctor_block"]
            doc_text = f"Dr. {campaign_input.doctor_name}"
            if campaign_input.doctor_qualification:
                doc_text += f"  •  {campaign_input.doctor_qualification}"
            layers.append({
                "type": "text",
                "role": "doctor",
                "text": doc_text,
                "x": int(db_["x"] * scale_x),
                "y": int(db_["y"] * scale_y),
                "font_size": int(db_["font_size"] * scale_x),
                "color": db_.get("color", "#FCD34D"),
                "bold": db_.get("bold", False),
                "font_family": font,
            })

        # Service grid (premium agency/business templates)
        # Used instead of or in addition to the checklist
        if "service_grid" in layout and bilingual.english_services:
            sg = layout["service_grid"]
            items_en = bilingual.english_services[:6]
            items_reg = bilingual.regional_services[:6] if bilingual.regional_services else []
            combined = []
            for i, en in enumerate(items_en):
                if i < len(items_reg) and items_reg[i] and items_reg[i] != en:
                    combined.append(f"{en}")  # keep English only in grid for readability
                else:
                    combined.append(en)
            layers.append({
                "type": "service_grid",
                "role": "services_grid",
                "items": combined,
                "columns": sg.get("columns", 3),
                "icon": sg.get("icon", "◆"),
                "icon_color": accent if brand else sg.get("icon_color", "#F59E0B"),
                "item_bg": sg.get("item_bg", "rgba(255,255,255,0.10)"),
                "color": secondary if brand else "#FFFFFF",
                "font_size": int(sg.get("font_size", 21) * scale_x),
            })

        # Stat row (agencies + business service posters)
        if "stat_block" in layout:
            sb2 = layout["stat_block"]
            layers.append({
                "type": "stat_row",
                "role": "stats",
                "items": sb2.get("items", []),
                "font_size": int(sb2.get("font_size", 22) * scale_x),
                "value_color": accent if brand else sb2.get("value_color", "#F59E0B"),
                "color": secondary if brand else "rgba(255,255,255,0.7)",
                "bg": sb2.get("bg", "rgba(0,0,0,0.20)"),
                "divider_color": sb2.get("divider_color", "rgba(255,255,255,0.2)"),
            })

        # Checklist / services
        if "checklist" in layout and bilingual.english_services:
            cb = layout["checklist"]
            items_en = bilingual.english_services[:8]
            items_reg = bilingual.regional_services[:8] if bilingual.regional_services else []

            combined_items = []
            for i, en in enumerate(items_en):
                if i < len(items_reg) and items_reg[i] and items_reg[i] != en:
                    combined_items.append(f"{en} / {items_reg[i]}")
                else:
                    combined_items.append(en)

            layers.append({
                "type": "checklist",
                "role": "services",
                "items": combined_items,
                "x": int(cb["x"] * scale_x),
                "y": int(cb["y"] * scale_y),
                "font_size": int(cb["font_size"] * scale_x),
                "icon": cb.get("icon", "✓"),
                "icon_color": accent if brand else cb.get("icon_color", "#F59E0B"),
                "color": cb.get("color", "#FFFFFF"),
                "columns": cb.get("columns", 2),
                "line_height": int(cb.get("line_height", 44) * scale_y),
                "font_family": regional_font,
            })

        # Price block
        if "price_block" in layout and (campaign_input.offer_price or bilingual.offer_line_english):
            pb = layout["price_block"]
            price_text = campaign_input.offer_price or bilingual.offer_line_english
            layers.append({
                "type": "text",
                "role": "price",
                "text": price_text,
                "x": int(pb["x"] * scale_x),
                "y": int(pb["y"] * scale_y),
                "font_size": int(pb["font_size"] * scale_x),
                "color": accent if brand else pb.get("color", "#F59E0B"),
                "bold": pb.get("bold", True),
                "align": pb.get("align", "center"),
                "font_family": font,
            })

        if "original_price" in layout and campaign_input.original_price:
            op = layout["original_price"]
            layers.append({
                "type": "text",
                "role": "original_price",
                "text": f"Worth {campaign_input.original_price}",
                "x": int(op["x"] * scale_x),
                "y": int(op["y"] * scale_y),
                "font_size": int(op["font_size"] * scale_x),
                "color": op.get("color", "#9CA3AF"),
                "strikethrough": op.get("strikethrough", True),
                "align": op.get("align", "center"),
                "font_family": font,
            })

        # Date block
        if "date_block" in layout and (campaign_input.date_range or bilingual.date_line_english):
            dt = layout["date_block"]
            date_en = campaign_input.date_range or bilingual.date_line_english
            date_reg = bilingual.date_line_regional
            date_text = f"📅 {date_en}"
            if date_reg and date_reg != date_en:
                date_text += f"  |  {date_reg}"
            if campaign_input.event_time:
                date_text += f"  •  🕐 {campaign_input.event_time}"
            layers.append({
                "type": "text",
                "role": "date_info",
                "text": date_text,
                "x": int(dt["x"] * scale_x),
                "y": int(dt["y"] * scale_y),
                "font_size": int(dt["font_size"] * scale_x),
                "color": dt.get("color", "#FFFFFF"),
                "bold": dt.get("bold", False),
                "align": dt.get("align", "center"),
                "font_family": font,
            })

        # CTA button
        if "cta" in layout:
            ca = layout["cta"]
            cta_en = bilingual.english_cta
            cta_reg = bilingual.regional_cta
            cta_text = f"{cta_en}  |  {cta_reg}" if cta_reg and cta_reg != cta_en else cta_en
            layers.append({
                "type": "cta_button",
                "role": "cta",
                "text": cta_text,
                "x": int(ca["x"] * scale_x),
                "y": int(ca["y"] * scale_y),
                "w": int(ca["w"] * scale_x),
                "h": int(ca["h"] * scale_y),
                "bg": accent if brand else ca["bg"],
                "text_color": ca.get("text_color", "#000"),
                "font_size": int(ca["font_size"] * scale_x),
                "bold": ca.get("bold", True),
                "border_radius": ca.get("border_radius", 12),
                "font_family": font,
            })

        # Footer
        if "footer" in layout:
            fb = layout["footer"]
            phone_str = "  |  ".join(footer_phones) if footer_phones else campaign_input.phone
            footer_line = f"📞 {phone_str}"
            if footer_address:
                footer_line += f"  •  📍 {footer_address[:80]}"
            layers.append({
                "type": "footer",
                "role": "footer",
                "brand_name": brand_name,
                "phone": phone_str,
                "address": footer_address or "",
                "tagline": footer_text or brand_name,
                "text": footer_line,
                "x": int(fb["x"] * scale_x),
                "y": int(fb["y"] * scale_y),
                "w": int(fb.get("w", 1080) * scale_x),
                "h": int(fb["h"] * scale_y),
                "bg": primary if brand else fb["bg"],
                "text_color": fb.get("text_color", "#FFFFFF"),
                "font_size": int(fb["font_size"] * scale_x),
                "font_family": font,
            })

        # 6. Compose final poster JSON
        poster_json = {
            "version": "1.0",
            "platform": platform,
            "template_slug": template_slug,
            "layout_type": "portrait" if h > w else ("square" if h == w else "landscape"),
            "dimensions": {"width": w, "height": h},
            "meta": {
                "brand_name": brand_name,
                "campaign_city": campaign_input.city,
                "language_primary": campaign_input.primary_language,
                "language_secondary": campaign_input.secondary_language or "",
                "template_category": template_slug,
                "generated_at": str(__import__("datetime").datetime.utcnow().isoformat()),
            },
            "bilingual_content": bilingual.model_dump(),
            "layers": layers,
        }

        return poster_json

    @staticmethod
    async def generate_all_variants(
        campaign_input: CampaignContentInput,
        brand: "BrandProfile | None",
        template_slug: str = "orthopedic_health_camp",
        platforms: list[str] | None = None,
    ) -> dict[str, dict]:
        """
        Generate poster JSON for multiple social media platforms.
        Returns a dict keyed by platform name.
        """
        if platforms is None:
            platforms = ["instagram_square", "instagram_story", "facebook_post", "whatsapp_share", "linkedin_banner"]

        # Generate bilingual content ONCE (cost-efficient — single AI call)
        bilingual = await LanguageService.generate_bilingual_content(campaign_input)

        results = {}
        for platform in platforms:
            try:
                poster = await PosterGenerator._build_poster_from_bilingual(
                    campaign_input, bilingual, brand, template_slug, platform
                )
                results[platform] = poster
            except Exception as e:
                results[platform] = {"error": str(e), "platform": platform}

        return results

    @staticmethod
    async def _build_poster_from_bilingual(
        campaign_input: CampaignContentInput,
        bilingual: BilingualCampaignContent,
        brand: "BrandProfile | None",
        template_slug: str,
        platform: str,
    ) -> dict:
        """Build poster JSON from pre-generated bilingual content (no extra AI call)."""
        layout = _resolve_template_layout(template_slug)
        dims = PLATFORM_DIMENSIONS.get(platform, PLATFORM_DIMENSIONS["instagram_square"])
        w, h = dims["width"], dims["height"]
        scale_x = w / 1080
        scale_y = h / 1080

        primary = brand.primary_color if brand else "#1E40AF"
        secondary = brand.secondary_color if brand else "#FFFFFF"
        accent = brand.accent_color if brand else "#F59E0B"
        font = brand.font_family if brand else "Inter"
        regional_font = brand.regional_font_family if brand else "Noto Sans"
        logo_url = brand.logo_url if brand else None
        brand_name = brand.brand_name if brand else campaign_input.org_name
        footer_phones = brand.phone_numbers if brand else [campaign_input.phone]
        footer_address = brand.address if brand else ""

        layers = []

        # Background
        bg = layout.get("background", {"type": "solid", "color": primary})
        if brand and brand.primary_color:
            bg = {"type": "gradient", "colors": [brand.primary_color, _darken_hex(brand.primary_color)], "direction": "135deg"}
        layers.append({"type": "background", **bg})

        # Story layout: compress vertically
        story_compress = 0.55 if platform == "instagram_story" else 1.0

        # Key text blocks — adapted for each platform
        _add_text_layers(layers, layout, bilingual, campaign_input, scale_x, scale_y, story_compress, font, regional_font, secondary, accent, brand)
        _add_service_checklist(layers, layout, bilingual, campaign_input, scale_x, scale_y, story_compress, accent, regional_font, brand)
        _add_footer(layers, layout, brand_name, footer_phones, footer_address, brand, font, scale_x, scale_y, primary, w)

        return {
            "version": "1.0",
            "platform": platform,
            "template_slug": template_slug,
            "dimensions": {"width": w, "height": h},
            "layers": layers,
            "meta": {
                "brand_name": brand_name,
                "city": campaign_input.city,
                "language": bilingual.language,
            },
            "bilingual_content": bilingual.model_dump(),
            "social_caption": bilingual.social_caption_english,
            "hashtags": bilingual.hashtags,
        }


# ── Helpers ────────────────────────────────────────────────────────────

def _darken_hex(hex_color: str, factor: float = 0.15) -> str:
    """Darken a hex color for gradient generation."""
    try:
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        return f"#{r:02X}{g:02X}{b:02X}"
    except Exception:
        return hex_color


def _scale_block(block: dict, sx: float, sy: float) -> dict:
    """Scale layout block position/size values."""
    numeric_fields = {"x", "y", "w", "h", "font_size", "height"}
    result = {}
    for k, v in block.items():
        if k in numeric_fields and isinstance(v, (int, float)):
            axis_scale = sx if k in ("x", "w", "font_size") else sy
            result[k] = int(v * axis_scale)
        else:
            result[k] = v
    return result


def _add_text_layers(layers, layout, bilingual, inp, sx, sy, compress, font, rfont, secondary, accent, brand):
    def t(y): return int(y * sy * compress)
    def s(x): return int(x * sx)

    if "logo" in layout and (brand and brand.logo_url):
        lb = layout["logo"]
        layers.append({"type": "image", "role": "logo", "src": brand.logo_url,
                        "x": s(lb["x"]), "y": t(lb["y"]), "w": s(lb["w"]), "h": t(lb["h"])})

    if "badge" in layout:
        bb = layout["badge"]
        layers.append({"type": "badge", "role": "badge", "text": bilingual.english_badge,
                        "x": s(bb["x"]), "y": t(bb["y"]),
                        "bg": accent if brand else bb["bg"], "text_color": bb.get("text_color", "#000"),
                        "font_size": s(bb["font_size"]), "bold": True, "font_family": font})

    if "title" in layout:
        tb = layout["title"]
        layers.append({"type": "text", "role": "title_english", "text": bilingual.english_title,
                        "x": s(tb["x"]), "y": t(tb["y"]), "w": s(tb["w"]),
                        "font_size": s(tb["font_size"]), "bold": True,
                        "color": secondary if brand else tb["color"], "align": "center", "font_family": font})

    if "regional_title" in layout and bilingual.regional_title:
        rb = layout["regional_title"]
        layers.append({"type": "text", "role": "title_regional", "text": bilingual.regional_title,
                        "x": s(rb["x"]), "y": t(rb["y"]), "w": s(rb["w"]),
                        "font_size": s(rb["font_size"]), "bold": True,
                        "color": accent if brand else rb["color"], "align": "center", "font_family": rfont})

    if "cta" in layout:
        ca = layout["cta"]
        cta = bilingual.english_cta
        if bilingual.regional_cta and bilingual.regional_cta != cta:
            cta = f"{cta}  |  {bilingual.regional_cta}"
        layers.append({"type": "cta_button", "role": "cta", "text": cta,
                        "x": s(ca["x"]), "y": t(ca["y"]), "w": s(ca["w"]), "h": t(ca["h"]),
                        "bg": accent if brand else ca["bg"], "text_color": ca.get("text_color", "#000"),
                        "font_size": s(ca["font_size"]), "bold": True, "border_radius": 12, "font_family": font})

    if "date_block" in layout and inp.date_range:
        dt = layout["date_block"]
        layers.append({"type": "text", "role": "date", "text": f"📅 {inp.date_range}",
                        "x": s(dt["x"]), "y": t(dt["y"]), "font_size": s(dt["font_size"]),
                        "color": dt.get("color", "#FFFFFF"), "align": "center", "font_family": font})


def _add_service_checklist(layers, layout, bilingual, inp, sx, sy, compress, accent, rfont, brand):
    if "checklist" not in layout or not bilingual.english_services:
        return
    cb = layout["checklist"]
    items_en = bilingual.english_services[:6]
    items_reg = bilingual.regional_services[:6] if bilingual.regional_services else []
    items = []
    for i, en in enumerate(items_en):
        reg = items_reg[i] if i < len(items_reg) else ""
        items.append(f"{en} / {reg}" if reg and reg != en else en)

    layers.append({"type": "checklist", "role": "services", "items": items,
                    "x": int(cb["x"] * sx), "y": int(cb["y"] * sy * compress),
                    "font_size": int(cb["font_size"] * sx), "icon": cb.get("icon", "✓"),
                    "icon_color": accent if brand else cb.get("icon_color", "#F59E0B"),
                    "color": cb.get("color", "#FFFFFF"), "columns": cb.get("columns", 2),
                    "line_height": int(cb.get("line_height", 44) * sy), "font_family": rfont})


def _add_footer(layers, layout, brand_name, phones, address, brand, font, sx, sy, primary, w):
    if "footer" not in layout:
        return
    fb = layout["footer"]
    phone_str = "  |  ".join(phones) if phones else ""
    footer_text = f"📞 {phone_str}"
    if address:
        footer_text += f"  •  📍 {address[:60]}"
    layers.append({"type": "footer", "role": "footer", "brand_name": brand_name,
                    "text": footer_text, "phone": phone_str, "address": address or "",
                    "x": 0, "y": int(fb["y"] * sy), "w": w, "h": int(fb["h"] * sy),
                    "bg": primary if brand else fb["bg"], "text_color": "#FFFFFF",
                    "font_size": int(fb["font_size"] * sx), "font_family": font})
