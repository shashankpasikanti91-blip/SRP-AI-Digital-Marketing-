import asyncio, sys, traceback, os
os.environ.setdefault('DATABASE_URL', 'postgresql+asyncpg://ats_user:ats_password@localhost:5434/srp_marketing')
os.environ.setdefault('SECRET_KEY', '6d15dab061abc0da8ab9ac736a7c0b9b8e55c4371d51c180d455a5dca28903b1')
os.environ.setdefault('APP_ENV', 'development')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
sys.path.insert(0, '.')

async def test():
    from app.config import settings
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy import text
    from app.services.analytics_service import AnalyticsService

    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(text('SELECT id FROM tenants LIMIT 1'))
        row = result.fetchone()
        if not row:
            print('No tenants found')
            return
        tid = row[0]
        print(f'Testing with tenant: {tid}')
        try:
            r = await AnalyticsService.get_overview(session, tid)
            print(f'SUCCESS: {r.overview.total_leads} leads')
        except Exception:
            print('ANALYTICS ERROR:')
            traceback.print_exc()

asyncio.run(test())
