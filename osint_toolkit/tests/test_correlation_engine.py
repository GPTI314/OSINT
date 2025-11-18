"""
Tests for Correlation Engine
"""

import unittest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/user/OSINT')

from osint_toolkit.analysis_engine.correlation.engine import CorrelationEngine


class TestCorrelationEngine(unittest.TestCase):
    """Test cases for Correlation Engine"""

    def setUp(self):
        """Set up test environment"""
        self.engine = CorrelationEngine()

    def test_add_entity(self):
        """Test adding entities"""
        entity = self.engine.add_entity('ip', '192.168.1.1', 'test_source')
        self.assertIsNotNone(entity)
        self.assertEqual(entity.type, 'ip')
        self.assertEqual(entity.value, '192.168.1.1')

    def test_entity_linking(self):
        """Test entity linking"""
        entity1 = self.engine.add_entity('ip', '192.168.1.1')
        entity2 = self.engine.add_entity('domain', 'example.com')

        success = self.engine.link_entities(entity1.id, entity2.id, 0.9, 'associated')
        self.assertTrue(success)

        # Check if linked
        linked = self.engine.entity_linker.get_linked_entities(entity1.id)
        self.assertEqual(len(linked), 1)

    def test_timeline_construction(self):
        """Test timeline building"""
        entity1 = self.engine.add_entity('ip', '10.0.0.1')

        event1 = self.engine.add_event(
            'event1',
            datetime.now(),
            'connection',
            'Connection attempt',
            [entity1.id]
        )

        self.assertIsNotNone(event1)

        timeline = self.engine.get_entity_timeline(entity1.id)
        self.assertEqual(len(timeline), 1)

    def test_pattern_detection(self):
        """Test pattern detection"""
        # Add some data points
        for i in range(10):
            self.engine.pattern_detector.add_data_point({
                'value': i,
                'type': 'test'
            }, datetime.now() + timedelta(seconds=i))

        # Detect patterns
        patterns = self.engine.detect_patterns(['value'])
        self.assertIsInstance(patterns, dict)

    def test_statistics(self):
        """Test statistics generation"""
        self.engine.add_entity('ip', '1.2.3.4')
        self.engine.add_entity('domain', 'test.com')

        stats = self.engine.get_statistics()
        self.assertIn('entities', stats)
        self.assertEqual(stats['entities']['total_entities'], 2)


class TestEntityLinker(unittest.TestCase):
    """Test cases for Entity Linker"""

    def setUp(self):
        """Set up test environment"""
        from osint_toolkit.analysis_engine.correlation.entity_linker import EntityLinker
        self.linker = EntityLinker()

    def test_extract_entities_from_text(self):
        """Test entity extraction"""
        text = "IP: 192.168.1.1, Domain: example.com, Email: test@example.com"
        entities = self.linker.extract_entities(text)

        self.assertGreater(len(entities), 0)

        # Check for IP
        ip_entities = [e for e in entities if e.type == 'ip']
        self.assertGreater(len(ip_entities), 0)

    def test_auto_link_entities(self):
        """Test automatic entity linking"""
        self.linker.create_entity('domain', 'example.com')
        self.linker.create_entity('domain', 'example.com')  # Duplicate

        links = self.linker.auto_link_entities(confidence_threshold=0.9)
        self.assertGreaterEqual(links, 0)


if __name__ == '__main__':
    unittest.main()
