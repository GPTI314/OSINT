"""Credit Risk API Routes."""

from fastapi import APIRouter
from api.routes.credit_risk import consumer, business

router = APIRouter(prefix="/credit-risk", tags=["credit-risk"])

# Include sub-routers
router.include_router(consumer.router, prefix="/consumer", tags=["consumer-credit"])
router.include_router(business.router, prefix="/business", tags=["business-credit"])

__all__ = ["router"]
