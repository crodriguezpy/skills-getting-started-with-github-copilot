import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root endpoint redirects to static index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Soccer" in data
    assert "participants" in data["Soccer"]
    assert "max_participants" in data["Soccer"]


def test_signup_success():
    """Test successful signup for an activity"""
    # First, get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_soccer_participants = len(initial_data["Soccer"]["participants"])

    # Sign up a new student
    response = client.post("/activities/Soccer/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Soccer" in data["message"]

    # Verify the participant was added
    response = client.get("/activities")
    updated_data = response.json()
    updated_soccer_participants = len(updated_data["Soccer"]["participants"])
    assert updated_soccer_participants == initial_soccer_participants + 1
    assert "test@example.com" in updated_data["Soccer"]["participants"]


def test_signup_duplicate():
    """Test signing up the same student twice fails"""
    # Sign up a student
    response = client.post("/activities/Soccer/signup?email=duplicate@example.com")
    assert response.status_code == 200

    # Try to sign up the same student again
    response = client.post("/activities/Soccer/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]


def test_signup_invalid_activity():
    """Test signing up for non-existent activity fails"""
    response = client.post("/activities/InvalidActivity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregistration from an activity"""
    # First sign up
    client.post("/activities/Basketball/signup?email=unregister@example.com")

    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_bb_participants = len(initial_data["Basketball"]["participants"])

    # Unregister
    response = client.delete("/activities/Basketball/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Basketball" in data["message"]

    # Verify the participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_bb_participants = len(updated_data["Basketball"]["participants"])
    assert updated_bb_participants == initial_bb_participants - 1
    assert "unregister@example.com" not in updated_data["Basketball"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering a student who is not signed up fails"""
    response = client.delete("/activities/Soccer/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student is not signed up" in data["detail"]


def test_unregister_invalid_activity():
    """Test unregistering from non-existent activity fails"""
    response = client.delete("/activities/InvalidActivity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]