"""
Migration 009 — AI Usage Tracking + Plan Credits

Creates:
  - ai_usage_log: per-request AI usage tracking with token counts, cost, feature bucket
  - tenant_plan_credits: monthly credit snapshots per tenant (optional, for billing)

All tables are purely additive — no existing table is altered.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "009_ai_usage_tracking"
down_revision = "008_global_localization"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ── ai_usage_log ──────────────────────────────────────────────────────────
    op.create_table(
        "ai_usage_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True, index=True),

        # Feature classification
        sa.Column("feature_bucket", sa.String(60), nullable=False, index=True),
        # text_basic | text_marketing | translation | localization | seo_keywords |
        # campaign_strategy | image_prompting | image_generation | lead_classification |
        # email_copywriting | chatbot

        sa.Column("billing_category", sa.String(40), nullable=False, index=True),
        # text_generation | translation | image_generation

        # Model / provider
        sa.Column("model_id", sa.String(120), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        # openrouter | openai | anthropic | google

        # Token counts
        sa.Column("input_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("output_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("total_tokens", sa.Integer(), nullable=False, default=0),
        sa.Column("estimated_cost_usd", sa.Numeric(precision=12, scale=8), nullable=False, default=0),

        # Locale context
        sa.Column("country_code", sa.String(5), nullable=True, index=True),
        sa.Column("language_mode", sa.String(20), nullable=True),
        sa.Column("industry", sa.String(60), nullable=True),
        sa.Column("platform", sa.String(40), nullable=True),

        # Creative counts
        sa.Column("creatives_count", sa.Integer(), nullable=False, default=0),
        sa.Column("translations_count", sa.Integer(), nullable=False, default=0),
        sa.Column("images_count", sa.Integer(), nullable=False, default=0),

        # Status
        sa.Column("success", sa.Boolean(), nullable=False, default=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("extra_metadata", JSONB, nullable=True),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    # Composite index for fast monthly summaries
    op.create_index(
        "ix_ai_usage_log_tenant_month",
        "ai_usage_log",
        ["tenant_id", "billing_category", "created_at"],
    )

    # ── tenant_plan_credits ───────────────────────────────────────────────────
    # Optional table for credit pack purchases or overrides
    op.create_table(
        "tenant_plan_credits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("billing_category", sa.String(40), nullable=False),
        sa.Column("credit_amount", sa.Integer(), nullable=False, default=0),
        sa.Column("used_amount", sa.Integer(), nullable=False, default=0),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(40), nullable=True),   # monthly_plan | top_up | promo
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_index("ix_ai_usage_log_tenant_month", table_name="ai_usage_log")
    op.drop_table("tenant_plan_credits")
    op.drop_table("ai_usage_log")
