"""Credit Risk Report Generator.

Generates comprehensive credit risk reports in various formats.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import (
    ConsumerApplication, BusinessApplication,
    ConsumerRiskScore, BusinessRiskScore
)

logger = logging.getLogger(__name__)


class CreditRiskReportGenerator:
    """Generate comprehensive credit risk reports."""

    def __init__(self, db: AsyncSession):
        """Initialize report generator."""
        self.db = db

    async def generate_consumer_report(
        self,
        application_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Generate consumer credit risk report.

        Args:
            application_id: Consumer application ID
            format: Report format (json, html, pdf)

        Returns:
            Generated report
        """
        try:
            logger.info(f"Generating consumer report for application {application_id}")

            # Get application and risk score
            app_result = await self.db.execute(
                select(ConsumerApplication).where(ConsumerApplication.id == application_id)
            )
            application = app_result.scalar_one_or_none()

            if not application:
                raise ValueError(f"Application {application_id} not found")

            score_result = await self.db.execute(
                select(ConsumerRiskScore).where(
                    ConsumerRiskScore.application_id == application_id
                ).order_by(ConsumerRiskScore.calculated_at.desc())
            )
            risk_score = score_result.scalar_one_or_none()

            # Generate report components
            executive_summary = self._generate_executive_summary_consumer(application, risk_score)
            score_breakdown = self._generate_score_breakdown(risk_score) if risk_score else {}
            recommendations = self._generate_recommendations_section(risk_score) if risk_score else {}

            report = {
                'report_type': 'consumer_credit_risk',
                'application_id': application_id,
                'generated_at': datetime.utcnow().isoformat(),
                'executive_summary': executive_summary,
                'applicant_information': {
                    'name': application.applicant_name,
                    'email': application.email,
                    'phone': application.phone,
                    'application_date': application.created_at.isoformat() if application.created_at else None
                },
                'credit_assessment': score_breakdown,
                'recommendations': recommendations,
                'compliance_notices': self._generate_compliance_notices()
            }

            if format == 'json':
                return report
            elif format == 'html':
                return self._convert_to_html(report)
            elif format == 'pdf':
                return self._convert_to_pdf(report)
            else:
                return report

        except Exception as e:
            logger.error(f"Error generating consumer report: {str(e)}")
            raise

    async def generate_business_report(
        self,
        application_id: int,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Generate business credit risk report.

        Args:
            application_id: Business application ID
            format: Report format

        Returns:
            Generated report
        """
        try:
            logger.info(f"Generating business report for application {application_id}")

            # Get application and risk score
            app_result = await self.db.execute(
                select(BusinessApplication).where(BusinessApplication.id == application_id)
            )
            application = app_result.scalar_one_or_none()

            if not application:
                raise ValueError(f"Application {application_id} not found")

            score_result = await self.db.execute(
                select(BusinessRiskScore).where(
                    BusinessRiskScore.application_id == application_id
                ).order_by(BusinessRiskScore.calculated_at.desc())
            )
            risk_score = score_result.scalar_one_or_none()

            # Generate report components
            executive_summary = self._generate_executive_summary_business(application, risk_score)
            score_breakdown = self._generate_business_score_breakdown(risk_score) if risk_score else {}
            recommendations = self._generate_business_recommendations(risk_score) if risk_score else {}

            report = {
                'report_type': 'business_credit_risk',
                'application_id': application_id,
                'generated_at': datetime.utcnow().isoformat(),
                'executive_summary': executive_summary,
                'business_information': {
                    'company_name': application.company_name,
                    'legal_name': application.legal_name,
                    'registration_number': application.registration_number,
                    'industry': application.industry,
                    'domain': application.domain,
                    'application_date': application.created_at.isoformat() if application.created_at else None
                },
                'credit_assessment': score_breakdown,
                'recommendations': recommendations,
                'compliance_notices': self._generate_compliance_notices()
            }

            if format == 'json':
                return report
            elif format == 'html':
                return self._convert_to_html(report)
            elif format == 'pdf':
                return self._convert_to_pdf(report)
            else:
                return report

        except Exception as e:
            logger.error(f"Error generating business report: {str(e)}")
            raise

    def _generate_executive_summary_consumer(
        self,
        application: ConsumerApplication,
        risk_score: Optional[ConsumerRiskScore]
    ) -> Dict[str, Any]:
        """Generate executive summary for consumer report."""
        if not risk_score:
            return {
                'status': 'pending',
                'message': 'Credit assessment not yet completed'
            }

        return {
            'overall_score': risk_score.overall_score,
            'risk_tier': risk_score.risk_tier.value if risk_score.risk_tier else 'unknown',
            'risk_level': risk_score.risk_level.value if risk_score.risk_level else 'unknown',
            'recommendation': risk_score.approval_recommendation,
            'probability_of_default': risk_score.probability_of_default,
            'recommended_interest_rate': risk_score.recommended_interest_rate,
            'summary_text': self._generate_summary_text_consumer(risk_score)
        }

    def _generate_executive_summary_business(
        self,
        application: BusinessApplication,
        risk_score: Optional[BusinessRiskScore]
    ) -> Dict[str, Any]:
        """Generate executive summary for business report."""
        if not risk_score:
            return {
                'status': 'pending',
                'message': 'Credit assessment not yet completed'
            }

        return {
            'overall_score': risk_score.overall_score,
            'risk_tier': risk_score.risk_tier.value if risk_score.risk_tier else 'unknown',
            'risk_level': risk_score.risk_level.value if risk_score.risk_level else 'unknown',
            'recommendation': risk_score.approval_recommendation,
            'probability_of_default': risk_score.probability_of_default,
            'recommended_interest_rate': risk_score.recommended_interest_rate,
            'recommended_term_months': risk_score.recommended_term_months,
            'summary_text': self._generate_summary_text_business(risk_score)
        }

    def _generate_score_breakdown(self, risk_score: ConsumerRiskScore) -> Dict[str, Any]:
        """Generate score breakdown section."""
        return {
            'overall_score': risk_score.overall_score,
            'components': {
                'osint_score': risk_score.osint_score,
                'traditional_score': risk_score.traditional_score,
                'behavioral_score': risk_score.behavioral_score,
                'fraud_score': risk_score.fraud_score
            },
            'detailed_components': risk_score.score_components or {},
            'calculated_at': risk_score.calculated_at.isoformat() if risk_score.calculated_at else None
        }

    def _generate_business_score_breakdown(self, risk_score: BusinessRiskScore) -> Dict[str, Any]:
        """Generate business score breakdown section."""
        return {
            'overall_score': risk_score.overall_score,
            'components': {
                'osint_score': risk_score.osint_score,
                'financial_score': risk_score.financial_score,
                'operational_score': risk_score.operational_score,
                'industry_score': risk_score.industry_score,
                'management_score': risk_score.management_score
            },
            'detailed_components': risk_score.score_components or {},
            'calculated_at': risk_score.calculated_at.isoformat() if risk_score.calculated_at else None
        }

    def _generate_recommendations_section(self, risk_score: ConsumerRiskScore) -> Dict[str, Any]:
        """Generate recommendations section."""
        return {
            'approval_recommendation': risk_score.approval_recommendation,
            'recommended_interest_rate': f"{risk_score.recommended_interest_rate}%",
            'recommended_loan_amount': risk_score.recommended_loan_amount,
            'conditions': self._generate_conditions(risk_score),
            'improvement_suggestions': self._generate_improvement_suggestions(risk_score)
        }

    def _generate_business_recommendations(self, risk_score: BusinessRiskScore) -> Dict[str, Any]:
        """Generate business recommendations section."""
        return {
            'approval_recommendation': risk_score.approval_recommendation,
            'recommended_interest_rate': f"{risk_score.recommended_interest_rate}%",
            'recommended_loan_amount': risk_score.recommended_loan_amount,
            'recommended_term': f"{risk_score.recommended_term_months} months",
            'conditions': self._generate_business_conditions(risk_score),
            'monitoring_requirements': self._generate_monitoring_requirements(risk_score)
        }

    def _generate_compliance_notices(self) -> Dict[str, Any]:
        """Generate compliance notices section."""
        return {
            'fcra_notice': 'This report complies with Fair Credit Reporting Act requirements.',
            'ecoa_notice': 'Equal Credit Opportunity Act: Credit decisions are made without discrimination.',
            'gdpr_notice': 'Data processed in compliance with GDPR regulations.',
            'data_retention': 'This report will be retained for 7 years as required by law.'
        }

    def _generate_summary_text_consumer(self, risk_score: ConsumerRiskScore) -> str:
        """Generate summary text for consumer."""
        score = risk_score.overall_score
        tier = risk_score.risk_tier.value if risk_score.risk_tier else 'unknown'

        text = f"The applicant received a credit score of {score}, "
        text += f"classified as '{tier}' risk tier. "

        if risk_score.approval_recommendation == 'approve':
            text += "We recommend approval with the suggested terms."
        elif risk_score.approval_recommendation == 'reject':
            text += "We recommend rejection based on the risk assessment."
        else:
            text += "This application requires manual review."

        return text

    def _generate_summary_text_business(self, risk_score: BusinessRiskScore) -> str:
        """Generate summary text for business."""
        score = risk_score.overall_score
        tier = risk_score.risk_tier.value if risk_score.risk_tier else 'unknown'

        text = f"The business received a credit score of {score} (out of 1000), "
        text += f"classified as '{tier}' risk tier. "

        if risk_score.approval_recommendation == 'approve':
            text += "We recommend approval with the suggested terms."
        elif risk_score.approval_recommendation == 'reject':
            text += "We recommend rejection based on the risk assessment."
        else:
            text += "This application requires manual review and additional documentation."

        return text

    def _generate_conditions(self, risk_score: ConsumerRiskScore) -> List[str]:
        """Generate lending conditions."""
        conditions = []

        if risk_score.risk_level.value == 'medium':
            conditions.append("Require proof of income")
            conditions.append("Verify employment status")
        elif risk_score.risk_level.value in ['high', 'very_high']:
            conditions.append("Require co-signer")
            conditions.append("Provide additional collateral")
            conditions.append("Shorter loan term")

        return conditions

    def _generate_business_conditions(self, risk_score: BusinessRiskScore) -> List[str]:
        """Generate business lending conditions."""
        conditions = []

        if risk_score.risk_level.value == 'medium':
            conditions.append("Provide updated financial statements quarterly")
            conditions.append("Maintain minimum cash reserve")
        elif risk_score.risk_level.value in ['high', 'very_high']:
            conditions.append("Personal guarantee from owner")
            conditions.append("Monthly financial reporting")
            conditions.append("Restrict dividend payments")

        return conditions

    def _generate_improvement_suggestions(self, risk_score: ConsumerRiskScore) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []

        components = risk_score.score_components or {}

        if components.get('payment_history', 100) < 70:
            suggestions.append("Improve payment history by making all payments on time")

        if components.get('credit_utilization', 0) > 50:
            suggestions.append("Reduce credit card balances to improve credit utilization")

        if components.get('debt_to_income', 0) > 40:
            suggestions.append("Lower debt-to-income ratio by paying down debt")

        return suggestions

    def _generate_monitoring_requirements(self, risk_score: BusinessRiskScore) -> List[str]:
        """Generate monitoring requirements for business."""
        requirements = []

        if risk_score.risk_level.value in ['medium', 'high', 'very_high']:
            requirements.append("Monthly revenue reporting")
            requirements.append("Quarterly balance sheet review")
            requirements.append("Annual financial audit")

        return requirements

    def _convert_to_html(self, report: Dict[str, Any]) -> str:
        """Convert report to HTML format."""
        # Simplified HTML conversion
        html = f"<html><head><title>Credit Risk Report</title></head><body>"
        html += f"<h1>Credit Risk Assessment Report</h1>"
        html += f"<pre>{json.dumps(report, indent=2)}</pre>"
        html += "</body></html>"
        return html

    def _convert_to_pdf(self, report: Dict[str, Any]) -> bytes:
        """Convert report to PDF format."""
        # Placeholder: Would use reportlab or similar
        return json.dumps(report).encode('utf-8')
