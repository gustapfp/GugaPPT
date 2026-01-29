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

    async def summarize_facts(self, raw_context: List[str], slide_title: str) -> ResearchSummary:
        """Summarizes the facts from the raw context.

        Args:
            raw_context (List[str]): The raw context from the web search.
            slide_title (str): The title of the slide being researched.

        Returns:
            ResearchSummary: The summarized facts.
        """
        try:
            joined_context = "\n\n".join(raw_context)
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": USER_PROMPT.format(slide_title=slide_title, joined_context=joined_context),
                    },
                ],
                response_format=ResearchSummary,
            )

            summary = completion.choices[0].message.parsed
            return await self._validate_response(summary, slide_title, raw_context)

        except Exception as e:
            logger.error(f"ERROR_RESEARCHER_AGENT: Error summarizing facts for slide: {slide_title} - error: {e}")
            raise e

    async def _validate_response(
        self, summary: ResearchSummary | None, slide_title: str, raw_context: List[str]
    ) -> ResearchSummary:
        """Validates the response from the agent with a retry mechanism which calls the summarize_facts method if the response is None.

        Args:
            summary (ResearchSummary | None): The research summary from the agent.
            slide_title (str): The title of the slide being researched.
            raw_context (List[str]): The raw context from the web search.

        Raises:
            ValueError: If the response from the agent is None even after 3 retries.

        Returns:
            ResearchSummary: The validated research summary.
        """
        if summary is None:
            if self.retry_count < 3:
                self.retry_count += 1
                return await self.summarize_facts(raw_context, slide_title)
            raise ValueError(f"No response from the agent even after {self.retry_count} retries")
        return summary
