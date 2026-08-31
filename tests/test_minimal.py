import pytest

def test_app_exists():
    """Test that the app exists."""
    from app.main import app
    assert app is not None

def test_database_connection():
    """Test database connection."""
    from app.core.database import engine
    assert engine is not None

def test_models_import():
    """Test that models import correctly."""
    from app.models.user import User
    from app.models.widget import Widget
    from app.models.submission import Submission
    assert User is not None
    assert Widget is not None
    assert Submission is not None