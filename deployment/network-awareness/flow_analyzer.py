#!/usr/bin/env python3
"""
Network Flow Analysis and Visibility System
Comprehensive network awareness for OSINT platform
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from collections import defaultdict
import json

import aioredis
from elasticsearch import AsyncElasticsearch
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NetworkFlow:
    """Network flow data structure"""
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    timestamp: datetime
    duration: float
    application: Optional[str] = None
    device_id: Optional[str] = None


@dataclass
class NetworkDevice:
    """Network device information"""
    ip_address: str
    mac_address: str
    hostname: Optional[str]
    device_type: Optional[str]
    vendor: Optional[str]
    last_seen: datetime
    first_seen: datetime
    open_ports: List[int]
    services: Dict[int, str]


class NetworkFlowAnalyzer:
    """
    Complete network visibility and flow analysis system

    Features:
    - NetFlow/sFlow collection and analysis
    - Device discovery and fingerprinting
    - Application protocol detection
    - Bandwidth monitoring per device/service
    - Security event correlation
    - DNS query analysis
    - Network topology mapping
    - Anomaly detection
    """

    def __init__(
        self,
        redis_url: str,
        elasticsearch_url: str,
        pihole_api: str = None,
        ntopng_api: str = None
    ):
        self.redis_url = redis_url
        self.elasticsearch_url = elasticsearch_url
        self.pihole_api = pihole_api
        self.ntopng_api = ntopng_api

        self.redis: Optional[aioredis.Redis] = None
        self.es: Optional[AsyncElasticsearch] = None

        # In-memory caches
        self.devices: Dict[str, NetworkDevice] = {}
        self.flow_cache: List[NetworkFlow] = []
        self.anomaly_scores: Dict[str, float] = defaultdict(float)

    async def initialize(self):
        """Initialize connections"""
        self.redis = await aioredis.from_url(self.redis_url)
        self.es = AsyncElasticsearch([self.elasticsearch_url])

        await self._create_elasticsearch_indices()
        logger.info("Network Flow Analyzer initialized")

    async def _create_elasticsearch_indices(self):
        """Create Elasticsearch indices for network data"""

        # Network flows index
        flow_mapping = {
            "mappings": {
                "properties": {
                    "src_ip": {"type": "ip"},
                    "dst_ip": {"type": "ip"},
                    "src_port": {"type": "integer"},
                    "dst_port": {"type": "integer"},
                    "protocol": {"type": "keyword"},
                    "bytes_sent": {"type": "long"},
                    "bytes_recv": {"type": "long"},
                    "packets_sent": {"type": "long"},
                    "packets_recv": {"type": "long"},
                    "timestamp": {"type": "date"},
                    "duration": {"type": "float"},
                    "application": {"type": "keyword"},
                    "device_id": {"type": "keyword"}
                }
            }
        }

        # Network devices index
        device_mapping = {
            "mappings": {
                "properties": {
                    "ip_address": {"type": "ip"},
                    "mac_address": {"type": "keyword"},
                    "hostname": {"type": "keyword"},
                    "device_type": {"type": "keyword"},
                    "vendor": {"type": "keyword"},
                    "last_seen": {"type": "date"},
                    "first_seen": {"type": "date"},
                    "open_ports": {"type": "integer"},
                    "services": {"type": "object"}
                }
            }
        }

        # DNS queries index
        dns_mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "client_ip": {"type": "ip"},
                    "query": {"type": "keyword"},
                    "query_type": {"type": "keyword"},
                    "response": {"type": "ip"},
                    "blocked": {"type": "boolean"},
                    "response_time": {"type": "float"}
                }
            }
        }

        # Security events index
        security_mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "event_type": {"type": "keyword"},
                    "severity": {"type": "keyword"},
                    "src_ip": {"type": "ip"},
                    "dst_ip": {"type": "ip"},
                    "description": {"type": "text"},
                    "signature_id": {"type": "integer"},
                    "category": {"type": "keyword"}
                }
            }
        }

        indices = {
            "network-flows": flow_mapping,
            "network-devices": device_mapping,
            "dns-queries": dns_mapping,
            "security-events": security_mapping
        }

        for index_name, mapping in indices.items():
            if not await self.es.indices.exists(index=index_name):
                await self.es.indices.create(index=index_name, body=mapping)
                logger.info(f"Created Elasticsearch index: {index_name}")

    async def collect_netflow_data(self, flow_data: Dict):
        """
        Collect NetFlow/sFlow data from network devices

        Args:
            flow_data: NetFlow/sFlow data packet
        """
        try:
            flow = NetworkFlow(
                src_ip=flow_data.get('src_ip'),
                dst_ip=flow_data.get('dst_ip'),
                src_port=flow_data.get('src_port'),
                dst_port=flow_data.get('dst_port'),
                protocol=flow_data.get('protocol', 'unknown'),
                bytes_sent=flow_data.get('bytes', 0),
                bytes_recv=flow_data.get('bytes_recv', 0),
                packets_sent=flow_data.get('packets', 0),
                packets_recv=flow_data.get('packets_recv', 0),
                timestamp=datetime.now(),
                duration=flow_data.get('duration', 0),
                application=await self._detect_application(
                    flow_data.get('dst_port'),
                    flow_data.get('protocol')
                )
            )

            # Store in Elasticsearch
            await self.es.index(
                index="network-flows",
                body=flow.__dict__
            )

            # Update bandwidth metrics
            await self._update_bandwidth_metrics(flow)

            # Check for anomalies
            await self._check_flow_anomalies(flow)

        except Exception as e:
            logger.error(f"Error collecting NetFlow data: {e}")

    async def discover_devices(self, network_range: str = "10.0.0.0/24"):
        """
        Discover and identify network devices

        Args:
            network_range: Network range to scan (CIDR notation)
        """
        logger.info(f"Starting device discovery on {network_range}")

        # This would integrate with nmap or similar tool
        # For now, placeholder implementation

        discovered_devices = await self._scan_network(network_range)

        for device_info in discovered_devices:
            device = NetworkDevice(
                ip_address=device_info['ip'],
                mac_address=device_info['mac'],
                hostname=device_info.get('hostname'),
                device_type=await self._fingerprint_device(device_info),
                vendor=await self._lookup_vendor(device_info['mac']),
                last_seen=datetime.now(),
                first_seen=device_info.get('first_seen', datetime.now()),
                open_ports=device_info.get('open_ports', []),
                services=device_info.get('services', {})
            )

            self.devices[device.ip_address] = device

            # Store in Elasticsearch
            await self.es.index(
                index="network-devices",
                body=device.__dict__
            )

        logger.info(f"Discovered {len(discovered_devices)} devices")

    async def _detect_application(self, port: int, protocol: str) -> str:
        """
        Detect application protocol from port and protocol

        Args:
            port: Destination port
            protocol: Transport protocol (TCP/UDP)

        Returns:
            Application name
        """
        # Common port mappings
        port_map = {
            20: "FTP-DATA",
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            465: "SMTPS",
            587: "SMTP-Submission",
            993: "IMAPS",
            995: "POP3S",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            8080: "HTTP-Proxy",
            8443: "HTTPS-Alt",
            9200: "Elasticsearch",
            27017: "MongoDB"
        }

        return port_map.get(port, f"Unknown-{port}")

    async def _scan_network(self, network_range: str) -> List[Dict]:
        """
        Scan network range for devices

        Args:
            network_range: CIDR network range

        Returns:
            List of discovered devices
        """
        # Placeholder - would integrate with nmap or similar
        # Example implementation using python-nmap

        discovered = []

        # This would call actual network scanner
        # For demonstration, returning empty list

        return discovered

    async def _fingerprint_device(self, device_info: Dict) -> str:
        """
        Fingerprint device type based on characteristics

        Args:
            device_info: Device information

        Returns:
            Device type classification
        """
        # Device fingerprinting logic
        open_ports = set(device_info.get('open_ports', []))

        # Common device patterns
        if {22, 8000, 9100} & open_ports:
            return "raspberry-pi"
        elif {22, 5432} & open_ports:
            return "database-server"
        elif {80, 443, 8080} & open_ports:
            return "web-server"
        elif {53} & open_ports:
            return "dns-server"
        else:
            return "unknown"

    async def _lookup_vendor(self, mac_address: str) -> Optional[str]:
        """
        Lookup vendor from MAC address OUI

        Args:
            mac_address: MAC address

        Returns:
            Vendor name
        """
        # Would use MAC OUI lookup database
        # Placeholder implementation

        oui = mac_address[:8].upper().replace(":", "")

        # Example OUI mappings
        oui_map = {
            "B827EB": "Raspberry Pi Foundation",
            "DCB427": "Raspberry Pi Trading",
            "E45F01": "Raspberry Pi Foundation",
        }

        return oui_map.get(oui, "Unknown")

    async def analyze_dns_queries(self, query_data: Dict):
        """
        Analyze DNS queries for intelligence and threats

        Args:
            query_data: DNS query information from Pi-hole
        """
        try:
            dns_record = {
                "timestamp": datetime.now(),
                "client_ip": query_data.get('client'),
                "query": query_data.get('domain'),
                "query_type": query_data.get('type', 'A'),
                "response": query_data.get('response'),
                "blocked": query_data.get('status') == 'blocked',
                "response_time": query_data.get('response_time', 0)
            }

            await self.es.index(
                index="dns-queries",
                body=dns_record
            )

            # Check for suspicious domains
            await self._check_suspicious_domain(dns_record['query'])

        except Exception as e:
            logger.error(f"Error analyzing DNS query: {e}")

    async def _check_suspicious_domain(self, domain: str):
        """
        Check if domain is suspicious

        Args:
            domain: Domain name to check
        """
        # Suspicious patterns
        suspicious_patterns = [
            'dga-',  # Domain generation algorithm
            '.tk',   # Free TLD often used in malware
            '.ml',
            'tor2web',
            'onion.to',
        ]

        for pattern in suspicious_patterns:
            if pattern in domain.lower():
                await self._create_security_event(
                    event_type="suspicious_domain",
                    severity="medium",
                    description=f"Suspicious domain queried: {domain}"
                )

    async def _create_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        **kwargs
    ):
        """
        Create security event

        Args:
            event_type: Type of security event
            severity: Event severity (low/medium/high/critical)
            description: Event description
        """
        event = {
            "timestamp": datetime.now(),
            "event_type": event_type,
            "severity": severity,
            "description": description,
            **kwargs
        }

        await self.es.index(
            index="security-events",
            body=event
        )

        # Send alert if severity is high or critical
        if severity in ['high', 'critical']:
            await self._send_alert(event)

    async def _send_alert(self, event: Dict):
        """
        Send alert notification

        Args:
            event: Security event
        """
        # Would integrate with alerting system (Slack, email, etc.)
        logger.warning(f"SECURITY ALERT: {event['description']}")

        # Store in Redis for real-time access
        await self.redis.lpush(
            "security_alerts",
            json.dumps(event, default=str)
        )

    async def _update_bandwidth_metrics(self, flow: NetworkFlow):
        """
        Update bandwidth metrics for devices

        Args:
            flow: Network flow
        """
        # Update bandwidth counters in Redis
        pipe = self.redis.pipeline()

        # Per-device bandwidth
        pipe.hincrby(
            f"bandwidth:device:{flow.src_ip}",
            "bytes_sent",
            flow.bytes_sent
        )
        pipe.hincrby(
            f"bandwidth:device:{flow.dst_ip}",
            "bytes_recv",
            flow.bytes_recv
        )

        # Per-application bandwidth
        if flow.application:
            pipe.hincrby(
                f"bandwidth:app:{flow.application}",
                "bytes_total",
                flow.bytes_sent + flow.bytes_recv
            )

        await pipe.execute()

    async def _check_flow_anomalies(self, flow: NetworkFlow):
        """
        Check for anomalous network flows

        Args:
            flow: Network flow to check
        """
        # Anomaly detection logic
        anomaly_score = 0.0

        # Check for unusual ports
        if flow.dst_port > 49152:  # Ephemeral port range
            anomaly_score += 1.0

        # Check for large data transfers
        if flow.bytes_sent > 100_000_000:  # 100MB
            anomaly_score += 2.0

        # Check for unusual protocols
        if flow.protocol not in ['TCP', 'UDP', 'ICMP']:
            anomaly_score += 1.5

        # Check for connections to unusual destinations
        # (would integrate with threat intelligence)

        if anomaly_score >= 5.0:
            await self._create_security_event(
                event_type="network_anomaly",
                severity="medium",
                src_ip=flow.src_ip,
                dst_ip=flow.dst_ip,
                description=f"Anomalous network flow detected (score: {anomaly_score})"
            )

    async def get_network_statistics(self) -> Dict:
        """
        Get comprehensive network statistics

        Returns:
            Network statistics dictionary
        """
        stats = {
            "total_devices": len(self.devices),
            "total_flows": await self.es.count(index="network-flows"),
            "dns_queries_24h": await self._count_dns_queries_24h(),
            "security_events_24h": await self._count_security_events_24h(),
            "top_talkers": await self._get_top_talkers(),
            "top_applications": await self._get_top_applications(),
            "bandwidth_usage": await self._get_bandwidth_usage()
        }

        return stats

    async def _count_dns_queries_24h(self) -> int:
        """Count DNS queries in last 24 hours"""
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": "now-24h"
                    }
                }
            }
        }

        result = await self.es.count(index="dns-queries", body=query)
        return result['count']

    async def _count_security_events_24h(self) -> int:
        """Count security events in last 24 hours"""
        query = {
            "query": {
                "range": {
                    "timestamp": {
                        "gte": "now-24h"
                    }
                }
            }
        }

        result = await self.es.count(index="security-events", body=query)
        return result['count']

    async def _get_top_talkers(self, limit: int = 10) -> List[Dict]:
        """Get top bandwidth consumers"""
        query = {
            "size": 0,
            "aggs": {
                "top_sources": {
                    "terms": {
                        "field": "src_ip",
                        "size": limit,
                        "order": {"total_bytes": "desc"}
                    },
                    "aggs": {
                        "total_bytes": {
                            "sum": {"field": "bytes_sent"}
                        }
                    }
                }
            }
        }

        result = await self.es.search(index="network-flows", body=query)

        return [
            {
                "ip": bucket['key'],
                "bytes": bucket['total_bytes']['value']
            }
            for bucket in result['aggregations']['top_sources']['buckets']
        ]

    async def _get_top_applications(self, limit: int = 10) -> List[Dict]:
        """Get top applications by bandwidth"""
        query = {
            "size": 0,
            "aggs": {
                "top_apps": {
                    "terms": {
                        "field": "application",
                        "size": limit,
                        "order": {"total_bytes": "desc"}
                    },
                    "aggs": {
                        "total_bytes": {
                            "sum": {
                                "script": "doc['bytes_sent'].value + doc['bytes_recv'].value"
                            }
                        }
                    }
                }
            }
        }

        result = await self.es.search(index="network-flows", body=query)

        return [
            {
                "application": bucket['key'],
                "bytes": bucket['total_bytes']['value']
            }
            for bucket in result['aggregations']['top_apps']['buckets']
        ]

    async def _get_bandwidth_usage(self) -> Dict:
        """Get total bandwidth usage"""
        query = {
            "size": 0,
            "aggs": {
                "total_sent": {"sum": {"field": "bytes_sent"}},
                "total_recv": {"sum": {"field": "bytes_recv"}}
            }
        }

        result = await self.es.search(index="network-flows", body=query)

        return {
            "bytes_sent": result['aggregations']['total_sent']['value'],
            "bytes_recv": result['aggregations']['total_recv']['value'],
            "bytes_total": (
                result['aggregations']['total_sent']['value'] +
                result['aggregations']['total_recv']['value']
            )
        }

    async def run_continuous_monitoring(self):
        """Run continuous network monitoring"""
        logger.info("Starting continuous network monitoring...")

        while True:
            try:
                # Periodic device discovery
                await self.discover_devices()

                # Collect statistics
                stats = await self.get_network_statistics()
                logger.info(f"Network stats: {stats}")

                # Sleep before next iteration
                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)


async def main():
    """Main entry point"""
    analyzer = NetworkFlowAnalyzer(
        redis_url="redis://:changeme@10.0.0.13:6379/0",
        elasticsearch_url="http://10.0.0.14:9200",
        pihole_api="http://10.0.0.12/admin/api.php",
        ntopng_api="http://10.0.0.12:3000"
    )

    await analyzer.initialize()
    await analyzer.run_continuous_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
