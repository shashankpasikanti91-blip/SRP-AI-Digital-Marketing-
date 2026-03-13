import asyncio, asyncpg
async def check():
    conn = await asyncpg.connect('postgresql://ats_user:ats_password@localhost:5434/srp_marketing')
    row = await conn.fetchrow("SELECT data_type, udt_name FROM information_schema.columns WHERE table_name='leads' AND column_name='status'")
    print('leads.status type:', row)
    row2 = await conn.fetchrow("SELECT count(*) FROM leads")
    print('leads count:', row2['count'])
    row3 = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename")
    print('Tables:', [r['tablename'] for r in row3])
    await conn.close()
asyncio.run(check())
