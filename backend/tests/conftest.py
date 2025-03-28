import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.database import get_db
from app.models.base import Base
from app.main import app
from app.models.learning import Category, Course, Unit, Video
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
import uuid
import random
import os

# Set testing environment
os.environ["TESTING"] = "1"


# Use in-memory SQLite database for testing
@pytest.fixture(scope="session")
def engine():
    """Create a SQLite in-memory database engine for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def db_session(engine):
    """Create a fresh SQLAlchemy session for each test session."""
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def db(db_session):
    """Return a database session for a test."""
    try:
        yield db_session
        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


@pytest.fixture
def client(db):
    """Return a test client with a database session override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Use the standard TestClient without a custom base URL
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


def get_random_suffix():
    """Generate a random suffix for test data to avoid unique constraint violations."""
    return f"_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_user(db):
    """Create a test user."""
    suffix = get_random_suffix()
    user = User(
        username=f"testuser{suffix}",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db):
    """Create a test admin user."""
    suffix = get_random_suffix()
    admin = User(
        username=f"testadmin{suffix}",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def admin_user(db):
    """Create an admin user for testing."""
    suffix = get_random_suffix()
    admin = User(
        username=f"adminuser{suffix}",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_category(db):
    """Create a test category."""
    suffix = get_random_suffix()
    category = Category(
        name=f"Test Category{suffix}",
        description="Test Category Description",
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def test_course(db, test_category):
    """Create a test course."""
    suffix = get_random_suffix()
    course = Course(
        title=f"Test Course{suffix}",
        description="Test Course Description",
        category_id=test_category.id,
        order=1
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@pytest.fixture
def test_unit(db, test_course):
    """Create a test unit."""
    suffix = get_random_suffix()
    unit = Unit(
        title=f"Test Unit{suffix}",
        description="Test Unit Description",
        course_id=test_course.id,
        order=1
    )
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


@pytest.fixture
def test_video(db, test_unit):
    """Create a test video."""
    suffix = get_random_suffix()
    video = Video(
        title=f"Test Video{suffix}",
        description="Test Video Description",
        url="https://example.com/test.mp4",
        unit_id=test_unit.id,
        order=1,
        video_metadata={
            "duration": 120,
            "format": "mp4",
            "resolution": "720p"
        }
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@pytest.fixture
def test_token(test_user):
    """Create a test token for a user."""
    return create_access_token({"sub": test_user.username})


@pytest.fixture
def test_admin_token(test_admin):
    """Create a test token for an admin user."""
    return create_access_token({"sub": test_admin.username})


@pytest.fixture
def admin_token_headers(test_admin_token):
    """Create headers with admin token."""
    return {"Authorization": f"Bearer {test_admin_token}"}


@pytest.fixture
def normal_token_headers(test_token):
    """Create headers with normal user token."""
    return {"Authorization": f"Bearer {test_token}"} 