import pytest

def test_submit_form(client, test_widget):
    """Test submitting a form."""
    response = client.post(
        "/public/submissions/",
        json={
            "widget_id": test_widget.id,
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["widget_id"] == test_widget.id
    assert data["status"] == "new"
    assert data["ip_address"] == "127.0.0.1"
    assert "id" in data

def test_submit_form_inactive_widget(client, db_session, test_user):
    """Test submitting to inactive widget."""
    from app.models.widget import Widget
    
    inactive_widget = Widget(
        owner_id=test_user.id,
        title="Inactive Widget",
        widget_type="signup_form",
        fields=["name", "email"],
        button_text="Submit",
        is_active=False
    )
    db_session.add(inactive_widget)
    db_session.commit()
    
    response = client.post(
        "/public/submissions/",
        json={
            "widget_id": inactive_widget.id,
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
    )
    assert response.status_code == 404

def test_submit_form_invalid_data(client, test_widget):
    """Test submitting invalid form data."""
    response = client.post(
        "/public/submissions/",
        json={
            "widget_id": test_widget.id,
            "data": {}
        }
    )
    assert response.status_code == 400

def test_submit_form_spam_detection(client, test_widget):
    """Test spam detection."""
    response = client.post(
        "/public/submissions/",
        json={
            "widget_id": test_widget.id,
            "data": {
                "name": "Viagra Cheap Pills",
                "email": "spam@example.com",
                "message": "BUY CHEAP VIAGRA ONLINE!!!"
            }
        }
    )
    assert response.status_code == 400
    assert "Invalid form data" in response.json()["detail"]

def test_submit_form_honeypot(client, test_widget):
    """Test honeypot spam detection."""
    response = client.post(
        "/public/submissions/",
        json={
            "widget_id": test_widget.id,
            "data": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "honeypot": "filled"
        }
    )
    assert response.status_code == 400
    assert "Spam detected" in response.json()["detail"]

def test_get_submissions(client, auth_headers, test_submission):
    """Test getting submissions."""
    response = client.get(
        "/public/submissions/",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_get_submission_by_id(client, auth_headers, test_submission):
    """Test getting a specific submission."""
    response = client.get(
        f"/public/submissions/{test_submission.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_submission.id
    assert data["form_data"]["name"] == "John Doe"

def test_update_submission_status(client, auth_headers, test_submission):
    """Test updating submission status."""
    response = client.put(
        f"/public/submissions/{test_submission.id}",
        headers=auth_headers,
        json={"status": "read"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "read"

def test_submission_stats(client, auth_headers, test_submission):
    """Test getting submission stats."""
    response = client.get(
        "/public/submissions/stats/dashboard",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "new" in data
    assert "by_country" in data