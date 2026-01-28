from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import ValidationError

from app.routes.presentation.schemas import PresentationRequest, PresentationResponse
from mcp_server.workflow import main_workflow

presentation_router = APIRouter(
    prefix="/presentation",
    tags=["presentation"],
)


@presentation_router.post("/generate_ppt", status_code=202)
def generate_ppt(request: PresentationRequest, background_tasks: BackgroundTasks) -> PresentationResponse:
    """
    Generate a PowerPoint presentation based on the given topic and number of slides. The endpoint accepts a topic
    and triggers

    Args:
        request: PresentationRequest - The request containing the topic and number of slides.

    Returns:
        PresentationResponse - The response containing the message, status, and presentation ID.
    """
    try:
        background_tasks.add_task(main_workflow, topic=request.topic, slides=request.slides)
        return PresentationResponse(
            message="Presentation generation task created successfully! To retrieve the presentation, please use the pprt_id in the response.",
            status="Success",
            pprt_id="1234567890",
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: Invalid request parameters. Please check the request and try again. Error: {e.errors()}",
        )
    except Exception as e:
        return PresentationResponse(
            message=f"Error generating presentation: {e}",
            status="Error",
        )
