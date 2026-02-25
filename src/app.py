"""
High School Management System API

A FastAPI application that allows students to view and sign up for
extracurricular activities at Mergington High School.

Endpoints:
    GET  /              - Redirects to the static frontend.
    GET  /activities    - Returns all available activities and their details.
    POST /activities/{activity_name}/signup
                       - Registers a student (by email) for the given activity.

Data is stored in memory; all state resets when the server restarts.
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


@app.get("/")
def root():
    """Redirect the browser to the static frontend (index.html)."""
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Return all extracurricular activities.

    Returns:
        dict: A dictionary keyed by activity name. Each value contains:
            - description (str): What the activity involves.
            - schedule (str): When/where the activity meets.
            - max_participants (int): Maximum number of allowed participants.
            - participants (list[str]): Emails of currently enrolled students.
    """
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Register a student for an extracurricular activity.

    Args:
        activity_name (str): The exact name of the activity (path parameter).
        email (str): The student's school email address (query parameter).

    Returns:
        dict: A confirmation message on success,
              e.g. ``{"message": "Signed up alice@mergington.edu for Chess Club"}``.

    Raises:
        HTTPException 404: If ``activity_name`` does not match any known activity.
        HTTPException 400: If the student is already registered for the activity.
    """
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}
