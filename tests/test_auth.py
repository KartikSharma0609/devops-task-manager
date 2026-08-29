import pytest
from app.models.user import User

# =====================================================================
# 1. USER REGISTRATION TESTS
# =====================================================================


def test_register_user_success(client, app):
    """Test successful user registration creates a user and hashes the password."""
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
    }
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == payload["email"]
    assert "id" in data

    # Verify user exists in DB and password was securely hashed
    with app.app_context():
        user = User.query.filter_by(email=payload["email"]).first()
        assert user is not None
        assert user.password_hash != payload["password"]
        assert user.username == payload["username"]


def test_register_duplicate_email(client, app):
    """Test registering with an already existing email fails."""
    # The 'app' fixture from your conftest already creates 'test@example.com'
    payload = {
        "username": "unique_name",
        "email": "test@example.com",  # Duplicate email
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=payload)
    print("\nAPI RESPONSE:", response.get_json())
    assert response.status_code in (400, 409)
    assert "exists" in response.get_json().get("message", "").lower()


def test_register_duplicate_username(client, app):
    """Test registering with an already existing username fails."""
    # The 'app' fixture already creates 'testuser'
    payload = {
        "username": "testuser",  # Duplicate username
        "email": "unique@example.com",
        "password": "Password123!",
    }
    response = client.post("/auth/register", json=payload)

    assert response.status_code in (400, 409)
    assert "exists" in response.get_json().get("message", "").lower()


@pytest.mark.parametrize("missing_field", ["username", "email", "password"])
def test_register_missing_fields(client, missing_field):
    """Test registration with missing required fields fails validation."""
    payload = {
        "username": "test_user",
        "email": "incomplete@example.com",
        "password": "Password123!",
    }
    del payload[missing_field]

    response = client.post("/auth/register", json=payload)
    assert response.status_code in (400, 422)


# =====================================================================
# 2. LOGIN & JWT ISSUANCE TESTS
# =====================================================================


def test_login_success(client, app):
    """Test logging in with valid credentials returns access and refresh JWTs."""
    # First, register a valid user to test login against
    user_payload = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "CorrectPassword123!",
    }
    client.post("/auth/register", json=user_payload)

    # Attempt Login
    login_payload = {"email": "login@example.com", "password": "CorrectPassword123!"}
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.get_json()

    # Assert tokens are present
    assert "access_token" in data
    # If your app issues refresh tokens, uncomment the next line:
    # assert "refresh_token" in data

    # Assert token format (JWTs have three parts separated by dots)
    assert len(data["access_token"].split(".")) == 3


def test_login_invalid_password(client, app):
    """Test logging in with an incorrect password fails."""
    user_payload = {
        "username": "wrongpassuser",
        "email": "wrongpass@example.com",
        "password": "RealPassword123!",
    }
    client.post("/auth/register", json=user_payload)

    login_payload = {"email": "wrongpass@example.com", "password": "WrongPassword123!"}
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    assert "invalid" in response.get_json().get("message", "invalid").lower()


def test_login_nonexistent_user(client):
    """Test logging in with an email that is not in the database fails."""
    login_payload = {
        "email": "doesnotexist@example.com",
        "password": "SomePassword123!",
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code in (401, 404)


# =====================================================================
# 3. PROTECTED ROUTES & JWT AUTHORIZATION TESTS
# =====================================================================


def test_access_protected_route_success(client, auth_headers):
    """Test accessing a protected route with a valid JWT header succeeds."""
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    # Depending on your implementation, verify the returned data belongs to the user
    assert "username" in data or "email" in data


def test_access_protected_route_missing_token(client):
    """Test accessing a protected endpoint without an Authorization header fails."""
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert "missing" in response.get_json().get("msg", "").lower()


def test_access_protected_route_invalid_token(client):
    """Test accessing a protected endpoint with a malformed JWT fails."""
    bad_headers = {"Authorization": "Bearer fake_invalid_jwt_token"}
    response = client.get("/auth/me", headers=bad_headers)

    # Flask-JWT-Extended usually returns 422 for malformed/un-decodeable tokens
    assert response.status_code == 422
    response_msg = response.get_json().get("msg", "").lower()
    assert "segments" in response_msg or "invalid" in response_msg


def test_access_protected_route_wrong_header_format(client):
    """Test accessing a protected endpoint with a missing 'Bearer ' prefix fails."""
    # The header is missing the "Bearer " prefix standard in JWT Auth
    bad_headers = {"Authorization": "just_the_token_string_no_bearer"}
    response = client.get("/auth/me", headers=bad_headers)

    assert response.status_code == 401
    assert "Bearer" in response.get_json().get("msg", "")


# =====================================================================
# 4. TOKEN REFRESH TESTS (If applicable)
# =====================================================================


def test_refresh_token_success(client, app):
    """Test that a valid refresh token can be used to get a new access token."""
    # Setup: Register and login a user to get a refresh token
    client.post(
        "/auth/register",
        json={
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "Password123!",
        },
    )

    login_response = client.post(
        "/auth/login", json={"email": "refresh@example.com", "password": "Password123!"}
    )

    data = login_response.get_json()

    # Skip this test gracefully if your login route doesn't issue refresh tokens yet
    if "refresh_token" not in data:
        pytest.skip("Refresh tokens not implemented in login response.")

    refresh_token = data["refresh_token"]
    refresh_headers = {"Authorization": f"Bearer {refresh_token}"}

    # Attempt to use the refresh token to get a new access token
    refresh_response = client.post("/auth/refresh", headers=refresh_headers)

    assert refresh_response.status_code == 200
    new_data = refresh_response.get_json()
    assert "access_token" in new_data
    assert (
        new_data["access_token"] != data["access_token"]
    )  # Should be a newly generated token
