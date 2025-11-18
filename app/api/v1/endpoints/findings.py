"""Finding endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst, get_pagination_params
from app.models.user import User
from app.models.finding import Finding
from app.models.investigation import Investigation
from app.schemas.finding import FindingCreate, FindingUpdate, FindingResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.post("/", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(
    finding_data: FindingCreate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Create a new finding"""
    # Verify investigation exists
    result = await db.execute(
        select(Investigation).where(Investigation.id == finding_data.investigation_id)
    )
    investigation = result.scalar_one_or_none()

    if not investigation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investigation not found",
        )

    new_finding = Finding(
        **finding_data.model_dump(),
        created_by=current_user.id
    )

    db.add(new_finding)
    await db.commit()
    await db.refresh(new_finding)

    return new_finding


@router.get("/", response_model=PaginatedResponse[FindingResponse])
async def list_findings(
    investigation_id: Optional[int] = Query(None),
    severity_filter: Optional[str] = Query(None, alias="severity"),
    status_filter: Optional[str] = Query(None, alias="status"),
    pagination: dict = Depends(get_pagination_params),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List findings with filtering"""
    query = select(Finding)

    # Apply filters
    if investigation_id:
        query = query.where(Finding.investigation_id == investigation_id)
    if severity_filter:
        query = query.where(Finding.severity == severity_filter)
    if status_filter:
        query = query.where(Finding.status == status_filter)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # Get paginated results
    query = query.offset(pagination["offset"]).limit(pagination["page_size"])
    result = await db.execute(query)
    findings = result.scalars().all()

    return {
        "items": findings,
        "total": total,
        "page": pagination["page"],
        "page_size": pagination["page_size"],
        "total_pages": (total + pagination["page_size"] - 1) // pagination["page_size"]
    }


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get finding by ID"""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    return finding


@router.patch("/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: int,
    finding_data: FindingUpdate,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Update finding"""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    # Update finding
    for field, value in finding_data.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)

    await db.commit()
    await db.refresh(finding)

    return finding


@router.delete("/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(
    finding_id: int,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Delete finding"""
    result = await db.execute(select(Finding).where(Finding.id == finding_id))
    finding = result.scalar_one_or_none()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )

    await db.delete(finding)
    await db.commit()

    return None
