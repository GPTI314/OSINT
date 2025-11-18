"""
Compliance management for GDPR, CCPA, and other regulations
"""
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.models import User, AuditLog
from app.config import settings
import json


class ComplianceManager:
    """Manage data privacy and compliance requirements"""

    async def export_user_data(self, user_id: int, db: AsyncSession) -> Dict:
        """
        Export all user data for GDPR/CCPA compliance
        """
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Collect all user data
        user_data = {
            'personal_information': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'full_name': user.full_name,
                'phone': user.phone,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            },
            'account_status': {
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'two_factor_enabled': user.two_factor_enabled,
            },
            'oauth_connections': {
                'provider': user.oauth_provider,
            } if user.oauth_provider else None,
        }

        # Get audit logs
        audit_result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(1000)  # Last 1000 actions
        )
        audit_logs = audit_result.scalars().all()

        user_data['activity_history'] = [
            {
                'action': log.action,
                'timestamp': log.timestamp.isoformat(),
                'ip_address': log.ip_address,
                'status': log.status,
            }
            for log in audit_logs
        ]

        # Get API keys
        user_data['api_keys'] = [
            {
                'name': key.name,
                'created_at': key.created_at.isoformat(),
                'last_used_at': key.last_used_at.isoformat() if key.last_used_at else None,
            }
            for key in user.api_keys
        ]

        return user_data

    async def delete_user_data(self, user_id: int, db: AsyncSession) -> bool:
        """
        Delete user data (Right to be Forgotten - GDPR Article 17)
        """
        try:
            # Get user
            result = await db.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()

            if not user:
                return False

            # Soft delete approach - anonymize instead of hard delete
            user.email = f"deleted_{user_id}@anonymized.local"
            user.username = f"deleted_user_{user_id}"
            user.full_name = "Deleted User"
            user.phone = None
            user.hashed_password = "deleted"
            user.is_active = False
            user.deleted_at = datetime.utcnow()
            user.encrypted_data = None
            user.two_factor_secret = None

            # Anonymize audit logs (keep for compliance but remove PII)
            await db.execute(
                AuditLog.__table__.update()
                .where(AuditLog.user_id == user_id)
                .values(ip_address="0.0.0.0", user_agent="anonymized")
            )

            # Delete API keys
            for api_key in user.api_keys:
                api_key.is_active = False
                api_key.revoked_at = datetime.utcnow()

            # Delete sessions
            for session in user.sessions:
                session.is_active = False
                session.revoked_at = datetime.utcnow()

            await db.commit()
            return True

        except Exception as e:
            await db.rollback()
            raise e

    async def cleanup_expired_data(self, db: AsyncSession):
        """
        Clean up expired data according to retention policies
        """
        now = datetime.utcnow()

        # Delete old audit logs
        if settings.AUDIT_LOG_RETENTION_DAYS > 0:
            cutoff_date = now - timedelta(days=settings.AUDIT_LOG_RETENTION_DAYS)
            await db.execute(
                delete(AuditLog).where(AuditLog.timestamp < cutoff_date)
            )

        # Delete old deleted users
        if settings.DATA_RETENTION_DAYS > 0:
            cutoff_date = now - timedelta(days=settings.DATA_RETENTION_DAYS)
            await db.execute(
                delete(User).where(
                    User.deleted_at != None,
                    User.deleted_at < cutoff_date
                )
            )

        await db.commit()

    def get_privacy_policy(self) -> Dict:
        """
        Get privacy policy details
        """
        return {
            'data_retention': {
                'general_data_days': settings.DATA_RETENTION_DAYS,
                'pii_retention_days': settings.PII_RETENTION_DAYS,
                'audit_logs_days': settings.AUDIT_LOG_RETENTION_DAYS,
            },
            'user_rights': {
                'right_to_access': True,  # Data export
                'right_to_rectification': True,  # Data correction
                'right_to_erasure': True,  # Right to be forgotten
                'right_to_data_portability': True,  # Data export in JSON
                'right_to_object': True,  # Opt-out of processing
            },
            'data_protection': {
                'encryption_at_rest': settings.ENABLE_PII_ENCRYPTION,
                'encryption_in_transit': True,  # TLS/HTTPS
                'data_masking': settings.ENABLE_PII_MASKING,
            },
            'compliance': {
                'gdpr': settings.GDPR_ENABLED,
                'ccpa': settings.CCPA_ENABLED,
            },
            'contact': {
                'data_protection_officer': 'dpo@example.com',
                'privacy_inquiries': 'privacy@example.com',
            }
        }

    def get_terms_of_service(self) -> Dict:
        """
        Get terms of service for OSINT platform
        """
        return {
            'acceptable_use': {
                'ethical_research_only': True,
                'respect_robots_txt': settings.RESPECT_ROBOTS_TXT,
                'rate_limiting': True,
                'no_malicious_use': True,
            },
            'data_collection': {
                'respect_privacy': True,
                'legal_compliance': True,
                'no_unauthorized_access': True,
            },
            'user_responsibilities': [
                'Comply with all applicable laws and regulations',
                'Respect website terms of service',
                'Do not collect or process data illegally',
                'Use rate limiting and crawl delays',
                'Respect robots.txt directives',
                'Obtain necessary permissions for data collection',
            ],
            'prohibited_activities': [
                'Illegal surveillance or stalking',
                'Harassment or doxxing',
                'Unauthorized access to systems',
                'Collection of sensitive personal data without consent',
                'Violating website terms of service',
                'Bypassing security measures',
            ],
        }


# Global compliance manager instance
compliance_manager = ComplianceManager()
