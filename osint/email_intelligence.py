"""Email address intelligence gathering."""

from typing import Dict, Any, Optional
from datetime import datetime
import re
import httpx
from loguru import logger
from config.settings import settings


class EmailIntelligence:
    """
    Email address intelligence gathering.

    Features:
    - Email validation
    - Domain verification
    - Breach detection
    - Social media discovery
    - Professional profiles
    """

    def __init__(self):
        """Initialize email intelligence."""
        self.hunter_api_key = settings.hunter_io_api_key

        logger.info("Email intelligence initialized")

    async def gather_intelligence(self, email: str) -> Dict[str, Any]:
        """
        Gather comprehensive intelligence on an email address.

        Args:
            email: Email address to investigate

        Returns:
            Intelligence data dictionary
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Gathering email intelligence: {email}")

            # Validate email format
            if not self.is_valid_email(email):
                return {
                    "email": email,
                    "error": "Invalid email format",
                    "timestamp": datetime.utcnow().isoformat(),
                }

            # Extract domain
            domain = email.split("@")[1]

            # Parallel data gathering
            import asyncio
            tasks = {
                "validation": self.validate_email(email),
                "domain_info": self.get_domain_info(domain),
                "breaches": self.check_breaches(email),
            }

            # Gather all data
            results = {}
            for key, task in tasks.items():
                try:
                    results[key] = await task
                except Exception as e:
                    logger.error(f"Error gathering {key} for {email}: {e}")
                    results[key] = {"error": str(e)}

            # Compile intelligence report
            intelligence = {
                "email": email,
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "validation": results.get("validation", {}),
                "domain_info": results.get("domain_info", {}),
                "breaches": results.get("breaches", {}),
                "risk_score": self._calculate_risk_score(results),
            }

            logger.info(f"Email intelligence gathered: {email}")
            return intelligence

        except Exception as e:
            logger.error(f"Error gathering email intelligence: {e}")
            return {
                "email": email,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def is_valid_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    async def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Validate email deliverability.

        Args:
            email: Email address to validate

        Returns:
            Validation results
        """
        # Basic validation result
        validation = {
            "format_valid": self.is_valid_email(email),
            "disposable": False,
            "free_provider": self._is_free_provider(email),
        }

        # Use Hunter.io if API key available
        if self.hunter_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://api.hunter.io/v2/email-verifier",
                        params={
                            "email": email,
                            "api_key": self.hunter_api_key,
                        },
                        timeout=10,
                    )
                    if response.status_code == 200:
                        data = response.json().get("data", {})
                        validation.update({
                            "deliverable": data.get("result") == "deliverable",
                            "score": data.get("score"),
                            "sources": data.get("sources", []),
                        })
            except Exception as e:
                logger.debug(f"Hunter.io validation failed: {e}")

        return validation

    async def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """
        Get information about the email domain.

        Args:
            domain: Email domain

        Returns:
            Domain information
        """
        return {
            "domain": domain,
            "is_free_provider": self._is_free_provider(f"user@{domain}"),
            "is_disposable": False,  # Would check against disposable email list
        }

    async def check_breaches(self, email: str) -> Dict[str, Any]:
        """
        Check if email appears in data breaches.

        Args:
            email: Email address to check

        Returns:
            Breach information
        """
        # This would integrate with HIBP (Have I Been Pwned) or similar services
        # Requires API key and proper implementation
        return {
            "breached": False,
            "breaches": [],
            "note": "Breach checking requires HIBP API integration",
        }

    def _is_free_provider(self, email: str) -> bool:
        """Check if email is from a free provider."""
        free_providers = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "aol.com", "icloud.com", "mail.com", "protonmail.com",
        }
        domain = email.split("@")[1].lower()
        return domain in free_providers

    def _calculate_risk_score(self, results: Dict[str, Any]) -> float:
        """Calculate risk score from intelligence results."""
        score = 0.0

        breaches = results.get("breaches", {})
        if breaches.get("breached"):
            score += 0.4

        validation = results.get("validation", {})
        if validation.get("disposable"):
            score += 0.3

        return min(score, 1.0)
