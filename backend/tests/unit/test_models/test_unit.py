import pytest
from sqlalchemy.exc import IntegrityError
from app.models.learning import Unit


def test_create_unit(db, test_course):
    """Test creating a unit."""
    unit = Unit(
        title="New Test Unit",
        description="This is a new test unit",
        order=1,
        course_id=test_course.id
    )
    db.add(unit)
    db.commit()
    
    retrieved_unit = db.query(Unit).filter(Unit.title == "New Test Unit").first()
    assert retrieved_unit is not None
    assert retrieved_unit.title == "New Test Unit"
    assert retrieved_unit.description == "This is a new test unit"
    assert retrieved_unit.order == 1
    assert retrieved_unit.course_id == test_course.id


def test_unit_unique_title_per_course(db, test_course, test_unit):
    """Test that unit title must be unique per course."""
    with pytest.raises(IntegrityError):
        # Create a unit with the same title in the same course
        unit = Unit(
            title="Test Unit",  # Same as test_unit fixture
            description="This is a duplicate unit",
            order=2,
            course_id=test_course.id  # Same course as test_unit
        )
        db.add(unit)
        db.commit()
    
    # Rollback to clean up
    db.rollback()


def test_unit_same_title_different_course(db, test_course, test_unit):
    """Test that same unit title is allowed in different courses."""
    # Create a new course
    course = db.query(Unit).filter(Unit.id == test_unit.id).first()
    course_id = course.course_id
    
    # Create a new course
    new_course = db.query(Unit).filter(Unit.id != test_unit.id).first().course
    
    # Verify that course_id and new_course.id are different
    assert course_id != new_course.id
    
    # Create a unit with the same title but in a different course
    unit = Unit(
        title="Test Unit",  # Same as test_unit fixture
        description="This is a unit with the same title but in a different course",
        order=1,
        course_id=new_course.id
    )
    db.add(unit)
    db.commit()
    
    # Verify that both units exist
    units = db.query(Unit).filter(Unit.title == "Test Unit").all()
    assert len(units) >= 2
    # Ensure we have units in different courses
    course_ids = {u.course_id for u in units}
    assert len(course_ids) >= 2


def test_update_unit(db, test_unit):
    """Test updating a unit."""
    # Update the unit
    test_unit.title = "Updated Unit"
    test_unit.description = "This is an updated unit"
    test_unit.order = 99
    db.commit()
    
    # Verify changes
    updated_unit = db.query(Unit).filter(Unit.id == test_unit.id).first()
    assert updated_unit.title == "Updated Unit"
    assert updated_unit.description == "This is an updated unit"
    assert updated_unit.order == 99


def test_delete_unit(db, test_course):
    """Test deleting a unit."""
    # Create a unit to delete
    unit = Unit(
        title="Unit to Delete",
        description="This unit will be deleted",
        order=3,
        course_id=test_course.id
    )
    db.add(unit)
    db.commit()
    
    # Get the ID before deletion
    unit_id = unit.id
    
    # Delete the unit
    db.delete(unit)
    db.commit()
    
    # Verify deletion
    deleted_unit = db.query(Unit).filter(Unit.id == unit_id).first()
    assert deleted_unit is None


def test_unit_with_videos(db, test_unit, test_video):
    """Test retrieving videos associated with a unit."""
    # test_video is already associated with test_unit by the fixtures
    
    # Retrieve the unit and check if it has the video
    unit = db.query(Unit).filter(Unit.id == test_unit.id).first()
    assert len(unit.videos) > 0
    assert any(video.title == "Test Video" for video in unit.videos)


def test_repr_method(db, test_course):
    """Test the __repr__ method."""
    unit = Unit(
        title="ReprTest",
        description="Testing the repr method",
        order=1,
        course_id=test_course.id
    )
    
    # Test the __repr__ method
    assert str(unit) == "<Unit ReprTest>" 