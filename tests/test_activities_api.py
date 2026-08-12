from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities_returns_list():
    """Test that GET /activities returns a list of activities."""
    # Arrange
    # (no special setup needed, activities are pre-populated)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert len(activities) > 0


def test_signup_for_activity_success():
    """Test that a student can successfully sign up for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == f"Signed up {email} for {activity_name}"

    # Verify participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_email_returns_400():
    """Test that signing up with a duplicate email returns 400."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already registered

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity_returns_404():
    """Test that signing up for a nonexistent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_participant_removes_email():
    """Test that a participant can successfully unregister from an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"
    
    # First, sign up the student
    client.post(f"/activities/{activity_name}/signup?email={email}")

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={email}"
    )

    # Assert
    assert unregister_response.status_code == 200
    payload = unregister_response.json()
    assert payload["message"] == f"Removed {email} from {activity_name}"

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_email_returns_404():
    """Test that unregistering a non-existent participant returns 404."""
    # Arrange
    activity_name = "Chess Club"
    email = "missing-student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Student not found" in data["detail"]


def test_unregister_nonexistent_activity_returns_404():
    """Test that unregistering from a nonexistent activity returns 404."""
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]
