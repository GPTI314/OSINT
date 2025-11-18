"""
OSINT Toolkit - Open Source Intelligence Gathering Framework
"""

__version__ = "1.0.0"
__author__ = "OSINT Team"

from .modules.domain import DomainIntelligence
from .modules.ip import IPIntelligence
from .modules.email import EmailIntelligence
from .modules.phone import PhoneIntelligence
from .modules.social import SocialMediaIntelligence
from .modules.image import ImageIntelligence

__all__ = [
    "DomainIntelligence",
    "IPIntelligence",
    "EmailIntelligence",
    "PhoneIntelligence",
    "SocialMediaIntelligence",
    "ImageIntelligence",
]
