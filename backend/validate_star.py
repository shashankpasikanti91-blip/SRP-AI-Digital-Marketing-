"""Validate all Star Hospital API endpoints after seeding."""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import httpx

BASE = "http://localhost:8002/api/v1"

async def main():
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        # Login
        r = await client.post(f"{BASE}/auth/login", json={"email": "admin@starhospital.in", "password": "Star@12345"})
        assert r.status_code == 200, f"Login failed: {r.text}"
        token = r.json()["access_token"]
        h = {"Authorization": f"Bearer {token}"}
        print(f"[OK] Login as admin@starhospital.in")

        # Also test demo login still works
        r2 = await client.post(f"{BASE}/auth/login", json={"email": "demo@srp.ai", "password": "Demo@12345"})
        assert r2.status_code == 200, f"Demo login failed: {r2.text}"
        print(f"[OK] Demo login still works")

        # Test Star Hospital data
        endpoints = [
            ("leads", f"{BASE}/leads/"),
            ("campaigns", f"{BASE}/campaigns/"),
            ("social", f"{BASE}/social/posts/"),
            ("conversations", f"{BASE}/conversations/"),
            ("followups", f"{BASE}/followups/"),
            ("business", f"{BASE}/business/profile/"),
        ]

        for name, url in endpoints:
            resp = await client.get(url, headers=h)
            if resp.status_code == 200:
                data = resp.json()
                count = len(data) if isinstance(data, list) else "single object"
                print(f"[OK] {name}: {count}")
            else:
                print(f"[FAIL] {name}: {resp.status_code} - {resp.text[:100]}")

        # Test social posts with whatsapp platform
        social_resp = await client.get(f"{BASE}/social/posts/?platform=whatsapp", headers=h, follow_redirects=True)
        if social_resp.status_code == 200:
            wa = social_resp.json()
            print(f"[OK] WhatsApp social posts: {len(wa)}")
        else:
            print(f"[FAIL] WhatsApp social filter: {social_resp.status_code}")

        print("\n=== ALL VALIDATIONS COMPLETE ===")

asyncio.run(main())
