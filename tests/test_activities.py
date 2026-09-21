from fastapi.testclient import TestClient

from src.app import activities


def test_root_redirects_to_static_page(client: TestClient):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client: TestClient):
    # Arrange
    expected_fields = {
        "description",
        "schedule",
        "max_participants",
        "participants",
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_activities = response.json()
    assert response_activities
    assert set(response_activities["Chess Club"]) == expected_fields
    assert isinstance(response_activities["Chess Club"]["participants"], list)


def test_signup_adds_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert activities[activity_name]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client: TestClient):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert activities[activity_name]["participants"] == initial_participants


def test_signup_rejects_existing_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}
    assert activities[activity_name]["participants"] == initial_participants


def test_unregister_removes_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert len(activities[activity_name]["participants"]) == initial_count - 1
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client: TestClient):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_unknown_participant(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = "not.registered@mergington.edu"
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
    assert activities[activity_name]["participants"] == initial_participants


def test_unregister_rejects_repeated_request(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]
    client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_requires_email(client: TestClient):
    # Arrange
    activity_name = "Chess Club"
    initial_participants = list(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister")

    # Assert
    assert response.status_code == 422
    assert activities[activity_name]["participants"] == initial_participants