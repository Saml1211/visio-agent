from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from nicegui import ui
import uvicorn
from pathlib import Path
import logging
from typing import Optional
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules using absolute imports
from visio_agent.config.settings import Settings
from visio_agent.services.gui_service import GUIService
from visio_agent.models.shared_state import SharedState

# Initialize settings
settings = Settings()

# Create FastAPI app
app = FastAPI(
    title="Visio Agent",
    description="AI-powered system for automating AV system diagrams",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize shared state
shared_state = SharedState()

# Initialize GUI service
gui_service = GUIService(shared_state)

# Mount static files
static_path = Path(__file__).parent / "frontend" / "dist"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Configure NiceGUI
@ui.page('/')
async def index():
    """Main page of the application."""
    await gui_service.render_main_page()

@ui.page('/tools/{tool_name}')
async def tool_page(tool_name: str):
    """Dynamic tool pages."""
    await gui_service.render_tool_page(tool_name)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.VERSION}

# Initialize NiceGUI with FastAPI
ui.run_with(app, storage_secret=settings.JWT_SECRET)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
        log_level="info"
    ) 