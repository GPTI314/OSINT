"""
Pattern Detector - Identifies patterns, anomalies, and trends in OSINT data
"""

from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from collections import defaultdict, Counter
import re
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass


@dataclass
class Pattern:
    """Represents a detected pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    occurrences: int
    confidence: float
    first_seen: datetime
    last_seen: datetime
    examples: List[Any]
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'id': self.pattern_id,
            'type': self.pattern_type,
            'description': self.description,
            'occurrences': self.occurrences,
            'confidence': self.confidence,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'examples': self.examples[:5],  # Limit examples
            'metadata': self.metadata
        }


class PatternDetector:
    """
    Detects various patterns in OSINT data:
    - Behavioral patterns
    - Communication patterns
    - Anomalies and outliers
    - Recurring sequences
    - Statistical patterns
    """

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.data_history: List[Dict] = []
        self.pattern_rules: List[Callable] = []

    def add_data_point(self, data: Dict, timestamp: datetime = None) -> None:
        """Add a data point to the analysis history"""
        if timestamp is None:
            timestamp = datetime.now()

        data_entry = {
            'data': data,
            'timestamp': timestamp
        }
        self.data_history.append(data_entry)

    def detect_frequency_patterns(self, field: str, min_occurrences: int = 3,
                                 min_confidence: float = 0.5) -> List[Pattern]:
        """Detect frequently occurring values in a specific field"""
        values = []
        timestamps = []

        for entry in self.data_history:
            if field in entry['data']:
                values.append(entry['data'][field])
                timestamps.append(entry['timestamp'])

        if not values:
            return []

        # Count occurrences
        value_counts = Counter(values)
        total_count = len(values)

        patterns = []
        for value, count in value_counts.items():
            if count >= min_occurrences:
                confidence = count / total_count

                if confidence >= min_confidence:
                    # Find first and last occurrence
                    indices = [i for i, v in enumerate(values) if v == value]
                    first_seen = timestamps[indices[0]]
                    last_seen = timestamps[indices[-1]]

                    pattern = Pattern(
                        pattern_id=f"freq_{field}_{hash(str(value))}",
                        pattern_type="frequency",
                        description=f"Frequent value in {field}: {value}",
                        occurrences=count,
                        confidence=confidence,
                        first_seen=first_seen,
                        last_seen=last_seen,
                        examples=[value],
                        metadata={'field': field, 'value': value}
                    )
                    patterns.append(pattern)
                    self.patterns[pattern.pattern_id] = pattern

        return patterns

    def detect_sequential_patterns(self, field: str, sequence_length: int = 3,
                                  min_occurrences: int = 2) -> List[Pattern]:
        """Detect recurring sequences of values"""
        values = []

        for entry in self.data_history:
            if field in entry['data']:
                values.append(entry['data'][field])

        if len(values) < sequence_length:
            return []

        # Generate sequences
        sequences = []
        for i in range(len(values) - sequence_length + 1):
            seq = tuple(values[i:i + sequence_length])
            sequences.append(seq)

        # Count sequence occurrences
        sequence_counts = Counter(sequences)

        patterns = []
        for sequence, count in sequence_counts.items():
            if count >= min_occurrences:
                pattern = Pattern(
                    pattern_id=f"seq_{field}_{hash(sequence)}",
                    pattern_type="sequence",
                    description=f"Recurring sequence in {field}: {' -> '.join(map(str, sequence))}",
                    occurrences=count,
                    confidence=count / len(sequences),
                    first_seen=None,
                    last_seen=None,
                    examples=[list(sequence)],
                    metadata={'field': field, 'sequence': list(sequence), 'length': sequence_length}
                )
                patterns.append(pattern)
                self.patterns[pattern.pattern_id] = pattern

        return patterns

    def detect_temporal_patterns(self, event_field: str = None,
                                min_occurrences: int = 3) -> List[Pattern]:
        """Detect patterns in timing of events"""
        timestamps = [entry['timestamp'] for entry in self.data_history]

        if len(timestamps) < min_occurrences:
            return []

        # Calculate time differences
        intervals = []
        for i in range(1, len(timestamps)):
            delta = timestamps[i] - timestamps[i-1]
            intervals.append(delta.total_seconds())

        if not intervals:
            return []

        # Detect regular intervals
        patterns = []

        # Check for consistent intervals (within 20% variance)
        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

        if std_interval / avg_interval < 0.2:  # Low variance indicates pattern
            pattern = Pattern(
                pattern_id=f"temporal_regular_{hash(tuple(intervals))}",
                pattern_type="temporal_regular",
                description=f"Regular time interval: ~{timedelta(seconds=avg_interval)}",
                occurrences=len(intervals),
                confidence=1 - (std_interval / avg_interval),
                first_seen=timestamps[0],
                last_seen=timestamps[-1],
                examples=[timedelta(seconds=avg_interval)],
                metadata={
                    'avg_interval_seconds': avg_interval,
                    'std_deviation': std_interval
                }
            )
            patterns.append(pattern)
            self.patterns[pattern.pattern_id] = pattern

        # Detect clustering (multiple events in short time)
        time_threshold = timedelta(minutes=5)
        clusters = []
        current_cluster = [timestamps[0]]

        for ts in timestamps[1:]:
            if ts - current_cluster[-1] <= time_threshold:
                current_cluster.append(ts)
            else:
                if len(current_cluster) >= min_occurrences:
                    clusters.append(current_cluster)
                current_cluster = [ts]

        if len(current_cluster) >= min_occurrences:
            clusters.append(current_cluster)

        for idx, cluster in enumerate(clusters):
            pattern = Pattern(
                pattern_id=f"temporal_cluster_{idx}",
                pattern_type="temporal_cluster",
                description=f"Event cluster: {len(cluster)} events in {cluster[-1] - cluster[0]}",
                occurrences=len(cluster),
                confidence=0.8,
                first_seen=cluster[0],
                last_seen=cluster[-1],
                examples=cluster[:5],
                metadata={'cluster_duration': cluster[-1] - cluster[0]}
            )
            patterns.append(pattern)
            self.patterns[pattern.pattern_id] = pattern

        return patterns

    def detect_anomalies(self, field: str, method: str = 'zscore',
                        threshold: float = 3.0) -> List[Pattern]:
        """
        Detect anomalies in numerical data
        Methods: 'zscore', 'iqr', 'isolation'
        """
        values = []
        timestamps = []

        for entry in self.data_history:
            if field in entry['data']:
                try:
                    value = float(entry['data'][field])
                    values.append(value)
                    timestamps.append(entry['timestamp'])
                except (ValueError, TypeError):
                    continue

        if len(values) < 3:
            return []

        anomalies = []

        if method == 'zscore':
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0

            if std_val == 0:
                return []

            for i, value in enumerate(values):
                z_score = abs((value - mean_val) / std_val)
                if z_score > threshold:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'timestamp': timestamps[i],
                        'score': z_score
                    })

        elif method == 'iqr':
            sorted_values = sorted(values)
            q1_idx = len(sorted_values) // 4
            q3_idx = 3 * len(sorted_values) // 4
            q1 = sorted_values[q1_idx]
            q3 = sorted_values[q3_idx]
            iqr = q3 - q1

            lower_bound = q1 - threshold * iqr
            upper_bound = q3 + threshold * iqr

            for i, value in enumerate(values):
                if value < lower_bound or value > upper_bound:
                    distance = min(abs(value - lower_bound), abs(value - upper_bound))
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'timestamp': timestamps[i],
                        'score': distance / iqr if iqr > 0 else 0
                    })

        patterns = []
        for anomaly in anomalies:
            pattern = Pattern(
                pattern_id=f"anomaly_{field}_{anomaly['index']}",
                pattern_type="anomaly",
                description=f"Anomalous value in {field}: {anomaly['value']}",
                occurrences=1,
                confidence=min(anomaly['score'] / threshold, 1.0),
                first_seen=anomaly['timestamp'],
                last_seen=anomaly['timestamp'],
                examples=[anomaly['value']],
                metadata={
                    'field': field,
                    'method': method,
                    'score': anomaly['score']
                }
            )
            patterns.append(pattern)
            self.patterns[pattern.pattern_id] = pattern

        return patterns

    def detect_correlation_patterns(self, field1: str, field2: str,
                                   min_correlation: float = 0.7) -> Optional[Pattern]:
        """Detect correlation between two fields"""
        values1 = []
        values2 = []

        for entry in self.data_history:
            if field1 in entry['data'] and field2 in entry['data']:
                try:
                    v1 = float(entry['data'][field1])
                    v2 = float(entry['data'][field2])
                    values1.append(v1)
                    values2.append(v2)
                except (ValueError, TypeError):
                    continue

        if len(values1) < 3:
            return None

        # Calculate Pearson correlation coefficient
        try:
            import numpy as np
            correlation = np.corrcoef(values1, values2)[0, 1]

            if abs(correlation) >= min_correlation:
                pattern = Pattern(
                    pattern_id=f"correlation_{field1}_{field2}",
                    pattern_type="correlation",
                    description=f"Correlation between {field1} and {field2}: {correlation:.2f}",
                    occurrences=len(values1),
                    confidence=abs(correlation),
                    first_seen=None,
                    last_seen=None,
                    examples=list(zip(values1[:5], values2[:5])),
                    metadata={
                        'field1': field1,
                        'field2': field2,
                        'correlation': correlation
                    }
                )
                self.patterns[pattern.pattern_id] = pattern
                return pattern
        except ImportError:
            pass

        return None

    def detect_string_patterns(self, field: str, min_occurrences: int = 3) -> List[Pattern]:
        """Detect common patterns in string data using regex"""
        values = []

        for entry in self.data_history:
            if field in entry['data']:
                values.append(str(entry['data'][field]))

        if not values:
            return []

        # Common regex patterns to detect
        regex_patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'url': r'https?://[^\s]+',
            'phone': r'\+?[1-9]\d{1,14}',
            'date': r'\d{4}-\d{2}-\d{2}',
            'time': r'\d{2}:\d{2}:\d{2}',
            'hex': r'0x[0-9a-fA-F]+',
            'uuid': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        }

        patterns = []

        for pattern_name, regex in regex_patterns.items():
            matches = []
            for value in values:
                found = re.findall(regex, value)
                matches.extend(found)

            if len(matches) >= min_occurrences:
                pattern = Pattern(
                    pattern_id=f"string_pattern_{field}_{pattern_name}",
                    pattern_type="string_pattern",
                    description=f"String pattern in {field}: {pattern_name}",
                    occurrences=len(matches),
                    confidence=len(matches) / len(values),
                    first_seen=None,
                    last_seen=None,
                    examples=matches[:5],
                    metadata={
                        'field': field,
                        'pattern_name': pattern_name,
                        'regex': regex
                    }
                )
                patterns.append(pattern)
                self.patterns[pattern.pattern_id] = pattern

        return patterns

    def add_custom_pattern_rule(self, rule_func: Callable) -> None:
        """
        Add a custom pattern detection rule
        Rule function should take data_history and return list of Pattern objects
        """
        self.pattern_rules.append(rule_func)

    def run_custom_rules(self) -> List[Pattern]:
        """Run all custom pattern detection rules"""
        patterns = []
        for rule_func in self.pattern_rules:
            try:
                detected = rule_func(self.data_history)
                if detected:
                    patterns.extend(detected)
                    for pattern in detected:
                        self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                print(f"Error running custom rule: {e}")

        return patterns

    def analyze_all(self, fields: List[str] = None) -> Dict[str, List[Pattern]]:
        """Run all pattern detection methods on specified fields"""
        results = {
            'frequency': [],
            'sequential': [],
            'temporal': [],
            'anomalies': [],
            'string_patterns': [],
            'custom': []
        }

        if not fields:
            # Auto-detect fields
            fields = set()
            for entry in self.data_history:
                fields.update(entry['data'].keys())
            fields = list(fields)

        # Frequency patterns
        for field in fields:
            results['frequency'].extend(self.detect_frequency_patterns(field))

        # Sequential patterns
        for field in fields:
            results['sequential'].extend(self.detect_sequential_patterns(field))

        # Temporal patterns
        results['temporal'].extend(self.detect_temporal_patterns())

        # Anomaly detection (for numerical fields)
        for field in fields:
            results['anomalies'].extend(self.detect_anomalies(field))

        # String patterns
        for field in fields:
            results['string_patterns'].extend(self.detect_string_patterns(field))

        # Custom rules
        results['custom'].extend(self.run_custom_rules())

        return results

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a specific pattern by ID"""
        return self.patterns.get(pattern_id)

    def get_patterns_by_type(self, pattern_type: str) -> List[Pattern]:
        """Get all patterns of a specific type"""
        return [p for p in self.patterns.values() if p.pattern_type == pattern_type]

    def get_high_confidence_patterns(self, min_confidence: float = 0.7) -> List[Pattern]:
        """Get patterns with confidence above threshold"""
        return [p for p in self.patterns.values() if p.confidence >= min_confidence]

    def export_patterns(self) -> List[Dict]:
        """Export all detected patterns"""
        return [pattern.to_dict() for pattern in self.patterns.values()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about detected patterns"""
        if not self.patterns:
            return {
                'total_patterns': 0,
                'patterns_by_type': {},
                'avg_confidence': 0,
                'high_confidence_count': 0
            }

        patterns_by_type = defaultdict(int)
        confidences = []

        for pattern in self.patterns.values():
            patterns_by_type[pattern.pattern_type] += 1
            confidences.append(pattern.confidence)

        high_confidence = len([p for p in self.patterns.values() if p.confidence >= 0.7])

        return {
            'total_patterns': len(self.patterns),
            'patterns_by_type': dict(patterns_by_type),
            'avg_confidence': statistics.mean(confidences) if confidences else 0,
            'high_confidence_count': high_confidence,
            'data_points_analyzed': len(self.data_history)
        }
