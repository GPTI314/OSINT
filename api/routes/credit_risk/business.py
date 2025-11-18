"""Business Credit Risk API Endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from database.connection import get_db
from database.models import (
    BusinessApplication, BusinessRiskScore,
    User, ApplicationStatus
)
from auth.authenticator import Authenticator
from fastapi.security import OAuth2PasswordBearer
from credit_risk.business_scorer import BusinessCreditScorer
from credit_risk.reporting.report_generator import CreditRiskReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()


class BusinessApplicationCreate(BaseModel):
    """Business credit application creation schema."""
    investigation_id: Optional[int] = None
    company_name: str = Field(..., min_length=1, max_length=255)
    legal_name: Optional[str] = Field(None, max_length=255)
    registration_number: Optional[str] = Field(None, max_length=100)
    tax_id: Optional[str] = Field(None, max_length=100)
    domain: Optional[str] = Field(None, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    business_type: Optional[str] = Field(None, max_length=50)
    founded_date: Optional[datetime] = None
    number_of_employees: Optional[int] = Field(None, gt=0)
    annual_revenue: Optional[float] = Field(None, gt=0)
    requested_amount: Optional[float] = Field(None, gt=0)
    loan_purpose: Optional[str] = None


class BusinessApplicationResponse(BaseModel):
    """Business credit application response schema."""
    id: int
    company_name: str
    legal_name: Optional[str]
    registration_number: Optional[str]
    domain: Optional[str]
    industry: Optional[str]
    requested_amount: Optional[float]
    application_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BusinessCreditScoreResponse(BaseModel):
    """Business credit score response schema."""
    id: int
    application_id: int
    overall_score: Optional[int]
    risk_tier: Optional[str]
    risk_level: Optional[str]
    probability_of_default: Optional[float]
    recommended_interest_rate: Optional[float]
    recommended_term_months: Optional[int]
    approval_recommendation: Optional[str]
    calculated_at: datetime

    class Config:
        from_attributes = True


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Dependency to get current user."""
    user = await authenticator.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.post(
    "/applications",
    response_model=BusinessApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_business_application(
    application_data: BusinessApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new business credit application."""
    try:
        application = BusinessApplication(
            investigation_id=application_data.investigation_id,
            company_name=application_data.company_name,
            legal_name=application_data.legal_name,
            registration_number=application_data.registration_number,
            tax_id=application_data.tax_id,
            domain=application_data.domain,
            industry=application_data.industry,
            business_type=application_data.business_type,
            founded_date=application_data.founded_date,
            number_of_employees=application_data.number_of_employees,
            annual_revenue=application_data.annual_revenue,
            requested_amount=application_data.requested_amount,
            loan_purpose=application_data.loan_purpose,
            application_status=ApplicationStatus.PENDING
        )

        db.add(application)
        await db.commit()
        await db.refresh(application)

        logger.info(f"Created business application {application.id} by user {current_user.id}")

        return application

    except Exception as e:
        logger.error(f"Error creating business application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating application: {str(e)}"
        )


@router.get(
    "/applications",
    response_model=List[BusinessApplicationResponse]
)
async def list_business_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    industry: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List business credit applications."""
    try:
        query = select(BusinessApplication)

        if status_filter:
            query = query.where(BusinessApplication.application_status == ApplicationStatus(status_filter))

        if industry:
            query = query.where(BusinessApplication.industry == industry)

        query = query.offset(skip).limit(limit).order_by(BusinessApplication.created_at.desc())

        result = await db.execute(query)
        applications = result.scalars().all()

        return applications

    except Exception as e:
        logger.error(f"Error listing business applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing applications: {str(e)}"
        )


@router.get(
    "/applications/{application_id}",
    response_model=BusinessApplicationResponse
)
async def get_business_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get business credit application by ID."""
    try:
        result = await db.execute(
            select(BusinessApplication).where(BusinessApplication.id == application_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        return application

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting application: {str(e)}"
        )


@router.post(
    "/applications/{application_id}/assess",
    status_code=status.HTTP_202_ACCEPTED
)
async def assess_business_credit(
    application_id: int,
    collect_osint: bool = Query(True, description="Collect fresh OSINT data"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assess business credit risk."""
    try:
        # Verify application exists
        result = await db.execute(
            select(BusinessApplication).where(BusinessApplication.id == application_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        # Initialize scorer and perform assessment
        scorer = BusinessCreditScorer(db)
        assessment_result = await scorer.assess_business(application_id, collect_osint)

        logger.info(f"Business assessment completed for application {application_id}")

        return {
            'message': 'Assessment completed successfully',
            'assessment': assessment_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing business credit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing credit: {str(e)}"
        )


@router.get(
    "/applications/{application_id}/score",
    response_model=BusinessCreditScoreResponse
)
async def get_business_score(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get business risk score."""
    try:
        result = await db.execute(
            select(BusinessRiskScore).where(
                BusinessRiskScore.application_id == application_id
            ).order_by(BusinessRiskScore.calculated_at.desc())
        )
        risk_score = result.scalar_one_or_none()

        if not risk_score:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Risk score not found. Please run assessment first."
            )

        return risk_score

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting score: {str(e)}"
        )


@router.post(
    "/applications/{application_id}/collect-osint",
    status_code=status.HTTP_202_ACCEPTED
)
async def collect_business_osint(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Collect OSINT data for business application."""
    try:
        from credit_risk.osint_collector import CreditRiskOSINTCollector

        collector = CreditRiskOSINTCollector(db)
        result = await collector.collect_business_osint(application_id)

        logger.info(f"OSINT collection completed for business application {application_id}")

        return {
            'message': 'OSINT data collection completed',
            'result': result
        }

    except Exception as e:
        logger.error(f"Error collecting business OSINT data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error collecting OSINT data: {str(e)}"
        )


@router.get(
    "/applications/{application_id}/report"
)
async def get_business_report(
    application_id: int,
    format: str = Query('json', regex='^(json|html|pdf)$'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get business credit risk report."""
    try:
        report_generator = CreditRiskReportGenerator(db)
        report = await report_generator.generate_business_report(application_id, format)

        logger.info(f"Generated business report for application {application_id} in {format} format")

        if format == 'json':
            return report
        elif format == 'html':
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=report)
        elif format == 'pdf':
            from fastapi.responses import Response
            return Response(content=report, media_type='application/pdf')

    except Exception as e:
        logger.error(f"Error generating business report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )
