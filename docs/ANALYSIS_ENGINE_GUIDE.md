# OSINT Analysis Engine Guide

## Overview

The OSINT Analysis Engine is a comprehensive toolkit for analyzing open-source intelligence data. It consists of three main components:

1. **Correlation Engine**: Entity linking, relationship mapping, timeline construction, and pattern detection
2. **Threat Intelligence**: IOC detection, threat scoring, anomaly detection, reputation checking, and threat feeds
3. **Visualization**: Network graphs, timelines, geographic maps, charts, and heatmaps

## Table of Contents

- [Installation](#installation)
- [Correlation Engine](#correlation-engine)
- [Threat Intelligence](#threat-intelligence)
- [Visualization](#visualization)
- [Complete Examples](#complete-examples)

## Installation

```bash
pip install -e .
```

## Correlation Engine

### Entity Linking

Link related entities across different data sources:

```python
from osint_toolkit import CorrelationEngine

engine = CorrelationEngine()

# Add entities
entity1 = engine.add_entity('ip', '192.168.1.1', source='firewall_logs')
entity2 = engine.add_entity('domain', 'malicious.com', source='dns_logs')

# Link entities
engine.link_entities(entity1.id, entity2.id, confidence=0.95, link_type='connected_to')

# Extract entities from text
text = "Connection from 10.0.0.5 to example.com detected"
entities = engine.extract_entities_from_text(text)

# Auto-link similar entities
links_created = engine.auto_link_entities(confidence_threshold=0.8)
```

### Relationship Mapping

Build and analyze relationship graphs:

```python
# Add relationship
engine.add_relationship(
    source_id=entity1.id,
    target_id=entity2.id,
    rel_type='communicates_with',
    weight=0.9
)

# Find path between entities
path = engine.find_path(entity1.id, entity2.id)

# Get neighbors
neighbors = engine.get_entity_neighbors(entity1.id, depth=2)

# Calculate importance
importance = engine.calculate_entity_importance()

# Detect communities
communities = engine.detect_communities(method='louvain')

# Get pivotal entities
pivotal = engine.find_pivotal_entities(top_n=10)
```

### Timeline Construction

Build chronological timelines:

```python
from datetime import datetime

# Add events
event = engine.add_event(
    event_id='evt_001',
    timestamp=datetime.now(),
    event_type='connection',
    description='Suspicious connection detected',
    entities=[entity1.id, entity2.id],
    confidence=0.85
)

# Get entity timeline
timeline = engine.get_entity_timeline(entity1.id)

# Get events in timeframe
events = engine.get_events_in_timeframe(start_time, end_time)

# Detect temporal patterns
patterns = engine.detect_event_patterns(event_type='connection', min_occurrences=3)
```

### Pattern Detection

Identify patterns in data:

```python
# Detect all patterns
patterns = engine.detect_patterns(fields=['event_type', 'source_ip'])

# Detect anomalies
anomalies = engine.detect_anomalies('request_count', method='zscore')

# Get high-confidence patterns
high_conf = engine.get_high_confidence_patterns(min_confidence=0.8)
```

### Comprehensive Entity Analysis

```python
# Analyze a single entity
analysis = engine.analyze_entity('192.168.1.100')
print(analysis)
# Output:
# {
#   'entity': {...},
#   'linked_entities': 5,
#   'relationships': {'total': 8, 'incoming': 3, 'outgoing': 5},
#   'timeline': {'total_events': 42, ...},
#   'network': {'direct_neighbors': 5, 'cluster_size': 12, ...}
# }
```

## Threat Intelligence

### IOC Detection

Detect Indicators of Compromise:

```python
from osint_toolkit import ThreatIntelligence

ti = ThreatIntelligence()

# Extract IOCs from text
text = """
Malicious activity detected:
IP: 203.0.113.42
Domain: evil.com
Hash: 5d41402abc4b2a76b9719d911017c592
URL: http://malicious-site.com/payload
"""

iocs = ti.extract_iocs(text, source='incident_report')

# Add known malicious IOC
ti.add_known_malicious('badactor.com', ioc_type='domain')

# Get IOCs by threat level
critical_iocs = ti.get_iocs_by_threat_level('high')

# Search IOCs
results = ti.ioc_detector.search_ioc('malicious')
```

### Threat Scoring

Calculate threat scores:

```python
# Calculate comprehensive threat score
score = ti.calculate_threat_score(
    entity_id='192.168.1.100',
    entity_type='ip',
    analyze_iocs=True,
    analyze_reputation=True,
    analyze_behavior=True
)

print(f"Threat Score: {score.score}/100")
print(f"Threat Level: {score.threat_level.name}")
print(f"Recommendations: {score.recommendations}")

# Get high-threat entities
high_threats = ti.get_high_threat_entities(min_level=ThreatLevel.MEDIUM)

# Get threat trend
trend = ti.get_threat_trend('malicious.com')  # 'increasing', 'decreasing', 'stable'
```

### Anomaly Detection

Detect anomalies in data:

```python
# Detect anomalies using multiple methods
anomalies = ti.detect_anomalies('request_count', 5000.0, entity_id='server1')

# Detect using Z-score
anomaly = ti.detect_zscore_anomaly('latency', 150.0, threshold=3.0)

# Detect volume spikes
spike = ti.detect_volume_spike('requests', window_minutes=60)

# Get high-severity anomalies
severe = ti.get_high_severity_anomalies(min_severity=70.0)
```

### Reputation Checking

Check entity reputation:

```python
# Check IP reputation
ip_rep = ti.check_ip_reputation('8.8.8.8')
print(ip_rep['summary'])

# Check domain reputation
domain_rep = ti.check_domain_reputation('example.com')

# Check URL reputation
url_rep = ti.check_url_reputation('http://suspicious-site.com')
```

### Threat Feeds

Integrate with threat feeds:

```python
# Add custom threat feed
ti.add_threat_feed(
    feed_id='custom_feed',
    name='Custom Threat Feed',
    feed_type=FeedType.IP_BLACKLIST,
    url='https://example.com/threat-feed.txt',
    format=FeedFormat.TEXT,
    update_interval=timedelta(hours=6)
)

# Check against threat feeds
matches = ti.check_against_threat_feeds('ip', '192.168.1.1')

# Update all feeds
results = ti.update_all_threat_feeds()
```

### Comprehensive Analysis

```python
# Analyze entity with all threat intelligence
analysis = ti.analyze_entity('suspicious.com', 'domain')

print(analysis['assessment'])
print(f"IOCs found: {len(analysis['iocs'])}")
print(f"Threat score: {analysis['threat_score']['score']}")
print(f"Reputation: {analysis['reputation']['summary']}")
```

## Visualization

### Network Graphs

Visualize entity relationships:

```python
from osint_toolkit import Visualization

viz = Visualization()

# Add nodes
viz.add_node('node1', label='Attacker IP', color='#e74c3c', size=20)
viz.add_node('node2', label='Target Server', color='#3498db', size=15)

# Add edges
viz.add_edge('node1', 'node2', label='attacked', weight=2.0)

# Generate visualization
network_viz = viz.visualize_network(
    layout_type='force',
    style_by_centrality=True,
    color_by_community=True,
    title='Attack Network'
)

# Export
viz.export_network_graph('network.json', format='json')
```

### Timelines

Create interactive timelines:

```python
from datetime import datetime

# Add events
viz.add_event(
    'event1',
    datetime(2025, 1, 1, 10, 30),
    'Initial Compromise',
    description='Suspicious login detected',
    category='attack',
    color='#e74c3c'
)

# Create Gantt chart
viz.add_timeline_track(
    track_name='Attack Phase 1',
    event_id='phase1',
    start_time=datetime(2025, 1, 1, 10, 0),
    end_time=datetime(2025, 1, 1, 12, 0),
    title='Reconnaissance'
)

# Generate timeline
timeline_viz = viz.visualize_timeline(style='timeline')

# Generate Gantt chart
gantt_viz = viz.visualize_timeline(style='gantt')
```

### Geographic Maps

Visualize location-based data:

```python
# Add location markers
viz.add_location_marker(
    40.7128, -74.0060,
    title='New York - Attack Origin',
    description='Attacker location',
    color='#e74c3c'
)

viz.add_location_marker(
    51.5074, -0.1278,
    title='London - Target',
    color='#3498db'
)

# Add connection
viz.add_location_connection(
    40.7128, -74.0060,  # Source
    51.5074, -0.1278,   # Target
    label='Attack vector',
    color='#e74c3c',
    weight=2.0
)

# Add heatmap points
viz.add_heatmap_point(40.7128, -74.0060, intensity=0.9)

# Generate map
map_viz = viz.visualize_map(title='Attack Geography')

# Export
viz.export_map('map.html', format='html')
```

### Charts

Create various charts:

```python
# Bar chart
threat_counts = {'Critical': 5, 'High': 12, 'Medium': 23, 'Low': 45}
viz.create_bar_chart('threats', threat_counts, title='Threats by Severity')

# Line chart
daily_events = {'Mon': 10, 'Tue': 15, 'Wed': 8, 'Thu': 20, 'Fri': 12}
viz.create_line_chart('events', daily_events, title='Daily Events')

# Pie chart
viz.create_pie_chart('distribution', threat_counts, title='Threat Distribution')

# Scatter plot
x_data = [1, 2, 3, 4, 5]
y_data = [2, 4, 1, 5, 3]
viz.create_scatter_plot('correlation', x_data, y_data)

# Visualize
chart_viz = viz.visualize_chart('threats')
```

### Heatmaps

Create heatmaps for patterns:

```python
# Correlation matrix
correlation_matrix = [
    [1.0, 0.8, 0.3],
    [0.8, 1.0, 0.5],
    [0.3, 0.5, 1.0]
]
labels = ['Metric A', 'Metric B', 'Metric C']

viz.create_correlation_heatmap(
    'correlations',
    correlation_matrix,
    labels,
    title='Metric Correlations'
)

# Temporal activity heatmap
activity_data = {
    '2025-01-01': {'0': 5, '1': 3, '2': 1, '12': 15, '18': 20},
    '2025-01-02': {'0': 2, '1': 1, '12': 18, '18': 22}
}

viz.create_temporal_heatmap(
    'activity',
    activity_data,
    title='Hourly Activity'
)

# Visualize
heatmap_viz = viz.visualize_heatmap('correlations')
```

### Dashboards

Create comprehensive dashboards:

```python
dashboard_data = {
    'entities': [
        {'id': 'ip1', 'value': '192.168.1.1', 'type': 'ip', 'size': 20},
        {'id': 'dom1', 'value': 'evil.com', 'type': 'domain', 'size': 15}
    ],
    'relationships': [
        {'source': 'ip1', 'target': 'dom1', 'type': 'resolves_to', 'weight': 1.0}
    ],
    'events': [
        {
            'id': 'evt1',
            'timestamp': datetime.now().isoformat(),
            'title': 'DNS Query',
            'category': 'network'
        }
    ],
    'locations': [
        {'lat': 40.7128, 'lon': -74.0060, 'title': 'Attack Origin'}
    ]
}

dashboard = viz.create_dashboard(dashboard_data)
```

## Complete Examples

### Example 1: Investigate Suspicious Activity

```python
from osint_toolkit import CorrelationEngine, ThreatIntelligence, Visualization
from datetime import datetime

# Initialize engines
correlation = CorrelationEngine()
threat_intel = ThreatIntelligence()
viz = Visualization()

# Analyze suspicious text
log_entry = """
2025-01-15 10:30:45 - Suspicious connection from 203.0.113.42
to internal server 192.168.1.100 on port 445.
Domain resolved: malicious-c2.com
File hash: d41d8cd98f00b204e9800998ecf8427e
"""

# Extract entities
entities = correlation.extract_entities_from_text(log_entry, source='firewall')

# Extract IOCs
iocs = threat_intel.extract_iocs(log_entry, source='firewall')

# Add to timeline
correlation.add_event(
    'suspicious_connection',
    datetime(2025, 1, 15, 10, 30, 45),
    'suspicious_connection',
    log_entry,
    entities=[e.id for e in entities]
)

# Calculate threat scores
for entity in entities:
    score = threat_intel.calculate_threat_score(entity.value, entity.type)
    print(f"{entity.value}: Threat Score = {score.score}, Level = {score.threat_level.name}")

# Visualize
for entity in entities:
    viz.add_node(entity.id, label=entity.value, color='#e74c3c')

network = viz.visualize_network(title='Threat Network')

# Export analysis
analysis = {
    'entities': correlation.entity_linker.export_entities(),
    'iocs': [ioc.to_dict() for ioc in iocs],
    'statistics': correlation.get_statistics()
}
```

### Example 2: Track APT Campaign

```python
# Track Advanced Persistent Threat campaign
apt_tracker = CorrelationEngine()
apt_threats = ThreatIntelligence()

# Add multiple incidents
incidents = [
    {'ip': '45.33.32.156', 'domain': 'apt-c2.com', 'time': '2025-01-10 14:00'},
    {'ip': '45.33.32.156', 'domain': 'data-exfil.net', 'time': '2025-01-11 02:30'},
    {'ip': '203.0.113.77', 'domain': 'apt-c2.com', 'time': '2025-01-12 18:45'}
]

# Process incidents
for inc in incidents:
    ip_entity = apt_tracker.add_entity('ip', inc['ip'])
    domain_entity = apt_tracker.add_entity('domain', inc['domain'])

    apt_tracker.link_entities(ip_entity.id, domain_entity.id, 0.95, 'communicates_with')

    apt_tracker.add_event(
        f"incident_{inc['time']}",
        datetime.fromisoformat(inc['time']),
        'apt_activity',
        f"APT activity: {inc['ip']} -> {inc['domain']}",
        [ip_entity.id, domain_entity.id]
    )

# Detect communities (C2 infrastructure)
communities = apt_tracker.detect_communities()

# Find pivotal entities (key infrastructure)
pivotal = apt_tracker.find_pivotal_entities(top_n=5)

print(f"Detected {len(set(communities.values()))} infrastructure clusters")
print(f"Pivotal entities: {pivotal}")

# Get comprehensive statistics
stats = apt_tracker.get_statistics()
print(f"Total entities tracked: {stats['entities']['total_entities']}")
print(f"Total relationships: {stats['relationships']['total_relationships']}")
```

## API Reference

For detailed API documentation, see:
- [Correlation Engine API](./api/correlation_engine.md)
- [Threat Intelligence API](./api/threat_intelligence.md)
- [Visualization API](./api/visualization.md)

## Best Practices

1. **Data Quality**: Always validate and sanitize input data
2. **Performance**: Use batch operations when processing large datasets
3. **Memory**: Clear old data periodically using `clear_all()` methods
4. **Confidence Scores**: Tune confidence thresholds based on your use case
5. **Visualization**: Limit node count in network graphs for better performance
6. **Security**: Be cautious with API keys and sensitive data

## Troubleshooting

### Common Issues

**Issue**: Network graph too dense
- **Solution**: Filter entities by importance score or limit depth

**Issue**: Memory usage too high
- **Solution**: Process data in batches and clear caches regularly

**Issue**: Slow pattern detection
- **Solution**: Reduce window size or limit fields analyzed

## Support

For issues and questions:
- GitHub Issues: https://github.com/osint/osint-toolkit/issues
- Documentation: https://docs.osint-toolkit.com
