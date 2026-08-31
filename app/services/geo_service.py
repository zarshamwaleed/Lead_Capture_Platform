import httpx
import logging
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

class GeoService:
    # Primary provider: ip-api.com (free, no key, 45 req/min)
    PRIMARY_PROVIDER = "ip-api"
    PRIMARY_URL = "http://ip-api.com/json/{ip}?fields=status,message,country,city,regionName,lat,lon,isp,org,as,query"
    
    # Fallback provider: ipapi.co (free tier ~1000 lookups/day)
    FALLBACK_PROVIDER = "ipapi"
    FALLBACK_URL = "https://ipapi.co/{ip}/json/"
    
    # Cache for geolocation data (memory cache)
    _cache = {}
    _cache_ttl = 3600  # 1 hour cache
    
    @classmethod
    async def get_location(cls, ip: str) -> Tuple[Dict[str, Any], Optional[str]]:
        """
        Get geolocation data for an IP address with fallback.
        Returns: (location_data, provider_used)
        """
        # Check cache first
        cache_key = f"geo_{ip}"
        if cache_key in cls._cache:
            cached_data, cached_time = cls._cache[cache_key]
            if (datetime.utcnow() - cached_time).total_seconds() < cls._cache_ttl:
                logger.info(f"Geo data for {ip} returned from cache")
                return cached_data, "cache"
        
        # Try primary provider
        try:
            location_data, provider = await cls._try_provider(cls.PRIMARY_PROVIDER, cls.PRIMARY_URL, ip)
            if location_data:
                # Cache the result
                cls._cache[cache_key] = (location_data, datetime.utcnow())
                return location_data, provider
        except Exception as e:
            logger.warning(f"Primary geo provider failed for {ip}: {e}")
        
        # Try fallback provider
        try:
            location_data, provider = await cls._try_provider(cls.FALLBACK_PROVIDER, cls.FALLBACK_URL, ip)
            if location_data:
                # Cache the result
                cls._cache[cache_key] = (location_data, datetime.utcnow())
                return location_data, provider
        except Exception as e:
            logger.warning(f"Fallback geo provider failed for {ip}: {e}")
        
        # Both providers failed - return empty data
        logger.warning(f"All geo providers failed for IP: {ip}")
        return {}, None
    
    @classmethod
    async def _try_provider(cls, provider_name: str, url_template: str, ip: str) -> Tuple[Dict[str, Any], str]:
        """
        Try a specific geo provider.
        Returns: (location_data, provider_name)
        """
        try:
            url = url_template.format(ip=ip)
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                data = response.json()
                
                # Parse based on provider
                if provider_name == cls.PRIMARY_PROVIDER:
                    location_data = cls._parse_ip_api(data)
                elif provider_name == cls.FALLBACK_PROVIDER:
                    location_data = cls._parse_ipapi_co(data)
                else:
                    location_data = {}
                
                if location_data:
                    logger.info(f"Geo data fetched from {provider_name} for IP: {ip}")
                    return location_data, provider_name
                else:
                    logger.warning(f"No location data from {provider_name} for IP: {ip}")
                    return {}, provider_name
                    
        except httpx.TimeoutException:
            logger.warning(f"Timeout from {provider_name} for IP: {ip}")
            return {}, provider_name
        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error from {provider_name} for IP {ip}: {e.response.status_code}")
            return {}, provider_name
        except Exception as e:
            logger.error(f"Unexpected error from {provider_name} for IP {ip}: {e}")
            return {}, provider_name
    
    @classmethod
    def _parse_ip_api(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response from ip-api.com
        """
        if data.get('status') != 'success':
            return {}
        
        return {
            'country': data.get('country'),
            'city': data.get('city'),
            'region': data.get('regionName'),
            'latitude': data.get('lat'),
            'longitude': data.get('lon'),
            'isp': data.get('isp'),
            'org': data.get('org'),
            'as': data.get('as'),
            'ip': data.get('query'),
            'provider': 'ip-api'
        }
    
    @classmethod
    def _parse_ipapi_co(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse response from ipapi.co
        """
        if data.get('error'):
            return {}
        
        # ipapi.co returns empty strings for unknown fields
        return {
            'country': data.get('country_name') or data.get('country'),
            'city': data.get('city'),
            'region': data.get('region'),
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'isp': data.get('org'),
            'org': data.get('org'),
            'as': data.get('asn'),
            'ip': data.get('ip'),
            'provider': 'ipapi'
        }
    
    @classmethod
    def clear_cache(cls):
        """
        Clear the geolocation cache.
        """
        cls._cache.clear()
        logger.info("Geo cache cleared")
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get cache statistics.
        """
        return {
            'size': len(cls._cache),
            'ttl_seconds': cls._cache_ttl
        }
