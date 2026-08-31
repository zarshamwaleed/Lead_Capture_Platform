from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Create rate limiter with custom key function
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["10/minute"],
    strategy="fixed-window",
    storage_uri="memory://",
)

# Custom handler for rate limit exceeded - fixed version
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests. Please try again later.",
        },
        headers={
            "Retry-After": "60",
            "X-RateLimit-Limit": "10",
            "X-RateLimit-Remaining": "0",
        }
    )

# Get rate limit status
async def get_rate_limit_status(request: Request) -> dict:
    return {
        "limit": "10/minute",
        "remaining": "Unknown",
        "reset": "Unknown"
    }
