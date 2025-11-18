"""Intelligence Gathering endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.dependencies import get_current_active_user, require_analyst
from app.models.user import User
from app.models.intelligence import (
    DomainIntelligence,
    IPIntelligence,
    EmailIntelligence,
    PhoneIntelligence,
    SocialIntelligence,
    ImageIntelligence
)
from app.schemas.intelligence import (
    DomainIntelligenceBase,
    DomainIntelligenceResponse,
    IPIntelligenceBase,
    IPIntelligenceResponse,
    EmailIntelligenceBase,
    EmailIntelligenceResponse,
    PhoneIntelligenceBase,
    PhoneIntelligenceResponse,
    SocialIntelligenceBase,
    SocialIntelligenceResponse,
    ImageIntelligenceBase,
    ImageIntelligenceResponse
)

router = APIRouter()


# Domain Intelligence
@router.post("/domain", response_model=DomainIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_domain_intelligence(
    domain_data: DomainIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on a domain"""
    # Check if already exists
    result = await db.execute(
        select(DomainIntelligence).where(DomainIntelligence.domain == domain_data.domain)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = DomainIntelligence(domain=domain_data.domain)

    # TODO: Trigger actual intelligence gathering tasks
    # - WHOIS lookup
    # - DNS records
    # - Subdomain enumeration
    # - SSL certificate info
    # - Reputation checks

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/domain/{domain}", response_model=DomainIntelligenceResponse)
async def get_domain_intelligence(
    domain: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get domain intelligence"""
    result = await db.execute(
        select(DomainIntelligence).where(DomainIntelligence.domain == domain)
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Domain intelligence not found",
        )

    return intel


# IP Intelligence
@router.post("/ip", response_model=IPIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_ip_intelligence(
    ip_data: IPIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on an IP address"""
    # Check if already exists
    result = await db.execute(
        select(IPIntelligence).where(IPIntelligence.ip_address == ip_data.ip_address)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = IPIntelligence(ip_address=ip_data.ip_address)

    # TODO: Trigger actual intelligence gathering tasks
    # - Geolocation
    # - ASN info
    # - Reverse DNS
    # - Port scanning (if authorized)
    # - Threat intelligence

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/ip/{ip_address}", response_model=IPIntelligenceResponse)
async def get_ip_intelligence(
    ip_address: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get IP intelligence"""
    result = await db.execute(
        select(IPIntelligence).where(IPIntelligence.ip_address == ip_address)
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP intelligence not found",
        )

    return intel


# Email Intelligence
@router.post("/email", response_model=EmailIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_email_intelligence(
    email_data: EmailIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on an email address"""
    # Check if already exists
    result = await db.execute(
        select(EmailIntelligence).where(EmailIntelligence.email == email_data.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = EmailIntelligence(email=email_data.email)

    # TODO: Trigger actual intelligence gathering tasks
    # - Email validation
    # - MX records
    # - Breach database checks
    # - Associated accounts
    # - Social profiles

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/email/{email}", response_model=EmailIntelligenceResponse)
async def get_email_intelligence(
    email: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email intelligence"""
    result = await db.execute(
        select(EmailIntelligence).where(EmailIntelligence.email == email)
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email intelligence not found",
        )

    return intel


# Phone Intelligence
@router.post("/phone", response_model=PhoneIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_phone_intelligence(
    phone_data: PhoneIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on a phone number"""
    # Check if already exists
    result = await db.execute(
        select(PhoneIntelligence).where(PhoneIntelligence.phone_number == phone_data.phone_number)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = PhoneIntelligence(phone_number=phone_data.phone_number)

    # TODO: Trigger actual intelligence gathering tasks
    # - Phone validation
    # - Carrier lookup
    # - Country/region info
    # - Associated accounts

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/phone/{phone_number}", response_model=PhoneIntelligenceResponse)
async def get_phone_intelligence(
    phone_number: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get phone intelligence"""
    result = await db.execute(
        select(PhoneIntelligence).where(PhoneIntelligence.phone_number == phone_number)
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone intelligence not found",
        )

    return intel


# Social Media Intelligence
@router.post("/social", response_model=SocialIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_social_intelligence(
    social_data: SocialIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on a social media profile"""
    # Check if already exists
    result = await db.execute(
        select(SocialIntelligence).where(
            (SocialIntelligence.platform == social_data.platform) &
            (SocialIntelligence.username == social_data.username)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = SocialIntelligence(**social_data.model_dump())

    # TODO: Trigger actual intelligence gathering tasks
    # - Profile scraping
    # - Posts collection
    # - Connections analysis
    # - Activity patterns

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/social/{platform}/{username}", response_model=SocialIntelligenceResponse)
async def get_social_intelligence(
    platform: str,
    username: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get social media intelligence"""
    result = await db.execute(
        select(SocialIntelligence).where(
            (SocialIntelligence.platform == platform) &
            (SocialIntelligence.username == username)
        )
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Social intelligence not found",
        )

    return intel


# Image Intelligence
@router.post("/image", response_model=ImageIntelligenceResponse, status_code=status.HTTP_201_CREATED)
async def gather_image_intelligence(
    image_data: ImageIntelligenceBase,
    current_user: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db)
):
    """Gather intelligence on an image"""
    # Check if already exists
    result = await db.execute(
        select(ImageIntelligence).where(ImageIntelligence.image_hash == image_data.image_hash)
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    # Create new intelligence record
    new_intel = ImageIntelligence(**image_data.model_dump())

    # TODO: Trigger actual intelligence gathering tasks
    # - EXIF data extraction
    # - Reverse image search
    # - Object detection
    # - Text extraction (OCR)
    # - Face detection

    db.add(new_intel)
    await db.commit()
    await db.refresh(new_intel)

    return new_intel


@router.get("/image/{image_hash}", response_model=ImageIntelligenceResponse)
async def get_image_intelligence(
    image_hash: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get image intelligence"""
    result = await db.execute(
        select(ImageIntelligence).where(ImageIntelligence.image_hash == image_hash)
    )
    intel = result.scalar_one_or_none()

    if not intel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image intelligence not found",
        )

    return intel
