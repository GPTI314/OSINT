"""Consumer Credit Risk API Endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from database.connection import get_db
from database.models import (
    ConsumerApplication, ConsumerRiskScore,
    User, ApplicationStatus
)
from auth.authenticator import Authenticator
from fastapi.security import OAuth2PasswordBearer
from credit_risk.consumer_scorer import ConsumerCreditScorer
from credit_risk.reporting.report_generator import CreditRiskReportGenerator

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()


class ConsumerApplicationCreate(BaseModel):
    """Consumer credit application creation schema."""
    investigation_id: Optional[int] = None
    applicant_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    requested_amount: Optional[float] = Field(None, gt=0)
    loan_purpose: Optional[str] = Field(None, max_length=100)
    employment_status: Optional[str] = Field(None, max_length=50)
    monthly_income: Optional[float] = Field(None, gt=0)


class ConsumerApplicationResponse(BaseModel):
    """Consumer credit application response schema."""
    id: int
    applicant_name: str
    email: Optional[str]
    phone: Optional[str]
    requested_amount: Optional[float]
    application_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreditScoreResponse(BaseModel):
    """Credit score response schema."""
    id: int
    application_id: int
    overall_score: Optional[int]
    risk_tier: Optional[str]
    risk_level: Optional[str]
    probability_of_default: Optional[float]
    recommended_interest_rate: Optional[float]
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
    response_model=ConsumerApplicationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_consumer_application(
    application_data: ConsumerApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new consumer credit application."""
    try:
        application = ConsumerApplication(
            investigation_id=application_data.investigation_id,
            applicant_name=application_data.applicant_name,
            email=application_data.email,
            phone=application_data.phone,
            date_of_birth=application_data.date_of_birth,
            address=application_data.address,
            requested_amount=application_data.requested_amount,
            loan_purpose=application_data.loan_purpose,
            employment_status=application_data.employment_status,
            monthly_income=application_data.monthly_income,
            application_status=ApplicationStatus.PENDING
        )

        db.add(application)
        await db.commit()
        await db.refresh(application)

        logger.info(f"Created consumer application {application.id} by user {current_user.id}")

        return application

    except Exception as e:
        logger.error(f"Error creating consumer application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating application: {str(e)}"
        )


@router.get(
    "/applications",
    response_model=List[ConsumerApplicationResponse]
)
async def list_consumer_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List consumer credit applications."""
    try:
        query = select(ConsumerApplication)

        if status_filter:
            query = query.where(ConsumerApplication.application_status == ApplicationStatus(status_filter))

        query = query.offset(skip).limit(limit).order_by(ConsumerApplication.created_at.desc())

        result = await db.execute(query)
        applications = result.scalars().all()

        return applications

    except Exception as e:
        logger.error(f"Error listing consumer applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing applications: {str(e)}"
        )


@router.get(
    "/applications/{application_id}",
    response_model=ConsumerApplicationResponse
)
async def get_consumer_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consumer credit application by ID."""
    try:
        result = await db.execute(
            select(ConsumerApplication).where(ConsumerApplication.id == application_id)
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
        logger.error(f"Error getting consumer application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting application: {str(e)}"
        )


@router.post(
    "/applications/{application_id}/assess",
    status_code=status.HTTP_202_ACCEPTED
)
async def assess_consumer_credit(
    application_id: int,
    collect_osint: bool = Query(True, description="Collect fresh OSINT data"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Assess consumer credit risk."""
    try:
        # Verify application exists
        result = await db.execute(
            select(ConsumerApplication).where(ConsumerApplication.id == application_id)
        )
        application = result.scalar_one_or_none()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )

        # Initialize scorer and perform assessment
        scorer = ConsumerCreditScorer(db)
        assessment_result = await scorer.assess_consumer(application_id, collect_osint)

        logger.info(f"Consumer assessment completed for application {application_id}")

        return {
            'message': 'Assessment completed successfully',
            'assessment': assessment_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assessing consumer credit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assessing credit: {str(e)}"
        )


@router.get(
    "/applications/{application_id}/score",
    response_model=CreditScoreResponse
)
async def get_consumer_score(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consumer risk score."""
    try:
        result = await db.execute(
            select(ConsumerRiskScore).where(
                ConsumerRiskScore.application_id == application_id
            ).order_by(ConsumerRiskScore.calculated_at.desc())
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
        logger.error(f"Error getting consumer score: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting score: {str(e)}"
        )


@router.post(
    "/applications/{application_id}/collect-osint",
    status_code=status.HTTP_202_ACCEPTED
)
async def collect_consumer_osint(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Collect OSINT data for consumer application."""
    try:
        from credit_risk.osint_collector import CreditRiskOSINTCollector

        collector = CreditRiskOSINTCollector(db)
        result = await collector.collect_consumer_osint(application_id)

        logger.info(f"OSINT collection completed for consumer application {application_id}")

        return {
            'message': 'OSINT data collection completed',
            'result': result
        }

    except Exception as e:
        logger.error(f"Error collecting consumer OSINT data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error collecting OSINT data: {str(e)}"
        )


@router.get(
    "/applications/{application_id}/report"
)
async def get_consumer_report(
    application_id: int,
    format: str = Query('json', regex='^(json|html|pdf)$'),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get consumer credit risk report."""
    try:
        report_generator = CreditRiskReportGenerator(db)
        report = await report_generator.generate_consumer_report(application_id, format)

        logger.info(f"Generated consumer report for application {application_id} in {format} format")

        if format == 'json':
            return report
        elif format == 'html':
            from fastapi.responses import HTMLResponse
            return HTMLResponse(content=report)
        elif format == 'pdf':
            from fastapi.responses import Response
            return Response(content=report, media_type='application/pdf')

    except Exception as e:
        logger.error(f"Error generating consumer report: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )
