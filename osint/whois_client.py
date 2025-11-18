"""WHOIS lookup client."""

from typing import Dict, Any, Optional
import whois
from datetime import datetime
from loguru import logger


class WHOISClient:
    """
    WHOIS lookup client for domain registration information.

    Features:
    - Domain WHOIS lookups
    - Registrar information
    - Registration dates
    - Contact information
    - Name servers
    """

    def __init__(self):
        """Initialize WHOIS client."""
        logger.info("WHOIS client initialized")

    async def lookup(self, domain: str) -> Dict[str, Any]:
        """
        Perform WHOIS lookup for a domain.

        Args:
            domain: Domain name to lookup

        Returns:
            WHOIS data dictionary
        """
        try:
            logger.debug(f"Performing WHOIS lookup: {domain}")

            # Perform WHOIS query
            w = whois.whois(domain)

            # Parse and structure data
            data = {
                "domain_name": self._extract_value(w.domain_name),
                "registrar": self._extract_value(w.registrar),
                "whois_server": self._extract_value(w.whois_server),
                "creation_date": self._format_date(w.creation_date),
                "expiration_date": self._format_date(w.expiration_date),
                "updated_date": self._format_date(w.updated_date),
                "status": self._extract_value(w.status),
                "name_servers": self._extract_list(w.name_servers),
                "emails": self._extract_list(w.emails),
                "registrant": {
                    "name": self._extract_value(getattr(w, "name", None)),
                    "organization": self._extract_value(getattr(w, "org", None)),
                    "country": self._extract_value(getattr(w, "country", None)),
                },
            }

            logger.info(f"WHOIS lookup completed: {domain}")
            return data

        except Exception as e:
            logger.error(f"WHOIS lookup failed for {domain}: {e}")
            return {
                "domain": domain,
                "error": str(e),
            }

    def _extract_value(self, value):
        """Extract single value from WHOIS result."""
        if value is None:
            return None
        if isinstance(value, list):
            return value[0] if value else None
        return str(value)

    def _extract_list(self, value) -> list:
        """Extract list from WHOIS result."""
        if value is None:
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        return [str(value)]

    def _format_date(self, date_value) -> Optional[str]:
        """Format date from WHOIS result."""
        if date_value is None:
            return None

        if isinstance(date_value, list):
            date_value = date_value[0] if date_value else None

        if isinstance(date_value, datetime):
            return date_value.isoformat()
        elif isinstance(date_value, str):
            return date_value

        return None
