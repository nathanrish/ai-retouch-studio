import httpx
import pytest

BASE = "http://localhost:8000"

@pytest.mark.asyncio
async def test_root_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BASE}/")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
