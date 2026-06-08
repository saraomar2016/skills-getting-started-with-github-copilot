import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


@pytest.fixture
def clear_activities():
    """Reset activities to known state before each test"""
    from src.app import activities
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    activities.clear()
    activities.update(original)
    yield
    activities.clear()
    activities.update(original)


def test_root_redirect():
    """Test root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert "/static/index.html" in response.headers["location"]


def test_get_activities(clear_activities):
    """Test fetching all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_new_participant(clear_activities):
    """Test signing up a new participant"""
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "newstudent@mergington.edu" in response.json()["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    assert "newstudent@mergington.edu" in activities_response.json()["Chess Club"]["participants"]


def test_signup_duplicate_email(clear_activities):
    """Test preventing duplicate signups (case-insensitive)"""
    # First signup succeeds
    response1 = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response1.status_code == 200
    
    # Second signup with same email fails
    response2 = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response2.status_code == 400
    assert "already signed up" in response2.json()["detail"]


def test_signup_duplicate_case_insensitive(clear_activities):
    """Test duplicate prevention is case-insensitive"""
    response1 = client.post("/activities/Chess%20Club/signup?email=Test@Mergington.edu")
    assert response1.status_code == 200
    
    response2 = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
    assert response2.status_code == 400


def test_signup_nonexistent_activity():
    """Test signup to nonexistent activity returns 404"""
    response = client.post("/activities/FakeActivity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_remove_participant(clear_activities):
    """Test removing a participant"""
    # Add participant
    client.post("/activities/Chess%20Club/signup?email=toremove@mergington.edu")
    
    # Remove participant
    response = client.delete("/activities/Chess%20Club/participants?email=toremove@mergington.edu")
    assert response.status_code == 200
    assert "toremove@mergington.edu" in response.json()["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    assert "toremove@mergington.edu" not in activities_response.json()["Chess Club"]["participants"]


def test_remove_nonexistent_participant(clear_activities):
    """Test removing a participant that doesn't exist"""
    response = client.delete("/activities/Chess%20Club/participants?email=nothere@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]


def test_remove_from_nonexistent_activity():
    """Test removing from nonexistent activity"""
    response = client.delete("/activities/FakeActivity/participants?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_signup_email_normalization(clear_activities):
    """Test that emails are stored normalized (lowercase)"""
    response = client.post("/activities/Chess%20Club/signup?email=  NewUser@MERGINGTON.EDU  ")
    assert response.status_code == 200
    
    activities_response = client.get("/activities")
    participants = activities_response.json()["Chess Club"]["participants"]
    assert "newuser@mergington.edu" in participants
