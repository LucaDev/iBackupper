"""
Main application module for the iBackupper API.
"""
import logging
import os
import atexit
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as api_router
from backend.core.config import API_PREFIX, API_TITLE, API_DESCRIPTION, API_VERSION
from backend.core.device_manager import DeviceManager

from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Register cleanup function to be called on application exit
atexit.register(DeviceManager.cleanup)

# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Application starting up, initializing resources")
    # Initialize the device manager by refreshing the device list
    DeviceManager.refresh_device_list()
    yield
    logging.info("Application shutting down, cleaning up resources")
    DeviceManager.cleanup()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:5173"],  # Include Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=API_PREFIX)

# Check if Svelte UI directory exists
ui_dir = Path(__file__).parent.parent / "frontend" / "app" / "build"
if ui_dir.exists():
    # Mount Svelte UI static files
    app.mount("/svelte", StaticFiles(directory=str(ui_dir), html=True), name="svelte_ui")

@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run application
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
