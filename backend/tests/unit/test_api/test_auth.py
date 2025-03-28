import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.core.config import settings


def test_login_valid_credentials(client, test_user):
    """Test login with valid credentials."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_username(client):
    """Test login with invalid username."""
    login_data = {
        "username": "nonexistentuser",
        "password": "testpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_invalid_password(client, test_user):
    """Test login with invalid password."""
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_login_inactive_user(client, db, test_user):
    """Test login with an inactive user."""
    # Make the test user inactive
    test_user.is_active = False
    db.commit()
    
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    
    # Reactivate the user for other tests
    test_user.is_active = True
    db.commit()


def test_access_protected_endpoint_valid_token(client, normal_token_headers):
    """Test accessing a protected endpoint with a valid token."""
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "username" in data


def test_access_protected_endpoint_invalid_token(client):
    """Test accessing a protected endpoint with an invalid token."""
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert response.status_code == 401


def test_access_protected_endpoint_no_token(client):
    """Test accessing a protected endpoint without a token."""
    response = client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401


def test_access_admin_endpoint_admin_token(client, admin_token_headers):
    """Test accessing an admin-only endpoint with an admin token."""
    response = client.get(f"{settings.API_V1_STR}/users/", headers=admin_token_headers)
    assert response.status_code == 200


def test_access_admin_endpoint_non_admin_token(client, normal_token_headers):
    """Test accessing an admin-only endpoint with a non-admin token."""
    response = client.get(f"{settings.API_V1_STR}/users/", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_register_new_user(client, db):
    """Test registering a new user."""
    user_data = {
        "username": "registeruser",
        "password": "registerpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "registeruser"
    assert data["is_active"] is True
    assert data["is_admin"] is False
    assert "id" in data
    assert "hashed_password" not in data
    
    # Check that the user was actually created in the database
    user = db.query(User).filter(User.username == "registeruser").first()
    assert user is not None
    assert user.username == "registeruser"
    assert user.is_active is True
    assert user.is_admin is False


def test_register_existing_username(client, test_user):
    """Test registering with an existing username."""
    user_data = {
        "username": test_user.username,  # Same as test_user
        "password": "newpassword"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/register", json=user_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_auth_token_endpoint_url(client, test_user):
    """Test that the auth token endpoint is accessible at the correct URL with API prefix."""
    login_data = {
        "username": test_user.username,
        "password": "testpassword"
    }
    
    # Test with the API v1 path
    response = client.post(f"{settings.API_V1_STR}/auth/token", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json() 