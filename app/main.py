"""
Facebook Ads Manager Integration API
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from app.api.routes import campaigns, advertisers, health
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Facebook Ads Integration API")
    yield
    logger.info("Shutting down Facebook Ads Integration API")


# Create FastAPI application
app = FastAPI(
    title="Facebook Ads Manager Integration API",
    description="RESTful API for managing Facebook advertising campaigns with automatic synchronization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["Campaigns"])
app.include_router(advertisers.router, prefix="/api/v1/advertisers", tags=["Advertisers"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Facebook Ads Manager Integration API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "ui_demo": "/static/index.html"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
