"""
Tests for IP Intelligence Module
"""

import pytest
from osint.modules.ip import IPIntelligence
from osint.core.config import Config


class TestIPIntelligence:
    """Test IP Intelligence Module"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = Config()
        self.module = IPIntelligence(self.config.get_all())

    def test_collect_basic(self):
        """Test basic IP intelligence collection"""
        result = self.module.collect('8.8.8.8')

        assert result['success'] is True
        assert result['target'] == '8.8.8.8'
        assert 'data' in result

    def test_collect_invalid_ip(self):
        """Test collection with invalid IP"""
        result = self.module.collect('not-an-ip')

        assert result['success'] is False
        assert 'error' in result

    def test_geolocation(self):
        """Test IP geolocation"""
        geo_data = self.module.get_geolocation('8.8.8.8')

        assert isinstance(geo_data, dict)
        # Should have at least one geolocation source
        assert geo_data

    def test_asn_info(self):
        """Test ASN information retrieval"""
        asn_data = self.module.get_asn_info('8.8.8.8')

        assert isinstance(asn_data, dict)
        # Should contain ASN data or error
        assert asn_data

    def test_service_detection(self):
        """Test service detection"""
        service_data = self.module.detect_services('8.8.8.8')

        assert isinstance(service_data, dict)
