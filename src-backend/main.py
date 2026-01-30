from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.routes.presentation.router import presentation_router

BASE_DIR = Path(__file__).resolve().parent

api = FastAPI(
    title="Presentation Generator API",
    description="API for generating PowerPoint presentations with a MCP server.",
    version="1.0.0",
)
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")
api.include_router(presentation_router)


@api.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main page"""
    return templates.TemplateResponse("home.html", {"request": request})
