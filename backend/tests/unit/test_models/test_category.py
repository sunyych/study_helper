import pytest
from sqlalchemy.exc import IntegrityError
from app.models.learning import Category


def test_create_category(db):
    """Test creating a category."""
    category = Category(
        name="Test Category",
        description="This is a test category"
    )
    db.add(category)
    db.commit()
    
    retrieved_category = db.query(Category).filter(Category.name == "Test Category").first()
    assert retrieved_category is not None
    assert retrieved_category.name == "Test Category"
    assert retrieved_category.description == "This is a test category"


def test_category_unique_name(db, test_category):
    """Test that category name must be unique."""
    with pytest.raises(IntegrityError):
        # Create a category with the same name as test_category
        category = Category(
            name="Test Category",  # Same as test_category fixture
            description="This is a duplicate category"
        )
        db.add(category)
        db.commit()
    
    # Rollback to clean up
    db.rollback()


def test_update_category(db, test_category):
    """Test updating a category."""
    # Update the category
    test_category.name = "Updated Category"
    test_category.description = "This is an updated category"
    db.commit()
    
    # Verify changes
    updated_category = db.query(Category).filter(Category.id == test_category.id).first()
    assert updated_category.name == "Updated Category"
    assert updated_category.description == "This is an updated category"


def test_delete_category(db):
    """Test deleting a category."""
    # Create a category to delete
    category = Category(
        name="Category to Delete",
        description="This category will be deleted"
    )
    db.add(category)
    db.commit()
    
    # Get the ID before deletion
    category_id = category.id
    
    # Delete the category
    db.delete(category)
    db.commit()
    
    # Verify deletion
    deleted_category = db.query(Category).filter(Category.id == category_id).first()
    assert deleted_category is None


def test_category_with_courses(db, test_category, test_course):
    """Test retrieving courses associated with a category."""
    # test_course is already associated with test_category by the fixtures
    
    # Retrieve the category and check if it has the course
    category = db.query(Category).filter(Category.id == test_category.id).first()
    assert len(category.courses) > 0
    assert any(course.title == "Test Course" for course in category.courses)


def test_repr_method(db):
    """Test the __repr__ method."""
    category = Category(
        name="ReprTest",
        description="Testing the repr method"
    )
    
    # Test the __repr__ method
    assert str(category) == "<Category ReprTest>" 