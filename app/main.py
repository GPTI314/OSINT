"""
Main FastAPI application with comprehensive security features
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from app.config import settings
from app.database.base import engine, Base
from app.middleware import (
    AuditMiddleware,
    audit_logger,
    RateLimitMiddleware,
    rate_limiter,
    SecurityHeadersMiddleware,
)
from app.api.routes import auth
from app.auth.rbac import initialize_rbac
from app.database import async_session


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting OSINT Platform...")

    # Create logs directory
    Path("logs").mkdir(exist_ok=True)

    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    # Initialize RBAC
    async with async_session() as db:
        await initialize_rbac(db)
    logger.info("RBAC initialized")

    # Initialize rate limiter
    await rate_limiter.init_redis()
    logger.info("Rate limiter initialized")

    logger.info("OSINT Platform started successfully")

    yield

    # Shutdown
    logger.info("Shutting down OSINT Platform...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Secure Open-Source Intelligence Platform with comprehensive security features",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)

# Audit logging middleware
app.add_middleware(AuditMiddleware, logger=audit_logger)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error" if not settings.DEBUG else str(exc)
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "OSINT Platform API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix=settings.API_PREFIX)


# API information endpoints
@app.get(f"{settings.API_PREFIX}/info/security", tags=["Information"])
async def security_info():
    """Get security features information"""
    return {
        "authentication": {
            "jwt_tokens": True,
            "oauth2_providers": ["google", "github"],
            "api_keys": True,
            "session_management": True,
            "password_hashing": "Argon2/bcrypt",
            "two_factor_auth": settings.ENABLE_2FA,
        },
        "authorization": {
            "rbac": True,
            "role_based_access": True,
            "permission_based_access": True,
        },
        "data_security": {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "pii_protection": settings.ENABLE_PII_ENCRYPTION,
            "data_masking": settings.ENABLE_PII_MASKING,
        },
        "compliance": {
            "gdpr": settings.GDPR_ENABLED,
            "ccpa": settings.CCPA_ENABLED,
            "audit_logging": True,
            "data_retention_policies": True,
        },
        "ethical_features": {
            "robots_txt_compliance": settings.RESPECT_ROBOTS_TXT,
            "rate_limiting": True,
            "crawl_delay": settings.DEFAULT_CRAWL_DELAY,
        },
        "security_headers": {
            "hsts": settings.ENABLE_HSTS,
            "csp": settings.ENABLE_CSP,
            "x_content_type_options": True,
            "x_frame_options": True,
        }
    }


@app.get(f"{settings.API_PREFIX}/info/compliance", tags=["Information"])
async def compliance_info():
    """Get compliance information"""
    from app.utils.compliance import compliance_manager

    return {
        "privacy_policy": compliance_manager.get_privacy_policy(),
        "terms_of_service": compliance_manager.get_terms_of_service(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
