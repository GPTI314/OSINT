"""
Chart Visualizer - Creates various chart visualizations for statistical data
"""

from typing import Dict, List, Optional, Any
import json


class ChartVisualizer:
    """
    Creates various chart visualizations:
    - Bar charts
    - Line charts
    - Pie charts
    - Scatter plots
    - Area charts
    - Histogram
    """

    def __init__(self):
        self.charts: Dict[str, Dict] = {}

    def create_bar_chart(self, chart_id: str, data: Dict[str, float],
                        title: str = "Bar Chart", x_label: str = "",
                        y_label: str = "", color: str = "#3498db") -> None:
        """Create a bar chart"""
        self.charts[chart_id] = {
            'type': 'bar',
            'data': data,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'color': color
        }

    def create_line_chart(self, chart_id: str, data: Dict[str, float],
                         title: str = "Line Chart", x_label: str = "",
                         y_label: str = "", color: str = "#3498db") -> None:
        """Create a line chart"""
        self.charts[chart_id] = {
            'type': 'line',
            'data': data,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'color': color
        }

    def create_pie_chart(self, chart_id: str, data: Dict[str, float],
                        title: str = "Pie Chart") -> None:
        """Create a pie chart"""
        self.charts[chart_id] = {
            'type': 'pie',
            'data': data,
            'title': title
        }

    def create_scatter_plot(self, chart_id: str, x_data: List[float],
                          y_data: List[float], title: str = "Scatter Plot",
                          x_label: str = "", y_label: str = "",
                          color: str = "#3498db") -> None:
        """Create a scatter plot"""
        self.charts[chart_id] = {
            'type': 'scatter',
            'x_data': x_data,
            'y_data': y_data,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'color': color
        }

    def create_histogram(self, chart_id: str, data: List[float],
                        bins: int = 20, title: str = "Histogram",
                        x_label: str = "", y_label: str = "Frequency",
                        color: str = "#3498db") -> None:
        """Create a histogram"""
        self.charts[chart_id] = {
            'type': 'histogram',
            'data': data,
            'bins': bins,
            'title': title,
            'x_label': x_label,
            'y_label': y_label,
            'color': color
        }

    def create_multi_line_chart(self, chart_id: str,
                               datasets: Dict[str, Dict[str, float]],
                               title: str = "Multi-Line Chart",
                               x_label: str = "", y_label: str = "") -> None:
        """Create a multi-line chart"""
        self.charts[chart_id] = {
            'type': 'multi_line',
            'datasets': datasets,
            'title': title,
            'x_label': x_label,
            'y_label': y_label
        }

    def generate_plotly_chart(self, chart_id: str) -> Dict:
        """Generate Plotly-compatible chart data"""
        if chart_id not in self.charts:
            return {'data': [], 'layout': {}}

        chart = self.charts[chart_id]
        chart_type = chart['type']

        if chart_type == 'bar':
            return self._generate_plotly_bar(chart)
        elif chart_type == 'line':
            return self._generate_plotly_line(chart)
        elif chart_type == 'pie':
            return self._generate_plotly_pie(chart)
        elif chart_type == 'scatter':
            return self._generate_plotly_scatter(chart)
        elif chart_type == 'histogram':
            return self._generate_plotly_histogram(chart)
        elif chart_type == 'multi_line':
            return self._generate_plotly_multi_line(chart)
        else:
            return {'data': [], 'layout': {}}

    def _generate_plotly_bar(self, chart: Dict) -> Dict:
        """Generate Plotly bar chart"""
        data = [{
            'type': 'bar',
            'x': list(chart['data'].keys()),
            'y': list(chart['data'].values()),
            'marker': {'color': chart['color']}
        }]

        layout = {
            'title': chart['title'],
            'xaxis': {'title': chart.get('x_label', '')},
            'yaxis': {'title': chart.get('y_label', '')},
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_line(self, chart: Dict) -> Dict:
        """Generate Plotly line chart"""
        data = [{
            'type': 'scatter',
            'mode': 'lines+markers',
            'x': list(chart['data'].keys()),
            'y': list(chart['data'].values()),
            'line': {'color': chart['color'], 'width': 2}
        }]

        layout = {
            'title': chart['title'],
            'xaxis': {'title': chart.get('x_label', '')},
            'yaxis': {'title': chart.get('y_label', '')},
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_pie(self, chart: Dict) -> Dict:
        """Generate Plotly pie chart"""
        data = [{
            'type': 'pie',
            'labels': list(chart['data'].keys()),
            'values': list(chart['data'].values())
        }]

        layout = {
            'title': chart['title']
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_scatter(self, chart: Dict) -> Dict:
        """Generate Plotly scatter plot"""
        data = [{
            'type': 'scatter',
            'mode': 'markers',
            'x': chart['x_data'],
            'y': chart['y_data'],
            'marker': {'color': chart['color'], 'size': 8}
        }]

        layout = {
            'title': chart['title'],
            'xaxis': {'title': chart.get('x_label', '')},
            'yaxis': {'title': chart.get('y_label', '')},
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_histogram(self, chart: Dict) -> Dict:
        """Generate Plotly histogram"""
        data = [{
            'type': 'histogram',
            'x': chart['data'],
            'nbinsx': chart['bins'],
            'marker': {'color': chart['color']}
        }]

        layout = {
            'title': chart['title'],
            'xaxis': {'title': chart.get('x_label', '')},
            'yaxis': {'title': chart.get('y_label', '')},
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': data, 'layout': layout}

    def _generate_plotly_multi_line(self, chart: Dict) -> Dict:
        """Generate Plotly multi-line chart"""
        data = []

        colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6']

        for idx, (name, dataset) in enumerate(chart['datasets'].items()):
            trace = {
                'type': 'scatter',
                'mode': 'lines+markers',
                'name': name,
                'x': list(dataset.keys()),
                'y': list(dataset.values()),
                'line': {'color': colors[idx % len(colors)], 'width': 2}
            }
            data.append(trace)

        layout = {
            'title': chart['title'],
            'xaxis': {'title': chart.get('x_label', '')},
            'yaxis': {'title': chart.get('y_label', '')},
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': data, 'layout': layout}

    def export_to_json(self, filepath: str) -> bool:
        """Export all charts to JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.charts, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting charts: {e}")
            return False

    def get_chart(self, chart_id: str) -> Optional[Dict]:
        """Get a specific chart"""
        return self.charts.get(chart_id)

    def list_charts(self) -> List[str]:
        """List all chart IDs"""
        return list(self.charts.keys())

    def clear(self) -> None:
        """Clear all charts"""
        self.charts.clear()
