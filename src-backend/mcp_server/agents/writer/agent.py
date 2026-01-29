import json
from typing import List

from openai import AsyncOpenAI

from core.logger_config import logger
from core.settings import settings
from mcp_server.agents.writer.schemas import PresentationContent
from mcp_server.agents.writer.prompts import SYSTEM_PROMPT, USER_PROMPT
from mcp import ClientSession


class WriterAgent:
    """
    A writer agent that synthesizes the plan and research into a final slide deck structure.
    """

    def __init__(self):
        self.model = "gpt-4o"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0

    async def prepare_presentation(self, topic: str, plan_json: dict, research_data: List[dict]) -> PresentationContent:
        """
        Synthesizes the plan and research into a final slide deck structure.
        """
        logger.info(f"WRITER_AGENT: Drafting content for topic='{topic}'")

        # Convert inputs to strings for the prompt
        plan_str = json.dumps(plan_json, indent=2)
        research_str = json.dumps(research_data, indent=2)

        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": USER_PROMPT.format(topic=topic, plan_str=plan_str, research_str=research_str),
                    },
                ],
                response_format=PresentationContent,
            )

            content = completion.choices[0].message.parsed
            return await self._validate_response(content, topic, plan_json, research_data)

        except Exception as e:
            logger.error(f"ERROR_WRITER_AGENT: Error drafting presentation for topic='{topic}' - error: {e}")
            raise e

    async def write_presentation(
        self, content: PresentationContent, plan_json: dict, research_data: List[dict], session: ClientSession
    ):
        slides_payload = [{"title": s.title, "points": s.points} for s in content.slides]

        await session.call_tool(
            "create_presentation",
            arguments={"filename": content.filename_suggestion, "slides_content": json.dumps(slides_payload)},
        )

        return content

    async def _validate_response(
        self, content: PresentationContent | None, topic: str, plan_json: dict, research_data: List[dict]
    ) -> PresentationContent:
        """Validates the response from the agent with a retry mechanism.

        If the response is None, it retries up to 3 times before raising an error.
        """
        if content is None:
            if self.retry_count < 3:
                self.retry_count += 1
                logger.warning(
                    f"WRITER_AGENT: Empty response received. Retrying {self.retry_count}/3 for topic='{topic}'"
                )
                # Re-run the main method to regenerate the content
                return await self.prepare_presentation(topic, plan_json, research_data)
            raise ValueError(f"No response from WriterAgent even after {self.retry_count} retries for topic='{topic}'")

        return content


# --- 3. Example Integration (Workflow Logic) ---
# This shows how to connect the Writer output to the MCP Tool
if __name__ == "__main__":
    import asyncio

    # Mock Data for testing
    mock_plan = {"slides": [{"title": "Intro to AI", "goal": "Define AI"}]}
    mock_research = [{"topic": "Intro to AI", "data": "AI is the simulation of human intelligence..."}]

    async def test():
        agent = WriterAgent()
        content = await agent.prepare_presentation("AI Overview", mock_plan, mock_research)

        print(f"Suggested Filename: {content.filename_suggestion}")
        print(f"First Slide Points: {content.slides[0].points}")

        # In the real workflow, you would do this:
        # tool_args = {
        #     "filename": content.filename_suggestion,
        #     "slides_content": content.model_dump_json(include={'slides'})
        # }
        # await session.call_tool("create_presentation", arguments=tool_args)

    asyncio.run(test())
