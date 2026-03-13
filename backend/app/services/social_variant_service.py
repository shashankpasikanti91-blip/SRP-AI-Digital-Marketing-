"""
Social Variant Service — auto-generates poster variants for all social media platforms.

Output variants:
  - Instagram Square (1080x1080)
  - Instagram Story (1080x1920)
  - Facebook Post (1200x630)
  - WhatsApp Share (1080x1080 compact)
  - LinkedIn Banner (1200x628)

Each variant adapts text spacing, font sizes, and layout while keeping brand identity.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.services.language_service import CampaignContentInput
from app.services.poster_generator import PosterGenerator

if TYPE_CHECKING:
    from app.models.brand_profile import BrandProfile


# ── Platform variant specifications ───────────────────────────────────

VARIANT_SPECS = {
    "instagram_square": {
        "width": 1080, "height": 1080,
        "label": "Instagram Square",
        "icon": "📸",
        "best_for": "Feed posts, product showcases",
        "text_density": "medium",
        "services_max": 6,
    },
    "instagram_story": {
        "width": 1080, "height": 1920,
        "label": "Instagram Story",
        "icon": "📱",
        "best_for": "Stories, Reels cover",
        "text_density": "low",
        "services_max": 4,
    },
    "facebook_post": {
        "width": 1200, "height": 630,
        "label": "Facebook Post",
        "icon": "👥",
        "best_for": "Facebook feed, boosted posts",
        "text_density": "medium",
        "services_max": 6,
    },
    "whatsapp_share": {
        "width": 1080, "height": 1080,
        "label": "WhatsApp Share",
        "icon": "💬",
        "best_for": "WhatsApp groups, broadcast",
        "text_density": "high",
        "services_max": 8,
        "compact_footer": True,
    },
    "linkedin_banner": {
        "width": 1200, "height": 628,
        "label": "LinkedIn Banner",
        "icon": "💼",
        "best_for": "LinkedIn posts, company page",
        "text_density": "low",
        "services_max": 4,
    },
}


class SocialVariantService:
    """
    Generates all social media poster variants for a campaign.

    Design principle:
    - Generate bilingual content ONCE per campaign (one AI call)
    - Reuse that content across all platform variants
    - Each variant only adapts layout/dimensions, not content
    """

    @staticmethod
    async def generate_all_variants(
        campaign_input: CampaignContentInput,
        brand: "BrandProfile | None",
        template_slug: str,
        platforms: list[str] | None = None,
    ) -> dict:
        """
        Generate poster JSON for all requested social media variants.

        Returns:
          {
            "instagram_square": {poster_json},
            "instagram_story": {poster_json},
            ...
            "summary": {bilingual_content, hashtags, captions}
          }
        """
        selected = platforms or list(VARIANT_SPECS.keys())

        # Single AI call — generate all variants
        variants = await PosterGenerator.generate_all_variants(
            campaign_input=campaign_input,
            brand=brand,
            template_slug=template_slug,
            platforms=selected,
        )

        # Add platform metadata to each variant
        for platform, data in variants.items():
            if isinstance(data, dict) and "error" not in data:
                spec = VARIANT_SPECS.get(platform, {})
                data["platform_meta"] = {
                    "label": spec.get("label", platform),
                    "icon": spec.get("icon", "🖼"),
                    "dimensions": f"{spec.get('width', '?')}×{spec.get('height', '?')}",
                    "best_for": spec.get("best_for", ""),
                }

        # Extract summary from first successful variant
        first_ok = next((v for v in variants.values() if isinstance(v, dict) and "error" not in v), {})
        bilingual = first_ok.get("bilingual_content", {})

        # Generate platform-specific captions
        captions = SocialVariantService._generate_captions(bilingual, campaign_input)

        return {
            "variants": variants,
            "summary": {
                "bilingual_content": bilingual,
                "captions": captions,
                "hashtags": bilingual.get("hashtags", []),
                "platforms_generated": [p for p in selected if "error" not in variants.get(p, {})],
                "template_slug": template_slug,
                "city": campaign_input.city,
                "language": campaign_input.secondary_language or "english",
            },
        }

    @staticmethod
    def _generate_captions(bilingual: dict, inp: CampaignContentInput) -> dict[str, str]:
        """Platform-specific caption copy from bilingual content."""
        en_caption = bilingual.get("social_caption_english", "")
        reg_caption = bilingual.get("social_caption_regional", "")
        cta = bilingual.get("english_cta", "Contact us today!")
        hashtags = " ".join(bilingual.get("hashtags", [])[:10])

        ig_caption = f"{en_caption}\n\n{reg_caption}\n\n{cta}\n\n{hashtags}" if reg_caption else f"{en_caption}\n\n{cta}\n\n{hashtags}"
        fb_caption = f"{en_caption}\n\n{reg_caption}\n\n📞 {inp.phone or 'Call us'}\n\n{hashtags}" if reg_caption else f"{en_caption}\n\n{hashtags}"
        wa_caption = f"*{bilingual.get('english_title', '')}*\n\n{en_caption}\n\n📞 {inp.phone or 'Call us'}"
        li_caption = f"{en_caption}\n\n{cta}\n\n{hashtags}"

        return {
            "instagram": ig_caption,
            "facebook": fb_caption,
            "whatsapp": wa_caption,
            "linkedin": li_caption,
        }

    @staticmethod
    def get_variant_specs() -> dict:
        return VARIANT_SPECS
