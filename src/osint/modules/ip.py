"""
IP Intelligence Module

Provides comprehensive IP address intelligence gathering including:
- Geolocation
- ASN information
- Port scanning
- Service detection
- Threat intelligence
- Historical data
"""

import requests
import nmap
import socket
from typing import Dict, Any, List, Optional
from ipwhois import IPWhois
import geoip2.database
import os

from ..core.base import BaseModule
from ..core.utils import is_valid_ip, reverse_dns


class IPIntelligence(BaseModule):
    """IP Intelligence gathering module"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.shodan_api_key = self.config.get('shodan_api_key')
        self.virustotal_api_key = self.config.get('virustotal_api_key')
        self.abuseipdb_api_key = self.config.get('abuseipdb_api_key')
        self.ipinfo_api_key = self.config.get('ipinfo_api_key')
        self.censys_api_id = self.config.get('censys_api_id')
        self.censys_api_secret = self.config.get('censys_api_secret')
        self.maxmind_db_path = self.config.get('maxmind_db_path')

    def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect comprehensive IP intelligence

        Args:
            target: IP address to investigate
            **kwargs: Additional options
                - include_geolocation: Include geolocation data (default: True)
                - include_asn: Include ASN information (default: True)
                - include_ports: Include port scanning (default: False)
                - include_services: Include service detection (default: False)
                - include_threat_intel: Include threat intelligence (default: True)
                - include_historical: Include historical data (default: True)
                - port_range: Port range for scanning (default: "1-1000")

        Returns:
            Dictionary with comprehensive IP intelligence
        """
        if not is_valid_ip(target):
            return self._create_result(
                target=target,
                data={},
                success=False,
                error="Invalid IP address"
            )

        try:
            data = {}

            if kwargs.get('include_geolocation', True):
                data['geolocation'] = self.get_geolocation(target)

            if kwargs.get('include_asn', True):
                data['asn'] = self.get_asn_info(target)

            if kwargs.get('include_ports', False):
                port_range = kwargs.get('port_range', '1-1000')
                data['ports'] = self.scan_ports(target, port_range)

            if kwargs.get('include_services', False):
                data['services'] = self.detect_services(target)

            if kwargs.get('include_threat_intel', True):
                data['threat_intelligence'] = self.get_threat_intelligence(target)

            if kwargs.get('include_historical', True):
                data['historical'] = self.get_historical_data(target)

            # Add reverse DNS
            data['reverse_dns'] = reverse_dns(target)

            return self._create_result(target=target, data=data)

        except Exception as e:
            return self._handle_error(target, e)

    def get_geolocation(self, ip: str) -> Dict[str, Any]:
        """
        Get geolocation information for IP address

        Args:
            ip: IP address

        Returns:
            Geolocation data
        """
        geolocation = {}

        # Method 1: MaxMind GeoIP2 (if database available)
        if self.maxmind_db_path and os.path.exists(self.maxmind_db_path):
            try:
                with geoip2.database.Reader(self.maxmind_db_path) as reader:
                    response = reader.city(ip)
                    geolocation['maxmind'] = {
                        'country': response.country.name,
                        'country_code': response.country.iso_code,
                        'city': response.city.name,
                        'postal_code': response.postal.code,
                        'latitude': response.location.latitude,
                        'longitude': response.location.longitude,
                        'timezone': response.location.time_zone,
                        'accuracy_radius': response.location.accuracy_radius
                    }
            except Exception as e:
                self.logger.warning(f"MaxMind lookup failed: {str(e)}")
                geolocation['maxmind'] = {}

        # Method 2: IPInfo.io API
        if self.ipinfo_api_key:
            try:
                url = f"https://ipinfo.io/{ip}/json?token={self.ipinfo_api_key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    geolocation['ipinfo'] = data
            except Exception as e:
                self.logger.warning(f"IPInfo lookup failed: {str(e)}")
                geolocation['ipinfo'] = {}

        # Method 3: Free IP-API.com
        try:
            url = f"http://ip-api.com/json/{ip}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    geolocation['ip_api'] = {
                        'country': data.get('country'),
                        'country_code': data.get('countryCode'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'zip': data.get('zip'),
                        'latitude': data.get('lat'),
                        'longitude': data.get('lon'),
                        'timezone': data.get('timezone'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'as': data.get('as')
                    }
        except Exception as e:
            self.logger.warning(f"IP-API lookup failed: {str(e)}")
            geolocation['ip_api'] = {}

        return geolocation

    def get_asn_info(self, ip: str) -> Dict[str, Any]:
        """
        Get ASN (Autonomous System Number) information

        Args:
            ip: IP address

        Returns:
            ASN information
        """
        try:
            obj = IPWhois(ip)
            results = obj.lookup_rdap()

            return {
                'asn': results.get('asn'),
                'asn_cidr': results.get('asn_cidr'),
                'asn_country_code': results.get('asn_country_code'),
                'asn_description': results.get('asn_description'),
                'asn_registry': results.get('asn_registry'),
                'network': {
                    'cidr': results.get('network', {}).get('cidr'),
                    'name': results.get('network', {}).get('name'),
                    'handle': results.get('network', {}).get('handle'),
                    'country': results.get('network', {}).get('country'),
                },
                'objects': results.get('objects', {})
            }

        except Exception as e:
            self.logger.warning(f"ASN lookup failed for {ip}: {str(e)}")
            return {'error': str(e)}

    def scan_ports(self, ip: str, port_range: str = "1-1000") -> Dict[str, Any]:
        """
        Scan ports on target IP

        Args:
            ip: IP address
            port_range: Port range to scan (e.g., "1-1000", "22,80,443")

        Returns:
            Port scan results
        """
        try:
            nm = nmap.PortScanner()
            nm.scan(ip, port_range, arguments='-sT')

            open_ports = []
            for proto in nm[ip].all_protocols():
                ports = nm[ip][proto].keys()
                for port in ports:
                    port_info = nm[ip][proto][port]
                    if port_info['state'] == 'open':
                        open_ports.append({
                            'port': port,
                            'protocol': proto,
                            'state': port_info['state'],
                            'name': port_info.get('name', ''),
                            'product': port_info.get('product', ''),
                            'version': port_info.get('version', ''),
                            'extrainfo': port_info.get('extrainfo', '')
                        })

            return {
                'scan_range': port_range,
                'total_open_ports': len(open_ports),
                'open_ports': open_ports,
                'scan_info': nm.scaninfo()
            }

        except Exception as e:
            self.logger.warning(f"Port scan failed for {ip}: {str(e)}")
            return {'error': str(e)}

    def detect_services(self, ip: str) -> Dict[str, Any]:
        """
        Detect services running on IP

        Args:
            ip: IP address

        Returns:
            Service detection results
        """
        services = {}

        # Check common services
        common_ports = {
            21: 'FTP',
            22: 'SSH',
            23: 'Telnet',
            25: 'SMTP',
            53: 'DNS',
            80: 'HTTP',
            110: 'POP3',
            143: 'IMAP',
            443: 'HTTPS',
            445: 'SMB',
            3306: 'MySQL',
            3389: 'RDP',
            5432: 'PostgreSQL',
            5900: 'VNC',
            6379: 'Redis',
            8080: 'HTTP-Proxy',
            8443: 'HTTPS-Alt',
            27017: 'MongoDB'
        }

        for port, service_name in common_ports.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                if result == 0:
                    services[port] = {
                        'name': service_name,
                        'status': 'open'
                    }

                    # Try to grab banner
                    try:
                        sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
                        banner = sock.recv(1024).decode('utf-8', errors='ignore')
                        services[port]['banner'] = banner[:200]
                    except:
                        pass

                sock.close()
            except:
                pass

        # Shodan API for comprehensive service detection
        if self.shodan_api_key:
            try:
                import shodan
                api = shodan.Shodan(self.shodan_api_key)
                host = api.host(ip)

                services['shodan'] = {
                    'hostnames': host.get('hostnames', []),
                    'ports': host.get('ports', []),
                    'vulns': host.get('vulns', []),
                    'tags': host.get('tags', []),
                    'services': []
                }

                for service in host.get('data', []):
                    services['shodan']['services'].append({
                        'port': service.get('port'),
                        'transport': service.get('transport'),
                        'product': service.get('product'),
                        'version': service.get('version'),
                        'data': service.get('data', '')[:200]
                    })

            except Exception as e:
                self.logger.warning(f"Shodan lookup failed: {str(e)}")
                services['shodan'] = {}

        return services

    def get_threat_intelligence(self, ip: str) -> Dict[str, Any]:
        """
        Get threat intelligence for IP address

        Args:
            ip: IP address

        Returns:
            Threat intelligence data
        """
        threat_intel = {}

        # AbuseIPDB
        if self.abuseipdb_api_key:
            try:
                headers = {
                    'Key': self.abuseipdb_api_key,
                    'Accept': 'application/json'
                }
                params = {
                    'ipAddress': ip,
                    'maxAgeInDays': 90,
                    'verbose': ''
                }
                url = 'https://api.abuseipdb.com/api/v2/check'
                response = requests.get(url, headers=headers, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json().get('data', {})
                    threat_intel['abuseipdb'] = {
                        'abuse_confidence_score': data.get('abuseConfidenceScore'),
                        'total_reports': data.get('totalReports'),
                        'num_distinct_users': data.get('numDistinctUsers'),
                        'is_public': data.get('isPublic'),
                        'is_whitelisted': data.get('isWhitelisted'),
                        'country_code': data.get('countryCode'),
                        'usage_type': data.get('usageType'),
                        'isp': data.get('isp'),
                        'domain': data.get('domain')
                    }
            except Exception as e:
                self.logger.warning(f"AbuseIPDB lookup failed: {str(e)}")
                threat_intel['abuseipdb'] = {}

        # VirusTotal
        if self.virustotal_api_key:
            try:
                headers = {'x-apikey': self.virustotal_api_key}
                url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
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
                        'last_analysis_date': attributes.get('last_analysis_date', '')
                    }
            except Exception as e:
                self.logger.warning(f"VirusTotal lookup failed: {str(e)}")
                threat_intel['virustotal'] = {}

        return threat_intel

    def get_historical_data(self, ip: str) -> Dict[str, Any]:
        """
        Get historical data for IP address

        Args:
            ip: IP address

        Returns:
            Historical data
        """
        historical = {}

        # Censys historical data
        if self.censys_api_id and self.censys_api_secret:
            try:
                from censys.search import CensysHosts
                h = CensysHosts(api_id=self.censys_api_id, api_secret=self.censys_api_secret)
                host = h.view(ip)

                historical['censys'] = {
                    'autonomous_system': host.get('autonomous_system', {}),
                    'services': len(host.get('services', [])),
                    'last_updated': host.get('last_updated_at', ''),
                    'protocols': [s.get('service_name') for s in host.get('services', [])]
                }
            except Exception as e:
                self.logger.warning(f"Censys lookup failed: {str(e)}")
                historical['censys'] = {}

        return historical
