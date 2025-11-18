"""
Anomaly Detector - Detects unusual patterns and anomalies using statistical and ML methods
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import statistics
import math


@dataclass
class Anomaly:
    """Represents a detected anomaly"""
    anomaly_id: str
    anomaly_type: str
    description: str
    severity: float  # 0-100
    timestamp: datetime
    entity_id: Optional[str]
    field: str
    expected_value: Any
    actual_value: Any
    deviation_score: float
    metadata: Dict

    def to_dict(self) -> Dict:
        return {
            'id': self.anomaly_id,
            'type': self.anomaly_type,
            'description': self.description,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'entity_id': self.entity_id,
            'field': self.field,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'deviation_score': self.deviation_score,
            'metadata': self.metadata
        }


class AnomalyDetector:
    """
    Detects anomalies using various methods:
    - Statistical anomaly detection (Z-score, IQR)
    - Time series anomaly detection
    - Behavioral anomaly detection
    - Volume/frequency anomalies
    - Pattern-based anomalies
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.data_windows: Dict[str, deque] = {}
        self.anomalies: List[Anomaly] = []
        self.baselines: Dict[str, Dict] = {}
        self.anomaly_counter = 0

    def add_data_point(self, field: str, value: float, timestamp: datetime = None,
                      entity_id: str = None) -> None:
        """Add a data point for anomaly detection"""
        if field not in self.data_windows:
            self.data_windows[field] = deque(maxlen=self.window_size)

        if timestamp is None:
            timestamp = datetime.now()

        self.data_windows[field].append({
            'value': value,
            'timestamp': timestamp,
            'entity_id': entity_id
        })

    def calculate_baseline(self, field: str) -> Dict:
        """Calculate baseline statistics for a field"""
        if field not in self.data_windows or len(self.data_windows[field]) < 3:
            return {}

        values = [dp['value'] for dp in self.data_windows[field]]

        baseline = {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
            'min': min(values),
            'max': max(values),
            'count': len(values)
        }

        # Calculate quartiles for IQR
        sorted_values = sorted(values)
        n = len(sorted_values)
        baseline['q1'] = sorted_values[n // 4]
        baseline['q3'] = sorted_values[3 * n // 4]
        baseline['iqr'] = baseline['q3'] - baseline['q1']

        self.baselines[field] = baseline
        return baseline

    def detect_zscore_anomaly(self, field: str, value: float,
                             threshold: float = 3.0,
                             entity_id: str = None) -> Optional[Anomaly]:
        """
        Detect anomalies using Z-score method
        threshold: number of standard deviations (default: 3.0)
        """
        baseline = self.baselines.get(field) or self.calculate_baseline(field)

        if not baseline or baseline.get('stdev', 0) == 0:
            return None

        z_score = abs((value - baseline['mean']) / baseline['stdev'])

        if z_score > threshold:
            severity = min((z_score / threshold) * 50, 100)

            anomaly = Anomaly(
                anomaly_id=f"zscore_{self.anomaly_counter}",
                anomaly_type="statistical_zscore",
                description=f"Value {value} deviates {z_score:.2f} standard deviations from mean",
                severity=severity,
                timestamp=datetime.now(),
                entity_id=entity_id,
                field=field,
                expected_value=baseline['mean'],
                actual_value=value,
                deviation_score=z_score,
                metadata={
                    'method': 'zscore',
                    'threshold': threshold,
                    'baseline': baseline
                }
            )

            self.anomalies.append(anomaly)
            self.anomaly_counter += 1
            return anomaly

        return None

    def detect_iqr_anomaly(self, field: str, value: float,
                          multiplier: float = 1.5,
                          entity_id: str = None) -> Optional[Anomaly]:
        """
        Detect anomalies using Interquartile Range (IQR) method
        multiplier: IQR multiplier for outlier detection (default: 1.5)
        """
        baseline = self.baselines.get(field) or self.calculate_baseline(field)

        if not baseline or baseline.get('iqr', 0) == 0:
            return None

        lower_bound = baseline['q1'] - multiplier * baseline['iqr']
        upper_bound = baseline['q3'] + multiplier * baseline['iqr']

        if value < lower_bound or value > upper_bound:
            # Calculate severity based on how far outside bounds
            if value < lower_bound:
                deviation = (lower_bound - value) / baseline['iqr']
                expected = lower_bound
            else:
                deviation = (value - upper_bound) / baseline['iqr']
                expected = upper_bound

            severity = min(deviation * 30, 100)

            anomaly = Anomaly(
                anomaly_id=f"iqr_{self.anomaly_counter}",
                anomaly_type="statistical_iqr",
                description=f"Value {value} is outside IQR bounds [{lower_bound:.2f}, {upper_bound:.2f}]",
                severity=severity,
                timestamp=datetime.now(),
                entity_id=entity_id,
                field=field,
                expected_value=expected,
                actual_value=value,
                deviation_score=deviation,
                metadata={
                    'method': 'iqr',
                    'multiplier': multiplier,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'baseline': baseline
                }
            )

            self.anomalies.append(anomaly)
            self.anomaly_counter += 1
            return anomaly

        return None

    def detect_rate_anomaly(self, field: str, current_rate: float,
                           threshold_multiplier: float = 2.0,
                           entity_id: str = None) -> Optional[Anomaly]:
        """
        Detect anomalies in rate of change
        threshold_multiplier: how many times normal rate constitutes anomaly
        """
        baseline = self.baselines.get(field) or self.calculate_baseline(field)

        if not baseline:
            return None

        # Calculate average rate from historical data
        if field in self.data_windows and len(self.data_windows[field]) >= 2:
            data_points = list(self.data_windows[field])
            rates = []

            for i in range(1, len(data_points)):
                time_diff = (data_points[i]['timestamp'] - data_points[i-1]['timestamp']).total_seconds()
                if time_diff > 0:
                    rate = (data_points[i]['value'] - data_points[i-1]['value']) / time_diff
                    rates.append(abs(rate))

            if rates:
                avg_rate = statistics.mean(rates)
                expected_rate = avg_rate

                if current_rate > avg_rate * threshold_multiplier:
                    severity = min((current_rate / avg_rate) * 20, 100)

                    anomaly = Anomaly(
                        anomaly_id=f"rate_{self.anomaly_counter}",
                        anomaly_type="rate_anomaly",
                        description=f"Rate {current_rate:.2f} exceeds normal rate by {current_rate/avg_rate:.2f}x",
                        severity=severity,
                        timestamp=datetime.now(),
                        entity_id=entity_id,
                        field=field,
                        expected_value=expected_rate,
                        actual_value=current_rate,
                        deviation_score=current_rate / avg_rate,
                        metadata={
                            'method': 'rate',
                            'threshold_multiplier': threshold_multiplier,
                            'avg_rate': avg_rate
                        }
                    )

                    self.anomalies.append(anomaly)
                    self.anomaly_counter += 1
                    return anomaly

        return None

    def detect_volume_spike(self, field: str, window_minutes: int = 60,
                           threshold_multiplier: float = 3.0) -> Optional[Anomaly]:
        """
        Detect spikes in volume/frequency
        """
        if field not in self.data_windows:
            return None

        now = datetime.now()
        recent_window = [
            dp for dp in self.data_windows[field]
            if (now - dp['timestamp']).total_seconds() / 60 <= window_minutes
        ]

        current_count = len(recent_window)

        # Calculate expected count based on historical average
        if len(self.data_windows[field]) >= window_minutes:
            historical_avg = len(self.data_windows[field]) / self.window_size * window_minutes

            if current_count > historical_avg * threshold_multiplier:
                severity = min((current_count / historical_avg) * 25, 100)

                anomaly = Anomaly(
                    anomaly_id=f"volume_{self.anomaly_counter}",
                    anomaly_type="volume_spike",
                    description=f"Volume spike: {current_count} events in {window_minutes}min (expected: {historical_avg:.1f})",
                    severity=severity,
                    timestamp=now,
                    entity_id=None,
                    field=field,
                    expected_value=historical_avg,
                    actual_value=current_count,
                    deviation_score=current_count / historical_avg,
                    metadata={
                        'method': 'volume_spike',
                        'window_minutes': window_minutes,
                        'threshold_multiplier': threshold_multiplier
                    }
                )

                self.anomalies.append(anomaly)
                self.anomaly_counter += 1
                return anomaly

        return None

    def detect_sequence_anomaly(self, field: str, sequence: List[Any],
                               entity_id: str = None) -> Optional[Anomaly]:
        """
        Detect anomalous sequences
        """
        if field not in self.data_windows or len(self.data_windows[field]) < len(sequence):
            return None

        # Check if this sequence has appeared before
        sequence_str = str(sequence)
        historical_sequences = []

        data_list = list(self.data_windows[field])
        for i in range(len(data_list) - len(sequence) + 1):
            hist_seq = [data_list[i+j]['value'] for j in range(len(sequence))]
            historical_sequences.append(str(hist_seq))

        # If sequence is unique or very rare
        occurrence_count = historical_sequences.count(sequence_str)
        total_sequences = len(historical_sequences)

        if total_sequences > 0:
            frequency = occurrence_count / total_sequences

            if frequency < 0.05:  # Less than 5% occurrence rate
                severity = (1 - frequency) * 60

                anomaly = Anomaly(
                    anomaly_id=f"sequence_{self.anomaly_counter}",
                    anomaly_type="sequence_anomaly",
                    description=f"Unusual sequence detected (frequency: {frequency:.2%})",
                    severity=severity,
                    timestamp=datetime.now(),
                    entity_id=entity_id,
                    field=field,
                    expected_value=None,
                    actual_value=sequence,
                    deviation_score=1 - frequency,
                    metadata={
                        'method': 'sequence',
                        'sequence': sequence,
                        'frequency': frequency,
                        'occurrences': occurrence_count
                    }
                )

                self.anomalies.append(anomaly)
                self.anomaly_counter += 1
                return anomaly

        return None

    def detect_temporal_anomaly(self, field: str, entity_id: str = None) -> List[Anomaly]:
        """
        Detect temporal anomalies (unusual timing patterns)
        """
        if field not in self.data_windows or len(self.data_windows[field]) < 3:
            return []

        anomalies = []
        data_points = list(self.data_windows[field])

        # Calculate time intervals
        intervals = []
        for i in range(1, len(data_points)):
            interval = (data_points[i]['timestamp'] - data_points[i-1]['timestamp']).total_seconds()
            intervals.append(interval)

        if len(intervals) < 2:
            return []

        avg_interval = statistics.mean(intervals)
        std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0

        # Check last interval
        last_interval = intervals[-1]

        if std_interval > 0:
            z_score = abs((last_interval - avg_interval) / std_interval)

            if z_score > 2.0:  # Significant deviation
                severity = min(z_score * 20, 100)

                anomaly = Anomaly(
                    anomaly_id=f"temporal_{self.anomaly_counter}",
                    anomaly_type="temporal_anomaly",
                    description=f"Unusual time interval: {last_interval:.1f}s (expected: {avg_interval:.1f}s)",
                    severity=severity,
                    timestamp=datetime.now(),
                    entity_id=entity_id,
                    field=field,
                    expected_value=avg_interval,
                    actual_value=last_interval,
                    deviation_score=z_score,
                    metadata={
                        'method': 'temporal',
                        'avg_interval': avg_interval,
                        'std_interval': std_interval
                    }
                )

                self.anomalies.append(anomaly)
                anomalies.append(anomaly)
                self.anomaly_counter += 1

        return anomalies

    def detect_all_anomalies(self, field: str, value: float,
                            entity_id: str = None) -> List[Anomaly]:
        """
        Run all anomaly detection methods on a data point
        """
        # Add data point
        self.add_data_point(field, value, entity_id=entity_id)

        anomalies = []

        # Z-score detection
        zscore_anomaly = self.detect_zscore_anomaly(field, value, entity_id=entity_id)
        if zscore_anomaly:
            anomalies.append(zscore_anomaly)

        # IQR detection
        iqr_anomaly = self.detect_iqr_anomaly(field, value, entity_id=entity_id)
        if iqr_anomaly:
            anomalies.append(iqr_anomaly)

        # Temporal anomalies
        temporal_anomalies = self.detect_temporal_anomaly(field, entity_id=entity_id)
        anomalies.extend(temporal_anomalies)

        # Volume spike
        volume_anomaly = self.detect_volume_spike(field)
        if volume_anomaly:
            anomalies.append(volume_anomaly)

        return anomalies

    def get_anomalies_by_severity(self, min_severity: float = 50.0) -> List[Anomaly]:
        """Get anomalies above a severity threshold"""
        return [a for a in self.anomalies if a.severity >= min_severity]

    def get_anomalies_by_type(self, anomaly_type: str) -> List[Anomaly]:
        """Get anomalies of a specific type"""
        return [a for a in self.anomalies if a.anomaly_type == anomaly_type]

    def get_anomalies_by_entity(self, entity_id: str) -> List[Anomaly]:
        """Get all anomalies for a specific entity"""
        return [a for a in self.anomalies if a.entity_id == entity_id]

    def get_recent_anomalies(self, minutes: int = 60) -> List[Anomaly]:
        """Get anomalies from the last N minutes"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [a for a in self.anomalies if a.timestamp >= cutoff]

    def export_anomalies(self) -> List[Dict]:
        """Export all anomalies"""
        return [anomaly.to_dict() for anomaly in self.anomalies]

    def get_statistics(self) -> Dict:
        """Get anomaly detection statistics"""
        if not self.anomalies:
            return {
                'total_anomalies': 0,
                'by_type': {},
                'avg_severity': 0,
                'high_severity_count': 0
            }

        anomaly_types = {}
        for anomaly in self.anomalies:
            anomaly_types[anomaly.anomaly_type] = anomaly_types.get(anomaly.anomaly_type, 0) + 1

        severities = [a.severity for a in self.anomalies]
        high_severity = len([a for a in self.anomalies if a.severity >= 70])

        return {
            'total_anomalies': len(self.anomalies),
            'by_type': anomaly_types,
            'avg_severity': statistics.mean(severities) if severities else 0,
            'high_severity_count': high_severity,
            'fields_monitored': len(self.data_windows),
            'baselines_calculated': len(self.baselines)
        }

    def clear_old_anomalies(self, days: int = 7) -> int:
        """Clear anomalies older than specified days"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=days)

        initial_count = len(self.anomalies)
        self.anomalies = [a for a in self.anomalies if a.timestamp >= cutoff]

        return initial_count - len(self.anomalies)
