"""
Geographic Map Visualizer - Creates geographic visualizations for location-based data
"""

from typing import Dict, List, Optional, Tuple
import json


class GeoMapVisualizer:
    """
    Creates geographic map visualizations:
    - Location markers
    - Heatmaps
    - Choropleth maps
    - Connection lines between locations
    """

    def __init__(self):
        self.markers: List[Dict] = []
        self.connections: List[Dict] = []
        self.heatmap_points: List[Tuple[float, float, float]] = []  # lat, lon, intensity

    def add_marker(self, lat: float, lon: float, title: str = "",
                  description: str = "", icon: str = "circle",
                  color: str = "#3498db", size: int = 10,
                  metadata: Dict = None) -> None:
        """Add a location marker to the map"""
        marker = {
            'lat': lat,
            'lon': lon,
            'title': title,
            'description': description,
            'icon': icon,
            'color': color,
            'size': size,
            'metadata': metadata or {}
        }
        self.markers.append(marker)

    def add_connection(self, source_lat: float, source_lon: float,
                      target_lat: float, target_lon: float,
                      label: str = "", color: str = "#95a5a6",
                      weight: float = 1.0, metadata: Dict = None) -> None:
        """Add a connection line between two locations"""
        connection = {
            'source': {'lat': source_lat, 'lon': source_lon},
            'target': {'lat': target_lat, 'lon': target_lon},
            'label': label,
            'color': color,
            'weight': weight,
            'metadata': metadata or {}
        }
        self.connections.append(connection)

    def add_heatmap_point(self, lat: float, lon: float, intensity: float = 1.0) -> None:
        """Add a point to the heatmap layer"""
        self.heatmap_points.append((lat, lon, intensity))

    def generate_folium_map(self, center: Tuple[float, float] = None,
                          zoom_start: int = 4) -> str:
        """
        Generate Folium map HTML
        Returns HTML string that can be saved to file
        """
        try:
            import folium
            from folium.plugins import HeatMap, MarkerCluster
        except ImportError:
            return "Error: folium library not installed"

        # Determine center if not provided
        if center is None and self.markers:
            avg_lat = sum(m['lat'] for m in self.markers) / len(self.markers)
            avg_lon = sum(m['lon'] for m in self.markers) / len(self.markers)
            center = (avg_lat, avg_lon)
        elif center is None:
            center = (0, 0)

        # Create map
        m = folium.Map(location=center, zoom_start=zoom_start)

        # Add markers with clustering
        if self.markers:
            marker_cluster = MarkerCluster().add_to(m)

            for marker in self.markers:
                folium.Marker(
                    location=[marker['lat'], marker['lon']],
                    popup=f"<b>{marker['title']}</b><br>{marker['description']}",
                    tooltip=marker['title'],
                    icon=folium.Icon(color=marker['color'], icon=marker['icon'])
                ).add_to(marker_cluster)

        # Add connections
        for conn in self.connections:
            folium.PolyLine(
                locations=[
                    [conn['source']['lat'], conn['source']['lon']],
                    [conn['target']['lat'], conn['target']['lon']]
                ],
                color=conn['color'],
                weight=conn['weight'] * 2,
                popup=conn['label']
            ).add_to(m)

        # Add heatmap layer
        if self.heatmap_points:
            HeatMap(
                data=self.heatmap_points,
                radius=15,
                blur=25,
                max_zoom=13
            ).add_to(m)

        return m._repr_html_()

    def generate_plotly_map(self, title: str = "Geographic Map") -> Dict:
        """Generate Plotly-compatible map visualization"""
        data = []

        # Add markers
        if self.markers:
            lats = [m['lat'] for m in self.markers]
            lons = [m['lon'] for m in self.markers]
            texts = [m['title'] for m in self.markers]
            colors = [m['color'] for m in self.markers]
            sizes = [m['size'] for m in self.markers]

            marker_trace = {
                'type': 'scattergeo',
                'lon': lons,
                'lat': lats,
                'text': texts,
                'mode': 'markers',
                'marker': {
                    'size': sizes,
                    'color': colors,
                    'line': {'width': 1, 'color': 'white'}
                },
                'hoverinfo': 'text'
            }
            data.append(marker_trace)

        # Add connections
        for conn in self.connections:
            line_trace = {
                'type': 'scattergeo',
                'lon': [conn['source']['lon'], conn['target']['lon']],
                'lat': [conn['source']['lat'], conn['target']['lat']],
                'mode': 'lines',
                'line': {
                    'width': conn['weight'] * 2,
                    'color': conn['color']
                },
                'hoverinfo': 'text',
                'text': conn['label']
            }
            data.append(line_trace)

        layout = {
            'title': title,
            'geo': {
                'projection': {'type': 'natural earth'},
                'showland': True,
                'landcolor': 'rgb(243, 243, 243)',
                'coastlinecolor': 'rgb(204, 204, 204)',
                'showlakes': True,
                'lakecolor': 'rgb(255, 255, 255)'
            }
        }

        return {'data': data, 'layout': layout}

    def generate_geojson(self) -> Dict:
        """Generate GeoJSON format data"""
        features = []

        # Add markers as Point features
        for marker in self.markers:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [marker['lon'], marker['lat']]
                },
                'properties': {
                    'title': marker['title'],
                    'description': marker['description'],
                    'color': marker['color'],
                    'icon': marker['icon'],
                    'metadata': marker['metadata']
                }
            }
            features.append(feature)

        # Add connections as LineString features
        for conn in self.connections:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': [
                        [conn['source']['lon'], conn['source']['lat']],
                        [conn['target']['lon'], conn['target']['lat']]
                    ]
                },
                'properties': {
                    'label': conn['label'],
                    'color': conn['color'],
                    'weight': conn['weight'],
                    'metadata': conn['metadata']
                }
            }
            features.append(feature)

        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def export_to_geojson(self, filepath: str) -> bool:
        """Export map data to GeoJSON file"""
        try:
            geojson_data = self.generate_geojson()
            with open(filepath, 'w') as f:
                json.dump(geojson_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to GeoJSON: {e}")
            return False

    def export_to_html(self, filepath: str, center: Tuple[float, float] = None,
                      zoom_start: int = 4) -> bool:
        """Export map to HTML file"""
        try:
            html_content = self.generate_folium_map(center, zoom_start)
            with open(filepath, 'w') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get map statistics"""
        if self.markers:
            lats = [m['lat'] for m in self.markers]
            lons = [m['lon'] for m in self.markers]

            bounds = {
                'north': max(lats),
                'south': min(lats),
                'east': max(lons),
                'west': min(lons)
            }
        else:
            bounds = None

        return {
            'num_markers': len(self.markers),
            'num_connections': len(self.connections),
            'num_heatmap_points': len(self.heatmap_points),
            'bounds': bounds
        }

    def clear(self) -> None:
        """Clear all map data"""
        self.markers.clear()
        self.connections.clear()
        self.heatmap_points.clear()
