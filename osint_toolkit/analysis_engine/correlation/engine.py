"""
Correlation Engine - Main engine integrating all correlation components
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from osint_toolkit.analysis_engine.correlation.entity_linker import EntityLinker, Entity
from osint_toolkit.analysis_engine.correlation.relationship_mapper import RelationshipMapper, Relationship
from osint_toolkit.analysis_engine.correlation.timeline_builder import TimelineBuilder, Event
from osint_toolkit.analysis_engine.correlation.pattern_detector import PatternDetector, Pattern


class CorrelationEngine:
    """
    Main correlation engine that integrates:
    - Entity linking
    - Relationship mapping
    - Timeline construction
    - Pattern detection
    """

    def __init__(self):
        self.entity_linker = EntityLinker()
        self.relationship_mapper = RelationshipMapper(directed=True)
        self.timeline_builder = TimelineBuilder()
        self.pattern_detector = PatternDetector()

    # Entity Operations
    def add_entity(self, entity_type: str, value: str,
                  source: str = None, metadata: Dict = None) -> Entity:
        """Add an entity to the correlation engine"""
        entity = self.entity_linker.create_entity(entity_type, value, source, metadata)
        self.relationship_mapper.add_entity(entity.id, {
            'type': entity_type,
            'value': value,
            'source': source
        })
        return entity

    def extract_entities_from_text(self, text: str, source: str = None) -> List[Entity]:
        """Extract entities from text"""
        entities = self.entity_linker.extract_entities(text, source)

        # Add to relationship mapper
        for entity in entities:
            self.relationship_mapper.add_entity(entity.id, {
                'type': entity.type,
                'value': entity.value,
                'source': source
            })

        return entities

    def link_entities(self, entity1_id: str, entity2_id: str,
                     confidence: float = 1.0, link_type: str = "related") -> bool:
        """Link two entities"""
        # Link in entity linker
        success = self.entity_linker.link_entities(entity1_id, entity2_id, confidence, link_type)

        # Add relationship in mapper
        if success:
            self.relationship_mapper.create_relationship(
                entity1_id, entity2_id, link_type, confidence
            )

        return success

    def auto_link_entities(self, confidence_threshold: float = 0.8) -> int:
        """Automatically link similar entities"""
        return self.entity_linker.auto_link_entities(confidence_threshold)

    def get_entity_cluster(self, entity_id: str) -> List[Entity]:
        """Get all entities linked to the given entity"""
        cluster_ids = self.entity_linker.get_entity_cluster(entity_id)
        return [self.entity_linker.entities[eid] for eid in cluster_ids
                if eid in self.entity_linker.entities]

    # Relationship Operations
    def add_relationship(self, source_id: str, target_id: str, rel_type: str,
                        weight: float = 1.0, timestamp: datetime = None,
                        metadata: Dict = None) -> Relationship:
        """Add a relationship between entities"""
        relationship = self.relationship_mapper.create_relationship(
            source_id, target_id, rel_type, weight, timestamp, metadata
        )

        # Also link in entity linker
        self.entity_linker.link_entities(source_id, target_id, weight, rel_type)

        return relationship

    def get_relationships(self, entity_id: str, direction: str = "both") -> List[Relationship]:
        """Get all relationships for an entity"""
        return self.relationship_mapper.get_relationships(entity_id, direction)

    def find_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find the shortest path between two entities"""
        return self.relationship_mapper.find_shortest_path(source_id, target_id)

    def get_entity_neighbors(self, entity_id: str, depth: int = 1) -> List[Entity]:
        """Get neighboring entities within specified depth"""
        neighbor_ids = self.relationship_mapper.get_neighbors(entity_id, depth)
        return [self.entity_linker.entities[eid] for eid in neighbor_ids
                if eid in self.entity_linker.entities]

    def calculate_entity_importance(self) -> Dict[str, float]:
        """Calculate importance scores for entities using PageRank"""
        centrality = self.relationship_mapper.calculate_centrality()
        return centrality.get('pagerank', {})

    def detect_communities(self, method: str = 'louvain') -> Dict[str, int]:
        """Detect communities in the entity network"""
        return self.relationship_mapper.detect_communities(method)

    # Timeline Operations
    def add_event(self, event_id: str, timestamp: datetime, event_type: str,
                 description: str, entities: List[str] = None,
                 metadata: Dict = None, confidence: float = 1.0) -> Event:
        """Add an event to the timeline"""
        event = self.timeline_builder.create_event(
            event_id, timestamp, event_type, description,
            entities, metadata, confidence
        )

        # Add pattern detector data point
        self.pattern_detector.add_data_point({
            'event_type': event_type,
            'entities': entities or [],
            'description': description
        }, timestamp)

        # Create temporal relationships between entities involved in the same event
        if entities and len(entities) > 1:
            for i, entity1 in enumerate(entities):
                for entity2 in entities[i+1:]:
                    self.add_relationship(
                        entity1, entity2, "co-occurred",
                        weight=0.5, timestamp=timestamp,
                        metadata={'event_id': event_id}
                    )

        return event

    def get_entity_timeline(self, entity_id: str) -> List[Event]:
        """Get timeline of events for an entity"""
        return self.timeline_builder.get_entity_timeline(entity_id)

    def get_events_in_timeframe(self, start_time: datetime,
                               end_time: datetime) -> List[Event]:
        """Get events within a time range"""
        return self.timeline_builder.get_events_in_range(start_time, end_time)

    def detect_event_patterns(self, event_type: str = None,
                            min_occurrences: int = 3) -> List[Dict]:
        """Detect temporal patterns in events"""
        return self.timeline_builder.detect_temporal_patterns(event_type, min_occurrences)

    # Pattern Detection Operations
    def detect_patterns(self, fields: List[str] = None) -> Dict[str, List[Pattern]]:
        """Run pattern detection on all data"""
        return self.pattern_detector.analyze_all(fields)

    def detect_anomalies(self, field: str, method: str = 'zscore') -> List[Pattern]:
        """Detect anomalies in data"""
        return self.pattern_detector.detect_anomalies(field, method)

    def get_high_confidence_patterns(self, min_confidence: float = 0.7) -> List[Pattern]:
        """Get patterns with high confidence"""
        return self.pattern_detector.get_high_confidence_patterns(min_confidence)

    # Integrated Analysis
    def analyze_entity(self, entity_id: str) -> Dict[str, Any]:
        """Comprehensive analysis of a single entity"""
        if entity_id not in self.entity_linker.entities:
            return {'error': 'Entity not found'}

        entity = self.entity_linker.entities[entity_id]

        # Get linked entities
        linked = self.entity_linker.get_linked_entities(entity_id)

        # Get relationships
        relationships = self.get_relationships(entity_id)

        # Get timeline
        timeline = self.get_entity_timeline(entity_id)

        # Get neighbors
        neighbors = self.get_entity_neighbors(entity_id, depth=1)

        # Get cluster
        cluster = self.get_entity_cluster(entity_id)

        # Calculate importance
        importance = self.calculate_entity_importance()
        entity_importance = importance.get(entity_id, 0.0)

        return {
            'entity': {
                'id': entity.id,
                'type': entity.type,
                'value': entity.value,
                'source': entity.source,
                'metadata': entity.metadata
            },
            'linked_entities': len(linked),
            'relationships': {
                'total': len(relationships),
                'incoming': len(self.get_relationships(entity_id, 'in')),
                'outgoing': len(self.get_relationships(entity_id, 'out'))
            },
            'timeline': {
                'total_events': len(timeline),
                'first_event': timeline[0].timestamp if timeline else None,
                'last_event': timeline[-1].timestamp if timeline else None
            },
            'network': {
                'direct_neighbors': len(neighbors),
                'cluster_size': len(cluster),
                'importance_score': entity_importance
            }
        }

    def correlate_entities_by_time(self, time_threshold_minutes: int = 60) -> List[List[str]]:
        """Find entities that appear together in similar timeframes"""
        from datetime import timedelta

        # Get concurrent events
        concurrent = self.timeline_builder.get_concurrent_events(
            timedelta(minutes=time_threshold_minutes)
        )

        # Extract entity groups
        entity_groups = []
        for event_group in concurrent:
            entities = set()
            for event in event_group:
                entities.update(event.entities)
            if len(entities) > 1:
                entity_groups.append(list(entities))

        return entity_groups

    def find_pivotal_entities(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find the most important/central entities in the network"""
        return self.relationship_mapper.get_top_entities('betweenness', top_n)

    def export_analysis(self) -> Dict[str, Any]:
        """Export complete analysis data"""
        return {
            'entities': self.entity_linker.export_entities(),
            'relationships': self.relationship_mapper.export_to_dict(),
            'timeline': self.timeline_builder.export_timeline(),
            'patterns': self.pattern_detector.export_patterns(),
            'statistics': self.get_statistics()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all components"""
        return {
            'entities': self.entity_linker.get_statistics(),
            'relationships': self.relationship_mapper.get_statistics(),
            'timeline': self.timeline_builder.get_statistics(),
            'patterns': self.pattern_detector.get_statistics()
        }

    def clear_all(self) -> None:
        """Clear all data from the correlation engine"""
        self.entity_linker = EntityLinker()
        self.relationship_mapper = RelationshipMapper(directed=True)
        self.timeline_builder = TimelineBuilder()
        self.pattern_detector = PatternDetector()
