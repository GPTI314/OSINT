"""
Domain intelligence collector for WHOIS, DNS, and subdomain enumeration.
"""
from typing import Dict, Any
import whois
import dns.resolver
import socket
from datetime import datetime
import logging

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class DomainCollector(BaseCollector):
    """Collector for domain intelligence gathering."""

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect intelligence on a domain.

        Args:
            target: Domain name
            **kwargs: Additional parameters

        Returns:
            Dict containing domain intelligence
        """
        domain = target.lower().strip()

        # Collect WHOIS data
        await self._collect_whois(domain)

        # Collect DNS records
        await self._collect_dns(domain)

        # Collect IP resolution
        await self._collect_ip_resolution(domain)

        # Collect subdomains (if enabled)
        if kwargs.get("enumerate_subdomains", False):
            await self._enumerate_subdomains(domain)

        return {
            "target": domain,
            "target_type": "domain",
            "results": self.results,
            "errors": self.errors,
            "summary": self.get_summary(),
            "collected_at": datetime.utcnow().isoformat()
        }

    async def _collect_whois(self, domain: str):
        """Collect WHOIS information."""
        try:
            w = whois.whois(domain)
            whois_data = {
                "registrar": w.registrar,
                "creation_date": str(w.creation_date) if w.creation_date else None,
                "expiration_date": str(w.expiration_date) if w.expiration_date else None,
                "updated_date": str(w.updated_date) if w.updated_date else None,
                "name_servers": w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                "status": w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                "emails": w.emails if isinstance(w.emails, list) else [w.emails] if w.emails else [],
                "organization": w.org,
                "country": w.country
            }
            self.add_result("whois", whois_data, confidence=0.95)
        except Exception as e:
            self.add_error("whois", str(e))

    async def _collect_dns(self, domain: str):
        """Collect DNS records."""
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        dns_data = {}

        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                dns_data[record_type] = [str(rdata) for rdata in answers]
            except dns.resolver.NoAnswer:
                dns_data[record_type] = []
            except dns.resolver.NXDOMAIN:
                self.add_error("dns", f"Domain {domain} does not exist")
                return
            except Exception as e:
                logger.debug(f"Error getting {record_type} records: {e}")
                dns_data[record_type] = []

        if dns_data:
            self.add_result("dns", dns_data, confidence=1.0)

    async def _collect_ip_resolution(self, domain: str):
        """Resolve domain to IP addresses."""
        try:
            ip_addresses = socket.gethostbyname_ex(domain)[2]
            self.add_result("ip_resolution", {
                "ips": ip_addresses,
                "primary_ip": ip_addresses[0] if ip_addresses else None
            }, confidence=1.0)
        except socket.gaierror as e:
            self.add_error("ip_resolution", str(e))

    async def _enumerate_subdomains(self, domain: str):
        """
        Enumerate subdomains using common subdomain wordlist.

        Note: This is a basic implementation. Production systems should use
        specialized tools like Amass, Subfinder, or SecurityTrails API.
        """
        common_subdomains = [
            "www", "mail", "ftp", "admin", "api", "dev", "staging",
            "test", "blog", "shop", "store", "portal", "vpn", "remote"
        ]

        found_subdomains = []

        for sub in common_subdomains:
            subdomain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(subdomain)
                found_subdomains.append(subdomain)
            except socket.gaierror:
                pass

        if found_subdomains:
            self.add_result("subdomains", {
                "found": found_subdomains,
                "count": len(found_subdomains)
            }, confidence=0.8)
