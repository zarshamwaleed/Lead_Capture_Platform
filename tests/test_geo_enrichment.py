import pytest
from unittest.mock import patch, AsyncMock
from app.services.geo_service import GeoService

@pytest.mark.asyncio
async def test_geo_service_primary_provider():
    """Test primary geo provider."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "status": "success",
            "country": "United States",
            "city": "New York",
            "regionName": "New York",
            "lat": 40.7128,
            "lon": -74.0060,
            "isp": "Test ISP",
            "org": "Test Org",
            "as": "AS1234",
            "query": "8.8.8.8"
        })
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        location_data, provider = await GeoService.get_location("8.8.8.8")
        
        assert location_data is not None
        assert location_data.get('country') == "United States"
        assert location_data.get('city') == "New York"
        assert provider == "ip-api"

@pytest.mark.asyncio
async def test_geo_service_fallback_provider():
    """Test fallback geo provider."""
    with patch('httpx.AsyncClient.get') as mock_get:
        # First call fails for primary
        mock_response1 = AsyncMock()
        mock_response1.json = AsyncMock(return_value={"status": "fail"})
        mock_response1.raise_for_status = AsyncMock(side_effect=Exception("Provider failed"))
        
        # Second call succeeds for fallback
        mock_response2 = AsyncMock()
        mock_response2.json = AsyncMock(return_value={
            "country_name": "United Kingdom",
            "city": "London",
            "region": "London",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "org": "Test Org",
            "ip": "8.8.8.8"
        })
        mock_response2.raise_for_status = AsyncMock()
        
        mock_get.side_effect = [mock_response1, mock_response2]
        
        location_data, provider = await GeoService.get_location("8.8.8.8")
        
        assert location_data is not None
        assert location_data.get('country') == "United Kingdom"
        assert location_data.get('city') == "London"
        assert provider == "ipapi"

@pytest.mark.asyncio
async def test_geo_service_cache():
    """Test geo service caching."""
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            "status": "success",
            "country": "Canada",
            "city": "Toronto",
            "regionName": "Ontario",
            "query": "1.1.1.1"
        })
        mock_response.raise_for_status = AsyncMock()
        mock_get.return_value = mock_response
        
        # First call - should hit provider
        location_data1, provider1 = await GeoService.get_location("1.1.1.1")
        assert provider1 == "ip-api"
        assert location_data1.get('country') == "Canada"
        
        # Second call - should hit cache
        location_data2, provider2 = await GeoService.get_location("1.1.1.1")
        assert provider2 == "cache"
        assert location_data2.get('country') == "Canada"
        
        # Clear cache
        GeoService.clear_cache()
        
        # Third call - should hit provider again
        location_data3, provider3 = await GeoService.get_location("1.1.1.1")
        assert provider3 == "ip-api"