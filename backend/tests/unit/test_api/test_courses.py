import pytest
from fastapi.testclient import TestClient
from app.models.learning import Course


def test_get_courses(client):
    """Test retrieving all courses."""
    response = client.get("/courses/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the test course should be in the response
    assert len(data) >= 1


def test_get_course(client, test_course):
    """Test retrieving a specific course by ID."""
    response = client.get(f"/courses/{test_course.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_course.title
    assert data["description"] == test_course.description
    assert data["id"] == test_course.id
    assert data["category_id"] == test_course.category_id


def test_get_nonexistent_course(client):
    """Test retrieving a nonexistent course."""
    response = client.get("/courses/999999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_course_admin(client, admin_token_headers, db, test_category):
    """Test creating a new course as admin."""
    course_data = {
        "title": "New Course",
        "description": "This is a new course created by the admin",
        "category_id": test_category.id
    }
    response = client.post("/courses/", json=course_data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Course"
    assert data["description"] == "This is a new course created by the admin"
    assert data["category_id"] == test_category.id
    assert "id" in data
    
    # Check that the course was actually created in the database
    course = db.query(Course).filter(Course.title == "New Course").first()
    assert course is not None
    assert course.title == "New Course"
    assert course.description == "This is a new course created by the admin"
    assert course.category_id == test_category.id


def test_create_course_regular_user(client, normal_token_headers, test_category):
    """Test that regular users cannot create new courses."""
    course_data = {
        "title": "Unauthorized Course",
        "description": "This course should not be created",
        "category_id": test_category.id
    }
    response = client.post("/courses/", json=course_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_create_course_nonexistent_category(client, admin_token_headers):
    """Test creating a course with a nonexistent category."""
    course_data = {
        "title": "Invalid Category Course",
        "description": "This course should not be created",
        "category_id": 999999  # Assuming this ID doesn't exist
    }
    response = client.post("/courses/", json=course_data, headers=admin_token_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_duplicate_course(client, admin_token_headers, test_category, test_course):
    """Test creating a course with a title that already exists in the same category."""
    course_data = {
        "title": test_course.title,  # Same as test_course
        "description": "This is a duplicate course",
        "category_id": test_category.id  # Same category as test_course
    }
    response = client.post("/courses/", json=course_data, headers=admin_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_update_course_admin(client, admin_token_headers, db, test_course):
    """Test updating a course as admin."""
    update_data = {
        "title": "Updated Course",
        "description": "This is an updated course"
    }
    response = client.put(f"/courses/{test_course.id}", json=update_data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Course"
    assert data["description"] == "This is an updated course"
    
    # Check that the course was actually updated in the database
    db.refresh(test_course)
    assert test_course.title == "Updated Course"
    assert test_course.description == "This is an updated course"


def test_update_course_regular_user(client, normal_token_headers, test_course):
    """Test that regular users cannot update courses."""
    update_data = {
        "title": "Unauthorized Update",
        "description": "This update should not be applied"
    }
    response = client.put(f"/courses/{test_course.id}", json=update_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_update_nonexistent_course(client, admin_token_headers):
    """Test updating a nonexistent course."""
    update_data = {
        "title": "Update Nonexistent",
        "description": "This update should not be applied"
    }
    response = client.put("/courses/999999", json=update_data, headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_course_admin(client, admin_token_headers, db, test_category):
    """Test deleting a course as admin."""
    # Create a course to delete
    course = Course(
        title="Course to Delete",
        description="This course will be deleted",
        category_id=test_category.id
    )
    db.add(course)
    db.commit()
    course_id = course.id
    
    response = client.delete(f"/courses/{course_id}", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Course to Delete"
    
    # Check that the course was actually deleted from the database
    deleted_course = db.query(Course).filter(Course.id == course_id).first()
    assert deleted_course is None


def test_delete_course_regular_user(client, normal_token_headers, test_course):
    """Test that regular users cannot delete courses."""
    response = client.delete(f"/courses/{test_course.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_nonexistent_course(client, admin_token_headers):
    """Test deleting a nonexistent course."""
    response = client.delete("/courses/999999", headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_course_units(client, test_course, test_unit):
    """Test retrieving units for a specific course."""
    response = client.get(f"/courses/{test_course.id}/units")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(unit["title"] == test_unit.title for unit in data) 