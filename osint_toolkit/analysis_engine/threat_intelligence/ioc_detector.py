"""
IOC Detector - Detects Indicators of Compromise in data
"""

import re
import hashlib
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class IOCType(Enum):
    """Types of Indicators of Compromise"""
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    FILE_HASH_MD5 = "file_hash_md5"
    FILE_HASH_SHA1 = "file_hash_sha1"
    FILE_HASH_SHA256 = "file_hash_sha256"
    CRYPTOCURRENCY = "cryptocurrency"
    CVE = "cve"
    MUTEX = "mutex"
    REGISTRY_KEY = "registry_key"
    FILE_PATH = "file_path"
    USER_AGENT = "user_agent"


@dataclass
class IOC:
    """Represents an Indicator of Compromise"""
    ioc_type: IOCType
    value: str
    source: str
    confidence: float
    first_seen: datetime
    last_seen: datetime
    context: str = ""
    metadata: Dict = None
    threat_level: str = "unknown"  # low, medium, high, critical

    def to_dict(self) -> Dict:
        return {
            'type': self.ioc_type.value,
            'value': self.value,
            'source': self.source,
            'confidence': self.confidence,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'context': self.context,
            'metadata': self.metadata or {},
            'threat_level': self.threat_level
        }


class IOCDetector:
    """
    Detects various Indicators of Compromise (IOCs) in data:
    - IP addresses
    - Domains
    - URLs
    - Email addresses
    - File hashes
    - CVEs
    - Cryptocurrency addresses
    - And more...
    """

    def __init__(self):
        self.iocs: Dict[str, IOC] = {}
        self.known_malicious: Set[str] = set()
        self.whitelist: Set[str] = set()
        self.detection_patterns = self._initialize_patterns()

    def _initialize_patterns(self) -> Dict[IOCType, List[str]]:
        """Initialize regex patterns for IOC detection"""
        return {
            IOCType.IP_ADDRESS: [
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            ],
            IOCType.DOMAIN: [
                r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
            ],
            IOCType.URL: [
                r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
                r'ftp://[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
            ],
            IOCType.EMAIL: [
                r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
            ],
            IOCType.FILE_HASH_MD5: [
                r'\b[a-fA-F0-9]{32}\b',
            ],
            IOCType.FILE_HASH_SHA1: [
                r'\b[a-fA-F0-9]{40}\b',
            ],
            IOCType.FILE_HASH_SHA256: [
                r'\b[a-fA-F0-9]{64}\b',
            ],
            IOCType.CRYPTOCURRENCY: [
                r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',  # Bitcoin
                r'\b0x[a-fA-F0-9]{40}\b',  # Ethereum
                r'\b[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}\b',  # Litecoin
            ],
            IOCType.CVE: [
                r'CVE-\d{4}-\d{4,7}',
            ],
            IOCType.REGISTRY_KEY: [
                r'HKEY_[A-Z_]+\\[\\a-zA-Z0-9_\-\.]+',
            ],
            IOCType.FILE_PATH: [
                r'[A-Za-z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]*',  # Windows
                r'/(?:[^/\0]+/)*[^/\0]*',  # Unix (simplified)
            ],
        }

    def add_known_malicious(self, ioc_value: str, ioc_type: IOCType = None) -> None:
        """Add a known malicious IOC to the database"""
        self.known_malicious.add(ioc_value.lower())

    def add_to_whitelist(self, value: str) -> None:
        """Add a value to the whitelist (won't be flagged as IOC)"""
        self.whitelist.add(value.lower())

    def is_whitelisted(self, value: str) -> bool:
        """Check if a value is whitelisted"""
        return value.lower() in self.whitelist

    def is_known_malicious(self, value: str) -> bool:
        """Check if a value is known to be malicious"""
        return value.lower() in self.known_malicious

    def extract_iocs(self, text: str, source: str = "unknown",
                    context: str = "") -> List[IOC]:
        """Extract all IOCs from text"""
        iocs = []
        timestamp = datetime.now()

        for ioc_type, patterns in self.detection_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)

                for match in matches:
                    value = match.group(0)

                    # Skip whitelisted values
                    if self.is_whitelisted(value):
                        continue

                    # Determine confidence based on context and known databases
                    confidence = 0.5  # Base confidence

                    if self.is_known_malicious(value):
                        confidence = 1.0
                        threat_level = "high"
                    else:
                        threat_level = "unknown"

                    # Additional validation for specific types
                    if ioc_type == IOCType.IP_ADDRESS:
                        if not self._validate_ip(value):
                            continue
                    elif ioc_type == IOCType.DOMAIN:
                        if not self._validate_domain(value):
                            continue

                    # Create IOC
                    ioc_id = hashlib.sha256(f"{ioc_type.value}:{value}".encode()).hexdigest()[:16]

                    if ioc_id in self.iocs:
                        # Update existing IOC
                        existing_ioc = self.iocs[ioc_id]
                        existing_ioc.last_seen = timestamp
                        existing_ioc.confidence = max(existing_ioc.confidence, confidence)
                    else:
                        # Create new IOC
                        ioc = IOC(
                            ioc_type=ioc_type,
                            value=value,
                            source=source,
                            confidence=confidence,
                            first_seen=timestamp,
                            last_seen=timestamp,
                            context=context,
                            metadata={'position': match.span()},
                            threat_level=threat_level
                        )
                        self.iocs[ioc_id] = ioc
                        iocs.append(ioc)

        return iocs

    def _validate_ip(self, ip: str) -> bool:
        """Validate IP address format and check for private ranges"""
        parts = ip.split('.')
        if len(parts) != 4:
            return False

        try:
            octets = [int(p) for p in parts]
            if not all(0 <= o <= 255 for o in octets):
                return False

            # Filter out common private/reserved ranges (optional)
            # Uncomment to exclude private IPs
            # if octets[0] == 10:  # 10.0.0.0/8
            #     return False
            # if octets[0] == 172 and 16 <= octets[1] <= 31:  # 172.16.0.0/12
            #     return False
            # if octets[0] == 192 and octets[1] == 168:  # 192.168.0.0/16
            #     return False
            # if octets[0] == 127:  # 127.0.0.0/8 (localhost)
            #     return False

            return True
        except ValueError:
            return False

    def _validate_domain(self, domain: str) -> bool:
        """Validate domain format"""
        # Basic domain validation
        if len(domain) > 253:
            return False

        # Check for common non-domain patterns
        if domain.endswith('.local') or domain.endswith('.localhost'):
            return False

        # Must have at least one dot
        if '.' not in domain:
            return False

        # Basic TLD check (at least 2 chars)
        tld = domain.split('.')[-1]
        if len(tld) < 2:
            return False

        return True

    def detect_ioc_type(self, value: str) -> Optional[IOCType]:
        """Detect the type of an IOC"""
        for ioc_type, patterns in self.detection_patterns.items():
            for pattern in patterns:
                if re.fullmatch(pattern, value, re.IGNORECASE):
                    return ioc_type
        return None

    def add_ioc(self, ioc: IOC) -> str:
        """Manually add an IOC"""
        ioc_id = hashlib.sha256(f"{ioc.ioc_type.value}:{ioc.value}".encode()).hexdigest()[:16]
        self.iocs[ioc_id] = ioc
        return ioc_id

    def get_iocs_by_type(self, ioc_type: IOCType) -> List[IOC]:
        """Get all IOCs of a specific type"""
        return [ioc for ioc in self.iocs.values() if ioc.ioc_type == ioc_type]

    def get_iocs_by_threat_level(self, threat_level: str) -> List[IOC]:
        """Get IOCs by threat level"""
        return [ioc for ioc in self.iocs.values() if ioc.threat_level == threat_level]

    def get_high_confidence_iocs(self, min_confidence: float = 0.7) -> List[IOC]:
        """Get IOCs with confidence above threshold"""
        return [ioc for ioc in self.iocs.values() if ioc.confidence >= min_confidence]

    def search_ioc(self, value: str) -> List[IOC]:
        """Search for IOCs matching a value"""
        results = []
        value_lower = value.lower()

        for ioc in self.iocs.values():
            if value_lower in ioc.value.lower():
                results.append(ioc)

        return results

    def get_ioc_statistics(self) -> Dict:
        """Get statistics about detected IOCs"""
        stats = {
            'total_iocs': len(self.iocs),
            'by_type': {},
            'by_threat_level': {},
            'high_confidence_count': 0,
            'known_malicious_count': len(self.known_malicious),
            'whitelisted_count': len(self.whitelist)
        }

        for ioc in self.iocs.values():
            # Count by type
            type_name = ioc.ioc_type.value
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1

            # Count by threat level
            stats['by_threat_level'][ioc.threat_level] = \
                stats['by_threat_level'].get(ioc.threat_level, 0) + 1

            # High confidence count
            if ioc.confidence >= 0.7:
                stats['high_confidence_count'] += 1

        return stats

    def export_iocs(self, format: str = "dict") -> List[Dict]:
        """Export IOCs in specified format"""
        if format == "dict":
            return [ioc.to_dict() for ioc in self.iocs.values()]
        elif format == "stix":
            # STIX format (simplified)
            return self._export_stix()
        elif format == "csv":
            return self._export_csv()
        else:
            return [ioc.to_dict() for ioc in self.iocs.values()]

    def _export_stix(self) -> List[Dict]:
        """Export IOCs in STIX-like format"""
        stix_objects = []

        for ioc in self.iocs.values():
            stix_obj = {
                "type": "indicator",
                "id": f"indicator--{hashlib.sha256(ioc.value.encode()).hexdigest()}",
                "created": ioc.first_seen.isoformat(),
                "modified": ioc.last_seen.isoformat(),
                "pattern": f"[{ioc.ioc_type.value}:value = '{ioc.value}']",
                "pattern_type": "stix",
                "valid_from": ioc.first_seen.isoformat(),
                "confidence": int(ioc.confidence * 100),
                "labels": [ioc.threat_level, ioc.ioc_type.value]
            }
            stix_objects.append(stix_obj)

        return stix_objects

    def _export_csv(self) -> List[Dict]:
        """Export IOCs in CSV-ready format"""
        csv_data = []

        for ioc in self.iocs.values():
            csv_data.append({
                'type': ioc.ioc_type.value,
                'value': ioc.value,
                'threat_level': ioc.threat_level,
                'confidence': ioc.confidence,
                'first_seen': ioc.first_seen.isoformat(),
                'last_seen': ioc.last_seen.isoformat(),
                'source': ioc.source
            })

        return csv_data

    def bulk_import_iocs(self, ioc_list: List[Dict]) -> int:
        """Bulk import IOCs from a list"""
        imported = 0

        for ioc_data in ioc_list:
            try:
                ioc_type = IOCType(ioc_data['type'])
                ioc = IOC(
                    ioc_type=ioc_type,
                    value=ioc_data['value'],
                    source=ioc_data.get('source', 'import'),
                    confidence=ioc_data.get('confidence', 0.5),
                    first_seen=datetime.fromisoformat(ioc_data.get('first_seen', datetime.now().isoformat())),
                    last_seen=datetime.fromisoformat(ioc_data.get('last_seen', datetime.now().isoformat())),
                    context=ioc_data.get('context', ''),
                    metadata=ioc_data.get('metadata', {}),
                    threat_level=ioc_data.get('threat_level', 'unknown')
                )
                self.add_ioc(ioc)
                imported += 1
            except Exception as e:
                print(f"Error importing IOC: {e}")

        return imported
