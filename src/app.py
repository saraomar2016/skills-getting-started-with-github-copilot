"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
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

# Additional activities: 2 sports, 2 artistic, 2 intellectual
activities.update({
    "Basketball Team": {
        "description": "Competitive basketball team practicing and playing matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": ["aaron@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap swimming, technique practice, and lifeguard training",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 20,
        "participants": ["linda@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting workshops and school play productions",
        "schedule": "Wednesdays, 3:45 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu"]
    },
    "Art Society": {
        "description": "Drawing, painting, and portfolio development",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["mia@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Problem solving club preparing for math competitions",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["ethan@mergington.edu"]
    },
    "Debate Team": {
        "description": "Learn debating skills and compete in tournaments",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 16,
        "participants": ["ava@mergington.edu"]
    }
})


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Normalize email and prevent duplicate signups (case-insensitive)
    normalized = email.strip().lower()
    if any(p.strip().lower() == normalized for p in activity.get("participants", [])):
        raise HTTPException(status_code=400,
                            detail="Student already signed up for this activity")

    # Add student (store normalized email)
    activity.setdefault("participants", []).append(normalized)
    return {"message": f"Signed up {normalized} for {activity_name}"}


@app.delete("/activities/{activity_name}/participants")
def remove_participant(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    activity = activities[activity_name]
    normalized = email.strip().lower()

    participants = activity.get("participants", [])
    for i, p in enumerate(participants):
        if p.strip().lower() == normalized:
            participants.pop(i)
            return {"message": f"Removed {normalized} from {activity_name}"}

    raise HTTPException(status_code=404, detail="Participant not found")
