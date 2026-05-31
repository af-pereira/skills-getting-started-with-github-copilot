from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange: prepare the request path
    path = "/"

    # Act: send the request without following redirects
    response = client.get(path, follow_redirects=False)

    # Assert: verify redirect behavior
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange: expected activity keys based on the seeded data
    expected_activity = "Chess Club"

    # Act: fetch activities
    response = client.get("/activities")

    # Assert: verify response payload and status
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert isinstance(payload[expected_activity]["participants"], list)


def test_signup_for_activity_success(client):
    # Arrange: choose an activity and a new student email
    activity_name = "Chess Club"
    email = "julia@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act: sign up the student
    response = client.post(url, params={"email": email})

    # Assert: verify signup succeeded and state changed
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_returns_400(client):
    # Arrange: sign up a student, then attempt again
    activity_name = "Chess Club"
    email = "julia@mergington.edu"
    url = f"/activities/{activity_name}/signup"
    client.post(url, params={"email": email})

    # Act: duplicate signup attempt
    response = client.post(url, params={"email": email})

    # Assert: verify duplicate signup is rejected
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_for_nonexistent_activity_returns_404(client):
    # Arrange: invalid activity name
    activity_name = "Flying Club"
    email = "julia@mergington.edu"
    url = f"/activities/{activity_name}/signup"

    # Act: send the request
    response = client.post(url, params={"email": email})

    # Assert: verify the activity was not found
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_success(client):
    # Arrange: use an existing participant for unregistering
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    url = f"/activities/{activity_name}/unregister"

    # Act: unregister the student
    response = client.post(url, params={"email": email})

    # Assert: verify unregister succeeded and the participant was removed
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_student_not_signed_up_returns_400(client):
    # Arrange: choose an activity and an email that is not registered
    activity_name = "Chess Club"
    email = "nobody@mergington.edu"
    url = f"/activities/{activity_name}/unregister"

    # Act: attempt to unregister a non-participant
    response = client.post(url, params={"email": email})

    # Assert: verify the request is rejected
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_from_nonexistent_activity_returns_404(client):
    # Arrange: invalid activity name
    activity_name = "Flying Club"
    email = "nobody@mergington.edu"
    url = f"/activities/{activity_name}/unregister"

    # Act: send the request
    response = client.post(url, params={"email": email})

    # Assert: verify the activity was not found
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
