from typing import List
from mcp import ClientSession
from mcp.types import TextContent
from openai import AsyncOpenAI
from core.settings import settings
from core.logger_config import logger
from mcp_server.agents.researcher.schemas import ResearchSummary, ResearcherPayload
from mcp_server.agents.researcher.prompts import SYSTEM_PROMPT, USER_PROMPT


class ResearcherAgent:
    """
    A researcher agent that researches the web for information based on the presentation plan.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0

    async def research_web(self, payload: ResearcherPayload, session: ClientSession) -> ResearchSummary:
        """Researches the web for information based on the presentation plan.

        Args:
            payload (ResearcherPayload): The payload containing the slide title, search queries, and session.

        Returns:
            str: The research results.
        """
        raw_context = []
        for query in payload.search_queries:
            results = await session.call_tool("search_web", arguments={"query": query})
            texts = [c.text for c in results.content if isinstance(c, TextContent)]
            logger.info(f"texts: {texts} results: {results}")
            if texts:
                raw_context.append("\n".join(texts))
        if not raw_context:
            return ResearchSummary(slide_topic=payload.slide_title, facts=[])

        return ResearchSummary(slide_topic=payload.slide_title, facts=raw_context)
