from typing import List
from mcp import ClientSession
from mcp.types import TextContent
from openai import AsyncOpenAI
from core.settings import settings
from core.logger_config import logger


class IlustratorAgent:
    """
    A ilustrator agent that generates visual assets for the presentation.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0
