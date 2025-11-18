"""
Timeline Visualizer - Creates timeline visualizations for chronological data
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json


class TimelineVisualizer:
    """
    Creates timeline visualizations:
    - Interactive timelines
    - Gantt charts
    - Event sequences
    - Time-based analysis
    """

    def __init__(self):
        self.events: List[Dict] = []
        self.tracks: Dict[str, List[Dict]] = {}

    def add_event(self, event_id: str, timestamp: datetime, title: str,
                 description: str = "", category: str = "default",
                 duration: timedelta = None, color: str = "#3498db",
                 metadata: Dict = None) -> None:
        """Add an event to the timeline"""
        event = {
            'id': event_id,
            'timestamp': timestamp,
            'title': title,
            'description': description,
            'category': category,
            'duration': duration,
            'color': color,
            'metadata': metadata or {}
        }
        self.events.append(event)

    def add_event_to_track(self, track_name: str, event_id: str,
                          start_time: datetime, end_time: datetime,
                          title: str, color: str = "#3498db",
                          metadata: Dict = None) -> None:
        """Add an event to a specific track (for Gantt-style visualization)"""
        if track_name not in self.tracks:
            self.tracks[track_name] = []

        event = {
            'id': event_id,
            'start': start_time,
            'end': end_time,
            'title': title,
            'color': color,
            'metadata': metadata or {}
        }
        self.tracks[track_name].append(event)

    def generate_plotly_timeline(self, title: str = "Timeline") -> Dict:
        """Generate Plotly-compatible timeline visualization"""
        if not self.events:
            return {'data': [], 'layout': {}}

        # Sort events by timestamp
        sorted_events = sorted(self.events, key=lambda x: x['timestamp'])

        # Group by category
        categories = {}
        for event in sorted_events:
            cat = event['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(event)

        # Create traces for each category
        traces = []
        for cat_name, cat_events in categories.items():
            x_values = [e['timestamp'] for e in cat_events]
            y_values = [e['title'] for e in cat_events]
            text_values = [e['description'] for e in cat_events]
            colors = [e['color'] for e in cat_events]

            trace = {
                'x': x_values,
                'y': y_values,
                'mode': 'markers',
                'marker': {
                    'size': 12,
                    'color': colors,
                    'line': {'width': 2, 'color': 'white'}
                },
                'text': text_values,
                'hoverinfo': 'text+x',
                'name': cat_name
            }
            traces.append(trace)

        layout = {
            'title': title,
            'xaxis': {
                'title': 'Time',
                'type': 'date'
            },
            'yaxis': {
                'title': 'Events'
            },
            'hovermode': 'closest',
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': traces, 'layout': layout}

    def generate_gantt_chart(self, title: str = "Gantt Chart") -> Dict:
        """Generate Gantt chart visualization"""
        if not self.tracks:
            return {'data': [], 'layout': {}}

        traces = []
        y_pos = 0
        y_labels = []

        for track_name, events in self.tracks.items():
            y_labels.append(track_name)

            for event in events:
                duration = (event['end'] - event['start']).total_seconds() / 3600  # hours

                trace = {
                    'x': [duration],
                    'y': [y_pos],
                    'base': event['start'],
                    'orientation': 'h',
                    'marker': {
                        'color': event['color']
                    },
                    'text': event['title'],
                    'hoverinfo': 'text+x',
                    'showlegend': False,
                    'type': 'bar'
                }
                traces.append(trace)

            y_pos += 1

        layout = {
            'title': title,
            'xaxis': {
                'title': 'Time',
                'type': 'date'
            },
            'yaxis': {
                'ticktext': y_labels,
                'tickvals': list(range(len(y_labels)))
            },
            'barmode': 'overlay',
            'plot_bgcolor': '#f8f9fa'
        }

        return {'data': traces, 'layout': layout}

    def generate_timeline_json(self) -> List[Dict]:
        """Generate TimelineJS-compatible JSON"""
        timeline_events = []

        for event in sorted(self.events, key=lambda x: x['timestamp']):
            timeline_event = {
                'start_date': {
                    'year': event['timestamp'].year,
                    'month': event['timestamp'].month,
                    'day': event['timestamp'].day,
                    'hour': event['timestamp'].hour,
                    'minute': event['timestamp'].minute
                },
                'text': {
                    'headline': event['title'],
                    'text': event['description']
                }
            }

            if event['duration']:
                end_time = event['timestamp'] + event['duration']
                timeline_event['end_date'] = {
                    'year': end_time.year,
                    'month': end_time.month,
                    'day': end_time.day,
                    'hour': end_time.hour,
                    'minute': end_time.minute
                }

            timeline_events.append(timeline_event)

        return timeline_events

    def aggregate_by_period(self, period: str = 'day') -> Dict[str, int]:
        """Aggregate events by time period"""
        aggregated = {}

        for event in self.events:
            if period == 'hour':
                key = event['timestamp'].strftime('%Y-%m-%d %H:00')
            elif period == 'day':
                key = event['timestamp'].strftime('%Y-%m-%d')
            elif period == 'week':
                key = f"{event['timestamp'].year}-W{event['timestamp'].strftime('%W')}"
            elif period == 'month':
                key = event['timestamp'].strftime('%Y-%m')
            else:
                key = event['timestamp'].isoformat()

            aggregated[key] = aggregated.get(key, 0) + 1

        return aggregated

    def export_to_json(self, filepath: str) -> bool:
        """Export timeline data to JSON"""
        try:
            data = {
                'events': [
                    {
                        **event,
                        'timestamp': event['timestamp'].isoformat(),
                        'duration': event['duration'].total_seconds() if event['duration'] else None
                    }
                    for event in self.events
                ],
                'tracks': {
                    track_name: [
                        {
                            **event,
                            'start': event['start'].isoformat(),
                            'end': event['end'].isoformat()
                        }
                        for event in events
                    ]
                    for track_name, events in self.tracks.items()
                }
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            return True
        except Exception as e:
            print(f"Error exporting timeline: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get timeline statistics"""
        if not self.events:
            return {
                'total_events': 0,
                'time_span': None,
                'categories': []
            }

        sorted_events = sorted(self.events, key=lambda x: x['timestamp'])
        time_span = sorted_events[-1]['timestamp'] - sorted_events[0]['timestamp']

        categories = list(set(e['category'] for e in self.events))

        return {
            'total_events': len(self.events),
            'time_span': time_span.total_seconds(),
            'start_time': sorted_events[0]['timestamp'].isoformat(),
            'end_time': sorted_events[-1]['timestamp'].isoformat(),
            'categories': categories,
            'num_tracks': len(self.tracks)
        }

    def clear(self) -> None:
        """Clear all timeline data"""
        self.events.clear()
        self.tracks.clear()
