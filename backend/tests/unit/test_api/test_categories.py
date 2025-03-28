import pytest
from fastapi.testclient import TestClient
from app.models.learning import Category


def test_get_categories(client, test_category):
    """Test retrieving all categories."""
    response = client.get("/categories/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the test category should be in the response
    assert len(data) >= 1


def test_get_category(client, test_category):
    """Test retrieving a specific category by ID."""
    response = client.get(f"/categories/{test_category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_category.name
    assert data["description"] == test_category.description
    assert data["id"] == test_category.id


def test_get_nonexistent_category(client):
    """Test retrieving a nonexistent category."""
    response = client.get("/categories/999999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_category_admin(client, admin_token_headers, db):
    """Test creating a new category as admin."""
    category_data = {
        "name": "New Category",
        "description": "This is a new category created by the admin"
    }
    response = client.post("/categories/", json=category_data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Category"
    assert data["description"] == "This is a new category created by the admin"
    assert "id" in data
    
    # Check that the category was actually created in the database
    category = db.query(Category).filter(Category.name == "New Category").first()
    assert category is not None
    assert category.name == "New Category"
    assert category.description == "This is a new category created by the admin"


def test_create_category_regular_user(client, normal_token_headers):
    """Test that regular users cannot create new categories."""
    category_data = {
        "name": "Unauthorized Category",
        "description": "This category should not be created"
    }
    response = client.post("/categories/", json=category_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_create_duplicate_category(client, admin_token_headers, test_category):
    """Test creating a category with a name that already exists."""
    category_data = {
        "name": test_category.name,  # Same as test_category
        "description": "This is a duplicate category"
    }
    response = client.post("/categories/", json=category_data, headers=admin_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_update_category_admin(client, admin_token_headers, db, test_category):
    """Test updating a category as admin."""
    update_data = {
        "name": "Updated Category",
        "description": "This is an updated category"
    }
    response = client.put(f"/categories/{test_category.id}", json=update_data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["description"] == "This is an updated category"
    
    # Check that the category was actually updated in the database
    db.refresh(test_category)
    assert test_category.name == "Updated Category"
    assert test_category.description == "This is an updated category"


def test_update_category_regular_user(client, normal_token_headers, test_category):
    """Test that regular users cannot update categories."""
    update_data = {
        "name": "Unauthorized Update",
        "description": "This update should not be applied"
    }
    response = client.put(f"/categories/{test_category.id}", json=update_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_update_nonexistent_category(client, admin_token_headers):
    """Test updating a nonexistent category."""
    update_data = {
        "name": "Update Nonexistent",
        "description": "This update should not be applied"
    }
    response = client.put("/categories/999999", json=update_data, headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_category_admin(client, admin_token_headers, db):
    """Test deleting a category as admin."""
    # Create a category to delete
    category = Category(
        name="Category to Delete",
        description="This category will be deleted"
    )
    db.add(category)
    db.commit()
    category_id = category.id
    
    response = client.delete(f"/categories/{category_id}", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Category to Delete"
    
    # Check that the category was actually deleted from the database
    deleted_category = db.query(Category).filter(Category.id == category_id).first()
    assert deleted_category is None


def test_delete_category_regular_user(client, normal_token_headers, test_category):
    """Test that regular users cannot delete categories."""
    response = client.delete(f"/categories/{test_category.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_nonexistent_category(client, admin_token_headers):
    """Test deleting a nonexistent category."""
    response = client.delete("/categories/999999", headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_category_courses(client, test_category, test_course):
    """Test retrieving courses for a specific category."""
    response = client.get(f"/categories/{test_category.id}/courses")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(course["title"] == test_course.title for course in data) 