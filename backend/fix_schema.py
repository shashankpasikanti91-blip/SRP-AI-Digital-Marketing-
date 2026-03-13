"""Quick schema fix — add missing columns to existing tables."""
import asyncio
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine


async def fix():
    async with engine.begin() as conn:
        # Add all missing columns to social_posts
        await conn.execute(text(
            "ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS campaign VARCHAR(120)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_social_posts_campaign ON social_posts(campaign)"
        ))
        await conn.execute(text(
            "ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS ai_generated BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        await conn.execute(text(
            "ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS retry_count INTEGER NOT NULL DEFAULT 0"
        ))
        await conn.execute(text(
            "ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS external_post_id VARCHAR(128)"
        ))
        await conn.execute(text(
            "ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS error_message TEXT"
        ))
        print("[OK] social_posts columns ensured")

        # Add whatsapp/youtube/twitter to the social platform enum if it's a DB enum
        # (In our model we use VARCHAR so enum extension isn't needed)

        print("\n[DONE] Schema fix complete!")

asyncio.run(fix())
