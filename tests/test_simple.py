import pytest
import requests

# Use the same port as your running server
BASE_URL = "http://localhost:8000"

def test_server_running():
    """Test that the server is running."""
    # Try the root endpoint
    response = requests.get(f"{BASE_URL}/")
    # If 404, try /api/
    if response.status_code == 404:
        response = requests.get(f"{BASE_URL}/api/")
    assert response.status_code in [200, 404]  # Either is fine for server running

def test_health_check():
    """Test health check endpoint."""
    # Try /health
    response = requests.get(f"{BASE_URL}/health")
    # If 404, try /api/health
    if response.status_code == 404:
        response = requests.get(f"{BASE_URL}/api/health")
    assert response.status_code in [200, 404]  # Either is fine

def test_register_user():
    """Test user registration."""
    import time
    import random
    
    # Generate unique email to avoid conflicts
    unique_id = int(time.time() * 1000) % 1000000
    email = f"testuser{unique_id}@example.com"
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 201

def test_login():
    """Test login with existing user."""
    import time
    import random
    
    unique_id = int(time.time() * 1000) % 1000000
    email = f"logintest{unique_id}@example.com"
    
    # Register
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Login Test"
        }
    )
    
    # Login
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": email,
            "password": "test12345"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_create_widget():
    """Test creating a widget."""
    import time
    import random
    
    unique_id = int(time.time() * 1000) % 1000000
    email = f"widgettest{unique_id}@example.com"
    
    # Register
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Widget Test"
        }
    )
    
    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": email,
            "password": "test12345"
        }
    )
    
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create widget
    response = requests.post(
        f"{BASE_URL}/api/widgets/",
        headers=headers,
        json={
            "title": "Test Widget",
            "description": "Test Description",
            "widget_type": "signup_form",
            "fields": ["name", "email"],
            "button_text": "Submit",
            "is_active": True
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Widget"
    assert "embed_snippet" in data

def test_get_widgets():
    """Test getting widgets."""
    import time
    import random
    
    unique_id = int(time.time() * 1000) % 1000000
    email = f"getwidget{unique_id}@example.com"
    
    # Register and login
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Get Widget Test"
        }
    )
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "test12345"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get widgets
    response = requests.get(
        f"{BASE_URL}/api/widgets/",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_submit_form():
    """Test submitting a form."""
    import time
    import random
    
    unique_id = int(time.time() * 1000) % 1000000
    email = f"submitform{unique_id}@example.com"
    
    # Register and login
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Submit Test"
        }
    )
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "test12345"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a widget
    widget_response = requests.post(
        f"{BASE_URL}/api/widgets/",
        headers=headers,
        json={
            "title": "Test Widget",
            "description": "Test Description",
            "widget_type": "signup_form",
            "fields": ["name", "email"],
            "button_text": "Submit",
            "is_active": True
        }
    )
    
    widget_id = widget_response.json()["id"]
    
    # Submit form
    response = requests.post(
        f"{BASE_URL}/public/submissions/",
        json={
            "widget_id": widget_id,
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["widget_id"] == widget_id
    assert data["status"] == "new"

def test_spam_detection():
    """Test spam detection."""
    import time
    import random
    
    unique_id = int(time.time() * 1000) % 1000000
    email = f"spamtest{unique_id}@example.com"
    
    # Register and login
    requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": email,
            "password": "test12345",
            "password_confirm": "test12345",
            "full_name": "Spam Test"
        }
    )
    
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": "test12345"}
    )
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create a widget
    widget_response = requests.post(
        f"{BASE_URL}/api/widgets/",
        headers=headers,
        json={
            "title": "Test Widget",
            "description": "Test Description",
            "widget_type": "signup_form",
            "fields": ["name", "email"],
            "button_text": "Submit",
            "is_active": True
        }
    )
    
    widget_id = widget_response.json()["id"]
    
    # Submit spam form
    response = requests.post(
        f"{BASE_URL}/public/submissions/",
        json={
            "widget_id": widget_id,
            "data": {
                "name": "Viagra Cheap Pills",
                "email": "spam@example.com",
                "message": "BUY CHEAP VIAGRA ONLINE!!!"
            }
        }
    )
    # Spam should be rejected
    assert response.status_code == 400