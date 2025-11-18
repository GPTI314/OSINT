"""FastAPI application main entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from logging_config import setup_logging
from database.connection import close_connections

# Import routers
from .routes import (
    investigations,
    targets,
    scraping,
    crawling,
    intelligence,
    findings,
    reports,
    users,
    auth as auth_routes,
    seo_sem,
    linkedin,
    lists,
    zoning,
    health as health_routes,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    yield
    # Shutdown
    await close_connections()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="OSINT Intelligence Platform - Comprehensive OSINT tool repository",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
    openapi_url="/api/openapi.json" if settings.debug else None,
    lifespan=lifespan,
)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(
    auth_routes.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["Authentication"]
)

app.include_router(
    users.router,
    prefix=f"{settings.api_prefix}/users",
    tags=["Users"]
)

app.include_router(
    investigations.router,
    prefix=f"{settings.api_prefix}/investigations",
    tags=["Investigations"]
)

app.include_router(
    targets.router,
    prefix=f"{settings.api_prefix}/targets",
    tags=["Targets"]
)

app.include_router(
    scraping.router,
    prefix=f"{settings.api_prefix}/scraping",
    tags=["Scraping"]
)

app.include_router(
    crawling.router,
    prefix=f"{settings.api_prefix}/crawling",
    tags=["Crawling"]
)

app.include_router(
    intelligence.router,
    prefix=f"{settings.api_prefix}/intelligence",
    tags=["Intelligence"]
)

app.include_router(
    findings.router,
    prefix=f"{settings.api_prefix}/findings",
    tags=["Findings"]
)

app.include_router(
    reports.router,
    prefix=f"{settings.api_prefix}/reports",
    tags=["Reports"]
)

app.include_router(
    seo_sem.router,
    prefix=f"{settings.api_prefix}/seo-sem",
    tags=["SEO/SEM"]
)

app.include_router(
    linkedin.router,
    prefix=f"{settings.api_prefix}/linkedin",
    tags=["LinkedIn"]
)

app.include_router(
    lists.router,
    prefix=f"{settings.api_prefix}/lists",
    tags=["Lists"]
)

app.include_router(
    zoning.router,
    prefix=f"{settings.api_prefix}/zoning",
    tags=["Zoning"]
)

app.include_router(
    health_routes.router,
    prefix=f"{settings.api_prefix}/health",
    tags=["Health & Sanity"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint (basic, no auth required)."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


@app.get(f"{settings.api_prefix}/status")
async def api_status():
    """API status endpoint."""
    return {
        "api": "operational",
        "version": settings.app_version,
        "environment": settings.environment,
    }
