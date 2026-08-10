def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_successfully_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    endpoint = f"/activities/{activity_name}/signup"
    expected_payload = {"message": f"Signed up {email} for {activity_name}"}

    # Act
    response = client.post(endpoint, params={"email": email})
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_payload
    assert email in activities[activity_name]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    # Arrange
    endpoint = "/activities/Unknown Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_when_already_signed_up(client):
    # Arrange
    endpoint = "/activities/Chess Club/signup"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_signup_returns_400_when_activity_is_full(client):
    # Arrange
    endpoint = "/activities/Math Olympiad/signup"
    overflow_email = "overflow@mergington.edu"
    activities = client.get("/activities").json()
    max_size = activities["Math Olympiad"]["max_participants"]

    # Act
    for index in range(max_size - len(activities["Math Olympiad"]["participants"])):
        email = f"filled{index}@mergington.edu"
        signup_response = client.post(
            endpoint, params={"email": email}
        )
        assert signup_response.status_code == 200

    full_response = client.post(endpoint, params={"email": overflow_email})

    # Assert
    assert full_response.status_code == 400
    assert full_response.json() == {"detail": "Activity is full"}


def test_remove_participant_successfully(client):
    # Arrange
    activity_name = "Drama Club"
    email = "lucas@mergington.edu"
    endpoint = f"/activities/{activity_name}/participants"
    expected_payload = {"message": f"Removed {email} from {activity_name}"}

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )
    activities = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_payload
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_returns_404_for_unknown_activity(client):
    # Arrange
    endpoint = "/activities/Unknown Club/participants"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_returns_404_when_not_signed_up(client):
    # Arrange
    endpoint = "/activities/Drama Club/participants"
    email = "not-enrolled@mergington.edu"

    # Act
    response = client.delete(
        endpoint,
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found in this activity"}
