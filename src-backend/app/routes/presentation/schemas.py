from typing import Literal
from pydantic import BaseModel, Field


class PresentationRequest(BaseModel):
    topic: str
    slides: int = Field(default=5, gt=1, le=100)


class PresentationResponse(BaseModel):
    message: str
    status: Literal["Success", "Error"]
    pprt_id: str | None = None


class PresentationDownloadRequest(BaseModel):
    pprt_id: str


class PresentationDownloadResponse(BaseModel):
    message: str
    status: Literal["Completed", "Pending", "Error"]
    file_url: str
