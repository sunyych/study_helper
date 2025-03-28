import pytest
from fastapi.testclient import TestClient
from app.models.user import User


def test_get_users_admin(client, admin_token_headers):
    """Test retrieving all users as admin."""
    response = client.get("/users/", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the admin user should be in the response
    assert len(data) >= 1


def test_get_users_regular_user(client, normal_token_headers):
    """Test that regular users cannot retrieve all users."""
    response = client.get("/users/", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_create_user_admin(client, admin_token_headers, db):
    """Test creating a new user as admin."""
    user_data = {
        "username": "newuser",
        "password": "newpassword",
        "is_active": True,
        "is_admin": False
    }
    response = client.post("/users/", json=user_data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert data["is_admin"] == False


def test_create_user_regular_user(client, normal_token_headers):
    """Test that regular users cannot create new users."""
    user_data = {
        "username": "anothernewuser",
        "password": "newpassword",
        "is_active": True,
        "is_admin": False
    }
    response = client.post("/users/", json=user_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_get_user_me(client, normal_token_headers, test_user):
    """Test retrieving the current user."""
    response = client.get("/users/me", headers=normal_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["id"] == test_user.id


def test_update_user_me(client, normal_token_headers, db, test_user):
    """Test updating the current user."""
    update_data = {
        "username": "updatedusername"
    }
    response = client.put("/users/me", json=update_data, headers=normal_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "updatedusername"
    
    # Verify the update in the database
    db.refresh(test_user)
    assert test_user.username == "updatedusername"


def test_get_user_by_id_admin(client, admin_token_headers, test_user):
    """Test retrieving a user by ID as admin."""
    response = client.get(f"/users/{test_user.id}", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_user.username
    assert data["id"] == test_user.id


def test_get_user_by_id_regular_user(client, normal_token_headers, test_admin):
    """Test that regular users cannot retrieve other users by ID."""
    response = client.get(f"/users/{test_admin.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_update_user_admin(client, admin_token_headers, db, test_user):
    """Test updating a user as admin."""
    update_data = {
        "username": "adminupdated",
        "is_admin": True
    }
    response = client.put(f"/users/{test_user.id}", json=update_data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "adminupdated"
    assert data["is_admin"] == True
    
    # Verify the update in the database
    db.refresh(test_user)
    assert test_user.username == "adminupdated"
    assert test_user.is_admin == True


def test_update_user_regular_user(client, normal_token_headers, test_admin):
    """Test that regular users cannot update other users."""
    update_data = {
        "username": "regularupdated"
    }
    response = client.put(f"/users/{test_admin.id}", json=update_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_user_admin(client, admin_token_headers, db):
    """Test deleting a user as admin."""
    # Create a user to delete
    user = User(
        username="todelete",
        hashed_password="hashedpassword",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    user_id = user.id
    
    response = client.delete(f"/users/{user_id}", headers=admin_token_headers)
    assert response.status_code == 200
    
    # Verify the user was deleted
    deleted_user = db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_delete_user_regular_user(client, normal_token_headers, test_admin):
    """Test that regular users cannot delete other users."""
    response = client.delete(f"/users/{test_admin.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data 