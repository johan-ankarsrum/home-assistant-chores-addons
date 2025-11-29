"""
Home Assistant REST API client for sending notifications.
"""
import logging
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)


class HAClient:
    """Client for interacting with Home Assistant REST API."""

    def __init__(self, ha_url: str, ha_token: str):
        """
        Initialize Home Assistant client.

        Args:
            ha_url: Base URL of Home Assistant (e.g., http://192.168.1.100:8123)
            ha_token: Long-lived access token from Home Assistant
        """
        self.ha_url = ha_url.rstrip("/")
        self.ha_token = ha_token
        self.headers = {
            "Authorization": f"Bearer {ha_token}",
            "Content-Type": "application/json",
        }

    async def send_notification(
        self,
        notify_service: str,
        title: str,
        message: str,
        actions: Optional[list] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Send a notification via Home Assistant notify service.

        Args:
            notify_service: Service name (e.g., 'notify.mobile_app_johans_iphone')
            title: Notification title
            message: Notification body message
            actions: List of action dicts with 'action' and 'title' keys
            data: Additional notification data

        Returns:
            True if successful, False otherwise
        """
        if not notify_service.startswith("notify."):
            notify_service = f"notify.{notify_service}"

        payload = {
            "title": title,
            "message": message,
        }

        if actions:
            if data is None:
                data = {}
            data["actions"] = actions

        if data:
            payload["data"] = data

        try:
            async with httpx.AsyncClient() as client:
                # Call the notify service via Home Assistant API
                # The service name format is 'notify.service_name'
                url = f"{self.ha_url}/api/services/{notify_service.split('.')[0]}/{notify_service.split('.')[1]}"
                response = await client.post(url, json=payload, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                logger.info(f"Notification sent to {notify_service}: {title}")
                return True
        except Exception as e:
            logger.error(f"Failed to send notification to {notify_service}: {e}")
            return False

    async def check_connection(self) -> bool:
        """
        Check if connection to Home Assistant is working.

        Returns:
            True if connected, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.ha_url}/api/",
                    headers=self.headers,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info("Successfully connected to Home Assistant")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to Home Assistant at {self.ha_url}: {e}")
            return False
