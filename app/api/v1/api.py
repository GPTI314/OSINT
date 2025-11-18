"""API v1 router aggregation"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    api_keys,
    investigations,
    targets,
    scraping,
    crawling,
    intelligence,
    findings,
    reports,
    webhooks,
)

api_router = APIRouter()

# Authentication & Users
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])

# Core Resources
api_router.include_router(investigations.router, prefix="/investigations", tags=["Investigations"])
api_router.include_router(targets.router, prefix="/targets", tags=["Targets"])
api_router.include_router(scraping.router, prefix="/scraping-jobs", tags=["Scraping Jobs"])
api_router.include_router(crawling.router, prefix="/crawling-sessions", tags=["Crawling Sessions"])

# Intelligence Gathering
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])

# Findings & Reports
api_router.include_router(findings.router, prefix="/findings", tags=["Findings"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

# Webhooks
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
