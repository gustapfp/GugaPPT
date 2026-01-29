from typing import List, Optional
from pydantic import BaseModel, Field


class SlideContent(BaseModel):
    title: str = Field(description="The final title for the slide")
    points: List[str] = Field(description="3-5 bullet points summarizing the research")
    speaker_notes: Optional[str] = Field(description="Brief notes for the presenter to say")


class PresentationContent(BaseModel):
    filename_suggestion: str = Field(description="A clean, underscore-separated filename (e.g., 'ai_trends_2026')")
    slides: List[SlideContent]
