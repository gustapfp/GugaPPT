from pydantic import BaseModel, Field
from typing import List


class SlidePlan(BaseModel):
    slide_number: int
    title: str = Field(description="The main title of the slide")
    search_queries: List[str] = Field(
        description="Specific search queries for the Researcher to find facts for this slide"
    )
    content_goal: str = Field(description="A brief instruction on what this slide should cover")


class PresentationPlan(BaseModel):
    topic: str
    slides: List[SlidePlan]
