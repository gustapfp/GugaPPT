import os

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import ValidationError

from app.routes.presentation.schemas import (
    PresentationDownloadResponse,
    PresentationRequest,
    PresentationResponse,
)
from app.routes.presentation.utils import generate_pprt_id
from core.consts import FILE_PATH
from mcp_server.workflow import run_ppt_workflow

presentation_router = APIRouter(
    prefix="/presentation",
    tags=["presentation"],
)


@presentation_router.post("/generate_ppt", status_code=202)
async def generate_ppt(
    request: PresentationRequest, background_tasks: BackgroundTasks
) -> PresentationResponse:
    """
    Generate a PowerPoint presentation based on the given topic and number of slides. The endpoint accepts a topic
    and triggers

    Args:
        request: PresentationRequest - The request containing the topic and number of slides.

    Returns:
        PresentationResponse - The response containing the message, status, and presentation ID.
    """
    pprt_id = generate_pprt_id(request.topic)
    try:
        background_tasks.add_task(
            run_ppt_workflow, topic=request.topic, num_slides=request.slides, filename=pprt_id
        )
        return PresentationResponse(
            message="Presentation generation task created successfully! To retrieve the presentation, please use the pprt_id in the response.",
            status="Success",
            pprt_id=pprt_id,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: Invalid request parameters. Please check the request and try again. Error: {e.errors()}",
        ) from e
    except Exception as e:
        return PresentationResponse(
            message=f"Error generating presentation: {e}",
            status="Error",
        )


@presentation_router.get("/download/{pprt_id}", response_model=None)
async def download_ppt(pprt_id: str) -> FileResponse | PresentationDownloadResponse:
    """Download the PowerPoint presentation based on the given presentation ID.

    Args:
        pprt_id (str): The presentation ID.

    Returns:
        FileResponse | PresentationDownloadResponse: The file response or the presentation response with the status "Pending" if the presentation is not found.
    """
    if os.path.exists(f"{FILE_PATH}/{pprt_id}.pptx"):
        return FileResponse(path=f"{FILE_PATH}/{pprt_id}.pptx")
    else:
        return PresentationDownloadResponse(
            message="Presentation not found. Please check the presentation ID and try again in a few minutes.",
            status="Pending",
        )
