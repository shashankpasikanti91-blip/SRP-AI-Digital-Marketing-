import asyncio, os, sys
sys.path.insert(0, '.')
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://ats_user:ats_password@localhost:5434/srp_marketing'
os.environ['SECRET_KEY'] = 'x'
os.environ['APP_ENV'] = 'development'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

from app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        # Check missing columns in email_campaigns
        r = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='email_campaigns' ORDER BY ordinal_position"
        ))
        existing = [row[0] for row in r.fetchall()]
        print('email_campaigns columns:', existing)

        # Add missing columns
        missing_sql = []
        if 'description' not in existing:
            missing_sql.append("ALTER TABLE email_campaigns ADD COLUMN IF NOT EXISTS description TEXT")
        if 'from_name' not in existing:
            missing_sql.append("ALTER TABLE email_campaigns ADD COLUMN IF NOT EXISTS from_name VARCHAR(120)")
        if 'from_email' not in existing:
            missing_sql.append("ALTER TABLE email_campaigns ADD COLUMN IF NOT EXISTS from_email VARCHAR(255)")
        if 'campaign_tag' not in existing:
            missing_sql.append("ALTER TABLE email_campaigns ADD COLUMN IF NOT EXISTS campaign_tag VARCHAR(80)")

        for sql in missing_sql:
            print('Running:', sql)
            await conn.execute(text(sql))
        
        if not missing_sql:
            print('All columns already exist!')
        else:
            print('Done adding missing columns.')

        # Also check other tables that may have issues
        for tbl in ['leads', 'social_posts', 'campaigns', 'crm_pipeline']:
            r2 = await conn.execute(text(
                f"SELECT column_name FROM information_schema.columns WHERE table_name='{tbl}' ORDER BY ordinal_position"
            ))
            cols = [row[0] for row in r2.fetchall()]
            print(f'{tbl}: {cols}')

asyncio.run(main())
