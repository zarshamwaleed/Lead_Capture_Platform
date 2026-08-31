from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Determine if we're in test mode
IS_TESTING = os.environ.get('TESTING', 'False').lower() == 'true'

# Use test database if testing
if IS_TESTING:
    TEST_DATABASE_URL = "sqlite:///./test_lead_capture.db"
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=settings.DEBUG
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Import models to ensure they're registered with Base
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission

def get_db():
    """
    Dependency function that yields database sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Create all tables in the database.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def drop_tables():
    """
    Drop all tables in the database.
    """
    logger.info("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped successfully")

def setup_test_db():
    """
    Set up test database.
    """
    drop_tables()
    create_tables()
