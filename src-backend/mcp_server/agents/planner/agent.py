from openai import AsyncOpenAI

from core.logger_config import logger
from core.settings import settings
from mcp_server.agents.planner.prompts import SYSTEM_PROMPT, USER_PROMPT
from mcp_server.agents.planner.schemas import PresentationPayload, PresentationPlan


class PlannerAgent:
    """
    A planner agent that creates a presentation plan based on the topic and number of slides.
    """

    def __init__(self):
        self.model = "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.retry_count = 0

    async def create_presentation_plan(self, payload: PresentationPayload) -> PresentationPlan:
        """Creates a presentation plan based on the topic and number of slides.

        Args:
            payload (PresentationPayload): The payload containing the topic and number of slides.

        Raises:
            e: The error that occurred.

        Returns:
            PresentationPlan: The presentation plan.
        """
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": USER_PROMPT.format(
                            topic=payload.topic, num_slides=payload.num_slides
                        ),
                    },
                ],
                response_format=PresentationPlan,
            )
            plan = await self._validate_response(response.choices[0].message.parsed, payload)
            return plan
        except Exception as e:
            logger.error(
                f"ERROR_PLANNER_AGENT: Error creating presentation plan - for topic: {payload.topic} and number of slides: {payload.num_slides} - error: {e}"
            )
            raise e

    async def _validate_response(
        self, plan: PresentationPlan | None, payload: PresentationPayload
    ) -> PresentationPlan:
        """Validates the response from the agent with a retry mechanism which calls the create_presentation_plan method if the response is None.

        Args:
            plan (PresentationPlan | None): The presentation plan from the agent.
            payload (PresentationPayload): The payload containing the topic and number of slides.

        Raises:
            ValueError: If the response from the agent is None and the retry count is less than 3.
            ValueError: If the number of slides in the presentation plan does not match the number of slides requested.

        Returns:
            PresentationPlan: The presentation plan.
        """
        if plan is None:
            if self.retry_count < 3:
                self.retry_count += 1
                return await self.create_presentation_plan(payload)
            raise ValueError(f"No response from the agent even after {self.retry_count} retries")
        if len(plan.slides) != payload.num_slides:
            logger.warning(
                f"Number of slides in the presentation plan does not match the number of slides requested. Expected {payload.num_slides}, got {len(plan.slides)}"
            )
            raise ValueError(
                "Number of slides in the presentation plan does not match the number of slides requested"
            )
        return plan
