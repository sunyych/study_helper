import pytest
from fastapi.testclient import TestClient
from app.models.learning import Unit


def test_get_units(client):
    """Test retrieving all units."""
    response = client.get("/units/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # At least the test unit should be in the response
    assert len(data) >= 1


def test_get_unit(client, test_unit):
    """Test retrieving a specific unit by ID."""
    response = client.get(f"/units/{test_unit.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_unit.title
    assert data["description"] == test_unit.description
    assert data["id"] == test_unit.id
    assert data["course_id"] == test_unit.course_id
    assert data["order"] == test_unit.order


def test_get_nonexistent_unit(client):
    """Test retrieving a nonexistent unit."""
    response = client.get("/units/999999")  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_unit_admin(client, admin_token_headers, db, test_course):
    """Test creating a new unit as admin."""
    unit_data = {
        "title": "New Unit",
        "description": "This is a new unit created by the admin",
        "order": 2,
        "course_id": test_course.id
    }
    response = client.post("/units/", json=unit_data, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Unit"
    assert data["description"] == "This is a new unit created by the admin"
    assert data["order"] == 2
    assert data["course_id"] == test_course.id
    assert "id" in data
    
    # Check that the unit was actually created in the database
    unit = db.query(Unit).filter(Unit.title == "New Unit").first()
    assert unit is not None
    assert unit.title == "New Unit"
    assert unit.description == "This is a new unit created by the admin"
    assert unit.order == 2
    assert unit.course_id == test_course.id


def test_create_unit_regular_user(client, normal_token_headers, test_course):
    """Test that regular users cannot create new units."""
    unit_data = {
        "title": "Unauthorized Unit",
        "description": "This unit should not be created",
        "order": 3,
        "course_id": test_course.id
    }
    response = client.post("/units/", json=unit_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_create_unit_nonexistent_course(client, admin_token_headers):
    """Test creating a unit with a nonexistent course."""
    unit_data = {
        "title": "Invalid Course Unit",
        "description": "This unit should not be created",
        "order": 1,
        "course_id": 999999  # Assuming this ID doesn't exist
    }
    response = client.post("/units/", json=unit_data, headers=admin_token_headers)
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_create_duplicate_unit(client, admin_token_headers, test_course, test_unit):
    """Test creating a unit with a title that already exists in the same course."""
    unit_data = {
        "title": test_unit.title,  # Same as test_unit
        "description": "This is a duplicate unit",
        "order": 2,
        "course_id": test_course.id  # Same course as test_unit
    }
    response = client.post("/units/", json=unit_data, headers=admin_token_headers)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data


def test_update_unit_admin(client, admin_token_headers, db, test_unit):
    """Test updating a unit as admin."""
    update_data = {
        "title": "Updated Unit",
        "description": "This is an updated unit",
        "order": 10
    }
    response = client.put(f"/units/{test_unit.id}", json=update_data, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Unit"
    assert data["description"] == "This is an updated unit"
    assert data["order"] == 10
    
    # Check that the unit was actually updated in the database
    db.refresh(test_unit)
    assert test_unit.title == "Updated Unit"
    assert test_unit.description == "This is an updated unit"
    assert test_unit.order == 10


def test_update_unit_regular_user(client, normal_token_headers, test_unit):
    """Test that regular users cannot update units."""
    update_data = {
        "title": "Unauthorized Update",
        "description": "This update should not be applied",
        "order": 20
    }
    response = client.put(f"/units/{test_unit.id}", json=update_data, headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_update_nonexistent_unit(client, admin_token_headers):
    """Test updating a nonexistent unit."""
    update_data = {
        "title": "Update Nonexistent",
        "description": "This update should not be applied",
        "order": 5
    }
    response = client.put("/units/999999", json=update_data, headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_delete_unit_admin(client, admin_token_headers, db, test_course):
    """Test deleting a unit as admin."""
    # Create a unit to delete
    unit = Unit(
        title="Unit to Delete",
        description="This unit will be deleted",
        order=3,
        course_id=test_course.id
    )
    db.add(unit)
    db.commit()
    unit_id = unit.id
    
    response = client.delete(f"/units/{unit_id}", headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Unit to Delete"
    
    # Check that the unit was actually deleted from the database
    deleted_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    assert deleted_unit is None


def test_delete_unit_regular_user(client, normal_token_headers, test_unit):
    """Test that regular users cannot delete units."""
    response = client.delete(f"/units/{test_unit.id}", headers=normal_token_headers)
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data


def test_delete_nonexistent_unit(client, admin_token_headers):
    """Test deleting a nonexistent unit."""
    response = client.delete("/units/999999", headers=admin_token_headers)  # Assuming this ID doesn't exist
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_unit_videos(client, test_unit, test_video):
    """Test retrieving videos for a specific unit."""
    response = client.get(f"/units/{test_unit.id}/videos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(video["title"] == test_video.title for video in data)


def test_reorder_units_admin(client, admin_token_headers, db, test_course):
    """Test reordering units as admin."""
    # Create multiple units to reorder
    unit1 = Unit(
        title="Reorder Unit 1",
        description="This is the first unit to reorder",
        order=1,
        course_id=test_course.id
    )
    unit2 = Unit(
        title="Reorder Unit 2",
        description="This is the second unit to reorder",
        order=2,
        course_id=test_course.id
    )
    unit3 = Unit(
        title="Reorder Unit 3",
        description="This is the third unit to reorder",
        order=3,
        course_id=test_course.id
    )
    db.add_all([unit1, unit2, unit3])
    db.commit()
    
    # New order: unit3, unit1, unit2
    reorder_data = {
        "unit_ids": [unit3.id, unit1.id, unit2.id]
    }
    
    response = client.post(f"/courses/{test_course.id}/reorder-units", json=reorder_data, headers=admin_token_headers)
    assert response.status_code == 200
    
    # Check that the units were actually reordered in the database
    db.refresh(unit1)
    db.refresh(unit2)
    db.refresh(unit3)
    assert unit3.order == 1
    assert unit1.order == 2
    assert unit2.order == 3 