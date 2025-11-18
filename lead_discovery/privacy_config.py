"""
Privacy Configuration System

Configurable privacy controls with GDPR compliance toggle.
Allows runtime configuration for different jurisdictions and use cases.
"""

import os
from typing import Dict, Any, Optional
from enum import Enum


class PrivacyMode(Enum):
    """Privacy mode enumeration."""
    GDPR_STRICT = "gdpr_strict"  # Full GDPR compliance
    STANDARD = "standard"  # Standard privacy practices
    TESTING = "testing"  # Security testing mode (minimal restrictions)


class PrivacyConfig:
    """
    Privacy configuration manager.

    Controls:
    - Data retention policies
    - Cookie consent requirements
    - Data anonymization
    - User rights (access, deletion, portability)
    - Logging and analytics
    - Third-party integrations
    """

    def __init__(self):
        # Load from environment or default to STANDARD
        mode_str = os.getenv('PRIVACY_MODE', 'standard').lower()
        self.mode = self._parse_mode(mode_str)

        # Feature flags
        self.require_consent = os.getenv('REQUIRE_CONSENT', 'true').lower() == 'true'
        self.anonymize_data = os.getenv('ANONYMIZE_DATA', 'true').lower() == 'true'
        self.enable_cross_site_tracking = os.getenv('ENABLE_CROSS_SITE_TRACKING', 'false').lower() == 'true'
        self.enable_fingerprinting = os.getenv('ENABLE_FINGERPRINTING', 'false').lower() == 'true'

    def _parse_mode(self, mode_str: str) -> PrivacyMode:
        """Parse privacy mode from string."""
        mode_map = {
            'gdpr_strict': PrivacyMode.GDPR_STRICT,
            'gdpr': PrivacyMode.GDPR_STRICT,
            'standard': PrivacyMode.STANDARD,
            'testing': PrivacyMode.TESTING,
            'test': PrivacyMode.TESTING,
        }
        return mode_map.get(mode_str, PrivacyMode.STANDARD)

    def is_gdpr_mode(self) -> bool:
        """Check if GDPR strict mode is enabled."""
        return self.mode == PrivacyMode.GDPR_STRICT

    def is_testing_mode(self) -> bool:
        """Check if testing mode is enabled."""
        return self.mode == PrivacyMode.TESTING

    def get_data_retention_days(self, data_type: str) -> int:
        """
        Get data retention period in days.

        Args:
            data_type: Type of data (cookies, profiles, leads, etc.)

        Returns:
            Retention days
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            # GDPR: Limited retention
            return {
                'cookies': 30,
                'profiles': 90,
                'leads': 180,
                'tracking': 30,
                'analytics': 14,
            }.get(data_type, 30)

        elif self.mode == PrivacyMode.STANDARD:
            # Standard: Moderate retention
            return {
                'cookies': 90,
                'profiles': 365,
                'leads': 730,
                'tracking': 180,
                'analytics': 90,
            }.get(data_type, 90)

        else:  # TESTING
            # Testing: Extended retention
            return {
                'cookies': 365,
                'profiles': 730,
                'leads': 1825,
                'tracking': 365,
                'analytics': 365,
            }.get(data_type, 365)

    def requires_consent(self, tracking_type: str) -> bool:
        """
        Check if consent is required for tracking type.

        Args:
            tracking_type: Type of tracking (cookies, fingerprinting, etc.)

        Returns:
            True if consent required
        """
        if not self.require_consent:
            return False

        if self.mode == PrivacyMode.GDPR_STRICT:
            # GDPR: Consent required for all non-essential tracking
            return True

        elif self.mode == PrivacyMode.STANDARD:
            # Standard: Consent for invasive tracking
            return tracking_type in ['fingerprinting', 'cross_site_tracking', 'behavioral_tracking']

        else:  # TESTING
            # Testing: No consent required
            return False

    def should_anonymize(self, data_type: str) -> bool:
        """
        Check if data should be anonymized.

        Args:
            data_type: Type of data

        Returns:
            True if anonymization required
        """
        if not self.anonymize_data:
            return False

        if self.mode == PrivacyMode.GDPR_STRICT:
            # GDPR: Anonymize PII
            return data_type in ['email', 'phone', 'ip_address', 'identifier']

        elif self.mode == PrivacyMode.STANDARD:
            # Standard: Hash sensitive data
            return data_type in ['ip_address', 'identifier']

        else:  # TESTING
            # Testing: Minimal anonymization
            return data_type == 'ip_address'

    def allows_cross_site_tracking(self) -> bool:
        """Check if cross-site tracking is allowed."""
        if self.enable_cross_site_tracking:
            return True

        if self.mode == PrivacyMode.GDPR_STRICT:
            return False  # GDPR: No cross-site tracking without explicit consent

        elif self.mode == PrivacyMode.STANDARD:
            return False  # Standard: Disabled by default

        else:  # TESTING
            return True  # Testing: Allowed

    def allows_fingerprinting(self) -> bool:
        """Check if device fingerprinting is allowed."""
        if self.enable_fingerprinting:
            return True

        if self.mode == PrivacyMode.GDPR_STRICT:
            return False  # GDPR: No fingerprinting without consent

        elif self.mode == PrivacyMode.STANDARD:
            return False  # Standard: Disabled

        else:  # TESTING
            return True  # Testing: Allowed

    def get_cookie_policy(self) -> Dict[str, Any]:
        """
        Get cookie policy configuration.

        Returns:
            Cookie policy settings
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            return {
                'require_consent': True,
                'allow_third_party': False,
                'max_age_days': 30,
                'secure_only': True,
                'same_site': 'Strict',
                'http_only': True,
            }

        elif self.mode == PrivacyMode.STANDARD:
            return {
                'require_consent': True,
                'allow_third_party': False,
                'max_age_days': 90,
                'secure_only': True,
                'same_site': 'Lax',
                'http_only': True,
            }

        else:  # TESTING
            return {
                'require_consent': False,
                'allow_third_party': True,
                'max_age_days': 365,
                'secure_only': False,
                'same_site': 'None',
                'http_only': False,
            }

    def get_user_rights(self) -> Dict[str, bool]:
        """
        Get user rights configuration.

        Returns:
            User rights settings
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            return {
                'right_to_access': True,
                'right_to_deletion': True,
                'right_to_portability': True,
                'right_to_rectification': True,
                'right_to_restriction': True,
                'right_to_object': True,
                'automated_decision_info': True,
            }

        elif self.mode == PrivacyMode.STANDARD:
            return {
                'right_to_access': True,
                'right_to_deletion': True,
                'right_to_portability': False,
                'right_to_rectification': True,
                'right_to_restriction': False,
                'right_to_object': True,
                'automated_decision_info': False,
            }

        else:  # TESTING
            return {
                'right_to_access': True,
                'right_to_deletion': True,
                'right_to_portability': False,
                'right_to_rectification': False,
                'right_to_restriction': False,
                'right_to_object': False,
                'automated_decision_info': False,
            }

    def get_logging_policy(self) -> Dict[str, Any]:
        """
        Get logging policy configuration.

        Returns:
            Logging policy settings
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            return {
                'log_pii': False,
                'log_ip_addresses': False,
                'anonymize_logs': True,
                'retention_days': 30,
                'exclude_sensitive': True,
            }

        elif self.mode == PrivacyMode.STANDARD:
            return {
                'log_pii': False,
                'log_ip_addresses': True,
                'anonymize_logs': False,
                'retention_days': 90,
                'exclude_sensitive': True,
            }

        else:  # TESTING
            return {
                'log_pii': True,
                'log_ip_addresses': True,
                'anonymize_logs': False,
                'retention_days': 365,
                'exclude_sensitive': False,
            }

    def get_analytics_policy(self) -> Dict[str, Any]:
        """
        Get analytics policy configuration.

        Returns:
            Analytics policy settings
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            return {
                'enabled': True,
                'anonymize_ip': True,
                'track_users': False,
                'third_party_analytics': False,
                'retention_days': 14,
            }

        elif self.mode == PrivacyMode.STANDARD:
            return {
                'enabled': True,
                'anonymize_ip': True,
                'track_users': True,
                'third_party_analytics': False,
                'retention_days': 90,
            }

        else:  # TESTING
            return {
                'enabled': True,
                'anonymize_ip': False,
                'track_users': True,
                'third_party_analytics': True,
                'retention_days': 365,
            }

    def get_third_party_policy(self) -> Dict[str, Any]:
        """
        Get third-party integration policy.

        Returns:
            Third-party policy settings
        """
        if self.mode == PrivacyMode.GDPR_STRICT:
            return {
                'allow_third_party_cookies': False,
                'allow_third_party_tracking': False,
                'share_data': False,
                'require_dpa': True,  # Data Processing Agreement
            }

        elif self.mode == PrivacyMode.STANDARD:
            return {
                'allow_third_party_cookies': False,
                'allow_third_party_tracking': False,
                'share_data': True,
                'require_dpa': False,
            }

        else:  # TESTING
            return {
                'allow_third_party_cookies': True,
                'allow_third_party_tracking': True,
                'share_data': True,
                'require_dpa': False,
            }

    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        return {
            'mode': self.mode.value,
            'require_consent': self.require_consent,
            'anonymize_data': self.anonymize_data,
            'enable_cross_site_tracking': self.enable_cross_site_tracking,
            'enable_fingerprinting': self.enable_fingerprinting,
            'cookie_policy': self.get_cookie_policy(),
            'user_rights': self.get_user_rights(),
            'logging_policy': self.get_logging_policy(),
            'analytics_policy': self.get_analytics_policy(),
            'third_party_policy': self.get_third_party_policy(),
        }


# Global privacy configuration instance
_privacy_config: Optional[PrivacyConfig] = None


def get_privacy_config() -> PrivacyConfig:
    """Get global privacy configuration instance."""
    global _privacy_config
    if _privacy_config is None:
        _privacy_config = PrivacyConfig()
    return _privacy_config


def set_privacy_mode(mode: PrivacyMode):
    """Set privacy mode at runtime."""
    global _privacy_config
    if _privacy_config is None:
        _privacy_config = PrivacyConfig()
    _privacy_config.mode = mode


# Example .env configuration:
"""
# Privacy Mode: gdpr_strict, standard, or testing
PRIVACY_MODE=standard

# Feature Flags
REQUIRE_CONSENT=true
ANONYMIZE_DATA=true
ENABLE_CROSS_SITE_TRACKING=false
ENABLE_FINGERPRINTING=false
"""
