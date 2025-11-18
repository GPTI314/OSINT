"""
IP address intelligence collector for geolocation, reputation, and port scanning.
"""
from typing import Dict, Any
import socket
import ipaddress
from datetime import datetime
import logging

from .base_collector import BaseCollector

logger = logging.getLogger(__name__)


class IPCollector(BaseCollector):
    """Collector for IP address intelligence gathering."""

    async def collect(self, target: str, **kwargs) -> Dict[str, Any]:
        """
        Collect intelligence on an IP address.

        Args:
            target: IP address
            **kwargs: Additional parameters (port_scan, shodan_api_key, etc.)

        Returns:
            Dict containing IP intelligence
        """
        ip = target.strip()

        # Validate IP address
        try:
            ip_obj = ipaddress.ip_address(ip)
        except ValueError:
            self.add_error("validation", f"Invalid IP address: {ip}")
            return self._build_response(target)

        # Collect basic IP info
        await self._collect_basic_info(str(ip_obj))

        # Collect reverse DNS
        await self._collect_reverse_dns(str(ip_obj))

        # Collect geolocation (if API key available)
        if kwargs.get("geoip_enabled", False):
            await self._collect_geolocation(str(ip_obj))

        # Collect Shodan data (if API key available)
        if kwargs.get("shodan_api_key"):
            await self._collect_shodan(str(ip_obj), kwargs["shodan_api_key"])

        # Port scanning (if enabled)
        if kwargs.get("port_scan", False):
            await self._scan_ports(str(ip_obj), kwargs.get("ports", [80, 443, 22, 21, 25]))

        return self._build_response(target)

    def _build_response(self, target: str) -> Dict[str, Any]:
        """Build response dictionary."""
        return {
            "target": target,
            "target_type": "ip_address",
            "results": self.results,
            "errors": self.errors,
            "summary": self.get_summary(),
            "collected_at": datetime.utcnow().isoformat()
        }

    async def _collect_basic_info(self, ip: str):
        """Collect basic IP information."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            info = {
                "ip": ip,
                "version": ip_obj.version,
                "is_private": ip_obj.is_private,
                "is_global": ip_obj.is_global,
                "is_multicast": ip_obj.is_multicast,
                "is_loopback": ip_obj.is_loopback
            }
            self.add_result("basic_info", info, confidence=1.0)
        except Exception as e:
            self.add_error("basic_info", str(e))

    async def _collect_reverse_dns(self, ip: str):
        """Collect reverse DNS (PTR) record."""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            self.add_result("reverse_dns", {
                "hostname": hostname,
                "ip": ip
            }, confidence=0.95)
        except socket.herror:
            self.add_result("reverse_dns", {
                "hostname": None,
                "message": "No reverse DNS record found"
            }, confidence=0.5)
        except Exception as e:
            self.add_error("reverse_dns", str(e))

    async def _collect_geolocation(self, ip: str):
        """
        Collect geolocation data.

        Note: This requires GeoIP2 database or API. This is a placeholder.
        """
        # Placeholder for GeoIP integration
        self.add_result("geolocation", {
            "ip": ip,
            "message": "GeoIP integration required"
        }, confidence=0.0)

    async def _collect_shodan(self, ip: str, api_key: str):
        """
        Collect Shodan intelligence.

        Note: This requires Shodan API key and library integration.
        """
        try:
            # Placeholder for Shodan integration
            # import shodan
            # api = shodan.Shodan(api_key)
            # host = api.host(ip)
            self.add_result("shodan", {
                "ip": ip,
                "message": "Shodan API integration required"
            }, confidence=0.0)
        except Exception as e:
            self.add_error("shodan", str(e))

    async def _scan_ports(self, ip: str, ports: list):
        """
        Scan ports on the target IP.

        Args:
            ip: Target IP address
            ports: List of ports to scan
        """
        open_ports = []

        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            try:
                result = sock.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
            except Exception as e:
                logger.debug(f"Error scanning port {port}: {e}")
            finally:
                sock.close()

        self.add_result("port_scan", {
            "ip": ip,
            "scanned_ports": ports,
            "open_ports": open_ports,
            "count": len(open_ports)
        }, confidence=0.9)
