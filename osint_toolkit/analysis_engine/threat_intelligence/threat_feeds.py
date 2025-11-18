"""
Threat Feed Manager - Integrates with external threat intelligence feeds
"""

from typing import Dict, List, Optional, Set, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class FeedType(Enum):
    """Types of threat feeds"""
    IP_BLACKLIST = "ip_blacklist"
    DOMAIN_BLACKLIST = "domain_blacklist"
    URL_BLACKLIST = "url_blacklist"
    HASH_BLACKLIST = "hash_blacklist"
    CVE_FEED = "cve_feed"
    BOTNET_C2 = "botnet_c2"
    MALWARE_INDICATORS = "malware_indicators"
    PHISHING = "phishing"
    RANSOMWARE = "ransomware"
    APT_INDICATORS = "apt_indicators"


class FeedFormat(Enum):
    """Feed data formats"""
    JSON = "json"
    CSV = "csv"
    STIX = "stix"
    TEXT = "text"
    XML = "xml"


@dataclass
class ThreatFeed:
    """Represents a threat intelligence feed"""
    feed_id: str
    name: str
    feed_type: FeedType
    url: str
    format: FeedFormat
    update_interval: timedelta
    last_updated: Optional[datetime]
    enabled: bool
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'feed_id': self.feed_id,
            'name': self.name,
            'type': self.feed_type.value,
            'url': self.url,
            'format': self.format.value,
            'update_interval_hours': self.update_interval.total_seconds() / 3600,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'enabled': self.enabled,
            'metadata': self.metadata
        }


@dataclass
class ThreatIndicator:
    """Represents an indicator from a threat feed"""
    indicator_id: str
    indicator_type: str
    value: str
    feed_id: str
    first_seen: datetime
    last_seen: datetime
    confidence: float
    severity: str
    tags: List[str]
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'id': self.indicator_id,
            'type': self.indicator_type,
            'value': self.value,
            'feed_id': self.feed_id,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'confidence': self.confidence,
            'severity': self.severity,
            'tags': self.tags,
            'metadata': self.metadata
        }


class ThreatFeedManager:
    """
    Manages threat intelligence feeds:
    - Add/remove feeds
    - Update feeds
    - Query threat indicators
    - Match indicators against data
    """

    def __init__(self):
        self.feeds: Dict[str, ThreatFeed] = {}
        self.indicators: Dict[str, ThreatIndicator] = {}
        self.feed_parsers: Dict[FeedFormat, Callable] = {}
        self.indicator_index: Dict[str, Set[str]] = {}  # type -> indicator_ids

        # Initialize built-in feeds
        self._initialize_builtin_feeds()

    def _initialize_builtin_feeds(self) -> None:
        """Initialize some common public threat feeds"""
        # Note: These are examples. In production, use real feed URLs

        self.add_feed(
            feed_id="abuse_ch_sslbl",
            name="Abuse.ch SSL Blacklist",
            feed_type=FeedType.HASH_BLACKLIST,
            url="https://sslbl.abuse.ch/blacklist/sslblacklist.csv",
            format=FeedFormat.CSV,
            update_interval=timedelta(hours=1),
            metadata={'description': 'SSL certificate blacklist'}
        )

        self.add_feed(
            feed_id="abuse_ch_urlhaus",
            name="Abuse.ch URLhaus",
            feed_type=FeedType.URL_BLACKLIST,
            url="https://urlhaus.abuse.ch/downloads/csv_recent/",
            format=FeedFormat.CSV,
            update_interval=timedelta(hours=1),
            metadata={'description': 'Malware URL feed'}
        )

        self.add_feed(
            feed_id="blocklist_de",
            name="Blocklist.de",
            feed_type=FeedType.IP_BLACKLIST,
            url="https://lists.blocklist.de/lists/all.txt",
            format=FeedFormat.TEXT,
            update_interval=timedelta(hours=6),
            metadata={'description': 'IP addresses with malicious activity'}
        )

    def add_feed(self, feed_id: str, name: str, feed_type: FeedType,
                url: str, format: FeedFormat,
                update_interval: timedelta = timedelta(hours=24),
                enabled: bool = True,
                metadata: Dict = None) -> ThreatFeed:
        """Add a new threat feed"""
        feed = ThreatFeed(
            feed_id=feed_id,
            name=name,
            feed_type=feed_type,
            url=url,
            format=format,
            update_interval=update_interval,
            last_updated=None,
            enabled=enabled,
            metadata=metadata or {}
        )

        self.feeds[feed_id] = feed
        return feed

    def remove_feed(self, feed_id: str) -> bool:
        """Remove a threat feed"""
        if feed_id in self.feeds:
            del self.feeds[feed_id]

            # Remove associated indicators
            indicators_to_remove = [
                ind_id for ind_id, ind in self.indicators.items()
                if ind.feed_id == feed_id
            ]

            for ind_id in indicators_to_remove:
                self._remove_indicator(ind_id)

            return True
        return False

    def enable_feed(self, feed_id: str) -> bool:
        """Enable a feed"""
        if feed_id in self.feeds:
            self.feeds[feed_id].enabled = True
            return True
        return False

    def disable_feed(self, feed_id: str) -> bool:
        """Disable a feed"""
        if feed_id in self.feeds:
            self.feeds[feed_id].enabled = False
            return True
        return False

    def add_indicator(self, indicator_type: str, value: str, feed_id: str,
                     confidence: float = 0.8, severity: str = "medium",
                     tags: List[str] = None,
                     metadata: Dict = None) -> ThreatIndicator:
        """Add a threat indicator"""
        now = datetime.now()

        # Generate indicator ID
        indicator_id = hashlib.sha256(
            f"{indicator_type}:{value}:{feed_id}".encode()
        ).hexdigest()[:16]

        # Check if indicator already exists
        if indicator_id in self.indicators:
            # Update last_seen
            self.indicators[indicator_id].last_seen = now
            return self.indicators[indicator_id]

        indicator = ThreatIndicator(
            indicator_id=indicator_id,
            indicator_type=indicator_type,
            value=value,
            feed_id=feed_id,
            first_seen=now,
            last_seen=now,
            confidence=confidence,
            severity=severity,
            tags=tags or [],
            metadata=metadata or {}
        )

        self.indicators[indicator_id] = indicator

        # Index by type
        if indicator_type not in self.indicator_index:
            self.indicator_index[indicator_type] = set()
        self.indicator_index[indicator_type].add(indicator_id)

        return indicator

    def _remove_indicator(self, indicator_id: str) -> bool:
        """Remove an indicator"""
        if indicator_id not in self.indicators:
            return False

        indicator = self.indicators[indicator_id]

        # Remove from index
        if indicator.indicator_type in self.indicator_index:
            self.indicator_index[indicator.indicator_type].discard(indicator_id)

        # Remove indicator
        del self.indicators[indicator_id]
        return True

    def check_indicator(self, indicator_type: str, value: str) -> List[ThreatIndicator]:
        """Check if a value matches any threat indicators"""
        matches = []

        if indicator_type not in self.indicator_index:
            return matches

        for indicator_id in self.indicator_index[indicator_type]:
            indicator = self.indicators[indicator_id]

            # Check if feed is enabled
            if indicator.feed_id in self.feeds and not self.feeds[indicator.feed_id].enabled:
                continue

            # Match value
            if indicator.value.lower() == value.lower():
                matches.append(indicator)

        return matches

    def bulk_check_indicators(self, values: List[Tuple[str, str]]) -> Dict[str, List[ThreatIndicator]]:
        """
        Bulk check multiple indicators
        values: List of (indicator_type, value) tuples
        Returns: Dict of value -> matching indicators
        """
        results = {}

        for indicator_type, value in values:
            key = f"{indicator_type}:{value}"
            matches = self.check_indicator(indicator_type, value)
            if matches:
                results[key] = matches

        return results

    def update_feed(self, feed_id: str) -> Optional[int]:
        """
        Update a feed by fetching latest data
        Returns number of indicators added/updated
        """
        if feed_id not in self.feeds:
            return None

        feed = self.feeds[feed_id]

        if not feed.enabled:
            return 0

        # In production, fetch data from feed.url
        # For now, simulate update

        # Placeholder: In real implementation, fetch and parse feed data
        # Example:
        # data = self._fetch_feed_data(feed.url)
        # indicators = self._parse_feed_data(data, feed.format)
        # for indicator in indicators:
        #     self.add_indicator(...)

        feed.last_updated = datetime.now()

        # Return simulated count
        return 0

    def update_all_feeds(self) -> Dict[str, int]:
        """Update all enabled feeds"""
        results = {}

        for feed_id, feed in self.feeds.items():
            if feed.enabled:
                count = self.update_feed(feed_id)
                if count is not None:
                    results[feed_id] = count

        return results

    def get_feeds_needing_update(self) -> List[ThreatFeed]:
        """Get feeds that need updating based on their interval"""
        needs_update = []
        now = datetime.now()

        for feed in self.feeds.values():
            if not feed.enabled:
                continue

            if feed.last_updated is None:
                needs_update.append(feed)
            elif (now - feed.last_updated) >= feed.update_interval:
                needs_update.append(feed)

        return needs_update

    def get_indicators_by_type(self, indicator_type: str) -> List[ThreatIndicator]:
        """Get all indicators of a specific type"""
        if indicator_type not in self.indicator_index:
            return []

        return [
            self.indicators[ind_id]
            for ind_id in self.indicator_index[indicator_type]
            if ind_id in self.indicators
        ]

    def get_indicators_by_feed(self, feed_id: str) -> List[ThreatIndicator]:
        """Get all indicators from a specific feed"""
        return [
            ind for ind in self.indicators.values()
            if ind.feed_id == feed_id
        ]

    def get_indicators_by_severity(self, severity: str) -> List[ThreatIndicator]:
        """Get indicators by severity level"""
        return [
            ind for ind in self.indicators.values()
            if ind.severity == severity
        ]

    def get_high_confidence_indicators(self, min_confidence: float = 0.8) -> List[ThreatIndicator]:
        """Get indicators with high confidence"""
        return [
            ind for ind in self.indicators.values()
            if ind.confidence >= min_confidence
        ]

    def search_indicators(self, query: str) -> List[ThreatIndicator]:
        """Search indicators by value"""
        query_lower = query.lower()
        results = []

        for indicator in self.indicators.values():
            if query_lower in indicator.value.lower():
                results.append(indicator)

        return results

    def get_indicators_by_tags(self, tags: List[str]) -> List[ThreatIndicator]:
        """Get indicators that have any of the specified tags"""
        results = []

        for indicator in self.indicators.values():
            if any(tag in indicator.tags for tag in tags):
                results.append(indicator)

        return results

    def add_custom_parser(self, format: FeedFormat, parser_func: Callable) -> None:
        """Add custom parser for a feed format"""
        self.feed_parsers[format] = parser_func

    def export_feeds(self) -> List[Dict]:
        """Export feed configuration"""
        return [feed.to_dict() for feed in self.feeds.values()]

    def export_indicators(self, feed_id: str = None) -> List[Dict]:
        """Export threat indicators"""
        if feed_id:
            indicators = self.get_indicators_by_feed(feed_id)
        else:
            indicators = list(self.indicators.values())

        return [ind.to_dict() for ind in indicators]

    def import_indicators(self, indicators_data: List[Dict]) -> int:
        """Import threat indicators from data"""
        imported = 0

        for ind_data in indicators_data:
            try:
                self.add_indicator(
                    indicator_type=ind_data['type'],
                    value=ind_data['value'],
                    feed_id=ind_data.get('feed_id', 'imported'),
                    confidence=ind_data.get('confidence', 0.5),
                    severity=ind_data.get('severity', 'medium'),
                    tags=ind_data.get('tags', []),
                    metadata=ind_data.get('metadata', {})
                )
                imported += 1
            except Exception as e:
                print(f"Error importing indicator: {e}")

        return imported

    def cleanup_old_indicators(self, days: int = 30) -> int:
        """Remove indicators older than specified days"""
        cutoff = datetime.now() - timedelta(days=days)

        to_remove = [
            ind_id for ind_id, ind in self.indicators.items()
            if ind.last_seen < cutoff
        ]

        for ind_id in to_remove:
            self._remove_indicator(ind_id)

        return len(to_remove)

    def get_statistics(self) -> Dict:
        """Get threat feed statistics"""
        total_feeds = len(self.feeds)
        enabled_feeds = len([f for f in self.feeds.values() if f.enabled])

        indicators_by_type = {}
        for ind_type, ind_ids in self.indicator_index.items():
            indicators_by_type[ind_type] = len(ind_ids)

        indicators_by_feed = {}
        for feed_id in self.feeds.keys():
            count = len(self.get_indicators_by_feed(feed_id))
            indicators_by_feed[feed_id] = count

        feeds_needing_update = len(self.get_feeds_needing_update())

        return {
            'total_feeds': total_feeds,
            'enabled_feeds': enabled_feeds,
            'total_indicators': len(self.indicators),
            'indicators_by_type': indicators_by_type,
            'indicators_by_feed': indicators_by_feed,
            'feeds_needing_update': feeds_needing_update
        }
