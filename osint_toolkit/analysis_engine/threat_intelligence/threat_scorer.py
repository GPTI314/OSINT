"""
Threat Scorer - Risk assessment and threat scoring engine
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics


class ThreatLevel(Enum):
    """Threat severity levels"""
    UNKNOWN = 0
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class ThreatScore:
    """Represents a threat assessment score"""
    entity_id: str
    entity_type: str
    score: float  # 0.0 to 100.0
    threat_level: ThreatLevel
    factors: Dict[str, float]
    timestamp: datetime
    confidence: float
    recommendations: List[str]
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'score': self.score,
            'threat_level': self.threat_level.name,
            'factors': self.factors,
            'timestamp': self.timestamp.isoformat(),
            'confidence': self.confidence,
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }


class ThreatScorer:
    """
    Calculates threat scores based on multiple factors:
    - IOC presence
    - Reputation scores
    - Behavioral patterns
    - Temporal patterns
    - Network associations
    """

    def __init__(self):
        self.scores: Dict[str, ThreatScore] = {}
        self.scoring_weights = self._initialize_weights()
        self.threat_history: Dict[str, List[ThreatScore]] = {}

    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize default scoring weights"""
        return {
            'ioc_presence': 0.3,
            'reputation': 0.25,
            'behavior': 0.20,
            'temporal_anomaly': 0.15,
            'network_association': 0.10
        }

    def set_weight(self, factor: str, weight: float) -> None:
        """Set custom weight for a scoring factor"""
        if 0 <= weight <= 1:
            self.scoring_weights[factor] = weight

    def calculate_threat_score(self, entity_id: str, entity_type: str,
                              factors: Dict[str, float],
                              metadata: Dict = None) -> ThreatScore:
        """
        Calculate comprehensive threat score for an entity
        Factors should be normalized 0-100
        """
        # Calculate weighted score
        weighted_sum = 0.0
        total_weight = 0.0

        for factor, value in factors.items():
            if factor in self.scoring_weights:
                weight = self.scoring_weights[factor]
                weighted_sum += value * weight
                total_weight += weight

        # Normalize score
        if total_weight > 0:
            score = weighted_sum / total_weight
        else:
            score = sum(factors.values()) / len(factors) if factors else 0.0

        # Determine threat level
        threat_level = self._score_to_threat_level(score)

        # Calculate confidence based on number of factors
        confidence = min(len(factors) / len(self.scoring_weights), 1.0)

        # Generate recommendations
        recommendations = self._generate_recommendations(score, factors, threat_level)

        # Create threat score object
        threat_score = ThreatScore(
            entity_id=entity_id,
            entity_type=entity_type,
            score=score,
            threat_level=threat_level,
            factors=factors,
            timestamp=datetime.now(),
            confidence=confidence,
            recommendations=recommendations,
            metadata=metadata or {}
        )

        # Store score
        self.scores[entity_id] = threat_score

        # Add to history
        if entity_id not in self.threat_history:
            self.threat_history[entity_id] = []
        self.threat_history[entity_id].append(threat_score)

        return threat_score

    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """Convert numerical score to threat level"""
        if score < 10:
            return ThreatLevel.UNKNOWN
        elif score < 20:
            return ThreatLevel.INFO
        elif score < 40:
            return ThreatLevel.LOW
        elif score < 60:
            return ThreatLevel.MEDIUM
        elif score < 80:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL

    def _generate_recommendations(self, score: float, factors: Dict[str, float],
                                 threat_level: ThreatLevel) -> List[str]:
        """Generate security recommendations based on threat score"""
        recommendations = []

        if threat_level == ThreatLevel.CRITICAL:
            recommendations.append("IMMEDIATE ACTION REQUIRED: Block and isolate this entity")
            recommendations.append("Conduct full security audit")
            recommendations.append("Notify security team and stakeholders")

        elif threat_level == ThreatLevel.HIGH:
            recommendations.append("High priority investigation required")
            recommendations.append("Consider blocking or rate-limiting")
            recommendations.append("Review all associated entities")

        elif threat_level == ThreatLevel.MEDIUM:
            recommendations.append("Monitor closely for suspicious activity")
            recommendations.append("Review and verify entity legitimacy")
            recommendations.append("Check for false positives")

        elif threat_level == ThreatLevel.LOW:
            recommendations.append("Continue monitoring")
            recommendations.append("Document for future reference")

        # Factor-specific recommendations
        if factors.get('ioc_presence', 0) > 70:
            recommendations.append("Known malicious indicators detected - verify and block")

        if factors.get('reputation', 0) > 70:
            recommendations.append("Poor reputation detected - investigate source")

        if factors.get('behavior', 0) > 70:
            recommendations.append("Suspicious behavior patterns - analyze activity logs")

        if factors.get('temporal_anomaly', 0) > 70:
            recommendations.append("Unusual timing patterns - review temporal behavior")

        if factors.get('network_association', 0) > 70:
            recommendations.append("Associated with known threats - investigate connections")

        return recommendations

    def score_from_ioc(self, has_ioc: bool, ioc_count: int = 0,
                      ioc_severity: str = "medium") -> float:
        """Calculate IOC presence score"""
        if not has_ioc:
            return 0.0

        base_score = 50.0

        # Adjust for count
        count_multiplier = min(ioc_count * 10, 30)

        # Adjust for severity
        severity_multipliers = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5,
            'critical': 2.0
        }
        severity_mult = severity_multipliers.get(ioc_severity, 1.0)

        score = min(base_score + count_multiplier * severity_mult, 100.0)
        return score

    def score_from_reputation(self, reputation_score: float,
                             source_count: int = 1) -> float:
        """
        Calculate score from reputation data
        reputation_score: -100 (very bad) to 100 (very good)
        """
        # Convert to 0-100 threat score (inverse of reputation)
        # Good reputation (100) = low threat (0)
        # Bad reputation (-100) = high threat (100)

        if reputation_score >= 0:
            # Good reputation
            threat_score = (100 - reputation_score) * 0.3  # Max 30 for neutral
        else:
            # Bad reputation
            threat_score = abs(reputation_score)  # 0-100

        # Boost confidence if multiple sources agree
        if source_count > 1:
            threat_score = min(threat_score * (1 + source_count * 0.1), 100.0)

        return threat_score

    def score_from_behavior(self, behavior_metrics: Dict[str, float]) -> float:
        """
        Calculate score from behavioral analysis
        behavior_metrics: dict of metric_name -> anomaly_score (0-100)
        """
        if not behavior_metrics:
            return 0.0

        # Calculate average anomaly score
        avg_anomaly = statistics.mean(behavior_metrics.values())

        # Weight by number of anomalous behaviors
        anomaly_count = sum(1 for score in behavior_metrics.values() if score > 50)
        count_weight = min(anomaly_count * 10, 30)

        total_score = min(avg_anomaly + count_weight, 100.0)
        return total_score

    def score_from_temporal_pattern(self, pattern_type: str,
                                   anomaly_severity: float) -> float:
        """
        Calculate score from temporal patterns
        anomaly_severity: 0-100
        """
        base_scores = {
            'unusual_frequency': 40.0,
            'unusual_timing': 30.0,
            'burst_activity': 50.0,
            'dormancy_break': 35.0,
            'regular_beacon': 60.0  # High score - often malicious
        }

        base_score = base_scores.get(pattern_type, 30.0)
        total_score = min(base_score + (anomaly_severity * 0.5), 100.0)

        return total_score

    def score_from_network_associations(self, malicious_neighbors: int,
                                       total_neighbors: int,
                                       max_threat_score: float) -> float:
        """
        Calculate score from network associations
        """
        if total_neighbors == 0:
            return 0.0

        # Percentage of malicious associations
        malicious_ratio = malicious_neighbors / total_neighbors

        # Weight by the severity of associations
        base_score = malicious_ratio * 60.0

        # Boost if associated with high-threat entities
        threat_boost = max_threat_score * 0.4

        total_score = min(base_score + threat_boost, 100.0)
        return total_score

    def get_threat_score(self, entity_id: str) -> Optional[ThreatScore]:
        """Get the current threat score for an entity"""
        return self.scores.get(entity_id)

    def get_threat_history(self, entity_id: str) -> List[ThreatScore]:
        """Get threat score history for an entity"""
        return self.threat_history.get(entity_id, [])

    def get_threat_trend(self, entity_id: str) -> Optional[str]:
        """
        Analyze threat trend for an entity
        Returns: 'increasing', 'decreasing', 'stable', or None
        """
        history = self.get_threat_history(entity_id)

        if len(history) < 2:
            return None

        recent_scores = [ts.score for ts in history[-5:]]  # Last 5 scores

        # Calculate trend
        if len(recent_scores) >= 2:
            first_half_avg = statistics.mean(recent_scores[:len(recent_scores)//2])
            second_half_avg = statistics.mean(recent_scores[len(recent_scores)//2:])

            diff = second_half_avg - first_half_avg

            if diff > 10:
                return 'increasing'
            elif diff < -10:
                return 'decreasing'
            else:
                return 'stable'

        return None

    def get_high_threat_entities(self, min_level: ThreatLevel = ThreatLevel.MEDIUM,
                                min_confidence: float = 0.5) -> List[ThreatScore]:
        """Get entities with high threat scores"""
        high_threats = []

        for threat_score in self.scores.values():
            if (threat_score.threat_level.value >= min_level.value and
                threat_score.confidence >= min_confidence):
                high_threats.append(threat_score)

        # Sort by score (descending)
        high_threats.sort(key=lambda x: x.score, reverse=True)
        return high_threats

    def compare_scores(self, entity1_id: str, entity2_id: str) -> Optional[Dict]:
        """Compare threat scores of two entities"""
        score1 = self.get_threat_score(entity1_id)
        score2 = self.get_threat_score(entity2_id)

        if not score1 or not score2:
            return None

        return {
            'entity1': score1.to_dict(),
            'entity2': score2.to_dict(),
            'score_difference': abs(score1.score - score2.score),
            'higher_threat': entity1_id if score1.score > score2.score else entity2_id,
            'common_factors': set(score1.factors.keys()) & set(score2.factors.keys())
        }

    def aggregate_threat_score(self, entity_ids: List[str]) -> Optional[ThreatScore]:
        """Calculate aggregate threat score for a group of entities"""
        scores = [self.get_threat_score(eid) for eid in entity_ids if eid in self.scores]

        if not scores:
            return None

        # Calculate average score
        avg_score = statistics.mean([s.score for s in scores])

        # Find highest threat level
        max_threat_level = max([s.threat_level for s in scores], key=lambda x: x.value)

        # Aggregate factors
        all_factors = {}
        for score in scores:
            for factor, value in score.factors.items():
                if factor not in all_factors:
                    all_factors[factor] = []
                all_factors[factor].append(value)

        avg_factors = {
            factor: statistics.mean(values)
            for factor, values in all_factors.items()
        }

        # Create aggregate score
        aggregate = ThreatScore(
            entity_id='aggregate',
            entity_type='group',
            score=avg_score,
            threat_level=max_threat_level,
            factors=avg_factors,
            timestamp=datetime.now(),
            confidence=statistics.mean([s.confidence for s in scores]),
            recommendations=self._generate_recommendations(avg_score, avg_factors, max_threat_level),
            metadata={'entity_count': len(scores), 'entity_ids': entity_ids}
        )

        return aggregate

    def export_scores(self) -> List[Dict]:
        """Export all threat scores"""
        return [score.to_dict() for score in self.scores.values()]

    def get_statistics(self) -> Dict:
        """Get threat scoring statistics"""
        if not self.scores:
            return {
                'total_scores': 0,
                'threat_levels': {},
                'avg_score': 0,
                'avg_confidence': 0
            }

        threat_levels = {}
        for level in ThreatLevel:
            threat_levels[level.name] = len([
                s for s in self.scores.values()
                if s.threat_level == level
            ])

        return {
            'total_scores': len(self.scores),
            'threat_levels': threat_levels,
            'avg_score': statistics.mean([s.score for s in self.scores.values()]),
            'avg_confidence': statistics.mean([s.confidence for s in self.scores.values()]),
            'entities_tracked': len(self.threat_history)
        }
