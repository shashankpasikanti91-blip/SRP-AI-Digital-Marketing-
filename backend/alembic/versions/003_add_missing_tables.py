"""Add business_profiles, campaigns, conversations, followup tables

Revision ID: 003
Revises: 002
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── business_profiles ────────────────────────────────────────────────────
    op.create_table(
        "business_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_name", sa.String(200), nullable=False),
        sa.Column("business_type", sa.String(120), nullable=False),
        sa.Column("industry", sa.String(120), nullable=False),
        sa.Column("location", sa.String(200), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("main_offer", sa.Text(), nullable=True),
        sa.Column("unique_selling_proposition", sa.Text(), nullable=True),
        sa.Column("brand_voice", sa.String(100), nullable=True),
        sa.Column("brand_colors", postgresql.JSONB(), nullable=True),
        sa.Column("competitors", sa.Text(), nullable=True),
        sa.Column("current_challenges", sa.Text(), nullable=True),
        sa.Column("monthly_budget", sa.String(50), nullable=True),
        sa.Column("primary_goal", sa.String(200), nullable=True),
        sa.Column("channels", postgresql.JSONB(), nullable=True),
        sa.Column("contact_phone", sa.String(30), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("business_hours", sa.String(200), nullable=True),
        sa.Column("strategy_json", postgresql.JSONB(), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )
    op.create_index("ix_business_profiles_tenant_id", "business_profiles", ["tenant_id"])

    # ── campaigns ────────────────────────────────────────────────────────────
    op.execute("""DO $$ BEGIN CREATE TYPE campaign_status_enum AS ENUM ('draft','active','paused','completed','cancelled'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("objective", sa.String(200), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("target_audience", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(120), nullable=True),
        sa.Column("channels", postgresql.JSONB(), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_weeks", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("budget_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("budget_spent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(10), nullable=False, server_default="USD"),
        sa.Column("ai_plan_json", postgresql.JSONB(), nullable=True),
        sa.Column("leads_generated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("impressions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campaigns_tenant_id", "campaigns", ["tenant_id"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    # ── conversations ────────────────────────────────────────────────────────
    op.execute("""DO $$ BEGIN CREATE TYPE conversation_channel_enum AS ENUM ('facebook','instagram','whatsapp','email','website_chat','linkedin'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.execute("""DO $$ BEGIN CREATE TYPE conversation_status_enum AS ENUM ('open','waiting','resolved','escalated','spam'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="open"),
        sa.Column("contact_name", sa.String(120), nullable=True),
        sa.Column("contact_identifier", sa.String(255), nullable=True),
        sa.Column("external_thread_id", sa.String(255), nullable=True),
        sa.Column("assigned_to", sa.String(120), nullable=True),
        sa.Column("unread_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_preview", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversations_tenant_id", "conversations", ["tenant_id"])
    op.create_index("ix_conversations_lead_id", "conversations", ["lead_id"])

    # ── conversation_messages ────────────────────────────────────────────────
    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ai_metadata", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conv_messages_conversation_id", "conversation_messages", ["conversation_id"])
    op.create_index("ix_conv_messages_created_at", "conversation_messages", ["created_at"])

    # ── followup_sequences ───────────────────────────────────────────────────
    op.execute("""DO $$ BEGIN CREATE TYPE sequence_status_enum AS ENUM ('draft','active','paused','archived'); EXCEPTION WHEN duplicate_object THEN null; END $$""")
    op.create_table(
        "followup_sequences",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("trigger", sa.String(100), nullable=False),
        sa.Column("sequence_type", sa.String(60), nullable=False, server_default="new_lead"),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("target_segment", sa.String(100), nullable=True),
        sa.Column("exit_conditions", postgresql.JSONB(), nullable=True),
        sa.Column("ai_generated_json", postgresql.JSONB(), nullable=True),
        sa.Column("enrolled_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reply_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_followup_sequences_tenant_id", "followup_sequences", ["tenant_id"])

    # ── followup_steps ───────────────────────────────────────────────────────
    op.create_table(
        "followup_steps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_number", sa.Integer(), nullable=False),
        sa.Column("delay_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("subject", sa.String(300), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("cta", sa.String(200), nullable=True),
        sa.Column("goal", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["sequence_id"], ["followup_sequences.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_followup_steps_sequence_id", "followup_steps", ["sequence_id"])


def downgrade() -> None:
    op.drop_table("followup_steps")
    op.drop_table("followup_sequences")
    op.drop_table("conversation_messages")
    op.drop_table("conversations")
    op.drop_table("campaigns")
    op.drop_table("business_profiles")
    op.execute("DROP TYPE IF EXISTS sequence_status_enum")
    op.execute("DROP TYPE IF EXISTS conversation_status_enum")
    op.execute("DROP TYPE IF EXISTS conversation_channel_enum")
    op.execute("DROP TYPE IF EXISTS campaign_status_enum")
