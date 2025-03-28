import logging
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.models.learning import Category

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    # Create initial admin user
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if not user:
        user = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_superuser=True,
        )
        db.add(user)
        logger.info("Created initial admin user")
    
    # Create initial categories
    categories = ["Chinese", "Math", "English"]
    for cat_name in categories:
        category = db.query(Category).filter(Category.name == cat_name).first()
        if not category:
            category = Category(
                name=cat_name,
                description=f"Learning resources for {cat_name}",
            )
            db.add(category)
            logger.info(f"Created category: {cat_name}")
    
    db.commit()
    logger.info("Initial database setup completed")


def init_test_users(db: Session) -> None:
    """Initialize test admin and regular user if they don't exist."""
    
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin:
        admin = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        logger.info("Created test admin user")
    
    # Check if regular user exists
    user = db.query(User).filter(User.email == "user@example.com").first()
    if not user:
        user = User(
            email="user@example.com",
            full_name="Test User",
            hashed_password=get_password_hash("user123"),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        logger.info("Created test regular user")
    
    db.commit()
    logger.info("Test users initialization completed") 