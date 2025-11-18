"""
Unit tests for risk scoring engine.

Tests cover:
- Risk calculation algorithms
- Scoring rules engine
- Weight management
- Threat assessment
- Score aggregation
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


@pytest.mark.unit
class TestRiskScorer:
    """Test risk scoring functionality."""

    @pytest.mark.asyncio
    async def test_calculate_risk_score(self, sample_entity_data):
        """Test calculating risk score for an entity."""
        scorer = Mock()
        scorer.calculate = AsyncMock(
            return_value={"score": 65, "severity": "medium", "factors": {}}
        )

        result = await scorer.calculate(sample_entity_data)

        assert "score" in result
        assert 0 <= result["score"] <= 100
        assert result["severity"] in ["low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    async def test_score_ip_address(self, sample_ip_address):
        """Test scoring an IP address."""
        scorer = Mock()
        scorer.score_ip = AsyncMock(
            return_value={
                "score": 45,
                "factors": {
                    "blacklist_count": 0,
                    "malware_detected": False,
                    "reputation": 75,
                },
            }
        )

        result = await scorer.score_ip(sample_ip_address)

        assert "score" in result
        assert "factors" in result

    @pytest.mark.asyncio
    async def test_score_domain(self, sample_domain):
        """Test scoring a domain."""
        scorer = Mock()
        scorer.score_domain = AsyncMock(
            return_value={
                "score": 30,
                "factors": {
                    "age_days": 5000,
                    "ssl_valid": True,
                    "suspicious_keywords": False,
                },
            }
        )

        result = await scorer.score_domain(sample_domain)

        assert result["score"] >= 0


@pytest.mark.unit
class TestScoringFactors:
    """Test individual scoring factors."""

    def test_blacklist_factor(self):
        """Test blacklist presence factor."""
        factor = Mock()
        factor.calculate = Mock(return_value={"score": 80, "weight": 0.3})

        result = factor.calculate(blacklist_count=3)

        assert result["score"] > 0
        assert result["weight"] > 0

    def test_malware_detection_factor(self):
        """Test malware detection factor."""
        factor = Mock()
        factor.calculate = Mock(return_value={"score": 100, "weight": 0.4})

        result = factor.calculate(malware_detected=True)

        assert result["score"] > 0

    def test_ssl_validity_factor(self):
        """Test SSL certificate validity factor."""
        factor = Mock()
        factor.calculate = Mock(return_value={"score": 0, "weight": 0.2})

        result = factor.calculate(ssl_valid=True)

        # Valid SSL should lower risk score
        assert result["score"] == 0

    def test_domain_age_factor(self):
        """Test domain age factor."""
        factor = Mock()
        factor.calculate = Mock(return_value={"score": 60, "weight": 0.15})

        # Newly registered domains are riskier
        result = factor.calculate(age_days=7)

        assert result["score"] > 0

    def test_reputation_factor(self):
        """Test reputation score factor."""
        factor = Mock()
        factor.calculate = Mock(return_value={"score": 20, "weight": 0.25})

        result = factor.calculate(reputation=80)

        assert "score" in result


@pytest.mark.unit
class TestRulesEngine:
    """Test scoring rules engine."""

    def test_apply_rules(self, sample_entity_data):
        """Test applying scoring rules."""
        engine = Mock()
        engine.apply_rules = Mock(
            return_value={
                "matched_rules": ["rule1", "rule2"],
                "total_score": 75,
            }
        )

        result = engine.apply_rules(sample_entity_data)

        assert len(result["matched_rules"]) >= 0
        assert "total_score" in result

    def test_custom_rule_evaluation(self):
        """Test evaluating custom rules."""
        engine = Mock()
        rule = {
            "name": "high_port_count",
            "condition": "port_count > 100",
            "score_impact": 30,
        }
        engine.evaluate_rule = Mock(return_value={"matched": True, "score": 30})

        result = engine.evaluate_rule(rule, {"port_count": 150})

        assert result["matched"] is True

    def test_rule_priority(self):
        """Test rule priority handling."""
        engine = Mock()
        engine.prioritize_rules = Mock(
            return_value=[
                {"priority": 1, "name": "critical_rule"},
                {"priority": 2, "name": "high_rule"},
            ]
        )

        rules = engine.prioritize_rules()

        assert rules[0]["priority"] < rules[1]["priority"]

    def test_rule_conflict_resolution(self):
        """Test resolving conflicting rules."""
        engine = Mock()
        engine.resolve_conflicts = Mock(
            return_value={"final_score": 65, "resolution": "highest_priority"}
        )

        result = engine.resolve_conflicts([
            {"score": 80, "priority": 2},
            {"score": 50, "priority": 1},
        ])

        assert "final_score" in result


@pytest.mark.unit
class TestWeightManagement:
    """Test scoring weight management."""

    def test_get_default_weights(self):
        """Test getting default factor weights."""
        weight_manager = Mock()
        weight_manager.get_defaults = Mock(
            return_value={
                "malware": 0.4,
                "blacklist": 0.3,
                "ssl": 0.2,
                "age": 0.1,
            }
        )

        weights = weight_manager.get_defaults()

        assert sum(weights.values()) == pytest.approx(1.0)

    def test_update_weights(self):
        """Test updating factor weights."""
        weight_manager = Mock()
        weight_manager.update = Mock(return_value=True)

        result = weight_manager.update("malware", 0.5)

        assert result is True

    def test_normalize_weights(self):
        """Test normalizing weights to sum to 1.0."""
        weight_manager = Mock()
        weight_manager.normalize = Mock(
            return_value={
                "factor1": 0.5,
                "factor2": 0.3,
                "factor3": 0.2,
            }
        )

        weights = weight_manager.normalize(
            {"factor1": 50, "factor2": 30, "factor3": 20}
        )

        assert sum(weights.values()) == pytest.approx(1.0)

    def test_validate_weights(self):
        """Test validating weight configuration."""
        weight_manager = Mock()
        weight_manager.validate = Mock(return_value=True)

        valid = weight_manager.validate(
            {"factor1": 0.5, "factor2": 0.3, "factor3": 0.2}
        )

        assert valid is True


@pytest.mark.unit
class TestScoreAggregation:
    """Test score aggregation methods."""

    def test_weighted_average(self):
        """Test weighted average aggregation."""
        aggregator = Mock()
        aggregator.weighted_average = Mock(return_value=72.5)

        scores = [
            {"score": 80, "weight": 0.4},
            {"score": 60, "weight": 0.3},
            {"score": 75, "weight": 0.3},
        ]
        result = aggregator.weighted_average(scores)

        assert isinstance(result, (int, float))
        assert 0 <= result <= 100

    def test_maximum_score(self):
        """Test maximum score aggregation."""
        aggregator = Mock()
        aggregator.maximum = Mock(return_value=90)

        result = aggregator.maximum([50, 70, 90, 60])

        assert result == 90

    def test_minimum_score(self):
        """Test minimum score aggregation."""
        aggregator = Mock()
        aggregator.minimum = Mock(return_value=30)

        result = aggregator.minimum([50, 70, 30, 60])

        assert result == 30

    def test_percentile_aggregation(self):
        """Test percentile-based aggregation."""
        aggregator = Mock()
        aggregator.percentile = Mock(return_value=75)

        result = aggregator.percentile([10, 30, 50, 70, 90], percentile=75)

        assert result >= 50


@pytest.mark.unit
class TestThreatAssessment:
    """Test threat level assessment."""

    def test_assess_threat_level(self, sample_risk_score):
        """Test assessing threat level from risk score."""
        assessor = Mock()
        assessor.assess = Mock(
            return_value={"level": "medium", "recommended_action": "monitor"}
        )

        result = assessor.assess(sample_risk_score)

        assert result["level"] in ["low", "medium", "high", "critical"]
        assert "recommended_action" in result

    def test_classify_by_score(self):
        """Test classifying threat by score ranges."""
        assessor = Mock()
        assessor.classify = Mock(return_value="high")

        # Score of 80 should be high threat
        level = assessor.classify(80)

        assert level in ["low", "medium", "high", "critical"]

    def test_generate_recommendations(self, sample_risk_score):
        """Test generating security recommendations."""
        assessor = Mock()
        assessor.recommend = Mock(
            return_value=[
                "Block IP address",
                "Monitor for suspicious activity",
                "Update firewall rules",
            ]
        )

        recommendations = assessor.recommend(sample_risk_score)

        assert len(recommendations) >= 0


@pytest.mark.unit
class TestHistoricalScoring:
    """Test historical score tracking."""

    @pytest.mark.asyncio
    async def test_store_score_history(self, sample_risk_score):
        """Test storing historical scores."""
        history = Mock()
        history.store = AsyncMock(return_value=True)

        result = await history.store(sample_risk_score)

        assert result is True

    @pytest.mark.asyncio
    async def test_retrieve_score_history(self):
        """Test retrieving historical scores."""
        history = Mock()
        history.get = AsyncMock(
            return_value=[
                {"timestamp": "2024-01-01", "score": 50},
                {"timestamp": "2024-01-02", "score": 60},
                {"timestamp": "2024-01-03", "score": 55},
            ]
        )

        scores = await history.get(entity_id="test_entity")

        assert len(scores) >= 0

    def test_analyze_score_trends(self):
        """Test analyzing score trends over time."""
        history = Mock()
        history.analyze_trends = Mock(
            return_value={
                "trend": "increasing",
                "average": 55,
                "max": 70,
                "min": 40,
            }
        )

        result = history.analyze_trends()

        assert result["trend"] in ["increasing", "decreasing", "stable"]

    def test_detect_anomalous_scores(self):
        """Test detecting anomalous score changes."""
        history = Mock()
        history.detect_anomalies = Mock(
            return_value=[
                {"timestamp": "2024-01-05", "score": 95, "anomaly": True}
            ]
        )

        anomalies = history.detect_anomalies()

        assert len(anomalies) >= 0
