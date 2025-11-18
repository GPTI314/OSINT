"""DNS resolution and analysis."""

from typing import Dict, Any, List
import dns.resolver
import dns.reversename
from loguru import logger


class DNSResolver:
    """
    DNS resolver for domain name lookups.

    Features:
    - A/AAAA records
    - MX records
    - TXT records
    - NS records
    - CNAME records
    - Reverse DNS
    """

    def __init__(self, nameservers: List[str] = None):
        """
        Initialize DNS resolver.

        Args:
            nameservers: Custom nameservers to use
        """
        self.resolver = dns.resolver.Resolver()

        if nameservers:
            self.resolver.nameservers = nameservers

        logger.info("DNS resolver initialized")

    async def resolve_all(self, domain: str) -> Dict[str, Any]:
        """
        Resolve all DNS records for a domain.

        Args:
            domain: Domain name to resolve

        Returns:
            Dictionary of DNS records
        """
        try:
            logger.debug(f"Resolving DNS for: {domain}")

            records = {
                "A": await self.resolve_a(domain),
                "AAAA": await self.resolve_aaaa(domain),
                "MX": await self.resolve_mx(domain),
                "TXT": await self.resolve_txt(domain),
                "NS": await self.resolve_ns(domain),
                "CNAME": await self.resolve_cname(domain),
                "SOA": await self.resolve_soa(domain),
            }

            logger.info(f"DNS resolution completed: {domain}")
            return records

        except Exception as e:
            logger.error(f"DNS resolution failed for {domain}: {e}")
            return {"error": str(e)}

    async def resolve_a(self, domain: str) -> List[str]:
        """Resolve A (IPv4) records."""
        try:
            answers = self.resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"No A records for {domain}: {e}")
            return []

    async def resolve_aaaa(self, domain: str) -> List[str]:
        """Resolve AAAA (IPv6) records."""
        try:
            answers = self.resolver.resolve(domain, 'AAAA')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"No AAAA records for {domain}: {e}")
            return []

    async def resolve_mx(self, domain: str) -> List[Dict[str, Any]]:
        """Resolve MX (Mail Exchange) records."""
        try:
            answers = self.resolver.resolve(domain, 'MX')
            return [
                {"priority": rdata.preference, "server": str(rdata.exchange)}
                for rdata in answers
            ]
        except Exception as e:
            logger.debug(f"No MX records for {domain}: {e}")
            return []

    async def resolve_txt(self, domain: str) -> List[str]:
        """Resolve TXT records."""
        try:
            answers = self.resolver.resolve(domain, 'TXT')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"No TXT records for {domain}: {e}")
            return []

    async def resolve_ns(self, domain: str) -> List[str]:
        """Resolve NS (Name Server) records."""
        try:
            answers = self.resolver.resolve(domain, 'NS')
            return [str(rdata) for rdata in answers]
        except Exception as e:
            logger.debug(f"No NS records for {domain}: {e}")
            return []

    async def resolve_cname(self, domain: str) -> Optional[str]:
        """Resolve CNAME record."""
        try:
            answers = self.resolver.resolve(domain, 'CNAME')
            return str(answers[0]) if answers else None
        except Exception as e:
            logger.debug(f"No CNAME record for {domain}: {e}")
            return None

    async def resolve_soa(self, domain: str) -> Optional[Dict[str, Any]]:
        """Resolve SOA (Start of Authority) record."""
        try:
            answers = self.resolver.resolve(domain, 'SOA')
            if answers:
                soa = answers[0]
                return {
                    "mname": str(soa.mname),
                    "rname": str(soa.rname),
                    "serial": soa.serial,
                    "refresh": soa.refresh,
                    "retry": soa.retry,
                    "expire": soa.expire,
                    "minimum": soa.minimum,
                }
        except Exception as e:
            logger.debug(f"No SOA record for {domain}: {e}")
            return None

    async def reverse_dns(self, ip_address: str) -> Optional[str]:
        """
        Perform reverse DNS lookup.

        Args:
            ip_address: IP address to lookup

        Returns:
            Domain name or None
        """
        try:
            rev_name = dns.reversename.from_address(ip_address)
            answers = self.resolver.resolve(rev_name, 'PTR')
            return str(answers[0]) if answers else None
        except Exception as e:
            logger.debug(f"Reverse DNS failed for {ip_address}: {e}")
            return None
