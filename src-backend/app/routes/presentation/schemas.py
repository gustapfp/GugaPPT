from typing import Literal
from pydantic import BaseModel


class PresentationRequest(BaseModel):
    topic: str
    slides: int


class PresentationResponse(BaseModel):
    message: str
    status: Literal["Success", "Error"]
    pprt_id: str


class PresentationDownloadRequest(BaseModel):
    pprt_id: str


class PresentationDownloadResponse(BaseModel):
    message: str
    status: Literal["Completed", "Pending", "Error"]
    file_url: str
