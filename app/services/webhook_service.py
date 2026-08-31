import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class WebhookService:
    @staticmethod
    async def send_webhook(
        webhook_url: str,
        payload: Dict[str, Any],
        secret: Optional[str] = None
    ) -> bool:
        """
        Send data to a webhook URL.
        Returns: True if sent successfully, False otherwise.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "LeadCapturePlatform/1.0"
            }
            
            # Add webhook secret if provided
            if secret:
                headers["X-Webhook-Secret"] = secret
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                logger.info(f"Webhook sent successfully to {webhook_url}")
                return True
                
        except httpx.TimeoutException:
            logger.error(f"Webhook timeout: {webhook_url}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Webhook HTTP error {webhook_url}: {e.response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Webhook error {webhook_url}: {e}")
            return False
