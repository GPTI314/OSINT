"""Intelligence gathering models"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float

from app.core.database import Base


class DomainIntelligence(Base):
    """Domain Intelligence model"""
    __tablename__ = "domain_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)

    whois_data = Column(JSON, default=dict, nullable=False)
    dns_records = Column(JSON, default=dict, nullable=False)
    subdomains = Column(JSON, default=list, nullable=False)
    ssl_certificate = Column(JSON, default=dict, nullable=False)

    ip_addresses = Column(JSON, default=list, nullable=False)
    nameservers = Column(JSON, default=list, nullable=False)
    mail_servers = Column(JSON, default=list, nullable=False)

    reputation_score = Column(Float, nullable=True)
    risk_indicators = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<DomainIntelligence {self.domain}>"


class IPIntelligence(Base):
    """IP Address Intelligence model"""
    __tablename__ = "ip_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String, unique=True, index=True, nullable=False)

    geolocation = Column(JSON, default=dict, nullable=False)
    asn_info = Column(JSON, default=dict, nullable=False)
    reverse_dns = Column(String, nullable=True)

    open_ports = Column(JSON, default=list, nullable=False)
    services = Column(JSON, default=list, nullable=False)
    vulnerabilities = Column(JSON, default=list, nullable=False)

    reputation_score = Column(Float, nullable=True)
    is_proxy = Column(Integer, default=0, nullable=False)  # Boolean as int
    is_tor = Column(Integer, default=0, nullable=False)  # Boolean as int
    is_vpn = Column(Integer, default=0, nullable=False)  # Boolean as int

    threat_intel = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<IPIntelligence {self.ip_address}>"


class EmailIntelligence(Base):
    """Email Intelligence model"""
    __tablename__ = "email_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    is_valid = Column(Integer, default=1, nullable=False)  # Boolean as int
    is_disposable = Column(Integer, default=0, nullable=False)  # Boolean as int
    is_free_provider = Column(Integer, default=0, nullable=False)  # Boolean as int

    domain = Column(String, nullable=True)
    mx_records = Column(JSON, default=list, nullable=False)

    breach_data = Column(JSON, default=list, nullable=False)
    associated_accounts = Column(JSON, default=list, nullable=False)
    social_profiles = Column(JSON, default=list, nullable=False)

    reputation_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<EmailIntelligence {self.email}>"


class PhoneIntelligence(Base):
    """Phone Number Intelligence model"""
    __tablename__ = "phone_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)

    country_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    carrier = Column(String, nullable=True)
    line_type = Column(String, nullable=True)

    is_valid = Column(Integer, default=1, nullable=False)  # Boolean as int
    is_voip = Column(Integer, default=0, nullable=False)  # Boolean as int

    associated_accounts = Column(JSON, default=list, nullable=False)
    social_profiles = Column(JSON, default=list, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<PhoneIntelligence {self.phone_number}>"


class SocialIntelligence(Base):
    """Social Media Intelligence model"""
    __tablename__ = "social_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True, nullable=False)
    username = Column(String, index=True, nullable=False)
    profile_url = Column(String, nullable=False)

    profile_data = Column(JSON, default=dict, nullable=False)
    posts = Column(JSON, default=list, nullable=False)
    connections = Column(JSON, default=list, nullable=False)

    follower_count = Column(Integer, default=0, nullable=False)
    following_count = Column(Integer, default=0, nullable=False)
    post_count = Column(Integer, default=0, nullable=False)

    account_created_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)

    is_verified = Column(Integer, default=0, nullable=False)  # Boolean as int
    is_private = Column(Integer, default=0, nullable=False)  # Boolean as int

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<SocialIntelligence {self.platform}/{self.username}>"


class ImageIntelligence(Base):
    """Image Intelligence model (reverse image search, metadata)"""
    __tablename__ = "image_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    image_hash = Column(String, unique=True, index=True, nullable=False)
    image_url = Column(String, nullable=True)
    local_path = Column(String, nullable=True)

    exif_data = Column(JSON, default=dict, nullable=False)
    reverse_search_results = Column(JSON, default=list, nullable=False)

    similar_images = Column(JSON, default=list, nullable=False)
    detected_objects = Column(JSON, default=list, nullable=False)
    detected_text = Column(Text, nullable=True)
    detected_faces = Column(JSON, default=list, nullable=False)

    gps_coordinates = Column(JSON, default=dict, nullable=False)
    camera_info = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<ImageIntelligence {self.image_hash}>"
