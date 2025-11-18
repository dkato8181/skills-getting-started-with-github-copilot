from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity checks
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_and_unregister_flow():
    activity = "Basketball Team"
    email = "test.student@mergington.edu"

    # Ensure clean state by unregistering if present
    client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")

    # Signup
    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant appears
    all_activities = client.get("/activities").json()
    participants = all_activities[activity]["participants"]
    assert email in participants

    # Unregister
    resp2 = client.post(f"/activities/{quote(activity)}/unregister?email={quote(email)}")
    assert resp2.status_code == 200
    assert "Removed" in resp2.json().get("message", "")

    # Verify removal
    all_activities = client.get("/activities").json()
    participants = all_activities[activity]["participants"]
    assert email not in participants


def test_duplicate_signup_fails():
    activity = "Chess Club"
    # michael@mergington.edu is in initial data
    email = "michael@mergington.edu"

    resp = client.post(f"/activities/{quote(activity)}/signup?email={quote(email)}")
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()
