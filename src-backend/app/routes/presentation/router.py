import json
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
from core.logger_config import logger
from mcp_server.mcp_server import search_web
from mcp_server.workflow import main_workflow

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
    try:
        background_tasks.add_task(main_workflow, topic=request.topic, slides=request.slides)
        return PresentationResponse(
            message="Presentation generation task created successfully! To retrieve the presentation, please use the pprt_id in the response.",
            status="Success",
            pprt_id=generate_pprt_id(request.topic),
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


@presentation_router.get("/test")
async def test() -> None:
    query = "effect of quantum computing on encryption standards"

    print(f"🔎 Searching Live: '{query}'...")
    print("   (This involves fetching URL metadata, so it might take 5-10 seconds)...")

    result = search_web(query)
    data = json.loads(result)
    logger.info(f"Data: {data}")
    logger.info(f"Result: {result}")
    if not data:
        logger.error("❌ No Tier S/A results found (Filter might be too strict!)")
        return

    logger.info(f"\n✅ PASSED. Returning {len(data)} High-Quality Sources:\n")

    for i, item in enumerate(data, 1):
        v = item["validation"]
        logger.info(
            f"{i}. [{v['tier']}] Score: {v['score']} - {v['details'].get('author', 'No Author')}"
        )
        logger.info(f"   Url: {item['url']}")
        logger.info(f"   Title/Snippet: {item['content'][:60]}...")
        logger.info(f"   Content: {item['content']}")
        logger.info("-" * 40)
