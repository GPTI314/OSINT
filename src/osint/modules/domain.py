"""
Domain Intelligence Module

Provides comprehensive domain intelligence gathering including:
- WHOIS lookup
- DNS records
- Subdomain enumeration
- SSL certificate analysis
- Technology detection
- Historical data
- Threat intelligence
"""

import whois
import dns.resolver
import dns.zone
import dns.query
import ssl
import socket
import requests
from datetime import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import builtwith
import json

from ..core.base import BaseModule
from ..core.utils import is_valid_domain, resolve_domain, rate_limit


class DomainIntelligence(BaseModule):
    """Domain Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.shodan_api_key = self.config.get('shodan_api_key')
        self.virustotal_api_key = self.config.get('virustotal_api_key')
        self.securitytrails_api_key = self.config.get('securitytrails_api_key')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive domain intelligence

        Args:
            target: Domain name to investigate
            **kwargs: Additional options
                - include_whois: Include WHOIS data (default: True)
                - include_dns: Include DNS records (default: True)
                - include_subdomains: Include subdomain enumeration (default: True)
                - include_ssl: Include SSL certificate data (default: True)
                - include_technology: Include technology detection (default: True)
                - include_historical: Include historical data (default: True)
                - include_threat_intel: Include threat intelligence (default: True)

        Returns:
            Dictionary with comprehensive domain intelligence
        """
        if not is_valid_domain(target):
            return self._create_result(
                target=target,
                data={},
                success=False,
                error="Invalid domain name"
            )

        try:
            data = {}

            if kwargs.get('include_whois', True):
                data['whois'] = self.get_whois(target)

            if kwargs.get('include_dns', True):
                data['dns'] = self.get_dns_records(target)

            if kwargs.get('include_subdomains', True):
                data['subdomains'] = self.enumerate_subdomains(target)

            if kwargs.get('include_ssl', True):
                data['ssl'] = self.get_ssl_certificate(target)

            if kwargs.get('include_technology', True):
                data['technology'] = self.detect_technologies(target)

            if kwargs.get('include_historical', True):
                data['historical'] = self.get_historical_data(target)

            if kwargs.get('include_threat_intel', True):
                data['threat_intelligence'] = self.get_threat_intelligence(target)

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def get_whois(self, domain: str) -> Dict[str, Any]:
        """
        Get WHOIS information for domain

        Args:
            domain: Domain name

        Returns:
            WHOIS data dictionary
        """
        try:
            w = whois.whois(domain)

            # Convert datetime objects to strings
            def serialize_value(value):
                if isinstance(value, datetime):
                    return value.isoformat()
                elif isinstance(value, list):
                    return [serialize_value(v) for v in value]
                return value

            whois_data = {}
            for key, value in w.items():
                if value:
                    whois_data[key] = serialize_value(value)

            return {
                'domain_name': whois_data.get('domain_name', ''),
                'registrar': whois_data.get('registrar', ''),
                'creation_date': whois_data.get('creation_date', ''),
                'expiration_date': whois_data.get('expiration_date', ''),
                'updated_date': whois_data.get('updated_date', ''),
                'name_servers': whois_data.get('name_servers', []),
                'status': whois_data.get('status', []),
                'emails': whois_data.get('emails', []),
                'org': whois_data.get('org', ''),
                'registrant': whois_data.get('registrant', ''),
                'raw': whois_data
            }

        except Exception as e:
            self.logger.warning(f"WHOIS lookup failed for {domain}: {str(e)}")
            return {'error': str(e)}

    def get_dns_records(self, domain: str) -> Dict[str, Any]:
        """
        Get DNS records for domain

        Args:
            domain: Domain name

        Returns:
            DNS records dictionary
        """
        dns_data = {}
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME', 'SOA']

        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                dns_data[record_type] = [str(rdata) for rdata in answers]
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
                dns_data[record_type] = []
            except Exception as e:
                self.logger.warning(f"DNS lookup failed for {domain} {record_type}: {str(e)}")
                dns_data[record_type] = []

        # Extract SPF and DMARC from TXT records
        txt_records = dns_data.get('TXT', [])
        dns_data['SPF'] = [record for record in txt_records if 'v=spf1' in record.lower()]
        dns_data['DMARC'] = []

        try:
            dmarc_domain = f"_dmarc.{domain}"
            dmarc_answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            dns_data['DMARC'] = [str(rdata) for rdata in dmarc_answers]
        except:
            pass

        return dns_data

    def enumerate_subdomains(self, domain: str) -> Dict[str, Any]:
        """
        Enumerate subdomains using multiple methods

        Args:
            domain: Domain name

        Returns:
            Subdomain enumeration results
        """
        subdomains = set()

        # Method 1: Common subdomain wordlist
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
            'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn',
            'ns3', 'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx',
            'static', 'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar',
            'wiki', 'web', 'media', 'email', 'images', 'img', 'www1', 'intranet',
            'portal', 'video', 'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4',
            'www3', 'dns', 'search', 'staging', 'server', 'mx1', 'chat', 'wap', 'my',
            'svn', 'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup',
            'mx2', 'lyncdiscover', 'info', 'apps', 'download', 'remote', 'db', 'forums',
            'store', 'relay', 'files', 'newsletter', 'app', 'live', 'owa', 'en', 'start',
            'sms', 'office', 'exchange', 'ipv4'
        ]

        for subdomain in common_subdomains:
            full_domain = f"{subdomain}.{domain}"
            try:
                ips = resolve_domain(full_domain)
                if ips:
                    subdomains.add(full_domain)
            except:
                pass

        # Method 2: Certificate Transparency Logs (via crt.sh)
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry.get('name_value', '')
                    for subdomain in name.split('\n'):
                        subdomain = subdomain.strip()
                        if subdomain and subdomain.endswith(domain):
                            subdomains.add(subdomain)
        except Exception as e:
            self.logger.warning(f"Certificate transparency lookup failed: {str(e)}")

        # Method 3: SecurityTrails API (if available)
        if self.securitytrails_api_key:
            try:
                headers = {'APIKEY': self.securitytrails_api_key}
                url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for subdomain in data.get('subdomains', []):
                        subdomains.add(f"{subdomain}.{domain}")
            except Exception as e:
                self.logger.warning(f"SecurityTrails API failed: {str(e)}")

        return {
            'count': len(subdomains),
            'subdomains': sorted(list(subdomains))
        }

    def get_ssl_certificate(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Get SSL certificate information

        Args:
            domain: Domain name
            port: HTTPS port (default: 443)

        Returns:
            SSL certificate data
        """
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    return {
                        'subject': dict(x[0] for x in cert.get('subject', ())),
                        'issuer': dict(x[0] for x in cert.get('issuer', ())),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'subject_alt_names': [x[1] for x in cert.get('subjectAltName', [])],
                        'cipher': ssock.cipher(),
                        'tls_version': ssock.version()
                    }

        except Exception as e:
            self.logger.warning(f"SSL certificate retrieval failed for {domain}: {str(e)}")
            return {'error': str(e)}

    def detect_technologies(self, domain: str) -> Dict[str, Any]:
        """
        Detect technologies used by the domain

        Args:
            domain: Domain name

        Returns:
            Technology detection results
        """
        technologies = {}

        # BuiltWith detection
        try:
            url = f"https://{domain}"
            builtwith_data = builtwith.parse(url)
            technologies['builtwith'] = builtwith_data
        except Exception as e:
            self.logger.warning(f"BuiltWith detection failed: {str(e)}")
            technologies['builtwith'] = {}

        # Manual detection from HTTP headers and content
        try:
            url = f"https://{domain}"
            response = requests.get(url, timeout=10, allow_redirects=True)

            technologies['manual'] = {
                'server': response.headers.get('Server', ''),
                'x_powered_by': response.headers.get('X-Powered-By', ''),
                'content_type': response.headers.get('Content-Type', ''),
                'status_code': response.status_code,
                'headers': dict(response.headers)
            }

        except Exception as e:
            self.logger.warning(f"Manual technology detection failed: {str(e)}")
            technologies['manual'] = {}

        return technologies

    def get_historical_data(self, domain: str) -> Dict[str, Any]:
        """
        Get historical data for domain

        Args:
            domain: Domain name

        Returns:
            Historical data
        """
        historical = {}

        # Wayback Machine
        try:
            url = f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&limit=100"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if len(data) > 1:  # First row is headers
                    snapshots = []
                    for row in data[1:]:
                        snapshots.append({
                            'timestamp': row[1],
                            'url': row[2],
                            'status': row[4],
                            'mime_type': row[3]
                        })
                    historical['wayback_machine'] = {
                        'total_snapshots': len(snapshots),
                        'first_snapshot': snapshots[0]['timestamp'] if snapshots else None,
                        'last_snapshot': snapshots[-1]['timestamp'] if snapshots else None,
                        'snapshots': snapshots[:10]  # First 10 snapshots
                    }
        except Exception as e:
            self.logger.warning(f"Wayback Machine lookup failed: {str(e)}")
            historical['wayback_machine'] = {}

        return historical

    def get_threat_intelligence(self, domain: str) -> Dict[str, Any]:
        """
        Get threat intelligence for domain

        Args:
            domain: Domain name

        Returns:
            Threat intelligence data
        """
        threat_intel = {}

        # VirusTotal
        if self.virustotal_api_key:
            try:
                headers = {'x-apikey': self.virustotal_api_key}
                url = f"https://www.virustotal.com/api/v3/domains/{domain}"
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    attributes = data.get('data', {}).get('attributes', {})
                    last_analysis = attributes.get('last_analysis_stats', {})

                    threat_intel['virustotal'] = {
                        'reputation': attributes.get('reputation', 0),
                        'malicious': last_analysis.get('malicious', 0),
                        'suspicious': last_analysis.get('suspicious', 0),
                        'harmless': last_analysis.get('harmless', 0),
                        'undetected': last_analysis.get('undetected', 0),
                        'categories': attributes.get('categories', {}),
                        'last_analysis_date': attributes.get('last_analysis_date', '')
                    }
            except Exception as e:
                self.logger.warning(f"VirusTotal lookup failed: {str(e)}")
                threat_intel['virustotal'] = {}

        # Check various threat lists
        threat_intel['checks'] = {
            'is_suspicious': self._check_suspicious_indicators(domain),
            'domain_age_suspicious': False,  # Placeholder
            'reputation_score': 0  # Placeholder
        }

        return threat_intel

    def _check_suspicious_indicators(self, domain: str) -> bool:
        """
        Check for suspicious indicators in domain

        Args:
            domain: Domain name

        Returns:
            True if suspicious indicators found
        """
        suspicious_patterns = [
            '-payment', '-secure', '-login', '-verify', '-update',
            'account-', 'billing-', 'signin-', 'security-'
        ]

        domain_lower = domain.lower()
        return any(pattern in domain_lower for pattern in suspicious_patterns)
