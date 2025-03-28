import pytest
from sqlalchemy.exc import IntegrityError
from app.models.learning import Course, Category


def test_create_course(db, test_category):
    """Test creating a course."""
    course = Course(
        title="New Test Course",
        description="This is a new test course",
        category_id=test_category.id
    )
    db.add(course)
    db.commit()
    
    retrieved_course = db.query(Course).filter(Course.title == "New Test Course").first()
    assert retrieved_course is not None
    assert retrieved_course.title == "New Test Course"
    assert retrieved_course.description == "This is a new test course"
    assert retrieved_course.category_id == test_category.id


def test_course_unique_title_per_category(db, test_category, test_course):
    """Test that course title must be unique per category."""
    with pytest.raises(IntegrityError):
        # Create a course with the same title in the same category
        course = Course(
            title="Test Course",  # Same as test_course fixture
            description="This is a duplicate course",
            category_id=test_category.id  # Same category as test_course
        )
        db.add(course)
        db.commit()
    
    # Rollback to clean up
    db.rollback()


def test_course_same_title_different_category(db, test_category, test_course):
    """Test that same course title is allowed in different categories."""
    # Create a new category
    new_category = Category(
        name="Another Category",
        description="This is another test category"
    )
    db.add(new_category)
    db.commit()
    
    # Create a course with the same title but in a different category
    course = Course(
        title="Test Course",  # Same as test_course fixture
        description="This is a course with the same title but in a different category",
        category_id=new_category.id
    )
    db.add(course)
    db.commit()
    
    # Verify that both courses exist
    courses = db.query(Course).filter(Course.title == "Test Course").all()
    assert len(courses) == 2
    assert {c.category_id for c in courses} == {test_category.id, new_category.id}


def test_update_course(db, test_course):
    """Test updating a course."""
    # Update the course
    test_course.title = "Updated Course"
    test_course.description = "This is an updated course"
    db.commit()
    
    # Verify changes
    updated_course = db.query(Course).filter(Course.id == test_course.id).first()
    assert updated_course.title == "Updated Course"
    assert updated_course.description == "This is an updated course"


def test_delete_course(db, test_category):
    """Test deleting a course."""
    # Create a course to delete
    course = Course(
        title="Course to Delete",
        description="This course will be deleted",
        category_id=test_category.id
    )
    db.add(course)
    db.commit()
    
    # Get the ID before deletion
    course_id = course.id
    
    # Delete the course
    db.delete(course)
    db.commit()
    
    # Verify deletion
    deleted_course = db.query(Course).filter(Course.id == course_id).first()
    assert deleted_course is None


def test_course_with_units(db, test_course, test_unit):
    """Test retrieving units associated with a course."""
    # test_unit is already associated with test_course by the fixtures
    
    # Retrieve the course and check if it has the unit
    course = db.query(Course).filter(Course.id == test_course.id).first()
    assert len(course.units) > 0
    assert any(unit.title == "Test Unit" for unit in course.units)


def test_repr_method(db, test_category):
    """Test the __repr__ method."""
    course = Course(
        title="ReprTest",
        description="Testing the repr method",
        category_id=test_category.id
    )
    
    # Test the __repr__ method
    assert str(course) == "<Course ReprTest>" 