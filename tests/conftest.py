import pytest
import requests
import os
import subprocess
import time
import signal
import sys
from typing import Generator

# Set test environment
os.environ['TESTING'] = 'True'

# Server process
server_process = None

@pytest.fixture(scope="session", autouse=True)
def start_server():
    """Start the FastAPI server for testing."""
    global server_process
    
    # Start the server in a subprocess
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(3)
    
    yield
    
    # Stop the server
    if server_process:
        server_process.terminate()
        server_process.wait()

@pytest.fixture(scope="function")
def client():
    """Create a test client using requests."""
    return requests.Session()

@pytest.fixture(scope="function")
def test_user(client):
    """Create test user and return credentials."""
    # Register user
    response = client.post(
        "http://localhost:8001/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "test123",
            "password_confirm": "test123",
            "full_name": "Test User"
        }
    )
    
    if response.status_code == 409:
        # User already exists, try to login
        pass
    
    return {"email": "test@example.com", "password": "test123"}

@pytest.fixture(scope="function")
def auth_token(client, test_user):
    """Get authentication token."""
    response = client.post(
        "http://localhost:8001/api/auth/login",
        json={
            "email": test_user["email"],
            "password": test_user["password"]
        }
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

@pytest.fixture(scope="function")
def auth_headers(auth_token):
    """Get authentication headers."""
    if auth_token:
        return {"Authorization": f"Bearer {auth_token}"}
    return {}

@pytest.fixture(scope="function")
def test_widget(client, auth_headers):
    """Create test widget."""
    if not auth_headers:
        return None
    
    response = client.post(
        "http://localhost:8001/api/widgets/",
        headers=auth_headers,
        json={
            "title": "Test Widget",
            "description": "Test Description",
            "widget_type": "signup_form",
            "fields": ["name", "email"],
            "button_text": "Submit",
            "is_active": True
        }
    )
    
    if response.status_code == 201:
        return response.json()
    return None

@pytest.fixture(scope="function")
def test_submission(client, test_widget):
    """Create test submission."""
    if not test_widget:
        return None
    
    response = client.post(
        "http://localhost:8001/public/submissions/",
        json={
            "widget_id": test_widget["id"],
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    )
    
    if response.status_code == 201:
        return response.json()
    return None