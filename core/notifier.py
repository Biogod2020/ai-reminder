import os
import httpx
from typing import Optional

class Notifier:
    """Handles cross-platform push notifications."""

    def __init__(self, bark_key: Optional[str] = None):
        """Initializes the Notifier.

        Args:
            bark_key: The Bark API key. If not provided, it will be read from the
                BARK_KEY environment variable.
        """
        self.bark_key = bark_key or os.getenv('BARK_KEY')

    async def send_bark(self, title: str, body: str, group: str = "NSA") -> bool:
        """Sends a notification via the Bark iOS app.

        Args:
            title: The title of the notification.
            body: The content of the notification.
            group: Optional grouping tag for the Bark app.

        Returns:
            True if the notification was sent successfully, False otherwise.
        """
        if not self.bark_key:
            return False
            
        url = f"https://api.day.app/{self.bark_key}/{title}/{body}"
        params = {"group": group}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params)
                return response.status_code == 200
            except Exception:
                return False
