# OSINT Toolkit

Open-Source Intelligence (OSINT) toolkit with comprehensive analysis engine: modular collectors, enrichment pipeline, link analysis, threat intelligence, risk scoring, and investigative workflow automation.

## Features

### 🔗 Correlation Engine
- **Entity Linking**: Automatically link related entities across different data sources
- **Relationship Mapping**: Build and analyze complex relationship graphs with community detection
- **Timeline Construction**: Construct chronological timelines with event sequencing and pattern detection
- **Pattern Detection**: Identify behavioral patterns, anomalies, and trends in data

### 🛡️ Threat Intelligence
- **IOC Detection**: Extract and classify Indicators of Compromise (IPs, domains, hashes, URLs, etc.)
- **Threat Scoring**: Calculate comprehensive threat scores with multi-factor risk assessment
- **Anomaly Detection**: Statistical and ML-based anomaly detection (Z-score, IQR, temporal analysis)
- **Reputation Checking**: Integrated reputation checking across multiple threat intelligence sources
- **Threat Feeds**: Manage and integrate external threat intelligence feeds

### 📊 Visualization
- **Network Graphs**: Interactive entity relationship graphs with force-directed and hierarchical layouts
- **Timeline Views**: Interactive timelines and Gantt charts for temporal analysis
- **Geographic Maps**: Location-based visualizations with heatmaps and connection mapping
- **Charts & Graphs**: Bar charts, line charts, pie charts, scatter plots, and histograms
- **Heatmaps**: Correlation matrices, temporal activity heatmaps, and 2D density maps

## Installation

```bash
# Clone the repository
git clone https://github.com/your-org/OSINT.git
cd OSINT

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Quick Start

```python
from osint_toolkit import CorrelationEngine, ThreatIntelligence, Visualization
from datetime import datetime

# Initialize engines
correlation = CorrelationEngine()
threat_intel = ThreatIntelligence()
viz = Visualization()

# Extract entities from text
text = "Suspicious connection from 203.0.113.42 to malicious.com detected"
entities = correlation.extract_entities_from_text(text)

# Detect IOCs
iocs = threat_intel.extract_iocs(text)

# Calculate threat score
score = threat_intel.calculate_threat_score('203.0.113.42', 'ip')
print(f"Threat Score: {score.score}/100 - Level: {score.threat_level.name}")

# Build network visualization
for entity in entities:
    viz.add_node(entity.id, label=entity.value, node_type=entity.type)

network = viz.visualize_network(title='Threat Network')
```

## Architecture

```
osint_toolkit/
├── analysis_engine/
│   ├── correlation/
│   │   ├── entity_linker.py       # Entity extraction and linking
│   │   ├── relationship_mapper.py  # Graph-based relationship analysis
│   │   ├── timeline_builder.py     # Temporal analysis
│   │   └── pattern_detector.py     # Pattern and anomaly detection
│   ├── threat_intelligence/
│   │   ├── ioc_detector.py         # IOC extraction
│   │   ├── threat_scorer.py        # Risk assessment
│   │   ├── anomaly_detector.py     # Statistical anomaly detection
│   │   ├── reputation_checker.py   # Reputation analysis
│   │   └── threat_feeds.py         # Threat feed integration
│   └── visualization/
│       ├── network_graph.py        # Network visualizations
│       ├── timeline_viz.py         # Timeline visualizations
│       ├── geo_map.py              # Geographic visualizations
│       ├── charts.py               # Chart visualizations
│       └── heatmap.py              # Heatmap visualizations
├── tests/                          # Comprehensive test suite
└── examples/                       # Usage examples
```

## Usage Examples

### Entity Correlation

```python
# Link related entities
entity1 = correlation.add_entity('ip', '192.168.1.1')
entity2 = correlation.add_entity('domain', 'example.com')
correlation.link_entities(entity1.id, entity2.id, confidence=0.95)

# Find paths between entities
path = correlation.find_path(entity1.id, entity2.id)

# Detect communities
communities = correlation.detect_communities()

# Calculate entity importance
importance = correlation.calculate_entity_importance()
```

### Threat Analysis

```python
# Comprehensive threat analysis
analysis = threat_intel.analyze_entity('suspicious.com', 'domain')

print(f"Assessment: {analysis['assessment']}")
print(f"IOCs: {len(analysis['iocs'])}")
print(f"Threat Score: {analysis['threat_score']['score']}")
print(f"Reputation: {analysis['reputation']['summary']}")

# Check against threat feeds
matches = threat_intel.check_against_threat_feeds('ip', '203.0.113.42')
```

### Visualization

```python
# Create comprehensive dashboard
dashboard_data = {
    'entities': [...],
    'relationships': [...],
    'events': [...],
    'locations': [...]
}

dashboard = viz.create_dashboard(dashboard_data)

# Export visualizations
viz.export_network_graph('network.json')
viz.export_timeline('timeline.json')
viz.export_map('map.html', format='html')
```

## Documentation

- [Analysis Engine Guide](docs/ANALYSIS_ENGINE_GUIDE.md) - Comprehensive guide with examples
- [API Reference](docs/api/) - Detailed API documentation
- [Examples](examples/) - Code examples and tutorials

## Testing

```bash
# Run all tests
python -m pytest osint_toolkit/tests/

# Run specific test module
python -m pytest osint_toolkit/tests/test_correlation_engine.py

# Run with coverage
python -m pytest --cov=osint_toolkit osint_toolkit/tests/
```

## Requirements

- Python 3.8+
- NetworkX >= 3.1
- Pandas >= 2.0.0
- NumPy >= 1.24.0
- Plotly >= 5.14.0
- Folium >= 0.14.0
- See [requirements.txt](requirements.txt) for complete list

## Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- NetworkX for graph analysis
- Plotly for interactive visualizations
- Scikit-learn for machine learning capabilities

## Support

- Issues: [GitHub Issues](https://github.com/your-org/OSINT/issues)
- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)
