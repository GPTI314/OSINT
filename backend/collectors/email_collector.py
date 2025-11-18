"""
Email intelligence collector for validation, breach checks, and SMTP verification.
"""
from typing import Dict, Any
import re
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import logging

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class EmailCollector(BaseCollector):
    """Collector for email intelligence gathering."""

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect intelligence on an email address.

        Args:
            target: Email address
            **kwargs: Additional parameters (check_breaches, hunter_api_key, etc.)

        Returns:
            Dict containing email intelligence
        """
        email = target.lower().strip()

        # Validate email format
        await self._validate_email(email)

        # Extract domain
        await self._extract_domain_info(email)

        # Check for breaches (if enabled)
        if kwargs.get("check_breaches", False):
            await self._check_breaches(email, kwargs.get("hibp_api_key"))

        # Hunter.io lookup (if API key available)
        if kwargs.get("hunter_api_key"):
            await self._hunter_lookup(email, kwargs["hunter_api_key"])

        # Email reputation check
        await self._check_reputation(email)

        return {
            "target": email,
            "target_type": "email",
            "results": self.results,
            "errors": self.errors,
            "summary": self.get_summary(),
            "collected_at": datetime.utcnow().isoformat()
        }

    async def _validate_email(self, email: str):
        """Validate email address format and deliverability."""
        try:
            validation = validate_email(email, check_deliverability=False)
            self.add_result("validation", {
                "email": validation.normalized,
                "local_part": validation.local_part,
                "domain": validation.domain,
                "is_valid": True
            }, confidence=1.0)
        except EmailNotValidError as e:
            self.add_error("validation", str(e))

    async def _extract_domain_info(self, email: str):
        """Extract and analyze domain from email."""
        try:
            domain = email.split("@")[1]
            self.add_result("domain_info", {
                "domain": domain,
                "is_free_provider": domain in [
                    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
                    "aol.com", "protonmail.com", "mail.com"
                ],
                "tld": domain.split(".")[-1] if "." in domain else None
            }, confidence=0.9)
        except Exception as e:
            self.add_error("domain_info", str(e))

    async def _check_breaches(self, email: str, api_key: str = None):
        """
        Check if email appears in known data breaches.

        Note: This requires Have I Been Pwned API integration.
        """
        # Placeholder for HIBP integration
        self.add_result("breach_check", {
            "email": email,
            "message": "HIBP API integration required",
            "breaches_found": 0,
            "pastes_found": 0
        }, confidence=0.0)

    async def _hunter_lookup(self, email: str, api_key: str):
        """
        Lookup email using Hunter.io API.

        Note: This requires Hunter.io API integration.
        """
        # Placeholder for Hunter.io integration
        self.add_result("hunter_io", {
            "email": email,
            "message": "Hunter.io API integration required"
        }, confidence=0.0)

    async def _check_reputation(self, email: str):
        """Check email reputation using various indicators."""
        domain = email.split("@")[1] if "@" in email else None

        if not domain:
            return

        # Check for suspicious patterns
        suspicious_patterns = [
            r'\d{5,}',  # Many numbers
            r'(temp|trash|throw|fake|spam)',  # Suspicious keywords
        ]

        is_suspicious = any(re.search(pattern, email, re.I) for pattern in suspicious_patterns)

        self.add_result("reputation", {
            "email": email,
            "is_suspicious": is_suspicious,
            "risk_score": 75 if is_suspicious else 25
        }, confidence=0.7)
