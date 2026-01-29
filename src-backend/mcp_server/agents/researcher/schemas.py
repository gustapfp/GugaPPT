from typing import List
from mcp import ClientSession
from pydantic import BaseModel, Field


class Fact(BaseModel):
    content: str = Field(description="A specific, verified fact found in the search")
    source_url: str = Field(description=" The URL where this fact was found")


# TODO: Add the raw_facts
class ResearchSummary(BaseModel):
    slide_topic: str
    facts: List[Fact] = Field(description="A curated list of facts relevant to this slide")


class ResearcherPayload(BaseModel):
    slide_title: str
    search_queries: List[str]
