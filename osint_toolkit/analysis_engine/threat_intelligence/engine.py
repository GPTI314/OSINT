"""
Threat Intelligence Engine - Main engine integrating all threat intelligence components
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from osint_toolkit.analysis_engine.threat_intelligence.ioc_detector import IOCDetector, IOC, IOCType
from osint_toolkit.analysis_engine.threat_intelligence.threat_scorer import ThreatScorer, ThreatScore, ThreatLevel
from osint_toolkit.analysis_engine.threat_intelligence.anomaly_detector import AnomalyDetector, Anomaly
from osint_toolkit.analysis_engine.threat_intelligence.reputation_checker import ReputationChecker, ReputationSource
from osint_toolkit.analysis_engine.threat_intelligence.threat_feeds import ThreatFeedManager, FeedType


class ThreatIntelligence:
    """
    Main threat intelligence engine that integrates:
    - IOC detection
    - Threat scoring
    - Anomaly detection
    - Reputation checking
    - Threat feeds
    """

    def __init__(self, api_keys: Dict[str, str] = None):
        self.ioc_detector = IOCDetector()
        self.threat_scorer = ThreatScorer()
        self.anomaly_detector = AnomalyDetector()
        self.reputation_checker = ReputationChecker(api_keys)
        self.threat_feed_manager = ThreatFeedManager()

    # IOC Operations
    def extract_iocs(self, text: str, source: str = "unknown") -> List[IOC]:
        """Extract IOCs from text"""
        return self.ioc_detector.extract_iocs(text, source)

    def add_known_malicious(self, ioc_value: str, ioc_type: IOCType = None) -> None:
        """Add a known malicious IOC"""
        self.ioc_detector.add_known_malicious(ioc_value, ioc_type)

    def get_high_confidence_iocs(self, min_confidence: float = 0.7) -> List[IOC]:
        """Get high confidence IOCs"""
        return self.ioc_detector.get_high_confidence_iocs(min_confidence)

    def get_iocs_by_threat_level(self, threat_level: str) -> List[IOC]:
        """Get IOCs by threat level"""
        return self.ioc_detector.get_iocs_by_threat_level(threat_level)

    # Threat Scoring Operations
    def calculate_threat_score(self, entity_id: str, entity_type: str,
                              analyze_iocs: bool = True,
                              analyze_reputation: bool = True,
                              analyze_behavior: bool = True) -> ThreatScore:
        """
        Calculate comprehensive threat score for an entity
        """
        factors = {}

        # IOC presence score
        if analyze_iocs:
            ioc_score = self._calculate_ioc_score(entity_id, entity_type)
            factors['ioc_presence'] = ioc_score

        # Reputation score
        if analyze_reputation:
            rep_score = self._calculate_reputation_score(entity_id, entity_type)
            if rep_score is not None:
                factors['reputation'] = rep_score

        # Behavioral/anomaly score
        if analyze_behavior:
            behavior_score = self._calculate_behavior_score(entity_id)
            if behavior_score is not None:
                factors['behavior'] = behavior_score

        # Calculate final threat score
        return self.threat_scorer.calculate_threat_score(
            entity_id, entity_type, factors
        )

    def _calculate_ioc_score(self, entity_id: str, entity_type: str) -> float:
        """Calculate score based on IOC presence"""
        # Search for IOCs related to this entity
        iocs = self.ioc_detector.search_ioc(entity_id)

        if not iocs:
            return 0.0

        # Count by threat level
        threat_levels = [ioc.threat_level for ioc in iocs]

        if 'critical' in threat_levels or 'high' in threat_levels:
            severity = 'high'
        elif 'medium' in threat_levels:
            severity = 'medium'
        else:
            severity = 'low'

        return self.threat_scorer.score_from_ioc(
            has_ioc=True,
            ioc_count=len(iocs),
            ioc_severity=severity
        )

    def _calculate_reputation_score(self, entity_id: str, entity_type: str) -> Optional[float]:
        """Calculate score based on reputation"""
        # Map entity types to reputation check methods
        if entity_type == 'ip':
            rep_scores = self.reputation_checker.check_ip_reputation(entity_id)
        elif entity_type == 'domain':
            rep_scores = self.reputation_checker.check_domain_reputation(entity_id)
        elif entity_type == 'url':
            rep_scores = self.reputation_checker.check_url_reputation(entity_id)
        elif entity_type == 'hash':
            rep_scores = self.reputation_checker.check_hash_reputation(entity_id)
        else:
            return None

        if not rep_scores:
            return None

        # Get aggregate reputation
        aggregate = self.reputation_checker.aggregate_reputation(entity_id, entity_type)

        if not aggregate:
            return None

        # Convert to threat score
        return self.threat_scorer.score_from_reputation(
            aggregate['aggregate_score'],
            aggregate['source_count']
        )

    def _calculate_behavior_score(self, entity_id: str) -> Optional[float]:
        """Calculate score based on behavioral anomalies"""
        # Get anomalies for this entity
        anomalies = self.anomaly_detector.get_anomalies_by_entity(entity_id)

        if not anomalies:
            return None

        # Calculate average anomaly severity
        behavior_metrics = {
            f"anomaly_{i}": anomaly.severity
            for i, anomaly in enumerate(anomalies)
        }

        return self.threat_scorer.score_from_behavior(behavior_metrics)

    def get_high_threat_entities(self, min_level: ThreatLevel = ThreatLevel.MEDIUM) -> List[ThreatScore]:
        """Get entities with high threat scores"""
        return self.threat_scorer.get_high_threat_entities(min_level)

    def get_threat_trend(self, entity_id: str) -> Optional[str]:
        """Get threat trend for an entity"""
        return self.threat_scorer.get_threat_trend(entity_id)

    # Anomaly Detection Operations
    def detect_anomalies(self, field: str, value: float, entity_id: str = None) -> List[Anomaly]:
        """Detect anomalies in data"""
        return self.anomaly_detector.detect_all_anomalies(field, value, entity_id)

    def detect_zscore_anomaly(self, field: str, value: float,
                             threshold: float = 3.0,
                             entity_id: str = None) -> Optional[Anomaly]:
        """Detect anomalies using Z-score"""
        return self.anomaly_detector.detect_zscore_anomaly(field, value, threshold, entity_id)

    def detect_volume_spike(self, field: str, window_minutes: int = 60) -> Optional[Anomaly]:
        """Detect volume spikes"""
        return self.anomaly_detector.detect_volume_spike(field, window_minutes)

    def get_high_severity_anomalies(self, min_severity: float = 70.0) -> List[Anomaly]:
        """Get high severity anomalies"""
        return self.anomaly_detector.get_anomalies_by_severity(min_severity)

    # Reputation Checking Operations
    def check_ip_reputation(self, ip: str) -> Dict:
        """Check IP reputation"""
        scores = self.reputation_checker.check_ip_reputation(ip)
        aggregate = self.reputation_checker.aggregate_reputation(ip, 'ip')
        summary = self.reputation_checker.get_reputation_summary(ip, 'ip')

        return {
            'entity': ip,
            'type': 'ip',
            'scores': [s.to_dict() for s in scores],
            'aggregate': aggregate,
            'summary': summary
        }

    def check_domain_reputation(self, domain: str) -> Dict:
        """Check domain reputation"""
        scores = self.reputation_checker.check_domain_reputation(domain)
        aggregate = self.reputation_checker.aggregate_reputation(domain, 'domain')
        summary = self.reputation_checker.get_reputation_summary(domain, 'domain')

        return {
            'entity': domain,
            'type': 'domain',
            'scores': [s.to_dict() for s in scores],
            'aggregate': aggregate,
            'summary': summary
        }

    def check_url_reputation(self, url: str) -> Dict:
        """Check URL reputation"""
        scores = self.reputation_checker.check_url_reputation(url)
        aggregate = self.reputation_checker.aggregate_reputation(url, 'url')
        summary = self.reputation_checker.get_reputation_summary(url, 'url')

        return {
            'entity': url,
            'type': 'url',
            'scores': [s.to_dict() for s in scores],
            'aggregate': aggregate,
            'summary': summary
        }

    # Threat Feed Operations
    def add_threat_feed(self, feed_id: str, name: str, feed_type: FeedType,
                       url: str, **kwargs) -> Any:
        """Add a threat feed"""
        return self.threat_feed_manager.add_feed(feed_id, name, feed_type, url, **kwargs)

    def check_against_threat_feeds(self, indicator_type: str, value: str) -> List[Dict]:
        """Check if a value matches any threat feed indicators"""
        matches = self.threat_feed_manager.check_indicator(indicator_type, value)
        return [m.to_dict() for m in matches]

    def update_all_threat_feeds(self) -> Dict[str, int]:
        """Update all threat feeds"""
        return self.threat_feed_manager.update_all_feeds()

    # Integrated Analysis
    def analyze_entity(self, entity_value: str, entity_type: str) -> Dict[str, Any]:
        """
        Comprehensive threat analysis of an entity
        Combines IOC detection, reputation, threat feeds, and scoring
        """
        results = {
            'entity': entity_value,
            'type': entity_type,
            'timestamp': datetime.now().isoformat(),
            'iocs': [],
            'reputation': None,
            'threat_feeds': [],
            'threat_score': None,
            'anomalies': [],
            'assessment': ''
        }

        # Extract/search for IOCs
        iocs = self.ioc_detector.search_ioc(entity_value)
        results['iocs'] = [ioc.to_dict() for ioc in iocs]

        # Check reputation
        if entity_type == 'ip':
            rep_data = self.check_ip_reputation(entity_value)
        elif entity_type == 'domain':
            rep_data = self.check_domain_reputation(entity_value)
        elif entity_type == 'url':
            rep_data = self.check_url_reputation(entity_value)
        else:
            rep_data = None

        if rep_data:
            results['reputation'] = rep_data

        # Check threat feeds
        feed_matches = self.check_against_threat_feeds(entity_type, entity_value)
        results['threat_feeds'] = feed_matches

        # Calculate threat score
        threat_score = self.calculate_threat_score(entity_value, entity_type)
        results['threat_score'] = threat_score.to_dict()

        # Get related anomalies
        anomalies = self.anomaly_detector.get_anomalies_by_entity(entity_value)
        results['anomalies'] = [a.to_dict() for a in anomalies]

        # Generate assessment
        results['assessment'] = self._generate_assessment(threat_score, iocs, feed_matches)

        return results

    def _generate_assessment(self, threat_score: ThreatScore,
                           iocs: List[IOC],
                           feed_matches: List[Dict]) -> str:
        """Generate human-readable threat assessment"""
        assessment_parts = []

        # Threat level
        if threat_score.threat_level == ThreatLevel.CRITICAL:
            assessment_parts.append("CRITICAL THREAT: Immediate action required.")
        elif threat_score.threat_level == ThreatLevel.HIGH:
            assessment_parts.append("HIGH THREAT: Priority investigation needed.")
        elif threat_score.threat_level == ThreatLevel.MEDIUM:
            assessment_parts.append("MEDIUM THREAT: Monitor and investigate.")
        elif threat_score.threat_level == ThreatLevel.LOW:
            assessment_parts.append("LOW THREAT: Routine monitoring recommended.")
        else:
            assessment_parts.append("UNKNOWN THREAT: Insufficient data.")

        # IOC information
        if iocs:
            assessment_parts.append(f"Found {len(iocs)} IOC(s).")

        # Threat feed matches
        if feed_matches:
            assessment_parts.append(f"Matches {len(feed_matches)} threat feed indicator(s).")

        # Recommendations
        if threat_score.recommendations:
            assessment_parts.append("Recommendations: " + "; ".join(threat_score.recommendations[:3]))

        return " ".join(assessment_parts)

    def bulk_analyze(self, entities: List[Tuple[str, str]]) -> Dict[str, Dict]:
        """
        Bulk analyze multiple entities
        entities: List of (entity_value, entity_type) tuples
        """
        results = {}

        for entity_value, entity_type in entities:
            try:
                analysis = self.analyze_entity(entity_value, entity_type)
                results[f"{entity_type}:{entity_value}"] = analysis
            except Exception as e:
                results[f"{entity_type}:{entity_value}"] = {
                    'error': str(e)
                }

        return results

    def export_threat_intelligence(self) -> Dict[str, Any]:
        """Export all threat intelligence data"""
        return {
            'iocs': self.ioc_detector.export_iocs(),
            'threat_scores': self.threat_scorer.export_scores(),
            'anomalies': self.anomaly_detector.export_anomalies(),
            'reputation_data': self.reputation_checker.export_reputation_data(),
            'threat_feeds': self.threat_feed_manager.export_feeds(),
            'threat_indicators': self.threat_feed_manager.export_indicators(),
            'statistics': self.get_statistics()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components"""
        return {
            'iocs': self.ioc_detector.get_ioc_statistics(),
            'threat_scores': self.threat_scorer.get_statistics(),
            'anomalies': self.anomaly_detector.get_statistics(),
            'reputation': self.reputation_checker.get_statistics(),
            'threat_feeds': self.threat_feed_manager.get_statistics()
        }

    def clear_all(self) -> None:
        """Clear all threat intelligence data"""
        self.ioc_detector = IOCDetector()
        self.threat_scorer = ThreatScorer()
        self.anomaly_detector = AnomalyDetector()
        self.reputation_checker.clear_cache()
