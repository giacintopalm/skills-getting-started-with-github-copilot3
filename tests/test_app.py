"""
Unit tests for the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participants to original state before each test."""
    original = {name: {**data, "participants": list(data["participants"])}
                for name, data in activities.items()}
    yield
    for name, data in original.items():
        activities[name]["participants"] = data["participants"]


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_all():
    """GET /activities should return a dict that includes all three seeded activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_get_activities_contains_expected_fields():
    """Each activity object must expose description, schedule, max_participants and participants."""
    response = client.get("/activities")
    activity = response.json()["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    """POST /activities/{name}/signup with a new email should return 200 and store the participant."""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new_student@mergington.edu"}
    )
    assert response.status_code == 200
    assert "new_student@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity_returns_404():
    """Signing up for an activity that does not exist should return HTTP 404."""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400():
    """A student cannot register twice for the same activity."""
    client.post(
        "/activities/Chess Club/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"


def test_signup_adds_participant_to_list():
    """After a successful signup the email must appear in the activity's participants list."""
    email = "alice@mergington.edu"
    client.post("/activities/Programming Class/signup", params={"email": email})
    assert email in activities["Programming Class"]["participants"]
