"""007_add_regional_marketing_tables

Add tables for the India regional marketing architecture:
- brand_profiles    — tenant brand identity (colors, fonts, logo, footer)
- poster_templates  — reusable layout blueprints per campaign type
- poster_variants   — generated poster JSON per social media platform

Revision ID: 007
Revises: 006
Create Date: 2026-03-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── brand_profiles ────────────────────────────────────────────────
    op.create_table(
        "brand_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("brand_name", sa.String(200), nullable=False),
        sa.Column("tagline", sa.String(300), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("logo_dark_url", sa.String(500), nullable=True),
        sa.Column("primary_color", sa.String(7), nullable=False, server_default="#1E40AF"),
        sa.Column("secondary_color", sa.String(7), nullable=False, server_default="#FFFFFF"),
        sa.Column("accent_color", sa.String(7), nullable=False, server_default="#F59E0B"),
        sa.Column("background_color", sa.String(7), nullable=False, server_default="#F8FAFC"),
        sa.Column("text_color", sa.String(7), nullable=False, server_default="#1F2937"),
        sa.Column("font_family", sa.String(100), nullable=False, server_default="Inter"),
        sa.Column("regional_font_family", sa.String(100), nullable=False, server_default="Noto Sans"),
        sa.Column("footer_text", sa.String(500), nullable=True),
        sa.Column("phone_numbers", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("social_links", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("industry", sa.String(120), nullable=True),
        sa.Column("default_languages", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("country", sa.String(10), nullable=False, server_default="IN"),
        sa.Column("watermark_text", sa.String(200), nullable=True),
        sa.Column("accreditation_logos", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_brand_profiles_tenant_id", "brand_profiles", ["tenant_id"], unique=True)

    # ── poster_templates ──────────────────────────────────────────────
    op.create_table(
        "poster_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("brand_profile_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("brand_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False, server_default="general"),
        sa.Column("layout_type", sa.String(30), nullable=False, server_default="square"),
        sa.Column("width", sa.Integer(), nullable=False, server_default="1080"),
        sa.Column("height", sa.Integer(), nullable=False, server_default="1080"),
        sa.Column("layout_blocks", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("default_title_pattern", sa.String(300), nullable=True),
        sa.Column("default_cta_text", sa.String(200), nullable=True),
        sa.Column("default_badge_text", sa.String(100), nullable=True),
        sa.Column("required_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("optional_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_poster_templates_tenant_id", "poster_templates", ["tenant_id"])
    op.create_index("ix_poster_templates_slug", "poster_templates", ["slug"])

    # ── poster_variants ───────────────────────────────────────────────
    op.create_table(
        "poster_variants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True),
        sa.Column("template_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("poster_templates.id", ondelete="SET NULL"), nullable=True),
        sa.Column("brand_profile_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("brand_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("platform", sa.String(50), nullable=False, server_default="instagram_square"),
        sa.Column("width", sa.String(10), nullable=False, server_default="1080"),
        sa.Column("height", sa.String(10), nullable=False, server_default="1080"),
        sa.Column("campaign_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("language_primary", sa.String(20), nullable=False, server_default="english"),
        sa.Column("language_secondary", sa.String(20), nullable=True),
        sa.Column("bilingual_content", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("poster_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("social_caption", sa.Text(), nullable=True),
        sa.Column("hashtags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_poster_variants_tenant_id", "poster_variants", ["tenant_id"])
    op.create_index("ix_poster_variants_campaign_id", "poster_variants", ["campaign_id"])


def downgrade() -> None:
    op.drop_table("poster_variants")
    op.drop_table("poster_templates")
    op.drop_table("brand_profiles")
