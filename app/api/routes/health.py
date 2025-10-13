"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Facebook Ads Integration API"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check for Kubernetes/Docker"""
    # In a real implementation, you would check:
    # - Database connectivity
    # - External service availability
    # - Cache connectivity
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            "database": "ok",
            "facebook_api": "ok",
            "cache": "ok"
        }
    }
