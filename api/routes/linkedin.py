"""LinkedIn API Routes."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.connection import get_db
from linkedin.linkedin_extractor import LinkedInExtractor
from auth.dependencies import get_current_user
from database.models import User

router = APIRouter()


class ProfileExtractionRequest(BaseModel):
    profile_url: str = Field(..., description="LinkedIn profile URL")
    investigation_id: Optional[int] = None


class CompanyExtractionRequest(BaseModel):
    company_url: str = Field(..., description="LinkedIn company URL")
    investigation_id: Optional[int] = None


class EmployeeExtractionRequest(BaseModel):
    company_url: str = Field(..., description="LinkedIn company URL")
    filters: Optional[dict] = None
    investigation_id: Optional[int] = None


class VerticalCreationRequest(BaseModel):
    criteria: dict = Field(..., description="Vertical criteria")
    investigation_id: Optional[int] = None


class VerticalFilterRequest(BaseModel):
    filters: dict = Field(..., description="Filters to apply")


@router.post("/extract-profile")
async def extract_linkedin_profile(
    request: ProfileExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract LinkedIn profile data."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.extract_profile(
            request.profile_url,
            request.investigation_id
        )

        return {
            "success": True,
            "profile": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()


@router.post("/extract-company")
async def extract_linkedin_company(
    request: CompanyExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract LinkedIn company data."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.extract_company(
            request.company_url,
            request.investigation_id
        )

        return {
            "success": True,
            "company": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()


@router.post("/extract-employees")
async def extract_employees(
    request: EmployeeExtractionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Extract company employees."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.extract_employees(
            request.company_url,
            request.filters,
            request.investigation_id
        )

        return {
            "success": True,
            "employees": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()


@router.post("/create-vertical")
async def create_linkedin_vertical(
    request: VerticalCreationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create LinkedIn vertical."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.create_vertical(
            request.criteria,
            request.investigation_id
        )

        return {
            "success": True,
            "vertical": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()


@router.get("/verticals")
async def list_verticals(
    investigation_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all LinkedIn verticals."""
    from database.models import LinkedInVertical

    try:
        query = db.query(LinkedInVertical)

        if investigation_id:
            query = query.filter(LinkedInVertical.investigation_id == investigation_id)

        verticals = query.order_by(LinkedInVertical.created_at.desc()).all()

        return {
            "success": True,
            "total": len(verticals),
            "verticals": [
                {
                    "id": v.id,
                    "name": v.vertical_name,
                    "type": v.vertical_type,
                    "profile_count": len(v.profile_ids) if v.profile_ids else 0,
                    "company_count": len(v.company_ids) if v.company_ids else 0,
                    "created_at": v.created_at.isoformat()
                }
                for v in verticals
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verticals/{vertical_id}")
async def get_vertical(
    vertical_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vertical details."""
    from database.models import LinkedInVertical

    try:
        vertical = db.query(LinkedInVertical).filter(
            LinkedInVertical.id == vertical_id
        ).first()

        if not vertical:
            raise HTTPException(status_code=404, detail="Vertical not found")

        return {
            "success": True,
            "vertical": {
                "id": vertical.id,
                "name": vertical.vertical_name,
                "type": vertical.vertical_type,
                "criteria": vertical.criteria,
                "profile_ids": vertical.profile_ids,
                "company_ids": vertical.company_ids,
                "created_at": vertical.created_at.isoformat(),
                "updated_at": vertical.updated_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/verticals/{vertical_id}/filter")
async def filter_vertical(
    vertical_id: int,
    request: VerticalFilterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply filters to vertical."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.filter_vertical(
            vertical_id,
            request.filters
        )

        return {
            "success": True,
            "vertical": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()


@router.get("/verticals/{vertical_id}/export")
async def export_vertical(
    vertical_id: int,
    format: str = Query(default="json", regex="^(json|csv|excel)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export vertical data."""
    extractor = LinkedInExtractor(db)

    try:
        result = await extractor.export_vertical(vertical_id, format)

        return {
            "success": True,
            "export": result
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await extractor.close()
