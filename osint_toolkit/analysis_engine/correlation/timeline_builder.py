"""
Timeline Builder - Constructs and analyzes chronological event timelines
"""

from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict
import bisect


class Event:
    """Represents a timestamped event in the timeline"""

    def __init__(self, event_id: str, timestamp: datetime, event_type: str,
                 description: str, entities: List[str] = None,
                 metadata: Dict = None, confidence: float = 1.0):
        self.id = event_id
        self.timestamp = timestamp
        self.type = event_type
        self.description = description
        self.entities = entities or []
        self.metadata = metadata or {}
        self.confidence = confidence

    def __lt__(self, other):
        """Enable sorting by timestamp"""
        return self.timestamp < other.timestamp

    def __repr__(self):
        return f"Event({self.id}, {self.timestamp}, {self.type})"

    def to_dict(self) -> Dict:
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'type': self.type,
            'description': self.description,
            'entities': self.entities,
            'metadata': self.metadata,
            'confidence': self.confidence
        }


class TimelineBuilder:
    """
    Constructs and analyzes chronological timelines:
    - Add and manage events
    - Query events by time range
    - Detect temporal patterns
    - Analyze event sequences
    - Export timeline data
    """

    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.sorted_events: List[Event] = []
        self.entity_timelines: Dict[str, List[str]] = defaultdict(list)
        self.event_type_index: Dict[str, List[str]] = defaultdict(list)

    def add_event(self, event: Event) -> str:
        """Add an event to the timeline"""
        # Store event
        self.events[event.id] = event

        # Insert into sorted list (maintaining chronological order)
        bisect.insort(self.sorted_events, event)

        # Index by entities
        for entity_id in event.entities:
            self.entity_timelines[entity_id].append(event.id)

        # Index by event type
        self.event_type_index[event.type].append(event.id)

        return event.id

    def create_event(self, event_id: str, timestamp: datetime, event_type: str,
                    description: str, entities: List[str] = None,
                    metadata: Dict = None, confidence: float = 1.0) -> Event:
        """Create and add a new event"""
        event = Event(event_id, timestamp, event_type, description,
                     entities, metadata, confidence)
        self.add_event(event)
        return event

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID"""
        return self.events.get(event_id)

    def get_events_in_range(self, start_time: datetime,
                           end_time: datetime) -> List[Event]:
        """Get all events within a time range"""
        result = []
        for event in self.sorted_events:
            if start_time <= event.timestamp <= end_time:
                result.append(event)
            elif event.timestamp > end_time:
                break
        return result

    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type"""
        event_ids = self.event_type_index.get(event_type, [])
        return [self.events[eid] for eid in event_ids if eid in self.events]

    def get_entity_timeline(self, entity_id: str) -> List[Event]:
        """Get all events related to a specific entity"""
        event_ids = self.entity_timelines.get(entity_id, [])
        events = [self.events[eid] for eid in event_ids if eid in self.events]
        return sorted(events, key=lambda e: e.timestamp)

    def get_events_around(self, reference_time: datetime,
                         window: timedelta) -> List[Event]:
        """Get events within a time window around a reference point"""
        start_time = reference_time - window
        end_time = reference_time + window
        return self.get_events_in_range(start_time, end_time)

    def find_event_sequences(self, entity_id: str,
                           max_gap: timedelta = None) -> List[List[Event]]:
        """
        Find sequences of events for an entity
        If max_gap is specified, break sequences when gap exceeds it
        """
        events = self.get_entity_timeline(entity_id)

        if not events:
            return []

        if max_gap is None:
            return [events]

        # Split into sequences based on time gaps
        sequences = []
        current_sequence = [events[0]]

        for i in range(1, len(events)):
            gap = events[i].timestamp - events[i-1].timestamp

            if gap <= max_gap:
                current_sequence.append(events[i])
            else:
                sequences.append(current_sequence)
                current_sequence = [events[i]]

        sequences.append(current_sequence)
        return sequences

    def detect_temporal_patterns(self, event_type: str = None,
                                min_occurrences: int = 3) -> List[Dict]:
        """
        Detect recurring temporal patterns
        Returns patterns with their intervals and occurrences
        """
        if event_type:
            events = self.get_events_by_type(event_type)
        else:
            events = self.sorted_events

        if len(events) < min_occurrences:
            return []

        # Calculate time differences between consecutive events
        intervals = []
        for i in range(1, len(events)):
            delta = events[i].timestamp - events[i-1].timestamp
            intervals.append(delta.total_seconds())

        # Find recurring intervals (simple frequency analysis)
        interval_counts = defaultdict(int)
        tolerance = 3600  # 1 hour tolerance in seconds

        for interval in intervals:
            # Round to nearest hour
            rounded = round(interval / tolerance) * tolerance
            interval_counts[rounded] += 1

        # Filter patterns with minimum occurrences
        patterns = []
        for interval_seconds, count in interval_counts.items():
            if count >= min_occurrences - 1:
                patterns.append({
                    'interval': timedelta(seconds=interval_seconds),
                    'occurrences': count + 1,
                    'event_type': event_type
                })

        return sorted(patterns, key=lambda x: x['occurrences'], reverse=True)

    def get_event_velocity(self, time_window: timedelta,
                          event_type: str = None) -> List[Tuple[datetime, int]]:
        """
        Calculate event velocity (events per time window) over time
        Returns list of (timestamp, event_count) tuples
        """
        if event_type:
            events = self.get_events_by_type(event_type)
        else:
            events = self.sorted_events

        if not events:
            return []

        velocity = []
        start_time = events[0].timestamp
        end_time = events[-1].timestamp

        current_time = start_time
        while current_time <= end_time:
            window_end = current_time + time_window
            count = len(self.get_events_in_range(current_time, window_end))
            velocity.append((current_time, count))
            current_time = window_end

        return velocity

    def get_concurrent_events(self, time_threshold: timedelta = None) -> List[List[Event]]:
        """
        Find events that occur at the same time (or within threshold)
        Returns groups of concurrent events
        """
        if time_threshold is None:
            time_threshold = timedelta(seconds=0)

        concurrent_groups = []
        visited = set()

        for i, event1 in enumerate(self.sorted_events):
            if event1.id in visited:
                continue

            group = [event1]
            visited.add(event1.id)

            for event2 in self.sorted_events[i+1:]:
                if event2.id in visited:
                    continue

                time_diff = abs(event2.timestamp - event1.timestamp)
                if time_diff <= time_threshold:
                    group.append(event2)
                    visited.add(event2.id)
                else:
                    break  # Events are sorted, so we can break

            if len(group) > 1:
                concurrent_groups.append(group)

        return concurrent_groups

    def find_anomalous_gaps(self, expected_interval: timedelta,
                           tolerance_factor: float = 2.0) -> List[Dict]:
        """
        Find unusually large gaps between events
        Returns list of anomalous gaps with details
        """
        if len(self.sorted_events) < 2:
            return []

        anomalies = []
        expected_seconds = expected_interval.total_seconds()
        max_gap = expected_seconds * tolerance_factor

        for i in range(1, len(self.sorted_events)):
            gap = self.sorted_events[i].timestamp - self.sorted_events[i-1].timestamp
            gap_seconds = gap.total_seconds()

            if gap_seconds > max_gap:
                anomalies.append({
                    'before_event': self.sorted_events[i-1],
                    'after_event': self.sorted_events[i],
                    'gap_duration': gap,
                    'expected_duration': expected_interval,
                    'gap_ratio': gap_seconds / expected_seconds
                })

        return anomalies

    def aggregate_by_period(self, period: str = 'day',
                          event_type: str = None) -> Dict[str, int]:
        """
        Aggregate events by time period (hour, day, week, month)
        Returns dict of {period: event_count}
        """
        if event_type:
            events = self.get_events_by_type(event_type)
        else:
            events = self.sorted_events

        aggregated = defaultdict(int)

        for event in events:
            if period == 'hour':
                key = event.timestamp.strftime('%Y-%m-%d %H:00')
            elif period == 'day':
                key = event.timestamp.strftime('%Y-%m-%d')
            elif period == 'week':
                key = f"{event.timestamp.year}-W{event.timestamp.strftime('%W')}"
            elif period == 'month':
                key = event.timestamp.strftime('%Y-%m')
            elif period == 'year':
                key = event.timestamp.strftime('%Y')
            else:
                key = event.timestamp.isoformat()

            aggregated[key] += 1

        return dict(aggregated)

    def get_busiest_periods(self, period: str = 'day', top_n: int = 10) -> List[Tuple[str, int]]:
        """Get the periods with the most events"""
        aggregated = self.aggregate_by_period(period)
        sorted_periods = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
        return sorted_periods[:top_n]

    def export_timeline(self, start_time: datetime = None,
                       end_time: datetime = None) -> List[Dict]:
        """Export timeline to list of dictionaries"""
        if start_time and end_time:
            events = self.get_events_in_range(start_time, end_time)
        else:
            events = self.sorted_events

        return [event.to_dict() for event in events]

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive timeline statistics"""
        if not self.sorted_events:
            return {
                'total_events': 0,
                'time_span': None,
                'event_types': {},
                'entities_involved': 0
            }

        first_event = self.sorted_events[0]
        last_event = self.sorted_events[-1]
        time_span = last_event.timestamp - first_event.timestamp

        # Event type distribution
        event_type_dist = defaultdict(int)
        for event in self.sorted_events:
            event_type_dist[event.type] += 1

        # Calculate average time between events
        if len(self.sorted_events) > 1:
            total_gaps = sum(
                (self.sorted_events[i].timestamp - self.sorted_events[i-1].timestamp).total_seconds()
                for i in range(1, len(self.sorted_events))
            )
            avg_gap = total_gaps / (len(self.sorted_events) - 1)
        else:
            avg_gap = 0

        return {
            'total_events': len(self.sorted_events),
            'time_span': time_span,
            'start_time': first_event.timestamp,
            'end_time': last_event.timestamp,
            'event_types': dict(event_type_dist),
            'entities_involved': len(self.entity_timelines),
            'avg_time_between_events': timedelta(seconds=avg_gap),
            'events_per_day': len(self.sorted_events) / max(time_span.days, 1)
        }
