from datetime import datetime
from fastapi import APIRouter

health_router = APIRouter(prefix="/health", tags=["Health"])


@health_router.get("")
async def healthcheck():
    """Basic healthcheck endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }
