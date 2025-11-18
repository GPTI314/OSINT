"""
Reputation Checker - Checks reputation of IPs, domains, and other entities
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json


class ReputationSource(Enum):
    """Reputation data sources"""
    VIRUSTOTAL = "virustotal"
    SHODAN = "shodan"
    ABUSEIPDB = "abuseipdb"
    URLHAUS = "urlhaus"
    ALIENVAULT_OTX = "alienvault_otx"
    GREYNOISE = "greynoise"
    TALOS = "cisco_talos"
    INTERNAL = "internal"
    CUSTOM = "custom"


@dataclass
class ReputationScore:
    """Represents reputation data for an entity"""
    entity: str
    entity_type: str
    score: float  # -100 (very bad) to +100 (very good)
    source: ReputationSource
    confidence: float
    timestamp: datetime
    details: Dict
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'entity': self.entity,
            'entity_type': self.entity_type,
            'score': self.score,
            'source': self.source.value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'details': self.details,
            'metadata': self.metadata
        }


class ReputationChecker:
    """
    Checks and manages reputation data for entities:
    - IP addresses
    - Domains
    - URLs
    - Email addresses
    - File hashes
    """

    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.reputation_cache: Dict[str, List[ReputationScore]] = {}
        self.cache_ttl = timedelta(hours=24)
        self.reputation_weights = self._initialize_weights()

    def _initialize_weights(self) -> Dict[ReputationSource, float]:
        """Initialize source reliability weights"""
        return {
            ReputationSource.VIRUSTOTAL: 0.9,
            ReputationSource.ABUSEIPDB: 0.85,
            ReputationSource.SHODAN: 0.8,
            ReputationSource.URLHAUS: 0.85,
            ReputationSource.ALIENVAULT_OTX: 0.8,
            ReputationSource.GREYNOISE: 0.75,
            ReputationSource.TALOS: 0.85,
            ReputationSource.INTERNAL: 0.7,
            ReputationSource.CUSTOM: 0.5
        }

    def set_api_key(self, source: ReputationSource, api_key: str) -> None:
        """Set API key for a reputation source"""
        self.api_keys[source.value] = api_key

    def add_reputation_score(self, entity: str, entity_type: str,
                            score: float, source: ReputationSource,
                            confidence: float = 1.0,
                            details: Dict = None,
                            metadata: Dict = None) -> ReputationScore:
        """Manually add a reputation score"""
        rep_score = ReputationScore(
            entity=entity,
            entity_type=entity_type,
            score=score,
            source=source,
            confidence=confidence,
            timestamp=datetime.now(),
            details=details or {},
            metadata=metadata or {}
        )

        # Cache the score
        cache_key = f"{entity_type}:{entity}"
        if cache_key not in self.reputation_cache:
            self.reputation_cache[cache_key] = []
        self.reputation_cache[cache_key].append(rep_score)

        return rep_score

    def check_ip_reputation(self, ip: str, sources: List[ReputationSource] = None) -> List[ReputationScore]:
        """Check IP address reputation"""
        # Check cache first
        cache_key = f"ip:{ip}"
        cached = self._get_cached_reputation(cache_key)
        if cached:
            return cached

        scores = []

        # Simulate reputation checks (in production, call real APIs)
        if not sources or ReputationSource.ABUSEIPDB in sources:
            score = self._check_abuseipdb(ip)
            if score:
                scores.append(score)

        if not sources or ReputationSource.GREYNOISE in sources:
            score = self._check_greynoise(ip)
            if score:
                scores.append(score)

        # Cache results
        if scores:
            self.reputation_cache[cache_key] = scores

        return scores

    def check_domain_reputation(self, domain: str, sources: List[ReputationSource] = None) -> List[ReputationScore]:
        """Check domain reputation"""
        cache_key = f"domain:{domain}"
        cached = self._get_cached_reputation(cache_key)
        if cached:
            return cached

        scores = []

        if not sources or ReputationSource.VIRUSTOTAL in sources:
            score = self._check_virustotal_domain(domain)
            if score:
                scores.append(score)

        if not sources or ReputationSource.URLHAUS in sources:
            score = self._check_urlhaus_domain(domain)
            if score:
                scores.append(score)

        # Cache results
        if scores:
            self.reputation_cache[cache_key] = scores

        return scores

    def check_url_reputation(self, url: str, sources: List[ReputationSource] = None) -> List[ReputationScore]:
        """Check URL reputation"""
        cache_key = f"url:{url}"
        cached = self._get_cached_reputation(cache_key)
        if cached:
            return cached

        scores = []

        if not sources or ReputationSource.VIRUSTOTAL in sources:
            score = self._check_virustotal_url(url)
            if score:
                scores.append(score)

        if not sources or ReputationSource.URLHAUS in sources:
            score = self._check_urlhaus_url(url)
            if score:
                scores.append(score)

        # Cache results
        if scores:
            self.reputation_cache[cache_key] = scores

        return scores

    def check_hash_reputation(self, file_hash: str, sources: List[ReputationSource] = None) -> List[ReputationScore]:
        """Check file hash reputation"""
        cache_key = f"hash:{file_hash}"
        cached = self._get_cached_reputation(cache_key)
        if cached:
            return cached

        scores = []

        if not sources or ReputationSource.VIRUSTOTAL in sources:
            score = self._check_virustotal_hash(file_hash)
            if score:
                scores.append(score)

        # Cache results
        if scores:
            self.reputation_cache[cache_key] = scores

        return scores

    def _get_cached_reputation(self, cache_key: str) -> Optional[List[ReputationScore]]:
        """Get reputation from cache if not expired"""
        if cache_key not in self.reputation_cache:
            return None

        scores = self.reputation_cache[cache_key]

        # Check if cache is expired
        if scores and (datetime.now() - scores[0].timestamp) < self.cache_ttl:
            return scores

        # Remove expired cache
        del self.reputation_cache[cache_key]
        return None

    def _check_abuseipdb(self, ip: str) -> Optional[ReputationScore]:
        """
        Check IP reputation using AbuseIPDB
        Note: This is a placeholder. In production, implement actual API calls.
        """
        # Placeholder implementation
        # In production: Make API call to AbuseIPDB
        # For now, return simulated data

        # Simulate: Check if IP matches common patterns
        if ip.startswith('10.') or ip.startswith('192.168.'):
            # Private IP - neutral score
            score = 0
            details = {'abuse_score': 0, 'reports': 0}
        else:
            # Simulated score
            score = 50  # Neutral by default
            details = {'abuse_score': 0, 'reports': 0, 'note': 'simulated'}

        return ReputationScore(
            entity=ip,
            entity_type='ip',
            score=score,
            source=ReputationSource.ABUSEIPDB,
            confidence=0.8,
            timestamp=datetime.now(),
            details=details,
            metadata={'api_version': 'v2'}
        )

    def _check_greynoise(self, ip: str) -> Optional[ReputationScore]:
        """Check IP reputation using GreyNoise"""
        # Placeholder implementation
        return ReputationScore(
            entity=ip,
            entity_type='ip',
            score=50,
            source=ReputationSource.GREYNOISE,
            confidence=0.75,
            timestamp=datetime.now(),
            details={'classification': 'unknown', 'note': 'simulated'},
            metadata={}
        )

    def _check_virustotal_domain(self, domain: str) -> Optional[ReputationScore]:
        """Check domain reputation using VirusTotal"""
        # Placeholder implementation
        return ReputationScore(
            entity=domain,
            entity_type='domain',
            score=60,
            source=ReputationSource.VIRUSTOTAL,
            confidence=0.9,
            timestamp=datetime.now(),
            details={'positives': 0, 'total': 0, 'note': 'simulated'},
            metadata={}
        )

    def _check_virustotal_url(self, url: str) -> Optional[ReputationScore]:
        """Check URL reputation using VirusTotal"""
        # Placeholder implementation
        return ReputationScore(
            entity=url,
            entity_type='url',
            score=60,
            source=ReputationSource.VIRUSTOTAL,
            confidence=0.9,
            timestamp=datetime.now(),
            details={'positives': 0, 'total': 0, 'note': 'simulated'},
            metadata={}
        )

    def _check_virustotal_hash(self, file_hash: str) -> Optional[ReputationScore]:
        """Check file hash reputation using VirusTotal"""
        # Placeholder implementation
        return ReputationScore(
            entity=file_hash,
            entity_type='hash',
            score=60,
            source=ReputationSource.VIRUSTOTAL,
            confidence=0.9,
            timestamp=datetime.now(),
            details={'positives': 0, 'total': 0, 'note': 'simulated'},
            metadata={}
        )

    def _check_urlhaus_domain(self, domain: str) -> Optional[ReputationScore]:
        """Check domain reputation using URLhaus"""
        # Placeholder implementation
        return ReputationScore(
            entity=domain,
            entity_type='domain',
            score=55,
            source=ReputationSource.URLHAUS,
            confidence=0.85,
            timestamp=datetime.now(),
            details={'status': 'unknown', 'note': 'simulated'},
            metadata={}
        )

    def _check_urlhaus_url(self, url: str) -> Optional[ReputationScore]:
        """Check URL reputation using URLhaus"""
        # Placeholder implementation
        return ReputationScore(
            entity=url,
            entity_type='url',
            score=55,
            source=ReputationSource.URLHAUS,
            confidence=0.85,
            timestamp=datetime.now(),
            details={'status': 'unknown', 'note': 'simulated'},
            metadata={}
        )

    def aggregate_reputation(self, entity: str, entity_type: str) -> Optional[Dict]:
        """
        Aggregate reputation scores from multiple sources
        Returns weighted average and consensus
        """
        cache_key = f"{entity_type}:{entity}"

        if cache_key not in self.reputation_cache:
            return None

        scores = self.reputation_cache[cache_key]

        if not scores:
            return None

        # Calculate weighted average
        weighted_sum = 0.0
        total_weight = 0.0

        for rep_score in scores:
            weight = self.reputation_weights.get(rep_score.source, 0.5) * rep_score.confidence
            weighted_sum += rep_score.score * weight
            total_weight += weight

        if total_weight == 0:
            return None

        aggregate_score = weighted_sum / total_weight

        # Calculate consensus (how much sources agree)
        score_values = [s.score for s in scores]
        if len(score_values) > 1:
            import statistics
            score_std = statistics.stdev(score_values)
            consensus = max(0, 1 - (score_std / 100))  # Lower stdev = higher consensus
        else:
            consensus = 1.0

        return {
            'entity': entity,
            'entity_type': entity_type,
            'aggregate_score': aggregate_score,
            'consensus': consensus,
            'source_count': len(scores),
            'sources': [s.source.value for s in scores],
            'individual_scores': [s.to_dict() for s in scores],
            'timestamp': datetime.now().isoformat()
        }

    def get_reputation_summary(self, entity: str, entity_type: str) -> Optional[str]:
        """Get human-readable reputation summary"""
        aggregate = self.aggregate_reputation(entity, entity_type)

        if not aggregate:
            return None

        score = aggregate['aggregate_score']

        if score >= 75:
            category = "EXCELLENT"
            description = "Highly trusted, no known issues"
        elif score >= 50:
            category = "GOOD"
            description = "Generally trusted, minimal concerns"
        elif score >= 25:
            category = "NEUTRAL"
            description = "Unknown or mixed reputation"
        elif score >= 0:
            category = "SUSPICIOUS"
            description = "Some negative indicators present"
        elif score >= -50:
            category = "BAD"
            description = "Known malicious activity detected"
        else:
            category = "CRITICAL"
            description = "Confirmed malicious, high threat"

        return f"{category}: {description} (Score: {score:.1f}/100, Consensus: {aggregate['consensus']:.2f})"

    def clear_cache(self, entity: str = None, entity_type: str = None) -> int:
        """Clear reputation cache"""
        if entity and entity_type:
            cache_key = f"{entity_type}:{entity}"
            if cache_key in self.reputation_cache:
                del self.reputation_cache[cache_key]
                return 1
            return 0
        else:
            count = len(self.reputation_cache)
            self.reputation_cache.clear()
            return count

    def export_reputation_data(self) -> List[Dict]:
        """Export all cached reputation data"""
        all_scores = []
        for scores in self.reputation_cache.values():
            all_scores.extend([s.to_dict() for s in scores])
        return all_scores

    def get_statistics(self) -> Dict:
        """Get reputation checker statistics"""
        total_entities = len(self.reputation_cache)
        total_scores = sum(len(scores) for scores in self.reputation_cache.values())

        sources_used = set()
        for scores in self.reputation_cache.values():
            sources_used.update([s.source for s in scores])

        return {
            'total_entities_checked': total_entities,
            'total_reputation_scores': total_scores,
            'sources_used': [s.value for s in sources_used],
            'cache_size': total_entities,
            'api_keys_configured': len(self.api_keys)
        }
