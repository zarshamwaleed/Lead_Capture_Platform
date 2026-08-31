import pytest

def test_client_exists(client):
    """Test that client fixture works."""
    assert client is not None

def test_user_exists(test_user):
    """Test that test_user fixture works."""
    assert test_user is not None
    assert test_user.email == "test@example.com"

def test_widget_exists(test_widget):
    """Test that test_widget fixture works."""
    assert test_widget is not None
    assert test_widget.title == "Test Widget"

def test_auth_headers(auth_headers):
    """Test that auth_headers fixture works."""
    assert auth_headers is not None
    assert "Authorization" in auth_headers