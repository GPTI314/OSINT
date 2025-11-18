"""
Health check endpoints.
"""
from fastapi import APIRouter, status
from datetime import datetime
from typing import Dict, Any

from core.database import (
    postgres_engine,
    mongo_client,
    elasticsearch_client,
    redis_client
)
from config.settings import settings

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Returns the health status of the application and all dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "services": {}
    }

    # Check PostgreSQL
    try:
        if postgres_engine:
            async with postgres_engine.connect() as conn:
                await conn.execute("SELECT 1")
            health_status["services"]["postgres"] = "healthy"
        else:
            health_status["services"]["postgres"] = "not_initialized"
    except Exception as e:
        health_status["services"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check MongoDB
    try:
        if mongo_client:
            await mongo_client.admin.command('ping')
            health_status["services"]["mongodb"] = "healthy"
        else:
            health_status["services"]["mongodb"] = "not_initialized"
    except Exception as e:
        health_status["services"]["mongodb"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Elasticsearch
    try:
        if elasticsearch_client:
            await elasticsearch_client.ping()
            health_status["services"]["elasticsearch"] = "healthy"
        else:
            health_status["services"]["elasticsearch"] = "not_initialized"
    except Exception as e:
        health_status["services"]["elasticsearch"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_initialized"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe for Kubernetes.

    Returns whether the application is ready to accept traffic.
    """
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe for Kubernetes.

    Returns whether the application is alive.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
