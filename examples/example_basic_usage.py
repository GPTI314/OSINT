"""
Basic Usage Example - OSINT Analysis Engine
"""

from datetime import datetime
import sys
sys.path.insert(0, '/home/user/OSINT')

from osint_toolkit import CorrelationEngine, ThreatIntelligence, Visualization


def main():
    print("=" * 60)
    print("OSINT Analysis Engine - Basic Usage Example")
    print("=" * 60)

    # Initialize engines
    correlation = CorrelationEngine()
    threat_intel = ThreatIntelligence()
    viz = Visualization()

    print("\n1. Entity Extraction and Linking")
    print("-" * 60)

    # Sample security log
    log_text = """
    2025-01-15 14:30:00 - Alert: Suspicious connection detected
    Source IP: 203.0.113.42
    Destination: internal-server.company.com (192.168.1.100)
    Domain queried: malicious-site.com
    File hash: 5d41402abc4b2a76b9719d911017c592
    """

    # Extract entities
    entities = correlation.extract_entities_from_text(log_text, source='security_log')

    print(f"Extracted {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.type}: {entity.value}")

    # Auto-link similar entities
    links = correlation.auto_link_entities(confidence_threshold=0.8)
    print(f"\nCreated {links} automatic links")

    print("\n2. IOC Detection")
    print("-" * 60)

    # Detect IOCs
    iocs = threat_intel.extract_iocs(log_text, source='security_log')

    print(f"Detected {len(iocs)} IOCs:")
    for ioc in iocs[:5]:  # Show first 5
        print(f"  - {ioc.ioc_type.value}: {ioc.value} (confidence: {ioc.confidence:.2f})")

    print("\n3. Threat Scoring")
    print("-" * 60)

    # Score an IP address
    threat_score = threat_intel.calculate_threat_score(
        '203.0.113.42',
        'ip',
        analyze_iocs=True,
        analyze_reputation=True
    )

    print(f"Threat Score for 203.0.113.42:")
    print(f"  Score: {threat_score.score:.1f}/100")
    print(f"  Level: {threat_score.threat_level.name}")
    print(f"  Confidence: {threat_score.confidence:.2f}")
    print(f"  Recommendations:")
    for rec in threat_score.recommendations[:3]:
        print(f"    - {rec}")

    print("\n4. Timeline Construction")
    print("-" * 60)

    # Add events to timeline
    correlation.add_event(
        'event_001',
        datetime(2025, 1, 15, 14, 30, 0),
        'suspicious_connection',
        'Suspicious connection detected',
        entities=[e.id for e in entities[:2]],
        confidence=0.85
    )

    correlation.add_event(
        'event_002',
        datetime(2025, 1, 15, 14, 35, 0),
        'dns_query',
        'Malicious domain query',
        entities=[entities[0].id] if entities else [],
        confidence=0.92
    )

    timeline_stats = correlation.timeline_builder.get_statistics()
    print(f"Timeline has {timeline_stats['total_events']} events")
    print(f"Time span: {timeline_stats.get('start_time', 'N/A')} to {timeline_stats.get('end_time', 'N/A')}")

    print("\n5. Network Visualization")
    print("-" * 60)

    # Build network graph
    for entity in entities[:5]:  # Limit to first 5 entities
        color = '#e74c3c' if entity.type == 'ip' else '#3498db'
        viz.add_node(
            entity.id,
            label=entity.value,
            node_type=entity.type,
            color=color,
            size=15
        )

    # Add relationships
    if len(entities) >= 2:
        viz.add_edge(
            entities[0].id,
            entities[1].id,
            label='connected_to',
            weight=1.5
        )

    network_stats = viz.network_graph.get_statistics()
    print(f"Network graph:")
    print(f"  Nodes: {network_stats['num_nodes']}")
    print(f"  Edges: {network_stats['num_edges']}")

    print("\n6. Statistics Summary")
    print("-" * 60)

    correlation_stats = correlation.get_statistics()
    threat_stats = threat_intel.get_statistics()

    print("Correlation Engine:")
    print(f"  Entities: {correlation_stats['entities']['total_entities']}")
    print(f"  Relationships: {correlation_stats['relationships']['total_relationships']}")
    print(f"  Timeline events: {correlation_stats['timeline']['total_events']}")

    print("\nThreat Intelligence:")
    print(f"  IOCs detected: {threat_stats['iocs']['total_iocs']}")
    print(f"  Threat scores calculated: {threat_stats['threat_scores']['total_scores']}")

    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
