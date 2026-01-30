import json

from mcp import ClientSession
from openai import AsyncOpenAI

from core.logger_config import logger
from core.settings import settings
from mcp_server.agents.writer.prompts import SYSTEM_PROMPT, USER_PROMPT
from mcp_server.agents.writer.schemas import PresentationContent


class WriterAgent:
    """
    A writer agent that synthesizes the plan and research into a final slide deck structure.
    """

    def __init__(self):
        self.model = "gpt-4o"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0

    async def prepare_presentation(
        self, topic: str, plan_json: dict, research_data: list[dict]
    ) -> PresentationContent:
        """
        Synthesizes the plan and research into a final slide deck structure.
        """
        logger.info(f"WRITER_AGENT: Drafting content for topic='{topic}'")

        plan_str = json.dumps(plan_json, indent=2)
        research_str = json.dumps(research_data, indent=2)

        try:
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": USER_PROMPT.format(
                            topic=topic, plan_str=plan_str, research_str=research_str
                        ),
                    },
                ],
                response_format=PresentationContent,
            )

            content = completion.choices[0].message.parsed
            return await self._validate_response(content, topic, plan_json, research_data)

        except Exception as e:
            logger.error(
                f"ERROR_WRITER_AGENT: Error drafting presentation for topic='{topic}' - error: {e}"
            )
            raise e

    async def write_presentation(
        self,
        content: PresentationContent,
        session: ClientSession,
        generated_assets: list[dict] | None = None,
    ):
        """
        Assembles the final PPT.
        generated_assets: List of dicts like [{'slide_number': 0, 'file_path': '...'}]
        """
        slides_payload = []

        for i, s in enumerate(content.slides):
            slide_data = {"title": s.title, "points": s.points}

            if generated_assets:
                asset = next((a for a in generated_assets if a["slide_number"] == i), None)
                if asset:
                    slide_data["image"] = asset["file_path"]

            slides_payload.append(slide_data)

        await session.call_tool(
            "create_presentation",
            arguments={
                "filename": content.filename_suggestion,
                "slides_content": json.dumps(slides_payload),
            },
        )

        return content

    async def _validate_response(self, content, topic, plan, research):
        if content is None:
            if self.retry_count < 3:
                self.retry_count += 1
                logger.warning(f"WRITER_AGENT: Retrying {self.retry_count}/3...")
                return await self.prepare_presentation(topic, plan, research)
            raise ValueError(f"No response after retries for topic='{topic}'")
        return content
