"""Intelligence gathering routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

from auth.authenticator import Authenticator
from database.connection import get_db
from database.models import User
from fastapi.security import OAuth2PasswordBearer
from osint.domain_intelligence import DomainIntelligence
from osint.ip_intelligence import IPIntelligence
from osint.email_intelligence import EmailIntelligence


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
authenticator = Authenticator()

# Initialize intelligence modules
domain_intel = DomainIntelligence()
ip_intel = IPIntelligence()
email_intel = EmailIntelligence()


class DomainIntelligenceRequest(BaseModel):
    """Domain intelligence request schema."""
    domain: str
    include_subdomains: bool = True
    include_technology: bool = True


class IPIntelligenceRequest(BaseModel):
    """IP intelligence request schema."""
    ip_address: str


class EmailIntelligenceRequest(BaseModel):
    """Email intelligence request schema."""
    email: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db),
) -> User:
    """Dependency to get current user."""
    user = await authenticator.get_current_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    return user


@router.post("/domain", response_model=Dict[str, Any])
async def gather_domain_intelligence(
    request: DomainIntelligenceRequest,
    current_user: User = Depends(get_current_user),
):
    """Gather intelligence on a domain."""
    try:
        intelligence = await domain_intel.gather_intelligence(
            domain=request.domain,
            include_subdomains=request.include_subdomains,
            include_technology=request.include_technology,
        )
        return intelligence
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error gathering domain intelligence: {str(e)}",
        )


@router.post("/ip", response_model=Dict[str, Any])
async def gather_ip_intelligence(
    request: IPIntelligenceRequest,
    current_user: User = Depends(get_current_user),
):
    """Gather intelligence on an IP address."""
    try:
        intelligence = await ip_intel.gather_intelligence(
            ip_address=request.ip_address,
        )
        return intelligence
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error gathering IP intelligence: {str(e)}",
        )


@router.post("/email", response_model=Dict[str, Any])
async def gather_email_intelligence(
    request: EmailIntelligenceRequest,
    current_user: User = Depends(get_current_user),
):
    """Gather intelligence on an email address."""
    try:
        intelligence = await email_intel.gather_intelligence(
            email=request.email,
        )
        return intelligence
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error gathering email intelligence: {str(e)}",
        )
