"""IP address intelligence gathering."""

from typing import Dict, Any, Optional
from datetime import datetime
import httpx
from loguru import logger
from config.settings import settings


class IPIntelligence:
    """
    IP address intelligence gathering.

    Features:
    - Geolocation
    - ISP information
    - Threat intelligence
    - Shodan integration
    - Censys integration
    - Reputation checking
    """

    def __init__(self):
        """Initialize IP intelligence."""
        self.ipinfo_api_key = settings.ipinfo_api_key
        self.shodan_api_key = settings.shodan_api_key

        logger.info("IP intelligence initialized")

    async def gather_intelligence(self, ip_address: str) -> Dict[str, Any]:
        """
        Gather comprehensive intelligence on an IP address.

        Args:
            ip_address: IP address to investigate

        Returns:
            Intelligence data dictionary
        """
        start_time = datetime.utcnow()

        try:
            logger.info(f"Gathering IP intelligence: {ip_address}")

            # Parallel data gathering
            import asyncio
            tasks = {
                "geolocation": self.get_geolocation(ip_address),
                "reputation": self.check_reputation(ip_address),
            }

            if self.shodan_api_key:
                tasks["shodan"] = self.query_shodan(ip_address)

            # Gather all data
            results = {}
            for key, task in tasks.items():
                try:
                    results[key] = await task
                except Exception as e:
                    logger.error(f"Error gathering {key} for {ip_address}: {e}")
                    results[key] = {"error": str(e)}

            # Compile intelligence report
            intelligence = {
                "ip_address": ip_address,
                "timestamp": datetime.utcnow().isoformat(),
                "duration_seconds": (datetime.utcnow() - start_time).total_seconds(),
                "geolocation": results.get("geolocation", {}),
                "reputation": results.get("reputation", {}),
                "shodan": results.get("shodan", {}),
                "risk_score": self._calculate_risk_score(results),
            }

            logger.info(f"IP intelligence gathered: {ip_address}")
            return intelligence

        except Exception as e:
            logger.error(f"Error gathering IP intelligence: {e}")
            return {
                "ip_address": ip_address,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_geolocation(self, ip_address: str) -> Dict[str, Any]:
        """
        Get geolocation information for IP address.

        Args:
            ip_address: IP address to lookup

        Returns:
            Geolocation data
        """
        try:
            if self.ipinfo_api_key:
                url = f"https://ipinfo.io/{ip_address}"
                headers = {"Authorization": f"Bearer {self.ipinfo_api_key}"}
            else:
                url = f"https://ipinfo.io/{ip_address}/json"
                headers = {}

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"Error getting geolocation for {ip_address}: {e}")
            return {"error": str(e)}

    async def check_reputation(self, ip_address: str) -> Dict[str, Any]:
        """
        Check IP reputation across multiple sources.

        Args:
            ip_address: IP address to check

        Returns:
            Reputation data
        """
        reputation = {
            "is_threat": False,
            "threat_types": [],
            "sources": [],
        }

        # Here you would integrate with various threat intelligence feeds
        # For now, returning a placeholder structure

        return reputation

    async def query_shodan(self, ip_address: str) -> Dict[str, Any]:
        """
        Query Shodan for IP information.

        Args:
            ip_address: IP address to query

        Returns:
            Shodan data
        """
        if not self.shodan_api_key:
            return {"error": "Shodan API key not configured"}

        try:
            import shodan
            api = shodan.Shodan(self.shodan_api_key)

            # Run in executor to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            host_info = await loop.run_in_executor(None, api.host, ip_address)

            return {
                "ip": host_info.get("ip_str"),
                "organization": host_info.get("org"),
                "os": host_info.get("os"),
                "ports": host_info.get("ports", []),
                "vulnerabilities": host_info.get("vulns", []),
                "last_update": host_info.get("last_update"),
                "country": host_info.get("country_name"),
                "city": host_info.get("city"),
            }

        except Exception as e:
            logger.error(f"Error querying Shodan for {ip_address}: {e}")
            return {"error": str(e)}

    def _calculate_risk_score(self, results: Dict[str, Any]) -> float:
        """Calculate risk score from intelligence results."""
        score = 0.0

        reputation = results.get("reputation", {})
        if reputation.get("is_threat"):
            score += 0.5

        shodan = results.get("shodan", {})
        if shodan.get("vulnerabilities"):
            score += 0.3

        return min(score, 1.0)
