import pytest
from httpx import AsyncClient, ASGITransport

from src.app import app


@pytest.mark.asyncio
async def test_get_activities():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        assert "Chess Club" in data


@pytest.mark.asyncio
async def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ensure user is not already in participants
        resp = await ac.get("/activities")
        assert resp.status_code == 200
        data = resp.json()
        participants = data[activity]["participants"]
        if email in participants:
            # remove it first to ensure a clean state for the test
            await ac.delete(f"/activities/{activity}/participants?email={email}")

        # Sign up the user
        resp = await ac.post(f"/activities/{activity}/signup?email={email}")
        assert resp.status_code == 200
        assert "Signed up" in resp.json().get("message", "")

        # Verify they appear in the participants list
        resp = await ac.get("/activities")
        data = resp.json()
        assert email in data[activity]["participants"]

        # Signing up again should fail (already signed up)
        resp = await ac.post(f"/activities/{activity}/signup?email={email}")
        assert resp.status_code == 400

        # Unregister the participant
        resp = await ac.delete(f"/activities/{activity}/participants?email={email}")
        assert resp.status_code == 200
        assert "Removed" in resp.json().get("message", "")

        # Verify they are gone
        resp = await ac.get("/activities")
        data = resp.json()
        assert email not in data[activity]["participants"]
