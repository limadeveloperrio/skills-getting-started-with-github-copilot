"""
Tests for High School Management System API

Tests follow the AAA (Arrange-Act-Assert) pattern and use pytest with FastAPI's TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture to provide a TestClient for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Fixture to restore activity participant state after each test."""
    # Store original participants for all activities
    original_state = {
        name: details["participants"].copy()
        for name, details in activities.items()
    }
    yield
    # Restore original state after test
    for name, participants in original_state.items():
        activities[name]["participants"] = participants


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all known activity names."""
        # Arrange
        expected_activities = {"Chess Club", "Programming Class", "Gym Class"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        for activity_name in expected_activities:
            assert activity_name in data

    def test_get_activities_includes_activity_details(self, client):
        """Test that activity details include expected fields."""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]

        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successfully_adds_participant(self, client):
        """Test that successful signup registers a new participant."""
        # Arrange
        activity_name = "Basketball Team"
        email = "new_student@mergington.edu"
        assert email not in activities[activity_name]["participants"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_participant_returns_400(self, client):
        """Test that duplicate signup attempt returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_invalid_activity_returns_404(self, client):
        """Test that signup for nonexistent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_successfully(self, client):
        """Test that participant removal succeeds and removes from list."""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing nonexistent participant returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_invalid_activity_returns_404(self, client):
        """Test that removing participant from invalid activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "test@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
