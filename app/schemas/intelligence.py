"""Intelligence schemas"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class DomainIntelligenceBase(BaseModel):
    """Base domain intelligence schema"""
    domain: str


class DomainIntelligenceResponse(DomainIntelligenceBase):
    """Schema for domain intelligence response"""
    id: int
    whois_data: Dict[str, Any]
    dns_records: Dict[str, Any]
    subdomains: List[str]
    ssl_certificate: Dict[str, Any]
    ip_addresses: List[str]
    nameservers: List[str]
    mail_servers: List[str]
    reputation_score: Optional[float] = None
    risk_indicators: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class IPIntelligenceBase(BaseModel):
    """Base IP intelligence schema"""
    ip_address: str


class IPIntelligenceResponse(IPIntelligenceBase):
    """Schema for IP intelligence response"""
    id: int
    geolocation: Dict[str, Any]
    asn_info: Dict[str, Any]
    reverse_dns: Optional[str] = None
    open_ports: List[int]
    services: List[Dict[str, Any]]
    vulnerabilities: List[Dict[str, Any]]
    reputation_score: Optional[float] = None
    is_proxy: bool
    is_tor: bool
    is_vpn: bool
    threat_intel: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class EmailIntelligenceBase(BaseModel):
    """Base email intelligence schema"""
    email: str


class EmailIntelligenceResponse(EmailIntelligenceBase):
    """Schema for email intelligence response"""
    id: int
    is_valid: bool
    is_disposable: bool
    is_free_provider: bool
    domain: Optional[str] = None
    mx_records: List[str]
    breach_data: List[Dict[str, Any]]
    associated_accounts: List[str]
    social_profiles: List[Dict[str, Any]]
    reputation_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class PhoneIntelligenceBase(BaseModel):
    """Base phone intelligence schema"""
    phone_number: str


class PhoneIntelligenceResponse(PhoneIntelligenceBase):
    """Schema for phone intelligence response"""
    id: int
    country_code: Optional[str] = None
    country: Optional[str] = None
    carrier: Optional[str] = None
    line_type: Optional[str] = None
    is_valid: bool
    is_voip: bool
    associated_accounts: List[str]
    social_profiles: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class SocialIntelligenceBase(BaseModel):
    """Base social intelligence schema"""
    platform: str
    username: str
    profile_url: str


class SocialIntelligenceResponse(SocialIntelligenceBase):
    """Schema for social intelligence response"""
    id: int
    profile_data: Dict[str, Any]
    posts: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]
    follower_count: int
    following_count: int
    post_count: int
    account_created_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    is_verified: bool
    is_private: bool
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True


class ImageIntelligenceBase(BaseModel):
    """Base image intelligence schema"""
    image_hash: str
    image_url: Optional[str] = None


class ImageIntelligenceResponse(ImageIntelligenceBase):
    """Schema for image intelligence response"""
    id: int
    local_path: Optional[str] = None
    exif_data: Dict[str, Any]
    reverse_search_results: List[Dict[str, Any]]
    similar_images: List[str]
    detected_objects: List[Dict[str, Any]]
    detected_text: Optional[str] = None
    detected_faces: List[Dict[str, Any]]
    gps_coordinates: Dict[str, Any]
    camera_info: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]

    class Config:
        from_attributes = True
