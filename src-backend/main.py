from fastapi import FastAPI

from app.routes.presentation.router import presentation_router

api = FastAPI(
    title="Presentation Generator API",
    description="API for generating PowerPoint presentations with a MCP server.",
    version="1.0.0",
)
api.include_router(presentation_router)
