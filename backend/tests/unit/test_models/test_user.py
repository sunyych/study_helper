import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User


def test_create_user(db):
    """Test creating a user."""
    user = User(
        username="testcreate",
        hashed_password="hashedpassword",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    
    retrieved_user = db.query(User).filter(User.username == "testcreate").first()
    assert retrieved_user is not None
    assert retrieved_user.username == "testcreate"
    assert retrieved_user.hashed_password == "hashedpassword"
    assert retrieved_user.is_active is True
    assert retrieved_user.is_admin is False


def test_user_unique_username(db, test_user):
    """Test that username must be unique."""
    with pytest.raises(IntegrityError):
        # Create a user with the same username as test_user
        user = User(
            username="testuser",  # Same as test_user fixture
            hashed_password="hashedpassword",
            is_active=True,
            is_admin=False
        )
        db.add(user)
        db.commit()
    
    # Rollback to clean up
    db.rollback()


def test_update_user(db, test_user):
    """Test updating a user."""
    # Update the user
    test_user.username = "updatedusername"
    test_user.is_admin = True
    db.commit()
    
    # Verify changes
    updated_user = db.query(User).filter(User.id == test_user.id).first()
    assert updated_user.username == "updatedusername"
    assert updated_user.is_admin is True


def test_delete_user(db):
    """Test deleting a user."""
    # Create a user to delete
    user = User(
        username="todelete",
        hashed_password="hashedpassword",
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    
    # Get the ID before deletion
    user_id = user.id
    
    # Delete the user
    db.delete(user)
    db.commit()
    
    # Verify deletion
    deleted_user = db.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_repr_method(db):
    """Test the __repr__ method."""
    user = User(
        username="reprtest",
        hashed_password="hashedpassword",
        is_active=True,
        is_admin=False
    )
    
    # Test the __repr__ method
    assert str(user) == "<User reprtest>" 