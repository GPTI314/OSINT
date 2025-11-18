"""
Tests for Utility Functions
"""

import pytest
from osint.core.utils import (
    is_valid_domain,
    is_valid_ip,
    is_valid_email,
    is_valid_url,
    extract_domain_from_url,
    calculate_hash,
    parse_phone_number
)


class TestValidators:
    """Test validation functions"""

    def test_is_valid_domain(self):
        """Test domain validation"""
        assert is_valid_domain('example.com') is True
        assert is_valid_domain('sub.example.com') is True
        assert is_valid_domain('not a domain') is False
        assert is_valid_domain('192.168.1.1') is False

    def test_is_valid_ip(self):
        """Test IP validation"""
        assert is_valid_ip('192.168.1.1') is True
        assert is_valid_ip('8.8.8.8') is True
        assert is_valid_ip('2001:4860:4860::8888') is True
        assert is_valid_ip('not-an-ip') is False
        assert is_valid_ip('999.999.999.999') is False

    def test_is_valid_email(self):
        """Test email validation"""
        assert is_valid_email('user@example.com') is True
        assert is_valid_email('test.user@sub.example.com') is True
        assert is_valid_email('not-an-email') is False
        assert is_valid_email('@example.com') is False

    def test_is_valid_url(self):
        """Test URL validation"""
        assert is_valid_url('https://example.com') is True
        assert is_valid_url('http://example.com/path') is True
        assert is_valid_url('ftp://files.example.com') is True
        assert is_valid_url('not a url') is False


class TestUtilityFunctions:
    """Test utility functions"""

    def test_extract_domain_from_url(self):
        """Test domain extraction from URL"""
        assert extract_domain_from_url('https://www.example.com/path') == 'example.com'
        assert extract_domain_from_url('http://sub.example.co.uk') == 'example.co.uk'

    def test_calculate_hash(self):
        """Test hash calculation"""
        data = 'test data'
        md5_hash = calculate_hash(data, 'md5')
        sha256_hash = calculate_hash(data, 'sha256')

        assert len(md5_hash) == 32  # MD5 produces 32 hex characters
        assert len(sha256_hash) == 64  # SHA256 produces 64 hex characters

    def test_parse_phone_number(self):
        """Test phone number parsing"""
        result = parse_phone_number('+1234567890')

        assert isinstance(result, dict)
        assert 'valid' in result
