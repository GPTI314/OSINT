"""
Heatmap Visualizer - Creates heatmap visualizations for activity and correlation analysis
"""

from typing import Dict, List, Optional, Any
import json


class HeatmapVisualizer:
    """
    Creates heatmap visualizations:
    - Activity heatmaps (temporal patterns)
    - Correlation matrices
    - 2D density maps
    - Calendar heatmaps
    """

    def __init__(self):
        self.heatmaps: Dict[str, Dict] = {}

    def create_matrix_heatmap(self, heatmap_id: str, data: List[List[float]],
                            x_labels: List[str] = None,
                            y_labels: List[str] = None,
                            title: str = "Heatmap",
                            colorscale: str = "Viridis") -> None:
        """Create a matrix heatmap"""
        self.heatmaps[heatmap_id] = {
            'type': 'matrix',
            'data': data,
            'x_labels': x_labels or [str(i) for i in range(len(data[0]))],
            'y_labels': y_labels or [str(i) for i in range(len(data))],
            'title': title,
            'colorscale': colorscale
        }

    def create_correlation_heatmap(self, heatmap_id: str,
                                  correlation_matrix: List[List[float]],
                                  labels: List[str],
                                  title: str = "Correlation Matrix") -> None:
        """Create a correlation matrix heatmap"""
        self.heatmaps[heatmap_id] = {
            'type': 'correlation',
            'data': correlation_matrix,
            'labels': labels,
            'title': title,
            'colorscale': 'RdBu'  # Red-Blue for correlation
        }

    def create_temporal_heatmap(self, heatmap_id: str,
                               activity_data: Dict[str, Dict[str, float]],
                               title: str = "Activity Heatmap") -> None:
        """
        Create a temporal activity heatmap
        activity_data: {date: {hour: count}}
        """
        self.heatmaps[heatmap_id] = {
            'type': 'temporal',
            'data': activity_data,
            'title': title,
            'colorscale': 'YlOrRd'  # Yellow-Orange-Red for activity
        }

    def create_calendar_heatmap(self, heatmap_id: str,
                               daily_data: Dict[str, float],
                               title: str = "Calendar Heatmap") -> None:
        """
        Create a calendar heatmap
        daily_data: {date_string: value}
        """
        self.heatmaps[heatmap_id] = {
            'type': 'calendar',
            'data': daily_data,
            'title': title,
            'colorscale': 'Greens'
        }

    def create_2d_density_heatmap(self, heatmap_id: str,
                                  x_data: List[float],
                                  y_data: List[float],
                                  bins: int = 20,
                                  title: str = "2D Density Heatmap") -> None:
        """Create a 2D density heatmap from scatter data"""
        self.heatmaps[heatmap_id] = {
            'type': '2d_density',
            'x_data': x_data,
            'y_data': y_data,
            'bins': bins,
            'title': title,
            'colorscale': 'Hot'
        }

    def generate_plotly_heatmap(self, heatmap_id: str) -> Dict:
        """Generate Plotly-compatible heatmap data"""
        if heatmap_id not in self.heatmaps:
            return {'data': [], 'layout': {}}

        heatmap = self.heatmaps[heatmap_id]
        heatmap_type = heatmap['type']

        if heatmap_type == 'matrix' or heatmap_type == 'correlation':
            return self._generate_plotly_matrix(heatmap)
        elif heatmap_type == 'temporal':
            return self._generate_plotly_temporal(heatmap)
        elif heatmap_type == 'calendar':
            return self._generate_plotly_calendar(heatmap)
        elif heatmap_type == '2d_density':
            return self._generate_plotly_2d_density(heatmap)
        else:
            return {'data': [], 'layout': {}}

    def _generate_plotly_matrix(self, heatmap: Dict) -> Dict:
        """Generate Plotly matrix heatmap"""
        data = [{
            'type': 'heatmap',
            'z': heatmap['data'],
            'x': heatmap.get('x_labels', heatmap.get('labels')),
            'y': heatmap.get('y_labels', heatmap.get('labels')),
            'colorscale': heatmap.get('colorscale', 'Viridis'),
            'showscale': True
        }]

        # Add text annotations for correlation matrices
        if heatmap['type'] == 'correlation':
            annotations = []
            for i, row in enumerate(heatmap['data']):
                for j, value in enumerate(row):
                    annotations.append({
                        'x': j,
                        'y': i,
                        'text': f'{value:.2f}',
                        'showarrow': False,
                        'font': {'color': 'white' if abs(value) > 0.5 else 'black'}
                    })
            layout_annotations = {'annotations': annotations}
        else:
            layout_annotations = {}

        layout = {
            'title': heatmap['title'],
            'xaxis': {'side': 'bottom'},
            'yaxis': {'autorange': 'reversed'},
            **layout_annotations
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_temporal(self, heatmap: Dict) -> Dict:
        """Generate Plotly temporal heatmap"""
        # Convert temporal data to matrix format
        dates = sorted(heatmap['data'].keys())
        hours = list(range(24))

        z_data = []
        for date in dates:
            row = []
            for hour in hours:
                value = heatmap['data'][date].get(str(hour), 0)
                row.append(value)
            z_data.append(row)

        data = [{
            'type': 'heatmap',
            'z': z_data,
            'x': [f"{h:02d}:00" for h in hours],
            'y': dates,
            'colorscale': heatmap.get('colorscale', 'YlOrRd'),
            'showscale': True
        }]

        layout = {
            'title': heatmap['title'],
            'xaxis': {'title': 'Hour of Day'},
            'yaxis': {'title': 'Date'}
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_calendar(self, heatmap: Dict) -> Dict:
        """Generate Plotly calendar heatmap"""
        dates = list(heatmap['data'].keys())
        values = list(heatmap['data'].values())

        data = [{
            'type': 'scatter',
            'x': dates,
            'y': values,
            'mode': 'markers',
            'marker': {
                'size': 10,
                'color': values,
                'colorscale': heatmap.get('colorscale', 'Greens'),
                'showscale': True,
                'colorbar': {'title': 'Activity'}
            }
        }]

        layout = {
            'title': heatmap['title'],
            'xaxis': {'title': 'Date', 'type': 'date'},
            'yaxis': {'title': 'Value'}
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_2d_density(self, heatmap: Dict) -> Dict:
        """Generate Plotly 2D density heatmap"""
        data = [{
            'type': 'histogram2d',
            'x': heatmap['x_data'],
            'y': heatmap['y_data'],
            'nbinsx': heatmap.get('bins', 20),
            'nbinsy': heatmap.get('bins', 20),
            'colorscale': heatmap.get('colorscale', 'Hot'),
            'showscale': True
        }]

        layout = {
            'title': heatmap['title'],
            'xaxis': {'title': 'X'},
            'yaxis': {'title': 'Y'}
        }

        return {'data': data, 'layout': layout}

    def generate_seaborn_heatmap(self, heatmap_id: str) -> Optional[Dict]:
        """Generate Seaborn-compatible heatmap configuration"""
        if heatmap_id not in self.heatmaps:
            return None

        heatmap = self.heatmaps[heatmap_id]

        return {
            'data': heatmap['data'],
            'xticklabels': heatmap.get('x_labels', heatmap.get('labels', True)),
            'yticklabels': heatmap.get('y_labels', heatmap.get('labels', True)),
            'cmap': heatmap.get('colorscale', 'viridis').lower(),
            'annot': heatmap['type'] == 'correlation',
            'fmt': '.2f' if heatmap['type'] == 'correlation' else 'd',
            'square': heatmap['type'] == 'correlation',
            'linewidths': 0.5
        }

    def export_to_json(self, filepath: str) -> bool:
        """Export all heatmaps to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.heatmaps, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting heatmaps: {e}")
            return False

    def get_heatmap(self, heatmap_id: str) -> Optional[Dict]:
        """Get a specific heatmap"""
        return self.heatmaps.get(heatmap_id)

    def list_heatmaps(self) -> List[str]:
        """List all heatmap IDs"""
        return list(self.heatmaps.keys())

    def get_statistics(self) -> Dict:
        """Get heatmap statistics"""
        stats = {
            'total_heatmaps': len(self.heatmaps),
            'by_type': {}
        }

        for heatmap in self.heatmaps.values():
            htype = heatmap['type']
            stats['by_type'][htype] = stats['by_type'].get(htype, 0) + 1

        return stats

    def clear(self) -> None:
        """Clear all heatmaps"""
        self.heatmaps.clear()
