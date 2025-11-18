"""Credit Risk Scoring Module for OSINT Intelligence Platform.

This module provides comprehensive credit risk assessment capabilities
combining OSINT data with traditional financial analysis for both
consumer and business credit applications.
"""

__version__ = "1.0.0"

from credit_risk.consumer_scorer import ConsumerCreditScorer
from credit_risk.business_scorer import BusinessCreditScorer
from credit_risk.osint_collector import CreditRiskOSINTCollector
from credit_risk.consumer_factors import ConsumerRiskFactors
from credit_risk.business_factors import BusinessRiskFactors

__all__ = [
    "ConsumerCreditScorer",
    "BusinessCreditScorer",
    "CreditRiskOSINTCollector",
    "ConsumerRiskFactors",
    "BusinessRiskFactors",
]
