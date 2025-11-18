"""
Sensitive data masking utilities for logs.
"""

import re
import os
from typing import Dict, List, Pattern


class DataMasker:
    """Masks sensitive data in strings using regex patterns."""

    def __init__(self):
        """Initialize masking patterns."""
        self.patterns: Dict[str, Pattern] = {}
        self.enabled_masks: Dict[str, bool] = {}

        # Load configuration from environment
        self.enabled_masks = {
            'email': os.getenv('MASK_EMAILS', 'true').lower() == 'true',
            'ip': os.getenv('MASK_IPS', 'true').lower() == 'true',
            'phone': os.getenv('MASK_PHONE_NUMBERS', 'true').lower() == 'true',
            'api_key': os.getenv('MASK_API_KEYS', 'true').lower() == 'true',
        }

        # Compile regex patterns
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for different sensitive data types."""

        # Email addresses
        self.patterns['email'] = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )

        # IPv4 addresses
        self.patterns['ipv4'] = re.compile(
            r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
            r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        )

        # IPv6 addresses
        self.patterns['ipv6'] = re.compile(
            r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b|'
            r'\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b|'
            r'\b(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\b'
        )

        # Phone numbers (various formats)
        self.patterns['phone'] = re.compile(
            r'\b(?:\+?1[-.\s]?)?'
            r'\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b|'
            r'\b\+?[0-9]{1,3}[-.\s]?(?:\([0-9]{1,4}\)|[0-9]{1,4})[-.\s]?[0-9]{3,4}[-.\s]?[0-9]{3,4}\b'
        )

        # API Keys (common patterns)
        self.patterns['api_key'] = re.compile(
            r'\b(?:api[_-]?key|apikey|access[_-]?token|secret[_-]?key|private[_-]?key)'
            r'["\']?\s*[:=]\s*["\']?([A-Za-z0-9_\-]{16,})["\']?\b',
            re.IGNORECASE
        )

        # Credit card numbers
        self.patterns['credit_card'] = re.compile(
            r'\b(?:4[0-9]{12}(?:[0-9]{3})?|'  # Visa
            r'5[1-5][0-9]{14}|'  # MasterCard
            r'3[47][0-9]{13}|'  # American Express
            r'3(?:0[0-5]|[68][0-9])[0-9]{11}|'  # Diners Club
            r'6(?:011|5[0-9]{2})[0-9]{12}|'  # Discover
            r'(?:2131|1800|35\d{3})\d{11})\b'  # JCB
        )

        # Social Security Numbers (US)
        self.patterns['ssn'] = re.compile(
            r'\b(?!000|666|9\d{2})\d{3}-?(?!00)\d{2}-?(?!0000)\d{4}\b'
        )

        # Passwords in URLs or config
        self.patterns['password'] = re.compile(
            r'\b(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^\s"\']+)["\']?\b',
            re.IGNORECASE
        )

        # Bearer tokens
        self.patterns['bearer_token'] = re.compile(
            r'\bBearer\s+([A-Za-z0-9_\-\.]+)\b',
            re.IGNORECASE
        )

        # AWS Access Keys
        self.patterns['aws_key'] = re.compile(
            r'\b(AKIA[0-9A-Z]{16})\b'
        )

        # JWT tokens
        self.patterns['jwt'] = re.compile(
            r'\beyJ[A-Za-z0-9_\-]*\.eyJ[A-Za-z0-9_\-]*\.[A-Za-z0-9_\-]*\b'
        )

    def mask_email(self, text: str) -> str:
        """Mask email addresses."""
        if not self.enabled_masks.get('email', True):
            return text

        def replace_email(match):
            email = match.group(0)
            parts = email.split('@')
            if len(parts) == 2:
                username = parts[0]
                domain = parts[1]
                masked_username = username[0] + '*' * (len(username) - 1) if len(username) > 1 else '*'
                return f"{masked_username}@{domain}"
            return '***@***.***'

        return self.patterns['email'].sub(replace_email, text)

    def mask_ip(self, text: str) -> str:
        """Mask IP addresses."""
        if not self.enabled_masks.get('ip', True):
            return text

        # Mask IPv4
        text = self.patterns['ipv4'].sub('XXX.XXX.XXX.XXX', text)

        # Mask IPv6
        text = self.patterns['ipv6'].sub('XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:XXXX', text)

        return text

    def mask_phone(self, text: str) -> str:
        """Mask phone numbers."""
        if not self.enabled_masks.get('phone', True):
            return text

        return self.patterns['phone'].sub('XXX-XXX-XXXX', text)

    def mask_api_key(self, text: str) -> str:
        """Mask API keys and tokens."""
        if not self.enabled_masks.get('api_key', True):
            return text

        # API keys
        text = self.patterns['api_key'].sub(r'\1: ********', text)

        # Bearer tokens
        text = self.patterns['bearer_token'].sub('Bearer ********', text)

        # AWS keys
        text = self.patterns['aws_key'].sub('AKIA****************', text)

        # JWT tokens
        text = self.patterns['jwt'].sub('eyJ***.****.****', text)

        return text

    def mask_credit_card(self, text: str) -> str:
        """Mask credit card numbers."""
        def replace_cc(match):
            cc = match.group(0)
            return '*' * (len(cc) - 4) + cc[-4:] if len(cc) >= 4 else '****'

        return self.patterns['credit_card'].sub(replace_cc, text)

    def mask_ssn(self, text: str) -> str:
        """Mask Social Security Numbers."""
        return self.patterns['ssn'].sub('XXX-XX-XXXX', text)

    def mask_password(self, text: str) -> str:
        """Mask passwords in configuration strings."""
        return self.patterns['password'].sub(r'\1: ********', text)

    def mask_all(self, text: str) -> str:
        """
        Apply all masking patterns to the text.

        Args:
            text: Input text

        Returns:
            Text with sensitive data masked
        """
        if not isinstance(text, str):
            return text

        text = self.mask_email(text)
        text = self.mask_ip(text)
        text = self.mask_phone(text)
        text = self.mask_api_key(text)
        text = self.mask_credit_card(text)
        text = self.mask_ssn(text)
        text = self.mask_password(text)

        return text

    def mask_dict(self, data: dict, sensitive_keys: List[str] = None) -> dict:
        """
        Mask sensitive values in a dictionary.

        Args:
            data: Dictionary to mask
            sensitive_keys: List of keys to mask (default: common sensitive keys)

        Returns:
            Dictionary with masked values
        """
        if sensitive_keys is None:
            sensitive_keys = [
                'password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
                'apikey', 'access_key', 'private_key', 'auth', 'authorization',
                'credential', 'session', 'cookie'
            ]

        masked_data = {}
        for key, value in data.items():
            # Check if key is sensitive
            if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
                masked_data[key] = '********'
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value, sensitive_keys)
            elif isinstance(value, str):
                masked_data[key] = self.mask_all(value)
            else:
                masked_data[key] = value

        return masked_data
