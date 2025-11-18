"""
Visualization Engine - Main engine integrating all visualization components
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from osint_toolkit.analysis_engine.visualization.network_graph import NetworkGraphVisualizer
from osint_toolkit.analysis_engine.visualization.timeline_viz import TimelineVisualizer
from osint_toolkit.analysis_engine.visualization.geo_map import GeoMapVisualizer
from osint_toolkit.analysis_engine.visualization.charts import ChartVisualizer
from osint_toolkit.analysis_engine.visualization.heatmap import HeatmapVisualizer


class Visualization:
    """
    Main visualization engine that integrates:
    - Network graphs
    - Timeline views
    - Geographic maps
    - Charts and graphs
    - Heatmaps
    """

    def __init__(self):
        self.network_graph = NetworkGraphVisualizer()
        self.timeline = TimelineVisualizer()
        self.geo_map = GeoMapVisualizer()
        self.charts = ChartVisualizer()
        self.heatmaps = HeatmapVisualizer()

    # Network Graph Operations
    def add_node(self, node_id: str, **kwargs) -> None:
        """Add a node to the network graph"""
        self.network_graph.add_node(node_id, **kwargs)

    def add_edge(self, source: str, target: str, **kwargs) -> None:
        """Add an edge to the network graph"""
        self.network_graph.add_edge(source, target, **kwargs)

    def visualize_network(self, layout_type: str = 'force',
                         style_by_centrality: bool = True,
                         color_by_community: bool = True,
                         title: str = "Network Graph") -> Dict:
        """
        Create a comprehensive network visualization
        """
        # Apply styling
        if style_by_centrality:
            self.network_graph.style_by_centrality('pagerank')

        if color_by_community:
            try:
                self.network_graph.color_by_community('louvain')
            except:
                pass  # Skip if community detection fails

        # Generate visualization
        return self.network_graph.generate_plotly_graph(layout_type, title)

    def export_network_graph(self, filepath: str, format: str = 'json') -> bool:
        """Export network graph in specified format"""
        if format == 'json':
            return self.network_graph.export_to_json(filepath)
        elif format == 'gexf':
            return self.network_graph.export_to_gexf(filepath)
        elif format == 'graphml':
            return self.network_graph.export_to_graphml(filepath)
        else:
            return False

    # Timeline Operations
    def add_event(self, event_id: str, timestamp: datetime, title: str, **kwargs) -> None:
        """Add an event to the timeline"""
        self.timeline.add_event(event_id, timestamp, title, **kwargs)

    def add_timeline_track(self, track_name: str, event_id: str,
                          start_time: datetime, end_time: datetime,
                          title: str, **kwargs) -> None:
        """Add an event to a timeline track"""
        self.timeline.add_event_to_track(track_name, event_id, start_time,
                                        end_time, title, **kwargs)

    def visualize_timeline(self, style: str = 'timeline',
                          title: str = "Timeline") -> Dict:
        """
        Create a timeline visualization
        style: 'timeline' or 'gantt'
        """
        if style == 'gantt':
            return self.timeline.generate_gantt_chart(title)
        else:
            return self.timeline.generate_plotly_timeline(title)

    def export_timeline(self, filepath: str) -> bool:
        """Export timeline data to JSON"""
        return self.timeline.export_to_json(filepath)

    # Geographic Map Operations
    def add_location_marker(self, lat: float, lon: float, **kwargs) -> None:
        """Add a location marker to the map"""
        self.geo_map.add_marker(lat, lon, **kwargs)

    def add_location_connection(self, source_lat: float, source_lon: float,
                               target_lat: float, target_lon: float, **kwargs) -> None:
        """Add a connection between two locations"""
        self.geo_map.add_connection(source_lat, source_lon,
                                   target_lat, target_lon, **kwargs)

    def add_heatmap_point(self, lat: float, lon: float, intensity: float = 1.0) -> None:
        """Add a point to the geographic heatmap"""
        self.geo_map.add_heatmap_point(lat, lon, intensity)

    def visualize_map(self, title: str = "Geographic Map") -> Dict:
        """Create a geographic map visualization"""
        return self.geo_map.generate_plotly_map(title)

    def export_map(self, filepath: str, format: str = 'geojson',
                  center: Tuple[float, float] = None) -> bool:
        """Export map in specified format"""
        if format == 'geojson':
            return self.geo_map.export_to_geojson(filepath)
        elif format == 'html':
            return self.geo_map.export_to_html(filepath, center)
        else:
            return False

    # Chart Operations
    def create_bar_chart(self, chart_id: str, data: Dict[str, float], **kwargs) -> None:
        """Create a bar chart"""
        self.charts.create_bar_chart(chart_id, data, **kwargs)

    def create_line_chart(self, chart_id: str, data: Dict[str, float], **kwargs) -> None:
        """Create a line chart"""
        self.charts.create_line_chart(chart_id, data, **kwargs)

    def create_pie_chart(self, chart_id: str, data: Dict[str, float], **kwargs) -> None:
        """Create a pie chart"""
        self.charts.create_pie_chart(chart_id, data, **kwargs)

    def create_scatter_plot(self, chart_id: str, x_data: List[float],
                           y_data: List[float], **kwargs) -> None:
        """Create a scatter plot"""
        self.charts.create_scatter_plot(chart_id, x_data, y_data, **kwargs)

    def visualize_chart(self, chart_id: str) -> Dict:
        """Visualize a specific chart"""
        return self.charts.generate_plotly_chart(chart_id)

    def export_charts(self, filepath: str) -> bool:
        """Export all charts to JSON"""
        return self.charts.export_to_json(filepath)

    # Heatmap Operations
    def create_matrix_heatmap(self, heatmap_id: str, data: List[List[float]], **kwargs) -> None:
        """Create a matrix heatmap"""
        self.heatmaps.create_matrix_heatmap(heatmap_id, data, **kwargs)

    def create_correlation_heatmap(self, heatmap_id: str,
                                  correlation_matrix: List[List[float]],
                                  labels: List[str], **kwargs) -> None:
        """Create a correlation matrix heatmap"""
        self.heatmaps.create_correlation_heatmap(heatmap_id, correlation_matrix,
                                                 labels, **kwargs)

    def create_temporal_heatmap(self, heatmap_id: str,
                               activity_data: Dict[str, Dict[str, float]], **kwargs) -> None:
        """Create a temporal activity heatmap"""
        self.heatmaps.create_temporal_heatmap(heatmap_id, activity_data, **kwargs)

    def visualize_heatmap(self, heatmap_id: str) -> Dict:
        """Visualize a specific heatmap"""
        return self.heatmaps.generate_plotly_heatmap(heatmap_id)

    def export_heatmaps(self, filepath: str) -> bool:
        """Export all heatmaps to JSON"""
        return self.heatmaps.export_to_json(filepath)

    # Integrated Visualization Operations
    def visualize_entity_network(self, entities: List[Dict],
                                relationships: List[Dict],
                                layout: str = 'force') -> Dict:
        """
        Create a comprehensive entity relationship network visualization
        """
        # Clear existing graph
        self.network_graph.clear()

        # Add entities as nodes
        for entity in entities:
            self.network_graph.add_node(
                entity['id'],
                label=entity.get('value', entity['id']),
                node_type=entity.get('type', 'unknown'),
                size=entity.get('size', 10),
                color=entity.get('color', '#3498db'),
                metadata=entity.get('metadata', {})
            )

        # Add relationships as edges
        for rel in relationships:
            self.network_graph.add_edge(
                rel['source'],
                rel['target'],
                label=rel.get('type', ''),
                weight=rel.get('weight', 1.0),
                color=rel.get('color', '#95a5a6')
            )

        # Generate visualization
        return self.visualize_network(layout, True, True, "Entity Network")

    def visualize_threat_landscape(self, threat_data: Dict) -> Dict[str, Any]:
        """
        Create comprehensive threat landscape visualization
        """
        visualizations = {}

        # 1. Threat distribution pie chart
        if 'threat_levels' in threat_data:
            self.create_pie_chart(
                'threat_distribution',
                threat_data['threat_levels'],
                title="Threat Level Distribution"
            )
            visualizations['threat_distribution'] = self.visualize_chart('threat_distribution')

        # 2. Timeline of threats
        if 'timeline' in threat_data:
            for event in threat_data['timeline']:
                self.add_event(
                    event['id'],
                    datetime.fromisoformat(event['timestamp']),
                    event['title'],
                    description=event.get('description', ''),
                    category='threat'
                )
            visualizations['timeline'] = self.visualize_timeline()

        # 3. Geographic threat distribution
        if 'locations' in threat_data:
            for loc in threat_data['locations']:
                self.add_location_marker(
                    loc['lat'],
                    loc['lon'],
                    title=loc.get('title', ''),
                    description=loc.get('description', ''),
                    color='#e74c3c'  # Red for threats
                )
            visualizations['map'] = self.visualize_map("Threat Distribution")

        return visualizations

    def create_dashboard(self, data: Dict) -> Dict[str, Any]:
        """
        Create a comprehensive dashboard with multiple visualizations
        """
        dashboard = {
            'network': None,
            'timeline': None,
            'map': None,
            'charts': {},
            'heatmaps': {}
        }

        # Network visualization
        if 'entities' in data and 'relationships' in data:
            dashboard['network'] = self.visualize_entity_network(
                data['entities'],
                data['relationships']
            )

        # Timeline visualization
        if 'events' in data:
            for event in data['events']:
                self.add_event(
                    event['id'],
                    datetime.fromisoformat(event['timestamp']),
                    event['title'],
                    **{k: v for k, v in event.items()
                       if k not in ['id', 'timestamp', 'title']}
                )
            dashboard['timeline'] = self.visualize_timeline()

        # Map visualization
        if 'locations' in data:
            for loc in data['locations']:
                self.add_location_marker(loc['lat'], loc['lon'], **loc)
            dashboard['map'] = self.visualize_map()

        # Charts
        if 'charts' in data:
            for chart_id, chart_data in data['charts'].items():
                chart_type = chart_data.get('type', 'bar')
                if chart_type == 'bar':
                    self.create_bar_chart(chart_id, chart_data['data'], **chart_data)
                elif chart_type == 'line':
                    self.create_line_chart(chart_id, chart_data['data'], **chart_data)
                elif chart_type == 'pie':
                    self.create_pie_chart(chart_id, chart_data['data'], **chart_data)

                dashboard['charts'][chart_id] = self.visualize_chart(chart_id)

        # Heatmaps
        if 'heatmaps' in data:
            for hm_id, hm_data in data['heatmaps'].items():
                if hm_data['type'] == 'correlation':
                    self.create_correlation_heatmap(
                        hm_id,
                        hm_data['data'],
                        hm_data['labels'],
                        **hm_data
                    )
                dashboard['heatmaps'][hm_id] = self.visualize_heatmap(hm_id)

        return dashboard

    def export_all(self, directory: str) -> Dict[str, bool]:
        """Export all visualizations to specified directory"""
        import os

        os.makedirs(directory, exist_ok=True)

        results = {}

        # Export network graph
        results['network'] = self.export_network_graph(
            os.path.join(directory, 'network.json')
        )

        # Export timeline
        results['timeline'] = self.export_timeline(
            os.path.join(directory, 'timeline.json')
        )

        # Export map
        results['map'] = self.export_map(
            os.path.join(directory, 'map.geojson'),
            format='geojson'
        )

        # Export charts
        results['charts'] = self.export_charts(
            os.path.join(directory, 'charts.json')
        )

        # Export heatmaps
        results['heatmaps'] = self.export_heatmaps(
            os.path.join(directory, 'heatmaps.json')
        )

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from all visualization components"""
        return {
            'network': self.network_graph.get_statistics(),
            'timeline': self.timeline.get_statistics(),
            'map': self.geo_map.get_statistics(),
            'charts': {
                'total_charts': len(self.charts.list_charts()),
                'chart_ids': self.charts.list_charts()
            },
            'heatmaps': self.heatmaps.get_statistics()
        }

    def clear_all(self) -> None:
        """Clear all visualization data"""
        self.network_graph.clear()
        self.timeline.clear()
        self.geo_map.clear()
        self.charts.clear()
        self.heatmaps.clear()
