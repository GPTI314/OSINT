"""Consumer Credit Risk Scoring Engine.

This module provides comprehensive consumer credit risk assessment
combining OSINT data with traditional financial indicators.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import (
    ConsumerApplication, ConsumerRiskScore, ConsumerOSINTData,
    ConsumerFinancialData, ConsumerBehavioralData, ConsumerFraudIndicator,
    ApplicationStatus, RiskTier, RiskLevel, FraudSeverity
)
from credit_risk.consumer_factors import ConsumerRiskFactors
from credit_risk.osint_collector import CreditRiskOSINTCollector
from credit_risk.scoring.algorithms import ScoringAlgorithms
from credit_risk.models.risk_models import CreditRiskModels

logger = logging.getLogger(__name__)


class ConsumerCreditScorer:
    """
    Consumer credit risk scoring engine.

    Provides comprehensive consumer credit assessment including:
    - Personal information validation
    - Digital footprint analysis
    - Social media risk signals
    - Employment verification
    - Income estimation
    - Payment behavior analysis
    - Debt-to-income calculation
    - Credit utilization analysis
    - Behavioral scoring
    - Fraud detection
    - Identity verification
    - Risk tier classification
    """

    def __init__(self, db: AsyncSession):
        """Initialize consumer credit scorer."""
        self.db = db
        self.risk_factors = ConsumerRiskFactors()
        self.osint_collector = CreditRiskOSINTCollector(db)
        self.scoring_algorithms = ScoringAlgorithms()
        self.ml_models = CreditRiskModels()

        # Score weights for different components
        self.weights = {
            'osint': 0.30,
            'traditional': 0.35,
            'behavioral': 0.20,
            'fraud': 0.15
        }

    async def assess_consumer(
        self,
        application_id: int,
        collect_osint: bool = True
    ) -> Dict[str, Any]:
        """
        Comprehensive consumer credit assessment.

        Args:
            application_id: Consumer application ID
            collect_osint: Whether to collect fresh OSINT data

        Returns:
            Assessment results with risk score and recommendations
        """
        try:
            logger.info(f"Starting consumer credit assessment for application {application_id}")

            # Get application
            result = await self.db.execute(
                select(ConsumerApplication).where(ConsumerApplication.id == application_id)
            )
            application = result.scalar_one_or_none()

            if not application:
                raise ValueError(f"Application {application_id} not found")

            # Update status
            application.application_status = ApplicationStatus.ANALYZING
            await self.db.commit()

            # Collect OSINT data if requested
            if collect_osint:
                await self.osint_collector.collect_consumer_osint(application_id)

            # Get all related data
            osint_data = await self._get_osint_data(application_id)
            financial_data = await self._get_financial_data(application_id)
            behavioral_data = await self._get_behavioral_data(application_id)

            # Calculate component scores
            osint_score = await self.calculate_osint_score(osint_data)
            traditional_score = await self.calculate_traditional_score(
                application, financial_data
            )
            behavioral_score = await self.calculate_behavioral_score(
                behavioral_data, osint_data
            )

            # Detect fraud
            fraud_indicators = await self.detect_fraud_signals(
                application, osint_data, financial_data, behavioral_data
            )
            fraud_score = self._calculate_fraud_score(fraud_indicators)

            # Calculate combined score
            overall_score = await self.calculate_combined_score(
                osint_score, traditional_score, behavioral_score, fraud_score
            )

            # Determine risk tier and level
            risk_tier = self._determine_risk_tier(overall_score)
            risk_level = self._determine_risk_level(overall_score)

            # Calculate probability of default
            probability_of_default = await self._calculate_probability_of_default(
                application, overall_score, osint_score, traditional_score,
                behavioral_score, fraud_score
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                overall_score, risk_tier, probability_of_default,
                application.requested_amount
            )

            # Save risk score
            risk_score = ConsumerRiskScore(
                application_id=application_id,
                overall_score=int(overall_score),
                osint_score=int(osint_score),
                traditional_score=int(traditional_score),
                behavioral_score=int(behavioral_score),
                fraud_score=int(fraud_score),
                risk_tier=risk_tier,
                risk_level=risk_level,
                probability_of_default=probability_of_default,
                recommended_interest_rate=recommendations['interest_rate'],
                recommended_loan_amount=recommendations['loan_amount'],
                approval_recommendation=recommendations['recommendation'],
                score_components={
                    'identity_verification': osint_data.get('identity_score', 0),
                    'employment_verification': osint_data.get('employment_score', 0),
                    'digital_footprint': osint_data.get('digital_footprint_score', 0),
                    'social_media_risk': osint_data.get('social_media_risk', 0),
                    'financial_health': traditional_score,
                    'behavioral_patterns': behavioral_score,
                    'fraud_indicators': len(fraud_indicators)
                }
            )

            self.db.add(risk_score)

            # Update application status
            application.application_status = ApplicationStatus.SCORED
            await self.db.commit()

            logger.info(
                f"Consumer assessment completed for application {application_id}. "
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
                    'traditional_score': traditional_score,
                    'behavioral_score': behavioral_score,
                    'fraud_score': fraud_score
                },
                'fraud_indicators': len(fraud_indicators),
                'assessed_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error assessing consumer application {application_id}: {str(e)}")
            if application:
                application.application_status = ApplicationStatus.PENDING
                await self.db.commit()
            raise

    async def calculate_osint_score(self, osint_data: Dict[str, Any]) -> float:
        """
        Calculate risk score from OSINT data.

        Args:
            osint_data: Collected OSINT data

        Returns:
            OSINT-based risk score (300-850 scale)
        """
        try:
            # Identity verification score (0-100)
            identity_score = osint_data.get('identity_score', 50)

            # Employment verification score (0-100)
            employment_score = osint_data.get('employment_score', 50)

            # Digital footprint score (0-100)
            digital_footprint_score = osint_data.get('digital_footprint_score', 50)

            # Social media risk (lower is better, 0-100)
            social_media_risk = osint_data.get('social_media_risk', 50)

            # Email/phone verification (0-100)
            contact_verification = osint_data.get('contact_verification', 50)

            # Address verification (0-100)
            address_verification = osint_data.get('address_verification', 50)

            # Calculate weighted average (0-100)
            osint_raw_score = (
                identity_score * 0.25 +
                employment_score * 0.20 +
                digital_footprint_score * 0.20 +
                (100 - social_media_risk) * 0.15 +
                contact_verification * 0.10 +
                address_verification * 0.10
            )

            # Convert to 300-850 scale
            osint_score = 300 + (osint_raw_score / 100) * 550

            return osint_score

        except Exception as e:
            logger.error(f"Error calculating OSINT score: {str(e)}")
            return 500  # Default to mid-range score

    async def calculate_traditional_score(
        self,
        application: ConsumerApplication,
        financial_data: Optional[ConsumerFinancialData]
    ) -> float:
        """
        Calculate traditional credit score.

        Args:
            application: Consumer application
            financial_data: Financial data

        Returns:
            Traditional credit score (300-850 scale)
        """
        try:
            score_components = []

            # Payment history (35% of traditional score)
            payment_history_score = 70  # Default
            if financial_data and financial_data.loans:
                payment_history_score = self._analyze_payment_history(
                    financial_data.loans
                )
            score_components.append(payment_history_score * 0.35)

            # Credit utilization (30% of traditional score)
            utilization_score = 70  # Default
            if financial_data and financial_data.credit_utilization:
                utilization_score = self._analyze_credit_utilization(
                    financial_data.credit_utilization
                )
            score_components.append(utilization_score * 0.30)

            # Debt-to-income ratio (20% of traditional score)
            dti_score = 70  # Default
            if financial_data and financial_data.debt_to_income_ratio:
                dti_score = self._analyze_debt_to_income(
                    financial_data.debt_to_income_ratio
                )
            score_components.append(dti_score * 0.20)

            # Income stability (10% of traditional score)
            income_score = 70  # Default
            if application.monthly_income:
                income_score = self._analyze_income_stability(
                    application.monthly_income,
                    financial_data.income_sources if financial_data else {}
                )
            score_components.append(income_score * 0.10)

            # Employment status (5% of traditional score)
            employment_score = 70  # Default
            if application.employment_status:
                employment_score = self._analyze_employment(
                    application.employment_status
                )
            score_components.append(employment_score * 0.05)

            # Calculate weighted average (0-100)
            traditional_raw_score = sum(score_components)

            # Convert to 300-850 scale
            traditional_score = 300 + (traditional_raw_score / 100) * 550

            return traditional_score

        except Exception as e:
            logger.error(f"Error calculating traditional score: {str(e)}")
            return 500  # Default to mid-range score

    async def calculate_behavioral_score(
        self,
        behavioral_data: Optional[ConsumerBehavioralData],
        osint_data: Dict[str, Any]
    ) -> float:
        """
        Calculate behavioral risk score.

        Args:
            behavioral_data: Behavioral data
            osint_data: OSINT data

        Returns:
            Behavioral score (300-850 scale)
        """
        try:
            if not behavioral_data:
                return 500  # Default to mid-range

            # Online activity patterns (0-100)
            online_activity_score = behavioral_data.digital_footprint_score or 50

            # Payment patterns (0-100)
            payment_pattern_score = 70  # Default
            if behavioral_data.payment_patterns:
                payment_pattern_score = self._analyze_payment_patterns(
                    behavioral_data.payment_patterns
                )

            # Social media behavior (0-100)
            social_behavior_score = 70  # Default
            if behavioral_data.social_media_activity:
                social_behavior_score = self._analyze_social_behavior(
                    behavioral_data.social_media_activity
                )

            # Digital consistency (0-100)
            consistency_score = osint_data.get('consistency_score', 70)

            # Calculate weighted average (0-100)
            behavioral_raw_score = (
                online_activity_score * 0.30 +
                payment_pattern_score * 0.35 +
                social_behavior_score * 0.20 +
                consistency_score * 0.15
            )

            # Convert to 300-850 scale
            behavioral_score = 300 + (behavioral_raw_score / 100) * 550

            return behavioral_score

        except Exception as e:
            logger.error(f"Error calculating behavioral score: {str(e)}")
            return 500

    async def calculate_combined_score(
        self,
        osint_score: float,
        traditional_score: float,
        behavioral_score: float,
        fraud_score: float
    ) -> float:
        """
        Combine all scores into final risk score.

        Args:
            osint_score: OSINT component score
            traditional_score: Traditional component score
            behavioral_score: Behavioral component score
            fraud_score: Fraud component score (lower is worse)

        Returns:
            Combined risk score (300-850 scale)
        """
        try:
            # Weighted combination
            combined_score = (
                osint_score * self.weights['osint'] +
                traditional_score * self.weights['traditional'] +
                behavioral_score * self.weights['behavioral'] +
                fraud_score * self.weights['fraud']
            )

            # Ensure within bounds
            combined_score = max(300, min(850, combined_score))

            return combined_score

        except Exception as e:
            logger.error(f"Error calculating combined score: {str(e)}")
            return 500

    async def detect_fraud_signals(
        self,
        application: ConsumerApplication,
        osint_data: Dict[str, Any],
        financial_data: Optional[ConsumerFinancialData],
        behavioral_data: Optional[ConsumerBehavioralData]
    ) -> List[ConsumerFraudIndicator]:
        """
        Detect potential fraud indicators.

        Args:
            application: Consumer application
            osint_data: OSINT data
            financial_data: Financial data
            behavioral_data: Behavioral data

        Returns:
            List of detected fraud indicators
        """
        fraud_indicators = []

        try:
            # Identity inconsistencies
            if osint_data.get('identity_inconsistencies'):
                for inconsistency in osint_data['identity_inconsistencies']:
                    indicator = ConsumerFraudIndicator(
                        application_id=application.id,
                        indicator_type='identity_inconsistency',
                        severity=FraudSeverity.HIGH,
                        description=inconsistency['description'],
                        evidence=inconsistency
                    )
                    fraud_indicators.append(indicator)

            # Suspicious email patterns
            if osint_data.get('email_risk_level', 0) > 70:
                indicator = ConsumerFraudIndicator(
                    application_id=application.id,
                    indicator_type='suspicious_email',
                    severity=FraudSeverity.MEDIUM,
                    description='Email address shows high-risk patterns',
                    evidence={'email_risk_level': osint_data['email_risk_level']}
                )
                fraud_indicators.append(indicator)

            # Phone number issues
            if osint_data.get('phone_verification_failed'):
                indicator = ConsumerFraudIndicator(
                    application_id=application.id,
                    indicator_type='phone_verification_failed',
                    severity=FraudSeverity.HIGH,
                    description='Phone number verification failed',
                    evidence=osint_data.get('phone_verification_details', {})
                )
                fraud_indicators.append(indicator)

            # Digital footprint anomalies
            if osint_data.get('digital_footprint_anomalies'):
                indicator = ConsumerFraudIndicator(
                    application_id=application.id,
                    indicator_type='digital_footprint_anomaly',
                    severity=FraudSeverity.MEDIUM,
                    description='Unusual digital footprint patterns detected',
                    evidence=osint_data['digital_footprint_anomalies']
                )
                fraud_indicators.append(indicator)

            # Income inconsistencies
            if financial_data and osint_data.get('employment_income'):
                stated_income = application.monthly_income or 0
                verified_income = osint_data['employment_income']
                if abs(stated_income - verified_income) / max(stated_income, 1) > 0.3:
                    indicator = ConsumerFraudIndicator(
                        application_id=application.id,
                        indicator_type='income_inconsistency',
                        severity=FraudSeverity.HIGH,
                        description='Significant discrepancy between stated and verified income',
                        evidence={
                            'stated_income': stated_income,
                            'verified_income': verified_income
                        }
                    )
                    fraud_indicators.append(indicator)

            # Save fraud indicators
            for indicator in fraud_indicators:
                self.db.add(indicator)

            if fraud_indicators:
                await self.db.commit()
                logger.warning(
                    f"Detected {len(fraud_indicators)} fraud indicators "
                    f"for application {application.id}"
                )

            return fraud_indicators

        except Exception as e:
            logger.error(f"Error detecting fraud signals: {str(e)}")
            return fraud_indicators

    async def verify_identity(self, application: ConsumerApplication) -> Dict[str, Any]:
        """
        Identity verification using multiple sources.

        Args:
            application: Consumer application

        Returns:
            Identity verification results
        """
        # This would integrate with identity verification services
        # For now, returning placeholder
        return {
            'verified': True,
            'confidence': 0.85,
            'sources': ['email', 'phone', 'address']
        }

    async def assess_employment(self, employment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Employment verification and stability assessment.

        Args:
            employment_data: Employment data

        Returns:
            Employment assessment results
        """
        # This would integrate with employment verification services
        return {
            'verified': True,
            'stability_score': 75,
            'years_at_current': 3
        }

    async def estimate_income(
        self,
        application: ConsumerApplication,
        osint_data: Dict[str, Any]
    ) -> float:
        """
        Income estimation from various signals.

        Args:
            application: Consumer application
            osint_data: OSINT data

        Returns:
            Estimated monthly income
        """
        # Use stated income as baseline
        estimated_income = application.monthly_income or 0

        # Adjust based on OSINT signals
        if osint_data.get('employment_income'):
            estimated_income = osint_data['employment_income']

        return estimated_income

    # Helper methods

    async def _get_osint_data(self, application_id: int) -> Dict[str, Any]:
        """Get aggregated OSINT data for application."""
        result = await self.db.execute(
            select(ConsumerOSINTData).where(
                ConsumerOSINTData.application_id == application_id
            )
        )
        osint_records = result.scalars().all()

        # Aggregate OSINT data
        aggregated_data = {
            'identity_score': 70,
            'employment_score': 70,
            'digital_footprint_score': 70,
            'social_media_risk': 30,
            'contact_verification': 70,
            'address_verification': 70,
            'consistency_score': 70
        }

        for record in osint_records:
            if record.data_type == 'email':
                aggregated_data['contact_verification'] = record.data.get('verification_score', 70)
            elif record.data_type == 'phone':
                aggregated_data['contact_verification'] = max(
                    aggregated_data['contact_verification'],
                    record.data.get('verification_score', 70)
                )
            elif record.data_type == 'social_media':
                aggregated_data['social_media_risk'] = record.risk_signals.get('risk_level', 30)
                aggregated_data['digital_footprint_score'] = record.data.get('activity_score', 70)

        return aggregated_data

    async def _get_financial_data(
        self,
        application_id: int
    ) -> Optional[ConsumerFinancialData]:
        """Get financial data for application."""
        result = await self.db.execute(
            select(ConsumerFinancialData).where(
                ConsumerFinancialData.application_id == application_id
            ).order_by(ConsumerFinancialData.collected_at.desc())
        )
        return result.scalar_one_or_none()

    async def _get_behavioral_data(
        self,
        application_id: int
    ) -> Optional[ConsumerBehavioralData]:
        """Get behavioral data for application."""
        result = await self.db.execute(
            select(ConsumerBehavioralData).where(
                ConsumerBehavioralData.application_id == application_id
            ).order_by(ConsumerBehavioralData.collected_at.desc())
        )
        return result.scalar_one_or_none()

    def _calculate_fraud_score(self, fraud_indicators: List[ConsumerFraudIndicator]) -> float:
        """Calculate fraud score based on detected indicators."""
        if not fraud_indicators:
            return 850  # No fraud indicators = best score

        # Deduct points based on severity
        score = 850
        for indicator in fraud_indicators:
            if indicator.severity == FraudSeverity.CRITICAL:
                score -= 150
            elif indicator.severity == FraudSeverity.HIGH:
                score -= 100
            elif indicator.severity == FraudSeverity.MEDIUM:
                score -= 50
            elif indicator.severity == FraudSeverity.LOW:
                score -= 25

        return max(300, score)

    def _determine_risk_tier(self, score: float) -> RiskTier:
        """Determine risk tier from score."""
        if score >= 750:
            return RiskTier.EXCELLENT
        elif score >= 650:
            return RiskTier.GOOD
        elif score >= 550:
            return RiskTier.FAIR
        elif score >= 450:
            return RiskTier.POOR
        else:
            return RiskTier.HIGH_RISK

    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from score."""
        if score >= 700:
            return RiskLevel.LOW
        elif score >= 600:
            return RiskLevel.MEDIUM
        elif score >= 500:
            return RiskLevel.HIGH
        else:
            return RiskLevel.VERY_HIGH

    async def _calculate_probability_of_default(
        self,
        application: ConsumerApplication,
        overall_score: float,
        osint_score: float,
        traditional_score: float,
        behavioral_score: float,
        fraud_score: float
    ) -> float:
        """Calculate probability of default using ML model."""
        try:
            # Prepare features for ML model
            features = {
                'overall_score': overall_score,
                'osint_score': osint_score,
                'traditional_score': traditional_score,
                'behavioral_score': behavioral_score,
                'fraud_score': fraud_score,
                'requested_amount': application.requested_amount or 0,
                'monthly_income': application.monthly_income or 0
            }

            # Use ML model to predict probability of default
            # For now, using a simple formula
            # Lower score = higher probability of default
            probability = 1 - (overall_score - 300) / 550
            probability = max(0.01, min(0.99, probability))

            return round(probability, 4)

        except Exception as e:
            logger.error(f"Error calculating probability of default: {str(e)}")
            return 0.5

    def _generate_recommendations(
        self,
        overall_score: float,
        risk_tier: RiskTier,
        probability_of_default: float,
        requested_amount: float
    ) -> Dict[str, Any]:
        """Generate lending recommendations."""
        recommendations = {
            'recommendation': 'manual_review',
            'interest_rate': 15.0,
            'loan_amount': requested_amount or 0,
            'reasoning': []
        }

        # Determine approval recommendation
        if overall_score >= 700 and probability_of_default < 0.15:
            recommendations['recommendation'] = 'approve'
            recommendations['reasoning'].append('Strong credit profile')
        elif overall_score < 450 or probability_of_default > 0.50:
            recommendations['recommendation'] = 'reject'
            recommendations['reasoning'].append('High credit risk')
        else:
            recommendations['reasoning'].append('Borderline case requires manual review')

        # Calculate interest rate based on risk
        if overall_score >= 750:
            recommendations['interest_rate'] = 5.0
        elif overall_score >= 650:
            recommendations['interest_rate'] = 8.0
        elif overall_score >= 550:
            recommendations['interest_rate'] = 12.0
        elif overall_score >= 450:
            recommendations['interest_rate'] = 18.0
        else:
            recommendations['interest_rate'] = 24.0

        # Adjust loan amount based on risk
        if probability_of_default > 0.30:
            recommended_amount = (requested_amount or 0) * 0.5
            recommendations['loan_amount'] = recommended_amount
            recommendations['reasoning'].append('Loan amount reduced due to risk')

        return recommendations

    def _analyze_payment_history(self, loans: Dict[str, Any]) -> float:
        """Analyze payment history from loan data."""
        # Placeholder implementation
        return 75.0

    def _analyze_credit_utilization(self, utilization: float) -> float:
        """Analyze credit utilization ratio."""
        if utilization < 0.30:
            return 90
        elif utilization < 0.50:
            return 75
        elif utilization < 0.75:
            return 60
        else:
            return 40

    def _analyze_debt_to_income(self, dti_ratio: float) -> float:
        """Analyze debt-to-income ratio."""
        if dti_ratio < 0.30:
            return 90
        elif dti_ratio < 0.40:
            return 75
        elif dti_ratio < 0.50:
            return 60
        else:
            return 40

    def _analyze_income_stability(
        self,
        monthly_income: float,
        income_sources: Dict[str, Any]
    ) -> float:
        """Analyze income stability."""
        # Placeholder implementation
        return 70.0

    def _analyze_employment(self, employment_status: str) -> float:
        """Analyze employment status."""
        status_scores = {
            'full_time': 90,
            'part_time': 70,
            'self_employed': 65,
            'contract': 60,
            'unemployed': 30
        }
        return status_scores.get(employment_status.lower(), 50)

    def _analyze_payment_patterns(self, payment_patterns: Dict[str, Any]) -> float:
        """Analyze payment behavior patterns."""
        # Placeholder implementation
        return 70.0

    def _analyze_social_behavior(self, social_media_activity: Dict[str, Any]) -> float:
        """Analyze social media behavior."""
        # Placeholder implementation
        return 70.0
