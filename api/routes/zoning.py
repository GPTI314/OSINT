"""Austrian Zoning API Routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from scrapers.austrian_zoning.zoning_scraper import AustrianZoningScraper
from auth.dependencies import get_current_user
from database.models import User

router = APIRouter()


class ZoningSearchRequest(BaseModel):
    street_name: str = Field(..., description="Street name")
    house_number: str = Field(..., description="House number")
    city: Optional[str] = None
    investigation_id: Optional[int] = None


@router.post("/search")
async def search_zoning_plan(
    request: ZoningSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search Austrian zoning plan by address."""
    scraper = AustrianZoningScraper(db)

    try:
        result = await scraper.search_by_address(
            request.street_name,
            request.house_number,
            request.city,
            request.investigation_id
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


@router.get("/searches")
async def list_zoning_searches(
    investigation_id: Optional[int] = Query(None),
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all zoning searches."""
    scraper = AustrianZoningScraper(db)

    try:
        searches = await scraper.get_search_history(investigation_id, limit)

        return {
            "success": True,
            "total": len(searches),
            "searches": searches
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()


@router.get("/searches/{search_id}")
async def get_zoning_search(
    search_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get zoning search details."""
    scraper = AustrianZoningScraper(db)

    try:
        result = await scraper.get_search_details(search_id)

        return {
            "success": True,
            "search": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await scraper.close()
