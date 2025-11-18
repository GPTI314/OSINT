"""Consumer Risk Factor Analysis.

Analyzes various risk factors for consumer credit applications.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConsumerRiskFactors:
    """Consumer risk factor analysis."""

    def analyze_identity_risk(self, identity_data: Dict[str, Any]) -> float:
        """Analyze identity verification risk (0-100, lower is better)."""
        risk_score = 0.0

        if not identity_data.get('verified', False):
            risk_score += 50

        if identity_data.get('inconsistencies', []):
            risk_score += len(identity_data['inconsistencies']) * 10

        return min(100, risk_score)

    def analyze_employment_risk(self, employment_data: Dict[str, Any]) -> float:
        """Analyze employment stability risk."""
        risk_score = 50.0  # Base risk

        employment_status = employment_data.get('status', '').lower()
        if employment_status == 'full_time':
            risk_score -= 20
        elif employment_status == 'unemployed':
            risk_score += 30

        years_employed = employment_data.get('years_at_current', 0)
        if years_employed > 5:
            risk_score -= 15
        elif years_employed < 1:
            risk_score += 15

        return max(0, min(100, risk_score))

    def analyze_income_risk(self, income_data: Dict[str, Any]) -> float:
        """Analyze income stability risk."""
        risk_score = 50.0

        monthly_income = income_data.get('monthly_income', 0)
        if monthly_income > 10000:
            risk_score -= 20
        elif monthly_income < 2000:
            risk_score += 20

        income_sources = income_data.get('sources', [])
        if len(income_sources) > 1:
            risk_score -= 10  # Multiple income sources reduce risk

        return max(0, min(100, risk_score))

    def analyze_payment_risk(self, payment_history: Dict[str, Any]) -> float:
        """Analyze payment behavior risk."""
        risk_score = 50.0

        on_time_percentage = payment_history.get('on_time_percentage', 100)
        if on_time_percentage >= 95:
            risk_score -= 30
        elif on_time_percentage < 80:
            risk_score += 30

        late_payments = payment_history.get('late_payments_12mo', 0)
        risk_score += late_payments * 5

        return max(0, min(100, risk_score))

    def analyze_debt_risk(self, debt_data: Dict[str, Any]) -> float:
        """Analyze debt burden risk."""
        risk_score = 50.0

        dti_ratio = debt_data.get('debt_to_income_ratio', 0.5)
        if dti_ratio < 0.30:
            risk_score -= 25
        elif dti_ratio > 0.50:
            risk_score += 30

        total_debt = debt_data.get('total_debt', 0)
        if total_debt > 100000:
            risk_score += 15

        return max(0, min(100, risk_score))

    def analyze_behavioral_risk(self, behavioral_data: Dict[str, Any]) -> float:
        """Analyze behavioral risk."""
        risk_score = 50.0

        stability = behavioral_data.get('stability', 'medium')
        if stability == 'high':
            risk_score -= 20
        elif stability == 'low':
            risk_score += 20

        return max(0, min(100, risk_score))

    def analyze_digital_footprint_risk(self, osint_data: Dict[str, Any]) -> float:
        """Analyze digital footprint risk."""
        risk_score = 50.0

        footprint_score = osint_data.get('digital_footprint_score', 50)
        risk_score = 100 - footprint_score

        return max(0, min(100, risk_score))

    def analyze_social_media_risk(self, social_data: Dict[str, Any]) -> float:
        """Analyze social media risk signals."""
        risk_score = 50.0

        if social_data.get('suspicious_activity', False):
            risk_score += 30

        if social_data.get('inconsistent_info', False):
            risk_score += 20

        return max(0, min(100, risk_score))
