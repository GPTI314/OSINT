"""
Data encryption utilities for securing sensitive information
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Union
from app.config import settings


class DataEncryption:
    """AES-256 encryption for data at rest"""

    def __init__(self, key: str = None):
        """Initialize with encryption key"""
        key = key or settings.DATA_ENCRYPTION_KEY
        # Ensure key is proper length for Fernet (32 bytes base64 encoded)
        if not isinstance(key, bytes):
            key = key.encode()

        # Derive key if needed
        if len(key) != 44:  # Fernet key length
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'osint_platform_salt',  # In production, use random salt stored securely
                iterations=100000,
                backend=default_backend()
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(key))
            self.cipher = Fernet(derived_key)
        else:
            self.cipher = Fernet(key)

    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data and return base64 encoded string"""
        if isinstance(data, str):
            data = data.encode()

        encrypted = self.cipher.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data and return original string"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_dict(self, data: dict, fields: list = None) -> dict:
        """Encrypt specific fields in a dictionary"""
        encrypted_data = data.copy()
        fields = fields or settings.PII_FIELDS

        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))

        return encrypted_data

    def decrypt_dict(self, data: dict, fields: list = None) -> dict:
        """Decrypt specific fields in a dictionary"""
        decrypted_data = data.copy()
        fields = fields or settings.PII_FIELDS

        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception:
                    pass  # Field might not be encrypted

        return decrypted_data


class PIIProtection:
    """PII (Personally Identifiable Information) protection utilities"""

    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address"""
        if not email or '@' not in email:
            return email

        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number"""
        if not phone:
            return phone

        # Remove non-digits
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) < 4:
            return '*' * len(digits)

        return '*' * (len(digits) - 4) + digits[-4:]

    @staticmethod
    def mask_credit_card(card: str) -> str:
        """Mask credit card number"""
        if not card:
            return card

        digits = ''.join(filter(str.isdigit, card))
        if len(digits) < 4:
            return '*' * len(digits)

        return '*' * (len(digits) - 4) + digits[-4:]

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """Mask SSN (Social Security Number)"""
        if not ssn:
            return ssn

        digits = ''.join(filter(str.isdigit, ssn))
        if len(digits) != 9:
            return '*' * len(digits)

        return f"***-**-{digits[-4:]}"

    @staticmethod
    def mask_field(field_name: str, value: str) -> str:
        """Mask field based on field type"""
        if not value:
            return value

        maskers = {
            'email': PIIProtection.mask_email,
            'phone': PIIProtection.mask_phone,
            'credit_card': PIIProtection.mask_credit_card,
            'ssn': PIIProtection.mask_ssn,
        }

        masker = maskers.get(field_name.lower())
        if masker:
            return masker(value)

        # Default masking
        if len(value) <= 4:
            return '*' * len(value)
        return value[:2] + '*' * (len(value) - 4) + value[-2:]


# Initialize global encryption instance
encryption = DataEncryption()
pii = PIIProtection()
