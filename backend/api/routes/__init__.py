"""API routes package."""
from .auth import router as auth_router
from .users import router as users_router
from .osint import router as osint_router
from .scraping import router as scraping_router
from .crawling import router as crawling_router
from .analysis import router as analysis_router
from .reports import router as reports_router
from .tasks import router as tasks_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "osint_router",
    "scraping_router",
    "crawling_router",
    "analysis_router",
    "reports_router",
    "tasks_router",
    "health_router"
]
