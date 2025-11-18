"""
Tests for Visualization module
"""

import unittest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '/home/user/OSINT')

from osint_toolkit.analysis_engine.visualization.engine import Visualization


class TestVisualization(unittest.TestCase):
    """Test cases for Visualization"""

    def setUp(self):
        """Set up test environment"""
        self.viz = Visualization()

    def test_network_graph(self):
        """Test network graph creation"""
        self.viz.add_node('node1', label='Node 1')
        self.viz.add_node('node2', label='Node 2')
        self.viz.add_edge('node1', 'node2', label='connected')

        graph_data = self.viz.visualize_network()

        self.assertIn('data', graph_data)
        self.assertIn('layout', graph_data)

    def test_timeline(self):
        """Test timeline creation"""
        now = datetime.now()

        self.viz.add_event('event1', now, 'Event 1', description='First event')
        self.viz.add_event('event2', now + timedelta(hours=1), 'Event 2')

        timeline_data = self.viz.visualize_timeline()

        self.assertIn('data', timeline_data)
        self.assertGreater(len(timeline_data['data']), 0)

    def test_geographic_map(self):
        """Test geographic map creation"""
        self.viz.add_location_marker(40.7128, -74.0060, title='New York')
        self.viz.add_location_marker(51.5074, -0.1278, title='London')

        map_data = self.viz.visualize_map()

        self.assertIn('data', map_data)
        self.assertGreater(len(map_data['data']), 0)

    def test_charts(self):
        """Test chart creation"""
        data = {'A': 10, 'B': 20, 'C': 15}

        self.viz.create_bar_chart('test_bar', data, title='Test Bar Chart')
        chart_data = self.viz.visualize_chart('test_bar')

        self.assertIn('data', chart_data)
        self.assertIn('layout', chart_data)

    def test_heatmap(self):
        """Test heatmap creation"""
        matrix_data = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

        self.viz.create_matrix_heatmap('test_heatmap', matrix_data)
        heatmap_data = self.viz.visualize_heatmap('test_heatmap')

        self.assertIn('data', heatmap_data)
        self.assertGreater(len(heatmap_data['data']), 0)

    def test_dashboard_creation(self):
        """Test comprehensive dashboard creation"""
        dashboard_data = {
            'entities': [
                {'id': 'e1', 'value': 'Entity 1', 'type': 'ip'},
                {'id': 'e2', 'value': 'Entity 2', 'type': 'domain'}
            ],
            'relationships': [
                {'source': 'e1', 'target': 'e2', 'type': 'connected'}
            ],
            'events': [
                {
                    'id': 'ev1',
                    'timestamp': datetime.now().isoformat(),
                    'title': 'Test Event'
                }
            ]
        }

        dashboard = self.viz.create_dashboard(dashboard_data)

        self.assertIn('network', dashboard)
        self.assertIn('timeline', dashboard)

    def test_statistics(self):
        """Test visualization statistics"""
        self.viz.add_node('test1')
        self.viz.add_node('test2')

        stats = self.viz.get_statistics()

        self.assertIn('network', stats)
        self.assertEqual(stats['network']['num_nodes'], 2)


if __name__ == '__main__':
    unittest.main()
