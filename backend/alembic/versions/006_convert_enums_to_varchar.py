"""Convert native PG enum columns to VARCHAR to avoid case sensitivity issues

Revision ID: 006
Revises: 005
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Convert leads.status from leadstatus enum to varchar
    op.execute("ALTER TABLE leads ALTER COLUMN status TYPE VARCHAR(30) USING status::text")

    # Convert crm_pipelines.stage from crmstage enum to varchar
    op.execute("ALTER TABLE crm_pipelines ALTER COLUMN stage TYPE VARCHAR(50) USING stage::text")

    # Convert social_posts.platform from socialplatform enum to varchar
    op.execute("ALTER TABLE social_posts ALTER COLUMN platform TYPE VARCHAR(30) USING platform::text")

    # Convert social_posts.status from poststatus enum to varchar
    op.execute("ALTER TABLE social_posts ALTER COLUMN status TYPE VARCHAR(30) USING status::text")


def downgrade() -> None:
    # Note: downgrade would require recreating the enum types and casting back
    pass
