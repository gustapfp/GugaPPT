import json

from mcp import ClientSession
from openai import AsyncOpenAI

from core.logger_config import logger
from core.settings import settings
from mcp_server.agents.illustrator.schemas import IllustrationResult, VisualAsset


class IllustratorAgent:
    """
    A ilustrator agent that generates visual assets for the presentation.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0

    async def create_visuals(
        self, visual_requests: list[dict], session: ClientSession
    ) -> IllustrationResult:
        """Takes a list of requests (e.g., [{'slide': 1, 'type': 'chart', 'data': {...}}])
        and calls the appropriate MCP tools to generate them.

        Args:
            visual_requests (List[dict]): _description_
            session (ClientSession): _description_

        Returns:
            IllustrationResult: _description_
        """
        logger.info(f"IlustratorAgent: Creating visuals for {len(visual_requests)} requests")
        generated_assets = []

        for req in visual_requests:
            slide_num = req.get("slide_number", 0)
            req_type = req.get("type", "")
            prompt = req.get("prompt", "")
            data = req.get("data_json", {})

            try:
                if req_type == "chart" and data:
                    logger.info(f"   > Generating chart for Slide {slide_num}...")
                    data_json_str = json.dumps(data) if isinstance(data, dict) else data
                    result = await session.call_tool(
                        "generate_chart",
                        arguments={
                            "data_json": data_json_str,
                            "chart_type": "bar",
                            "title": prompt,
                        },
                    )
                    path = result.content[0].text
                    generated_assets.append(
                        VisualAsset(
                            slide_number=slide_num,
                            asset_type="chart",
                            description=prompt,
                            file_path=path,
                        )
                    )

            except Exception as e:
                logger.error(f"Failed to create visual for Slide {slide_num}: {e}")

        return IllustrationResult(assets=generated_assets)
