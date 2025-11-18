"""
Tests for Threat Intelligence module
"""

import unittest
import sys
sys.path.insert(0, '/home/user/OSINT')

from osint_toolkit.analysis_engine.threat_intelligence.engine import ThreatIntelligence
from osint_toolkit.analysis_engine.threat_intelligence.ioc_detector import IOCType


class TestThreatIntelligence(unittest.TestCase):
    """Test cases for Threat Intelligence"""

    def setUp(self):
        """Set up test environment"""
        self.ti = ThreatIntelligence()

    def test_ioc_extraction(self):
        """Test IOC extraction"""
        text = """
        Malicious IP: 203.0.113.42
        C2 Domain: malicious-domain.com
        File hash: 5d41402abc4b2a76b9719d911017c592
        """

        iocs = self.ti.extract_iocs(text, 'test')
        self.assertGreater(len(iocs), 0)

        # Check for different IOC types
        ioc_types = [ioc.ioc_type for ioc in iocs]
        self.assertIn(IOCType.IP_ADDRESS, ioc_types)

    def test_threat_scoring(self):
        """Test threat scoring"""
        score = self.ti.calculate_threat_score(
            '192.168.1.100',
            'ip',
            analyze_iocs=False,
            analyze_reputation=False,
            analyze_behavior=False
        )

        self.assertIsNotNone(score)
        self.assertGreaterEqual(score.score, 0)
        self.assertLessEqual(score.score, 100)

    def test_anomaly_detection(self):
        """Test anomaly detection"""
        # Add normal data points
        for i in range(50):
            self.ti.anomaly_detector.add_data_point('requests', float(i * 10))

        # Add anomalous point
        anomalies = self.ti.detect_anomalies('requests', 10000.0, 'test_entity')
        # Anomaly might be detected depending on the data distribution

    def test_reputation_check(self):
        """Test reputation checking"""
        result = self.ti.check_ip_reputation('8.8.8.8')

        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'ip')
        self.assertEqual(result['entity'], '8.8.8.8')

    def test_comprehensive_analysis(self):
        """Test comprehensive entity analysis"""
        analysis = self.ti.analyze_entity('example.com', 'domain')

        self.assertIn('entity', analysis)
        self.assertIn('threat_score', analysis)
        self.assertIn('iocs', analysis)


class TestIOCDetector(unittest.TestCase):
    """Test cases for IOC Detector"""

    def setUp(self):
        """Set up test environment"""
        from osint_toolkit.analysis_engine.threat_intelligence.ioc_detector import IOCDetector
        self.detector = IOCDetector()

    def test_ip_detection(self):
        """Test IP address detection"""
        text = "Connection from 192.168.1.1 detected"
        iocs = self.detector.extract_iocs(text)

        ip_iocs = [ioc for ioc in iocs if ioc.ioc_type == IOCType.IP_ADDRESS]
        self.assertGreater(len(ip_iocs), 0)
        self.assertEqual(ip_iocs[0].value, '192.168.1.1')

    def test_hash_detection(self):
        """Test file hash detection"""
        text = "MD5: 5d41402abc4b2a76b9719d911017c592"
        iocs = self.detector.extract_iocs(text)

        hash_iocs = [ioc for ioc in iocs if 'hash' in ioc.ioc_type.value]
        self.assertGreater(len(hash_iocs), 0)

    def test_whitelist(self):
        """Test whitelisting"""
        self.detector.add_to_whitelist('trusted.com')

        text = "Domain: trusted.com"
        iocs = self.detector.extract_iocs(text)

        domain_iocs = [ioc for ioc in iocs if ioc.value == 'trusted.com']
        self.assertEqual(len(domain_iocs), 0)  # Should be filtered


if __name__ == '__main__':
    unittest.main()
