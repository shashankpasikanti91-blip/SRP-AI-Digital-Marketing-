"""Direct analytics test to find the exact error."""
import asyncio
import os
import sys
import traceback

os.environ['DATABASE_URL'] = 'postgresql+asyncpg://ats_user:ats_password@localhost:5434/srp_marketing'
os.environ['SECRET_KEY'] = '6d15dab061abc0da8ab9ac736a7c0b9b8e55c4371d51c180d455a5dca28903b1'
os.environ['APP_ENV'] = 'development'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'
sys.path.insert(0, '.')

async def main():
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select, func
    import uuid

    DB_URL = os.environ['DATABASE_URL']
    engine = create_async_engine(DB_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Find Star Hospital tenant
    async with AsyncSessionLocal() as db:
        from app.models.tenant import Tenant
        result = await db.execute(select(Tenant).where(Tenant.email == 'admin@starhospital.in'))
        tenant = result.scalar_one_or_none()
        if not tenant:
            result2 = await db.execute(select(Tenant))
            tenants = result2.scalars().all()
            print(f"Available tenants: {[f'{t.name} ({t.email})' for t in tenants]}")
            tenant = tenants[0] if tenants else None
        if not tenant:
            print("No tenant found!")
            return
        
        print(f"Testing with tenant: {tenant.name} ({tenant.id})")
        
        # Test each analytics call individually
        from app.services.analytics_service import AnalyticsService
        
        try:
            print("Testing get_overview...")
            result = await AnalyticsService.get_overview(db, tenant.id)
            print(f"  SUCCESS: total_leads={result.overview.total_leads}")
        except Exception as e:
            print(f"  FAIL: {type(e).__name__}: {e}")
            traceback.print_exc()

asyncio.run(main())
