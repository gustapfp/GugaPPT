from pydantic import BaseModel, Field


class ChartData(BaseModel):
    labels: list[str]
    values: list[float]
    unit: str = Field(
        description="The unit of measurement (e.g., 'Billions USD', 'Millions', '%', 'Units Sold')"
    )

    class Config:
        extra = "forbid"  # This ensures additionalProperties: false


class VisualRequest(BaseModel):
    type: str = Field(description="'chart' if you have numerical data, 'image' for concepts")
    prompt: str = Field(description="Title of the chart OR search query for the image")
    data_json: ChartData | None = Field(
        description="Chart data with labels and values, ONLY for charts"
    )


class SlideContent(BaseModel):
    title: str = Field(description="The final title for the slide")
    points: list[str] = Field(description="3-5 bullet points summarizing the research")
    speaker_notes: str | None = Field(description="Brief notes for the presenter to say")
    sources: list[str] | None = Field(description="List of source URLs referenced in this slide")
    visual_request: VisualRequest | None = None


class PresentationContent(BaseModel):
    filename_suggestion: str = Field(
        description="A clean, underscore-separated filename (e.g., 'ai_trends_2026')"
    )
    slides: list[SlideContent]
