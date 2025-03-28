from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

from app.core.config import settings

# Use SQLite for testing
if os.environ.get("TESTING") == "1":
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Convert the PostgresDsn to a string
    db_url = str(settings.DATABASE_URL)
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models to ensure they are registered with the Base metadata
from app.models.base import Base
from app.models.user import User
from app.models.learning import Category, Course, Unit, Video

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine) 