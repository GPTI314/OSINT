"""
Tests for Domain Intelligence Module
"""

import pytest
from osint.modules.domain import DomainIntelligence
from osint.core.config import Config


class TestDomainIntelligence:
    """Test Domain Intelligence Module"""

    def setup_method(self):
        """Setup test fixtures"""
        self.config = Config()
        self.module = DomainIntelligence(self.config.get_all())

    def test_collect_basic(self):
        """Test basic domain intelligence collection"""
        result = self.module.collect('example.com')

        assert result['success'] is True
        assert result['target'] == 'example.com'
        assert 'data' in result
        assert 'timestamp' in result

    def test_collect_invalid_domain(self):
        """Test collection with invalid domain"""
        result = self.module.collect('not-a-valid-domain!')

        assert result['success'] is False
        assert 'error' in result

    def test_whois_lookup(self):
        """Test WHOIS lookup"""
        whois_data = self.module.get_whois('example.com')

        assert isinstance(whois_data, dict)
        # WHOIS data should contain some information or an error
        assert whois_data

    def test_dns_records(self):
        """Test DNS record retrieval"""
        dns_data = self.module.get_dns_records('example.com')

        assert isinstance(dns_data, dict)
        assert 'A' in dns_data
        assert 'MX' in dns_data
        assert 'TXT' in dns_data

    def test_ssl_certificate(self):
        """Test SSL certificate retrieval"""
        ssl_data = self.module.get_ssl_certificate('example.com')

        assert isinstance(ssl_data, dict)
        # May contain error if SSL connection fails
        assert ssl_data

    def test_technology_detection(self):
        """Test technology detection"""
        tech_data = self.module.detect_technologies('example.com')

        assert isinstance(tech_data, dict)

    def test_subdomain_enumeration(self):
        """Test subdomain enumeration"""
        subdomain_data = self.module.enumerate_subdomains('example.com')

        assert isinstance(subdomain_data, dict)
        assert 'count' in subdomain_data
        assert 'subdomains' in subdomain_data
        assert isinstance(subdomain_data['subdomains'], list)
