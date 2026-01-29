from mcp_server.agents.planner.schemas import PresentationPlan
from mcp_server.agents.planner.prompts import SYSTEM_PROMPT, USER_PROMPT
from openai import AsyncOpenAI
from core.settings import settings


class PlannerAgent:
    def __init__(self):
        self.name = "PlannerAgent"
        self.description = "A planner agent that creates a presentation plan"
        self.model = "gpt-4o-mini"
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    def create_presentation_plan(self, topic: str, num_slides: int) -> PresentationPlan:
        pass
