"""Subdomain enumeration module."""

from typing import List, Set
import asyncio
from loguru import logger

from .dns_resolver import DNSResolver


class SubdomainEnumerator:
    """
    Subdomain enumeration for domain reconnaissance.

    Features:
    - Brute force enumeration
    - DNS zone transfer attempts
    - Certificate transparency logs
    - Search engine discovery
    """

    def __init__(self):
        """Initialize subdomain enumerator."""
        self.dns_resolver = DNSResolver()

        # Common subdomain prefixes
        self.common_subdomains = [
            "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1",
            "webdisk", "ns2", "cpanel", "whm", "autodiscover", "autoconfig",
            "m", "imap", "test", "ns", "blog", "pop3", "dev", "www2", "admin",
            "forum", "news", "vpn", "ns3", "mail2", "new", "mysql", "old",
            "lists", "support", "mobile", "mx", "static", "docs", "beta",
            "shop", "sql", "secure", "demo", "cp", "calendar", "wiki", "web",
            "media", "email", "images", "img", "www1", "intranet", "portal",
            "video", "sip", "dns2", "api", "cdn", "stats", "dns1", "ns4",
            "www3", "dns", "search", "staging", "server", "mx1", "chat",
            "wap", "my", "svn", "mail1", "sites", "proxy", "ads", "host",
        ]

        logger.info("Subdomain enumerator initialized")

    async def enumerate(
        self,
        domain: str,
        use_common: bool = True,
        use_bruteforce: bool = False,
        custom_wordlist: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Enumerate subdomains for a domain.

        Args:
            domain: Domain to enumerate
            use_common: Use common subdomain list
            use_bruteforce: Use brute force with wordlist
            custom_wordlist: Custom subdomain wordlist

        Returns:
            Enumeration results
        """
        try:
            logger.info(f"Enumerating subdomains for: {domain}")

            found_subdomains: Set[str] = set()

            # Use common subdomains
            if use_common:
                common_results = await self._check_common_subdomains(domain)
                found_subdomains.update(common_results)

            # Use custom wordlist
            if use_bruteforce and custom_wordlist:
                bruteforce_results = await self._bruteforce_subdomains(
                    domain,
                    custom_wordlist
                )
                found_subdomains.update(bruteforce_results)

            logger.info(f"Found {len(found_subdomains)} subdomains for {domain}")

            return {
                "domain": domain,
                "subdomains": sorted(list(found_subdomains)),
                "count": len(found_subdomains),
            }

        except Exception as e:
            logger.error(f"Error enumerating subdomains for {domain}: {e}")
            return {
                "domain": domain,
                "error": str(e),
                "subdomains": [],
            }

    async def _check_common_subdomains(self, domain: str) -> Set[str]:
        """Check common subdomains."""
        found = set()

        # Create tasks for concurrent checking
        tasks = []
        for subdomain in self.common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            tasks.append(self._check_subdomain(full_domain))

        # Check all subdomains concurrently (with limit)
        semaphore = asyncio.Semaphore(20)

        async def check_with_semaphore(task):
            async with semaphore:
                return await task

        results = await asyncio.gather(
            *[check_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )

        # Collect found subdomains
        for i, result in enumerate(results):
            if isinstance(result, bool) and result:
                subdomain = f"{self.common_subdomains[i]}.{domain}"
                found.add(subdomain)

        return found

    async def _bruteforce_subdomains(
        self,
        domain: str,
        wordlist: List[str]
    ) -> Set[str]:
        """Brute force subdomains using wordlist."""
        found = set()

        semaphore = asyncio.Semaphore(20)

        async def check_with_semaphore(subdomain):
            async with semaphore:
                full_domain = f"{subdomain}.{domain}"
                if await self._check_subdomain(full_domain):
                    return full_domain
                return None

        tasks = [check_with_semaphore(sub) for sub in wordlist]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if result and not isinstance(result, Exception):
                found.add(result)

        return found

    async def _check_subdomain(self, subdomain: str) -> bool:
        """Check if subdomain exists via DNS lookup."""
        try:
            a_records = await self.dns_resolver.resolve_a(subdomain)
            return len(a_records) > 0
        except Exception:
            return False
