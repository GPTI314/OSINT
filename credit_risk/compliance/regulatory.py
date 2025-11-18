"""Regulatory Compliance for Credit Risk Scoring.

Ensures compliance with GDPR, FCRA, ECOA, and other financial regulations.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RegulatoryCompliance:
    """
    Regulatory compliance management.

    Ensures compliance with:
    - GDPR (General Data Protection Regulation)
    - FCRA (Fair Credit Reporting Act)
    - ECOA (Equal Credit Opportunity Act)
    - Explainable AI requirements
    - Data retention policies
    - Audit trails
    """

    def __init__(self):
        """Initialize regulatory compliance module."""
        self.data_retention_days = 2555  # 7 years for financial records
        self.audit_trail = []

    def ensure_gdpr_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure GDPR compliance for data processing.

        Args:
            data: Data to check for GDPR compliance

        Returns:
            Compliance status and recommendations
        """
        try:
            compliance_status = {
                'compliant': True,
                'issues': [],
                'recommendations': []
            }

            # Check for consent
            if not data.get('consent_obtained', False):
                compliance_status['compliant'] = False
                compliance_status['issues'].append('User consent not obtained')
                compliance_status['recommendations'].append(
                    'Obtain explicit user consent before processing data'
                )

            # Check for PII encryption
            if data.get('contains_pii', True) and not data.get('encrypted', False):
                compliance_status['issues'].append('PII not encrypted')
                compliance_status['recommendations'].append('Encrypt all personally identifiable information')

            # Check data minimization
            if data.get('excessive_data_collection', False):
                compliance_status['issues'].append('Excessive data collection')
                compliance_status['recommendations'].append(
                    'Collect only necessary data for credit assessment'
                )

            # Right to be forgotten
            if not data.get('deletion_capability', True):
                compliance_status['issues'].append('No data deletion capability')
                compliance_status['recommendations'].append(
                    'Implement data deletion procedures for user requests'
                )

            logger.info(f"GDPR compliance check: {compliance_status['compliant']}")
            return compliance_status

        except Exception as e:
            logger.error(f"Error ensuring GDPR compliance: {str(e)}")
            return {'compliant': False, 'error': str(e)}

    def ensure_fcra_compliance(self, credit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure Fair Credit Reporting Act compliance.

        Args:
            credit_data: Credit data to check

        Returns:
            Compliance status
        """
        try:
            compliance_status = {
                'compliant': True,
                'issues': [],
                'recommendations': []
            }

            # Adverse action notices
            if credit_data.get('application_denied', False):
                if not credit_data.get('adverse_action_notice_sent', False):
                    compliance_status['compliant'] = False
                    compliance_status['issues'].append('Adverse action notice not sent')
                    compliance_status['recommendations'].append(
                        'Send adverse action notice explaining denial reasons'
                    )

            # Accuracy requirements
            if not credit_data.get('data_accuracy_verified', False):
                compliance_status['issues'].append('Data accuracy not verified')
                compliance_status['recommendations'].append(
                    'Verify accuracy of all credit data used in decision'
                )

            # Permissible purpose
            if not credit_data.get('permissible_purpose', False):
                compliance_status['compliant'] = False
                compliance_status['issues'].append('No permissible purpose documented')
                compliance_status['recommendations'].append(
                    'Document permissible purpose for credit check'
                )

            logger.info(f"FCRA compliance check: {compliance_status['compliant']}")
            return compliance_status

        except Exception as e:
            logger.error(f"Error ensuring FCRA compliance: {str(e)}")
            return {'compliant': False, 'error': str(e)}

    def ensure_ecoa_compliance(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure Equal Credit Opportunity Act compliance.

        Args:
            application_data: Application data to check

        Returns:
            Compliance status
        """
        try:
            compliance_status = {
                'compliant': True,
                'issues': [],
                'recommendations': []
            }

            # Check for prohibited basis in decision
            prohibited_factors = ['race', 'color', 'religion', 'national_origin', 'sex',
                                'marital_status', 'age']

            scoring_factors = application_data.get('scoring_factors', [])
            for factor in scoring_factors:
                if factor in prohibited_factors:
                    compliance_status['compliant'] = False
                    compliance_status['issues'].append(
                        f'Decision based on prohibited factor: {factor}'
                    )

            # Notification requirements
            if not application_data.get('decision_notification_within_30_days', True):
                compliance_status['issues'].append('Decision notification not within 30 days')
                compliance_status['recommendations'].append(
                    'Notify applicant of decision within 30 days'
                )

            logger.info(f"ECOA compliance check: {compliance_status['compliant']}")
            return compliance_status

        except Exception as e:
            logger.error(f"Error ensuring ECOA compliance: {str(e)}")
            return {'compliant': False, 'error': str(e)}

    def provide_explanation(self, score: int, factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide explainable AI for regulatory compliance.

        Args:
            score: Credit score
            factors: Factors used in scoring

        Returns:
            Human-readable explanation
        """
        try:
            explanation = {
                'score': score,
                'score_range': self._get_score_range_explanation(score),
                'primary_factors': [],
                'detailed_explanation': '',
                'adverse_factors': [],
                'improvement_tips': []
            }

            # Identify primary factors
            sorted_factors = sorted(
                factors.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:5]

            for factor_name, factor_value in sorted_factors:
                explanation['primary_factors'].append({
                    'factor': factor_name,
                    'impact': 'positive' if factor_value > 0 else 'negative',
                    'description': self._get_factor_description(factor_name)
                })

            # Identify adverse factors (for adverse action notices)
            adverse_factors = [
                (name, value) for name, value in factors.items()
                if value < 0
            ]
            adverse_factors.sort(key=lambda x: x[1])

            for factor_name, _ in adverse_factors[:4]:  # Top 4 adverse factors
                explanation['adverse_factors'].append({
                    'factor': factor_name,
                    'description': self._get_factor_description(factor_name),
                    'recommendation': self._get_improvement_recommendation(factor_name)
                })

            # Generate detailed explanation
            explanation['detailed_explanation'] = self._generate_detailed_explanation(
                score, explanation['primary_factors']
            )

            return explanation

        except Exception as e:
            logger.error(f"Error providing explanation: {str(e)}")
            return {'score': score, 'error': str(e)}

    def maintain_audit_trail(self, actions: List[Dict[str, Any]]) -> None:
        """
        Maintain audit trail for compliance.

        Args:
            actions: List of actions to audit
        """
        try:
            for action in actions:
                audit_entry = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'action': action.get('action'),
                    'user': action.get('user'),
                    'details': action.get('details', {}),
                    'compliance_check': action.get('compliance_check', False)
                }
                self.audit_trail.append(audit_entry)

            logger.info(f"Added {len(actions)} entries to audit trail")

        except Exception as e:
            logger.error(f"Error maintaining audit trail: {str(e)}")

    def check_data_retention_compliance(self, data_age_days: int) -> bool:
        """Check if data retention is compliant."""
        return data_age_days <= self.data_retention_days

    def get_data_retention_policy(self) -> Dict[str, Any]:
        """Get data retention policy details."""
        return {
            'retention_days': self.data_retention_days,
            'retention_years': self.data_retention_days / 365,
            'policy_description': 'Financial records retained for 7 years as required by law',
            'deletion_procedure': 'Automated deletion after retention period expires'
        }

    # Helper methods

    def _get_score_range_explanation(self, score: int) -> str:
        """Get human-readable score range explanation."""
        if score >= 750:
            return "Excellent - Very low credit risk"
        elif score >= 650:
            return "Good - Low credit risk"
        elif score >= 550:
            return "Fair - Moderate credit risk"
        elif score >= 450:
            return "Poor - High credit risk"
        else:
            return "Very Poor - Very high credit risk"

    def _get_factor_description(self, factor_name: str) -> str:
        """Get human-readable factor description."""
        descriptions = {
            'payment_history': 'History of making payments on time',
            'debt_to_income': 'Ratio of monthly debt to monthly income',
            'credit_utilization': 'Percentage of available credit being used',
            'employment_stability': 'Length and consistency of employment',
            'income_level': 'Monthly income amount',
            'credit_age': 'Length of credit history',
            'recent_inquiries': 'Number of recent credit inquiries'
        }
        return descriptions.get(factor_name, factor_name.replace('_', ' ').title())

    def _get_improvement_recommendation(self, factor_name: str) -> str:
        """Get improvement recommendation for a factor."""
        recommendations = {
            'payment_history': 'Make all payments on time to build positive payment history',
            'debt_to_income': 'Reduce outstanding debt or increase income',
            'credit_utilization': 'Pay down credit card balances to below 30% of limits',
            'employment_stability': 'Maintain steady employment',
            'recent_inquiries': 'Avoid applying for multiple credit products in short period'
        }
        return recommendations.get(factor_name, 'Improve this factor to increase credit score')

    def _generate_detailed_explanation(
        self,
        score: int,
        primary_factors: List[Dict[str, Any]]
    ) -> str:
        """Generate detailed explanation text."""
        explanation = f"Your credit score is {score}. "
        explanation += self._get_score_range_explanation(score) + ". "

        if primary_factors:
            explanation += "The primary factors affecting your score are: "
            factor_names = [f['factor'].replace('_', ' ') for f in primary_factors[:3]]
            explanation += ', '.join(factor_names) + ". "

        return explanation
