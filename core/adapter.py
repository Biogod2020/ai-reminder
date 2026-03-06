import os
from typing import Optional, List, Any
from google import genai

class GeminiAdapter:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.base_url = base_url
        
        if not self.api_key:
            raise ValueError('GEMINI_API_KEY must be provided or set in environment')

        http_options = {}
        if self.base_url:
            http_options['base_url'] = self.base_url

        self.client = genai.Client(
            api_key=self.api_key,
            http_options=http_options if http_options else None
        )
        self.model_id = 'gemini-1.5-flash-latest'

    async def generate_content(self, prompt: str, images: Optional[List[Any]] = None) -> str:
        """Generates content asynchronously, supporting text and images."""
        content = [prompt]
        if images:
            content.extend(images)
        
        # Use the asynchronous client method
        response = await self.client.aio.models.generate_content(
            model=self.model_id,
            contents=content
        )
        return response.text
