import pytest

def test_dashboard_stats(client, auth_headers, test_submission):
    """Test dashboard stats endpoint."""
    response = client.get(
        "/api/dashboard/stats",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_submissions" in data
    assert "total_widgets" in data
    assert "conversion_rate" in data
    assert "spam_rate" in data
    assert data["total_submissions"] >= 1

def test_dashboard_summary(client, auth_headers, test_submission):
    """Test dashboard summary endpoint."""
    response = client.get(
        "/api/dashboard/summary",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "trends" in data
    assert "top_widgets" in data
    assert "geo_distribution" in data

def test_dashboard_trends(client, auth_headers, test_submission):
    """Test dashboard trends endpoint."""
    response = client.get(
        "/api/dashboard/trends?days=30",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_widget_performance(client, auth_headers, test_widget, test_submission):
    """Test widget performance endpoint."""
    response = client.get(
        "/api/dashboard/widgets/performance",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["widget_id"] == test_widget.id
    assert data[0]["total_submissions"] >= 1

def test_geo_distribution(client, auth_headers, test_submission):
    """Test geo distribution endpoint."""
    response = client.get(
        "/api/dashboard/geo",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # Should have at least one country
    assert len(data) >= 1
