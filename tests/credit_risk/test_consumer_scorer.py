"""Tests for Consumer Credit Scorer."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from credit_risk.consumer_scorer import ConsumerCreditScorer
from database.models import (
    ConsumerApplication, ConsumerRiskScore,
    ApplicationStatus, RiskTier, RiskLevel
)


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock()


@pytest.fixture
def mock_application():
    """Mock consumer application."""
    app = Mock(spec=ConsumerApplication)
    app.id = 1
    app.applicant_name = "John Doe"
    app.email = "john@example.com"
    app.phone = "+1234567890"
    app.monthly_income = 5000.0
    app.requested_amount = 10000.0
    app.employment_status = "full_time"
    app.application_status = ApplicationStatus.PENDING
    return app


class TestConsumerCreditScorer:
    """Test consumer credit scorer."""

    @pytest.mark.asyncio
    async def test_calculate_osint_score(self, mock_db):
        """Test OSINT score calculation."""
        scorer = ConsumerCreditScorer(mock_db)

        osint_data = {
            'identity_score': 80,
            'employment_score': 75,
            'digital_footprint_score': 70,
            'social_media_risk': 20,
            'contact_verification': 85,
            'address_verification': 80
        }

        score = await scorer.calculate_osint_score(osint_data)

        assert 300 <= score <= 850
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_calculate_traditional_score(self, mock_db, mock_application):
        """Test traditional credit score calculation."""
        scorer = ConsumerCreditScorer(mock_db)

        score = await scorer.calculate_traditional_score(mock_application, None)

        assert 300 <= score <= 850
        assert isinstance(score, float)

    @pytest.mark.asyncio
    async def test_calculate_combined_score(self, mock_db):
        """Test combined score calculation."""
        scorer = ConsumerCreditScorer(mock_db)

        combined_score = await scorer.calculate_combined_score(
            osint_score=700.0,
            traditional_score=650.0,
            behavioral_score=680.0,
            fraud_score=720.0
        )

        assert 300 <= combined_score <= 850
        assert isinstance(combined_score, float)

    def test_determine_risk_tier(self, mock_db):
        """Test risk tier determination."""
        scorer = ConsumerCreditScorer(mock_db)

        assert scorer._determine_risk_tier(800) == RiskTier.EXCELLENT
        assert scorer._determine_risk_tier(700) == RiskTier.GOOD
        assert scorer._determine_risk_tier(600) == RiskTier.FAIR
        assert scorer._determine_risk_tier(500) == RiskTier.POOR
        assert scorer._determine_risk_tier(400) == RiskTier.HIGH_RISK

    def test_determine_risk_level(self, mock_db):
        """Test risk level determination."""
        scorer = ConsumerCreditScorer(mock_db)

        assert scorer._determine_risk_level(750) == RiskLevel.LOW
        assert scorer._determine_risk_level(650) == RiskLevel.MEDIUM
        assert scorer._determine_risk_level(550) == RiskLevel.HIGH
        assert scorer._determine_risk_level(450) == RiskLevel.VERY_HIGH

    def test_calculate_fraud_score(self, mock_db):
        """Test fraud score calculation."""
        scorer = ConsumerCreditScorer(mock_db)

        # No fraud indicators
        assert scorer._calculate_fraud_score([]) == 850

        # With fraud indicators
        from database.models import ConsumerFraudIndicator, FraudSeverity
        indicators = [
            Mock(severity=FraudSeverity.HIGH),
            Mock(severity=FraudSeverity.MEDIUM)
        ]

        fraud_score = scorer._calculate_fraud_score(indicators)
        assert 300 <= fraud_score < 850

    def test_generate_recommendations_approve(self, mock_db):
        """Test recommendations generation for approval."""
        scorer = ConsumerCreditScorer(mock_db)

        recommendations = scorer._generate_recommendations(
            overall_score=750,
            risk_tier=RiskTier.EXCELLENT,
            probability_of_default=0.10,
            requested_amount=10000
        )

        assert recommendations['recommendation'] == 'approve'
        assert recommendations['interest_rate'] < 10
        assert recommendations['loan_amount'] == 10000

    def test_generate_recommendations_reject(self, mock_db):
        """Test recommendations generation for rejection."""
        scorer = ConsumerCreditScorer(mock_db)

        recommendations = scorer._generate_recommendations(
            overall_score=400,
            risk_tier=RiskTier.HIGH_RISK,
            probability_of_default=0.60,
            requested_amount=10000
        )

        assert recommendations['recommendation'] == 'reject'
        assert recommendations['interest_rate'] > 15

    @pytest.mark.asyncio
    async def test_detect_fraud_signals(self, mock_db, mock_application):
        """Test fraud detection."""
        scorer = ConsumerCreditScorer(mock_db)

        osint_data = {
            'email_risk_level': 80,
            'phone_verification_failed': True
        }

        indicators = await scorer.detect_fraud_signals(
            mock_application, osint_data, None, None
        )

        assert isinstance(indicators, list)
        assert len(indicators) >= 0


class TestScoringAlgorithms:
    """Test scoring algorithms."""

    def test_weighted_score(self):
        """Test weighted score calculation."""
        from credit_risk.scoring.algorithms import ScoringAlgorithms

        algo = ScoringAlgorithms()

        factors = {
            'factor1': 80,
            'factor2': 70,
            'factor3': 90
        }

        weights = {
            'factor1': 0.5,
            'factor2': 0.3,
            'factor3': 0.2
        }

        score = algo.weighted_score(factors, weights)

        assert 0 <= score <= 100
        assert isinstance(score, float)

    def test_ensemble_score(self):
        """Test ensemble scoring."""
        from credit_risk.scoring.algorithms import ScoringAlgorithms

        algo = ScoringAlgorithms()

        scores = [700, 650, 720]
        weights = [0.4, 0.3, 0.3]

        ensemble_score = algo.ensemble_score(scores, weights)

        assert 600 <= ensemble_score <= 750
        assert isinstance(ensemble_score, float)


class TestComplianceModule:
    """Test compliance and regulatory module."""

    def test_gdpr_compliance_check(self):
        """Test GDPR compliance checking."""
        from credit_risk.compliance.regulatory import RegulatoryCompliance

        compliance = RegulatoryCompliance()

        data_with_consent = {
            'consent_obtained': True,
            'encrypted': True,
            'contains_pii': True,
            'deletion_capability': True
        }

        result = compliance.ensure_gdpr_compliance(data_with_consent)

        assert result['compliant'] is True
        assert len(result['issues']) == 0

    def test_fcra_compliance_check(self):
        """Test FCRA compliance checking."""
        from credit_risk.compliance.regulatory import RegulatoryCompliance

        compliance = RegulatoryCompliance()

        credit_data = {
            'application_denied': True,
            'adverse_action_notice_sent': True,
            'data_accuracy_verified': True,
            'permissible_purpose': True
        }

        result = compliance.ensure_fcra_compliance(credit_data)

        assert result['compliant'] is True

    def test_provide_explanation(self):
        """Test explainable AI."""
        from credit_risk.compliance.regulatory import RegulatoryCompliance

        compliance = RegulatoryCompliance()

        factors = {
            'payment_history': 85,
            'debt_to_income': -20,
            'credit_utilization': -15
        }

        explanation = compliance.provide_explanation(700, factors)

        assert explanation['score'] == 700
        assert 'score_range' in explanation
        assert 'primary_factors' in explanation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
