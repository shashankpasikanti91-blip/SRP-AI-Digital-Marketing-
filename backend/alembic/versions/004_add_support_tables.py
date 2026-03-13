"""Add notifications, activity_logs, content_pieces, design_briefs

Revision ID: 004
Revises: 003
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── notifications ────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(60), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("link", sa.String(512), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_tenant_id", "notifications", ["tenant_id"])
    op.create_index("ix_notifications_created_at", "notifications", ["created_at"])

    # ── activity_logs ────────────────────────────────────────────────────────
    op.create_table(
        "activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(60), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("actor", sa.String(120), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_logs_tenant_id", "activity_logs", ["tenant_id"])
    op.create_index("ix_activity_logs_entity_id", "activity_logs", ["entity_id"])
    op.create_index("ix_activity_logs_created_at", "activity_logs", ["created_at"])

    # ── content_pieces ───────────────────────────────────────────────────────
    op.execute("""DO $$ BEGIN CREATE TYPE content_type_enum AS ENUM ('social_post','ad_copy','email','blog','caption','cta','sms'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.execute("""DO $$ BEGIN CREATE TYPE content_status_enum AS ENUM ('draft','approved','scheduled','published','archived'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.create_table(
        "content_pieces",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(30), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("headline", sa.String(300), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("cta", sa.String(300), nullable=True),
        sa.Column("platform", sa.String(50), nullable=True),
        sa.Column("tone", sa.String(50), nullable=True),
        sa.Column("hashtags", postgresql.JSONB(), nullable=True),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("ai_full_output", postgresql.JSONB(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_pieces_tenant_id", "content_pieces", ["tenant_id"])
    op.create_index("ix_content_pieces_campaign_id", "content_pieces", ["campaign_id"])

    # ── design_briefs ────────────────────────────────────────────────────────
    op.create_table(
        "design_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("campaign_name", sa.String(200), nullable=False),
        sa.Column("format_type", sa.String(50), nullable=False),
        sa.Column("platform", sa.String(50), nullable=False),
        sa.Column("headline", sa.String(300), nullable=False),
        sa.Column("subheadline", sa.String(300), nullable=True),
        sa.Column("cta_text", sa.String(100), nullable=True),
        sa.Column("color_palette", postgresql.JSONB(), nullable=True),
        sa.Column("mood", sa.String(100), nullable=True),
        sa.Column("imagery_description", sa.Text(), nullable=True),
        sa.Column("full_brief_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_design_briefs_tenant_id", "design_briefs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("design_briefs")
    op.drop_table("content_pieces")
    op.drop_table("activity_logs")
    op.drop_table("notifications")
    op.execute("DROP TYPE IF EXISTS content_status_enum")
    op.execute("DROP TYPE IF EXISTS content_type_enum")
