import pytest

def test_create_widget(client, auth_headers):
    """Test creating a widget."""
    response = client.post(
        "/api/widgets/",
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
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Widget"
    assert "embed_snippet" in data
    assert "id" in data

def test_get_widgets(client, auth_headers, test_widget):
    """Test getting all widgets."""
    response = client.get(
        "/api/widgets/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Widget"

def test_get_widget_by_id(client, auth_headers, test_widget):
    """Test getting a specific widget."""
    response = client.get(
        f"/api/widgets/{test_widget.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_widget.id
    assert data["title"] == "Test Widget"

def test_update_widget(client, auth_headers, test_widget):
    """Test updating a widget."""
    response = client.put(
        f"/api/widgets/{test_widget.id}",
        headers=auth_headers,
        json={
            "title": "Updated Widget",
            "description": "Updated Description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Widget"
    assert data["description"] == "Updated Description"

def test_delete_widget(client, auth_headers, test_widget):
    """Test deleting a widget."""
    response = client.delete(
        f"/api/widgets/{test_widget.id}",
        headers=auth_headers
    )
    assert response.status_code == 204

def test_get_widget_public_config(client, test_widget):
    """Test getting widget config without auth."""
    response = client.get(
        f"/api/widgets/public/{test_widget.id}/config"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_widget.id
    assert data["title"] == "Test Widget"

def test_get_widget_other_user(client, db_session, auth_headers):
    """Test accessing another user's widget."""
    from app.models.user import User
    from app.models.widget import Widget
    
    other_user = User(
        email="other@example.com",
        password="other123",
        full_name="Other User"
    )
    db_session.add(other_user)
    db_session.commit()
    
    other_widget = Widget(
        owner_id=other_user.id,
        title="Other Widget",
        widget_type="signup_form",
        fields=["name", "email"],
        button_text="Submit",
        is_active=True
    )
    db_session.add(other_widget)
    db_session.commit()
    
    response = client.get(
        f"/api/widgets/{other_widget.id}",
        headers=auth_headers
    )
    assert response.status_code == 404