"""Business Risk Factor Analysis.

Analyzes various risk factors for business credit applications.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class BusinessRiskFactors:
    """Business risk factor analysis."""

    def analyze_financial_risk(self, financial_data: Dict[str, Any]) -> float:
        """Analyze financial health risk."""
        risk_score = 50.0

        profitability = financial_data.get('net_profit_margin', 0)
        if profitability > 0.15:
            risk_score -= 20
        elif profitability < 0:
            risk_score += 30

        revenue_growth = financial_data.get('revenue_growth_rate', 0)
        if revenue_growth > 0.20:
            risk_score -= 15
        elif revenue_growth < 0:
            risk_score += 20

        return max(0, min(100, risk_score))

    def analyze_operational_risk(self, operational_data: Dict[str, Any]) -> float:
        """Analyze operational stability risk."""
        risk_score = 50.0

        years_in_business = operational_data.get('years_in_business', 0)
        if years_in_business > 10:
            risk_score -= 20
        elif years_in_business < 2:
            risk_score += 25

        employee_count = operational_data.get('employee_count', 0)
        if employee_count > 100:
            risk_score -= 10
        elif employee_count < 5:
            risk_score += 10

        return max(0, min(100, risk_score))

    def analyze_industry_risk(self, industry_data: Dict[str, Any]) -> float:
        """Analyze industry-specific risk."""
        risk_score = 50.0

        industry = industry_data.get('industry', '').lower()
        high_risk_industries = ['crypto', 'cannabis', 'gambling']
        if industry in high_risk_industries:
            risk_score += 30

        market_outlook = industry_data.get('market_outlook', 'neutral')
        if market_outlook == 'growing':
            risk_score -= 15
        elif market_outlook == 'declining':
            risk_score += 20

        return max(0, min(100, risk_score))

    def analyze_market_risk(self, market_data: Dict[str, Any]) -> float:
        """Analyze market position risk."""
        risk_score = 50.0

        market_position = market_data.get('market_position', 'moderate')
        if market_position == 'leader':
            risk_score -= 25
        elif market_position == 'struggling':
            risk_score += 25

        competition_level = market_data.get('competition_level', 'medium')
        if competition_level == 'high':
            risk_score += 10

        return max(0, min(100, risk_score))

    def analyze_management_risk(self, management_data: Dict[str, Any]) -> float:
        """Analyze management quality risk."""
        risk_score = 50.0

        experience_years = management_data.get('avg_experience_years', 0)
        if experience_years > 15:
            risk_score -= 15
        elif experience_years < 5:
            risk_score += 15

        team_size = management_data.get('team_size', 0)
        if team_size >= 3:
            risk_score -= 10

        return max(0, min(100, risk_score))

    def analyze_business_model_risk(self, business_model: Dict[str, Any]) -> float:
        """Analyze business model risk."""
        risk_score = 50.0

        revenue_model = business_model.get('revenue_model', '')
        if revenue_model in ['subscription', 'recurring']:
            risk_score -= 15
        elif revenue_model in ['one-time', 'project-based']:
            risk_score += 10

        customer_concentration = business_model.get('top_customer_percentage', 0)
        if customer_concentration > 0.40:
            risk_score += 20  # High concentration risk

        return max(0, min(100, risk_score))

    def analyze_credit_history_risk(self, credit_history: Dict[str, Any]) -> float:
        """Analyze credit history risk."""
        risk_score = 50.0

        payment_history_score = credit_history.get('payment_score', 50)
        risk_score = 100 - payment_history_score

        defaults = credit_history.get('defaults_count', 0)
        risk_score += defaults * 15

        return max(0, min(100, risk_score))

    def analyze_public_perception_risk(self, sentiment_data: Dict[str, Any]) -> float:
        """Analyze public perception risk."""
        risk_score = 50.0

        sentiment_score = sentiment_data.get('sentiment_score', 0.5)
        if sentiment_score > 0.7:
            risk_score -= 20
        elif sentiment_score < 0.3:
            risk_score += 25

        negative_news_count = sentiment_data.get('negative_news_count', 0)
        risk_score += negative_news_count * 5

        return max(0, min(100, risk_score))
