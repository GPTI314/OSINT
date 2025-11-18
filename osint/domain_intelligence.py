"""Domain intelligence gathering module."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .whois_client import WHOISClient
from .dns_resolver import DNSResolver
from .ssl_analyzer import SSLAnalyzer
from .subdomain_enumerator import SubdomainEnumerator
from .technology_detector import TechnologyDetector


class DomainIntelligence:
    """
    Comprehensive domain intelligence gathering.

    Features:
    - WHOIS lookup
    - DNS records
    - SSL certificate analysis
    - Subdomain enumeration
    - Technology detection
    - Historical data
    """

    def __init__(self):
        """Initialize domain intelligence."""
        self.whois_client = WHOISClient()
        self.dns_resolver = DNSResolver()
        self.ssl_analyzer = SSLAnalyzer()
        self.subdomain_enumerator = SubdomainEnumerator()
        self.technology_detector = TechnologyDetector()

        logger.info("Domain intelligence initialized")

    async def gather_intelligence(
        self,
        domain: str,
        include_subdomains: bool = True,
        include_technology: bool = True,
    ) -> Dict[str, Any]:
        """
        Gather comprehensive intelligence on a domain.

        Args:
            domain: Domain name to investigate
            include_subdomains: Whether to enumerate subdomains
            include_technology: Whether to detect technologies

        Returns:
            Intelligence data dictionary
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Gathering domain intelligence: {domain}")

            # Parallel data gathering
            import asyncio
            tasks = {
                "whois": self.whois_client.lookup(domain),
                "dns": self.dns_resolver.resolve_all(domain),
                "ssl": self.ssl_analyzer.analyze(domain),
            }

            if include_subdomains:
                tasks["subdomains"] = self.subdomain_enumerator.enumerate(domain)

            if include_technology:
                tasks["technology"] = self.technology_detector.detect(f"https://{domain}")

            # Gather all data
            results = {}
            for key, task in tasks.items():
                try:
                    results[key] = await task
                except Exception as e:
                    logger.error(f"Error gathering {key} for {domain}: {e}")
                    results[key] = {"error": str(e)}

            # Compile intelligence report
            intelligence = {
                "domain": domain,
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "whois": results.get("whois", {}),
                "dns": results.get("dns", {}),
                "ssl": results.get("ssl", {}),
                "subdomains": results.get("subdomains", {}),
                "technology": results.get("technology", {}),
                "risk_indicators": self._analyze_risk(results),
            }

            logger.info(f"Domain intelligence gathered: {domain}")
            return intelligence

        except Exception as e:
            logger.error(f"Error gathering domain intelligence: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _analyze_risk(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk indicators from gathered intelligence.

        Args:
            results: Intelligence results

        Returns:
            Risk analysis dictionary
        """
        risk_indicators = []
        risk_score = 0.0

        # Check WHOIS data
        whois_data = results.get("whois", {})
        if whois_data.get("creation_date"):
            # Recently registered domains might be suspicious
            pass

        # Check SSL certificate
        ssl_data = results.get("ssl", {})
        if ssl_data.get("expired"):
            risk_indicators.append("Expired SSL certificate")
            risk_score += 0.3

        if ssl_data.get("self_signed"):
            risk_indicators.append("Self-signed SSL certificate")
            risk_score += 0.2

        # Check DNS records
        dns_data = results.get("dns", {})
        if not dns_data.get("A"):
            risk_indicators.append("No A records found")
            risk_score += 0.1

        return {
            "risk_score": min(risk_score, 1.0),
            "risk_level": self._get_risk_level(risk_score),
            "indicators": risk_indicators,
        }

    def _get_risk_level(self, score: float) -> str:
        """Get risk level from score."""
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "info"

    async def get_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """
        Get domain reputation from multiple sources.

        Args:
            domain: Domain to check

        Returns:
            Reputation data
        """
        # This would integrate with reputation services
        # like VirusTotal, URLhaus, etc.
        return {
            "domain": domain,
            "reputation": "unknown",
            "sources": [],
        }
