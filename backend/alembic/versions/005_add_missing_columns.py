"""Add pipeline_id to leads, lost_reason to crm_pipelines, extend crmstage enum

Revision ID: 005
Revises: 004
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extend crmstage enum with new values
    op.execute("ALTER TYPE crmstage ADD VALUE IF NOT EXISTS 'interested'")
    op.execute("ALTER TYPE crmstage ADD VALUE IF NOT EXISTS 'appointment_booked'")
    op.execute("ALTER TYPE crmstage ADD VALUE IF NOT EXISTS 'proposal_sent'")

    # Add pipeline_id to leads
    op.add_column("leads", sa.Column("pipeline_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_leads_pipeline_id", "leads", "crm_pipelines", ["pipeline_id"], ["id"], ondelete="SET NULL")

    # Add lost_reason to crm_pipelines
    op.add_column("crm_pipelines", sa.Column("lost_reason", sa.String(255), nullable=True))

    # Add campaign and platform to analytics_events (present in model but missing from migration)
    op.add_column("analytics_events", sa.Column("campaign", sa.String(120), nullable=True))
    op.add_column("analytics_events", sa.Column("platform", sa.String(30), nullable=True))


def downgrade() -> None:
    op.drop_column("analytics_events", "platform")
    op.drop_column("analytics_events", "campaign")
    op.drop_column("crm_pipelines", "lost_reason")
    op.drop_constraint("fk_leads_pipeline_id", "leads", type_="foreignkey")
    op.drop_column("leads", "pipeline_id")
