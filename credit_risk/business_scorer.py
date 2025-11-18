"""Business Credit Risk Scoring Engine.

This module provides comprehensive business credit risk assessment
combining OSINT data with traditional financial analysis.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import (
    BusinessApplication, BusinessRiskScore, BusinessOSINTData,
    BusinessFinancialData, BusinessOperationalData, BusinessFraudIndicator,
    ApplicationStatus, RiskTier, RiskLevel, FraudSeverity
)
from credit_risk.business_factors import BusinessRiskFactors
from credit_risk.osint_collector import CreditRiskOSINTCollector

logger = logging.getLogger(__name__)


class BusinessCreditScorer:
    """
    Business credit risk scoring engine.

    Provides comprehensive business credit assessment including:
    - Company verification
    - Business registration validation
    - Financial statement analysis
    - Cash flow analysis
    - Industry risk assessment
    - Market position analysis
    - Management team assessment
    - Business model evaluation
    - Credit history analysis
    - Public records analysis
    - News and sentiment analysis
    - Risk tier classification
    """

    def __init__(self, db: AsyncSession):
        """Initialize business credit scorer."""
        self.db = db
        self.risk_factors = BusinessRiskFactors()
        self.osint_collector = CreditRiskOSINTCollector(db)

        # Score weights for different components
        self.weights = {
            'osint': 0.20,
            'financial': 0.40,
            'operational': 0.25,
            'industry': 0.10,
            'management': 0.05
        }

    async def assess_business(
        self,
        application_id: int,
        collect_osint: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive business credit assessment.

        Args:
            application_id: Business application ID
            collect_osint: Whether to collect fresh OSINT data

        Returns:
            Assessment results with risk score and recommendations
        """
        try:
            logger.info(f"Starting business credit assessment for application {application_id}")

            # Get application
            result = await self.db.execute(
                select(BusinessApplication).where(BusinessApplication.id == application_id)
            )
            application = result.scalar_one_or_none()

            if not application:
                raise ValueError(f"Application {application_id} not found")

            # Update status
            application.application_status = ApplicationStatus.ANALYZING
            await self.db.commit()

            # Collect OSINT data if requested
            if collect_osint:
                await self.osint_collector.collect_business_osint(application_id)

            # Get all related data
            osint_data = await self._get_osint_data(application_id)
            financial_data = await self._get_financial_data(application_id)
            operational_data = await self._get_operational_data(application_id)

            # Calculate component scores
            osint_score = await self.calculate_business_osint_score(osint_data)
            financial_score = await self.calculate_financial_score(
                financial_data, application
            )
            operational_score = await self.calculate_operational_score(
                operational_data, application
            )
            industry_score = await self.assess_industry_risk(
                application.industry, osint_data
            )
            management_score = await self.assess_management_team(
                operational_data
            )

            # Detect fraud
            fraud_indicators = await self.detect_business_fraud(
                application, osint_data, financial_data, operational_data
            )

            # Calculate overall score (0-1000 scale for businesses)
            overall_score = await self._calculate_overall_score(
                osint_score, financial_score, operational_score,
                industry_score, management_score
            )

            # Determine risk tier and level
            risk_tier = self._determine_risk_tier(overall_score)
            risk_level = self._determine_risk_level(overall_score)

            # Calculate probability of default
            probability_of_default = await self._calculate_probability_of_default(
                application, overall_score, financial_score
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                overall_score, risk_tier, probability_of_default,
                application.requested_amount, financial_data
            )

            # Save risk score
            risk_score = BusinessRiskScore(
                application_id=application_id,
                overall_score=int(overall_score),
                osint_score=int(osint_score),
                financial_score=int(financial_score),
                operational_score=int(operational_score),
                industry_score=int(industry_score),
                management_score=int(management_score),
                risk_tier=risk_tier,
                risk_level=risk_level,
                probability_of_default=probability_of_default,
                recommended_interest_rate=recommendations['interest_rate'],
                recommended_loan_amount=recommendations['loan_amount'],
                recommended_term_months=recommendations['term_months'],
                approval_recommendation=recommendations['recommendation'],
                score_components={
                    'company_verification': osint_data.get('verification_score', 0),
                    'financial_health': financial_score,
                    'operational_stability': operational_score,
                    'industry_outlook': industry_score,
                    'management_quality': management_score,
                    'fraud_indicators': len(fraud_indicators)
                }
            )

            self.db.add(risk_score)

            # Update application status
            application.application_status = ApplicationStatus.SCORED
            await self.db.commit()

            logger.info(
                f"Business assessment completed for application {application_id}. "
                f"Score: {overall_score}, Risk: {risk_tier.value}"
            )

            return {
                'application_id': application_id,
                'overall_score': overall_score,
                'risk_tier': risk_tier.value,
                'risk_level': risk_level.value,
                'probability_of_default': probability_of_default,
                'recommendations': recommendations,
                'score_breakdown': {
                    'osint_score': osint_score,
                    'financial_score': financial_score,
                    'operational_score': operational_score,
                    'industry_score': industry_score,
                    'management_score': management_score
                },
                'fraud_indicators': len(fraud_indicators),
                'assessed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error assessing business application {application_id}: {str(e)}")
            if application:
                application.application_status = ApplicationStatus.PENDING
                await self.db.commit()
            raise

    async def calculate_business_osint_score(self, osint_data: Dict[str, Any]) -> float:
        """Calculate risk score from business OSINT data (0-1000 scale)."""
        verification_score = osint_data.get('verification_score', 500)
        domain_score = osint_data.get('domain_score', 500)
        social_presence_score = osint_data.get('social_presence_score', 500)
        news_sentiment_score = osint_data.get('news_sentiment_score', 500)
        review_score = osint_data.get('review_score', 500)

        osint_score = (
            verification_score * 0.30 +
            domain_score * 0.20 +
            social_presence_score * 0.20 +
            news_sentiment_score * 0.20 +
            review_score * 0.10
        )

        return max(0, min(1000, osint_score))

    async def calculate_financial_score(
        self,
        financial_data: Optional[BusinessFinancialData],
        application: BusinessApplication
    ) -> float:
        """Calculate financial health score (0-1000 scale)."""
        if not financial_data:
            return 500  # Default mid-range

        score_components = []

        # Profitability (30%)
        if financial_data.income_statement:
            profitability_score = self._analyze_profitability(
                financial_data.income_statement
            )
            score_components.append(profitability_score * 0.30)

        # Liquidity (25%)
        if financial_data.balance_sheet:
            liquidity_score = self._analyze_liquidity(
                financial_data.balance_sheet
            )
            score_components.append(liquidity_score * 0.25)

        # Solvency (20%)
        if financial_data.financial_ratios:
            solvency_score = self._analyze_solvency(
                financial_data.financial_ratios
            )
            score_components.append(solvency_score * 0.20)

        # Cash flow (20%)
        if financial_data.cash_flow_statement:
            cash_flow_score = self._analyze_cash_flow(
                financial_data.cash_flow_statement
            )
            score_components.append(cash_flow_score * 0.20)

        # Credit history (5%)
        if financial_data.credit_history:
            credit_history_score = self._analyze_credit_history(
                financial_data.credit_history
            )
            score_components.append(credit_history_score * 0.05)

        financial_score = sum(score_components) if score_components else 500

        return max(0, min(1000, financial_score))

    async def calculate_operational_score(
        self,
        operational_data: Optional[BusinessOperationalData],
        application: BusinessApplication
    ) -> float:
        """Calculate operational risk score (0-1000 scale)."""
        if not operational_data:
            return 500

        score = 500  # Base score

        # Business age bonus
        if application.founded_date:
            years_in_business = (datetime.utcnow() - application.founded_date).days / 365
            if years_in_business > 10:
                score += 100
            elif years_in_business > 5:
                score += 50
            elif years_in_business < 1:
                score -= 100

        # Employee count
        if application.number_of_employees:
            if application.number_of_employees > 100:
                score += 50
            elif application.number_of_employees > 50:
                score += 25

        # Market position
        if operational_data.market_position:
            position_scores = {
                'leader': 100,
                'strong': 50,
                'moderate': 0,
                'weak': -50,
                'struggling': -100
            }
            score += position_scores.get(operational_data.market_position, 0)

        return max(0, min(1000, score))

    async def assess_industry_risk(
        self,
        industry: str,
        market_data: Dict[str, Any]
    ) -> float:
        """Assess industry-specific risks (0-1000 scale)."""
        # Industry risk baseline
        high_risk_industries = ['crypto', 'cannabis', 'gambling']
        moderate_risk_industries = ['retail', 'restaurant', 'hospitality']
        low_risk_industries = ['healthcare', 'technology', 'finance']

        if industry and industry.lower() in high_risk_industries:
            score = 400
        elif industry and industry.lower() in moderate_risk_industries:
            score = 600
        elif industry and industry.lower() in low_risk_industries:
            score = 800
        else:
            score = 600

        return score

    async def assess_management_team(
        self,
        operational_data: Optional[BusinessOperationalData]
    ) -> float:
        """Management team assessment (0-1000 scale)."""
        if not operational_data or not operational_data.management_team:
            return 500

        score = 500

        # Analyze management team experience and quality
        management_team = operational_data.management_team
        if isinstance(management_team, dict):
            team_size = len(management_team.get('members', []))
            if team_size >= 3:
                score += 100
            elif team_size >= 1:
                score += 50

        return max(0, min(1000, score))

    async def detect_business_fraud(
        self,
        application: BusinessApplication,
        osint_data: Dict[str, Any],
        financial_data: Optional[BusinessFinancialData],
        operational_data: Optional[BusinessOperationalData]
    ) -> List[BusinessFraudIndicator]:
        """Detect business fraud indicators."""
        fraud_indicators = []

        try:
            # Company registration issues
            if osint_data.get('registration_verification_failed'):
                indicator = BusinessFraudIndicator(
                    application_id=application.id,
                    indicator_type='registration_verification_failed',
                    severity=FraudSeverity.CRITICAL,
                    description='Company registration could not be verified',
                    evidence=osint_data.get('registration_details', {})
                )
                fraud_indicators.append(indicator)

            # Domain age mismatch
            if osint_data.get('domain_age_mismatch'):
                indicator = BusinessFraudIndicator(
                    application_id=application.id,
                    indicator_type='domain_age_mismatch',
                    severity=FraudSeverity.MEDIUM,
                    description='Domain age inconsistent with stated business age',
                    evidence=osint_data['domain_age_mismatch']
                )
                fraud_indicators.append(indicator)

            # Negative news
            if osint_data.get('negative_news_count', 0) > 5:
                indicator = BusinessFraudIndicator(
                    application_id=application.id,
                    indicator_type='negative_news',
                    severity=FraudSeverity.HIGH,
                    description='Multiple negative news articles found',
                    evidence={'negative_news_count': osint_data['negative_news_count']}
                )
                fraud_indicators.append(indicator)

            # Financial statement anomalies
            if financial_data and osint_data.get('revenue_mismatch'):
                indicator = BusinessFraudIndicator(
                    application_id=application.id,
                    indicator_type='revenue_mismatch',
                    severity=FraudSeverity.HIGH,
                    description='Revenue figures inconsistent across sources',
                    evidence=osint_data['revenue_mismatch']
                )
                fraud_indicators.append(indicator)

            # Save fraud indicators
            for indicator in fraud_indicators:
                self.db.add(indicator)

            if fraud_indicators:
                await self.db.commit()
                logger.warning(
                    f"Detected {len(fraud_indicators)} fraud indicators "
                    f"for business application {application.id}"
                )

            return fraud_indicators

        except Exception as e:
            logger.error(f"Error detecting business fraud signals: {str(e)}")
            return fraud_indicators

    async def analyze_cash_flow(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cash flow analysis and forecasting."""
        # Placeholder implementation
        return {
            'current_cash_flow': 0,
            'projected_cash_flow': 0,
            'health_status': 'stable'
        }

    # Helper methods

    async def _get_osint_data(self, application_id: int) -> Dict[str, Any]:
        """Get aggregated OSINT data for business application."""
        result = await self.db.execute(
            select(BusinessOSINTData).where(
                BusinessOSINTData.application_id == application_id
            )
        )
        osint_records = result.scalars().all()

        aggregated_data = {
            'verification_score': 500,
            'domain_score': 500,
            'social_presence_score': 500,
            'news_sentiment_score': 500,
            'review_score': 500
        }

        for record in osint_records:
            if record.data_type == 'domain':
                aggregated_data['domain_score'] = record.data.get('score', 500)
            elif record.data_type == 'social_media':
                aggregated_data['social_presence_score'] = record.data.get('score', 500)
            elif record.data_type == 'news':
                aggregated_data['news_sentiment_score'] = record.data.get('sentiment_score', 500)
            elif record.data_type == 'reviews':
                aggregated_data['review_score'] = record.data.get('average_rating', 3) * 200

        return aggregated_data

    async def _get_financial_data(
        self,
        application_id: int
    ) -> Optional[BusinessFinancialData]:
        """Get financial data for business application."""
        result = await self.db.execute(
            select(BusinessFinancialData).where(
                BusinessFinancialData.application_id == application_id
            ).order_by(BusinessFinancialData.collected_at.desc())
        )
        return result.scalar_one_or_none()

    async def _get_operational_data(
        self,
        application_id: int
    ) -> Optional[BusinessOperationalData]:
        """Get operational data for business application."""
        result = await self.db.execute(
            select(BusinessOperationalData).where(
                BusinessOperationalData.application_id == application_id
            ).order_by(BusinessOperationalData.collected_at.desc())
        )
        return result.scalar_one_or_none()

    async def _calculate_overall_score(
        self,
        osint_score: float,
        financial_score: float,
        operational_score: float,
        industry_score: float,
        management_score: float
    ) -> float:
        """Calculate overall business credit score."""
        overall_score = (
            osint_score * self.weights['osint'] +
            financial_score * self.weights['financial'] +
            operational_score * self.weights['operational'] +
            industry_score * self.weights['industry'] +
            management_score * self.weights['management']
        )

        return max(0, min(1000, overall_score))

    def _determine_risk_tier(self, score: float) -> RiskTier:
        """Determine risk tier from score (0-1000 scale)."""
        if score >= 800:
            return RiskTier.EXCELLENT
        elif score >= 650:
            return RiskTier.GOOD
        elif score >= 500:
            return RiskTier.FAIR
        elif score >= 350:
            return RiskTier.POOR
        else:
            return RiskTier.HIGH_RISK

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        if score >= 750:
            return RiskLevel.LOW
        elif score >= 600:
            return RiskLevel.MEDIUM
        elif score >= 450:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    async def _calculate_probability_of_default(
        self,
        application: BusinessApplication,
        overall_score: float,
        financial_score: float
    ) -> float:
        """Calculate probability of default."""
        # Simple formula: lower score = higher probability
        probability = 1 - (overall_score / 1000)
        probability = max(0.01, min(0.99, probability))
        return round(probability, 4)

    def _generate_recommendations(
        self,
        overall_score: float,
        risk_tier: RiskTier,
        probability_of_default: float,
        requested_amount: float,
        financial_data: Optional[BusinessFinancialData]
    ) -> Dict[str, Any]:
        """Generate lending recommendations for business."""
        recommendations = {
            'recommendation': 'manual_review',
            'interest_rate': 12.0,
            'loan_amount': requested_amount or 0,
            'term_months': 60,
            'reasoning': []
        }

        # Determine approval recommendation
        if overall_score >= 750 and probability_of_default < 0.15:
            recommendations['recommendation'] = 'approve'
            recommendations['reasoning'].append('Strong business profile')
        elif overall_score < 400 or probability_of_default > 0.50:
            recommendations['recommendation'] = 'reject'
            recommendations['reasoning'].append('High business risk')
        else:
            recommendations['reasoning'].append('Requires manual review')

        # Calculate interest rate
        if overall_score >= 800:
            recommendations['interest_rate'] = 6.0
        elif overall_score >= 650:
            recommendations['interest_rate'] = 9.0
        elif overall_score >= 500:
            recommendations['interest_rate'] = 12.0
        elif overall_score >= 350:
            recommendations['interest_rate'] = 16.0
        else:
            recommendations['interest_rate'] = 20.0

        # Adjust loan amount based on risk
        if probability_of_default > 0.30:
            recommended_amount = (requested_amount or 0) * 0.6
            recommendations['loan_amount'] = recommended_amount
            recommendations['reasoning'].append('Loan amount reduced due to risk')

        return recommendations

    def _analyze_profitability(self, income_statement: Dict[str, Any]) -> float:
        """Analyze profitability from income statement."""
        return 700.0  # Placeholder

    def _analyze_liquidity(self, balance_sheet: Dict[str, Any]) -> float:
        """Analyze liquidity from balance sheet."""
        return 700.0  # Placeholder

    def _analyze_solvency(self, financial_ratios: Dict[str, Any]) -> float:
        """Analyze solvency from financial ratios."""
        return 700.0  # Placeholder

    def _analyze_cash_flow(self, cash_flow_statement: Dict[str, Any]) -> float:
        """Analyze cash flow statement."""
        return 700.0  # Placeholder

    def _analyze_credit_history(self, credit_history: Dict[str, Any]) -> float:
        """Analyze business credit history."""
        return 700.0  # Placeholder
