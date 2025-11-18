"""
Entity Linker - Links related entities across different data sources
"""

import re
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import hashlib


class Entity:
    """Represents an entity in the OSINT data"""

    def __init__(self, entity_id: str, entity_type: str, value: str,
                 source: str = None, metadata: Dict = None):
        self.id = entity_id
        self.type = entity_type
        self.value = value
        self.source = source
        self.metadata = metadata or {}
        self.linked_entities = set()
        self.confidence_scores = {}

    def __hash__(self):
        return hash((self.id, self.type, self.value))

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return self.id == other.id and self.type == other.type

    def __repr__(self):
        return f"Entity(id={self.id}, type={self.type}, value={self.value})"


class EntityLinker:
    """
    Links related entities using various matching strategies:
    - Exact matching
    - Fuzzy matching
    - Pattern-based matching
    - Semantic similarity
    """

    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.entity_groups: Dict[str, Set[str]] = defaultdict(set)
        self.linking_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict:
        """Initialize entity linking rules"""
        return {
            'email': [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            ],
            'ip': [
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            ],
            'domain': [
                r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b',
            ],
            'url': [
                r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)',
            ],
            'hash': [
                r'\b[a-fA-F0-9]{32}\b',  # MD5
                r'\b[a-fA-F0-9]{40}\b',  # SHA1
                r'\b[a-fA-F0-9]{64}\b',  # SHA256
            ],
            'phone': [
                r'\+?[1-9]\d{1,14}',  # E.164 format
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            ],
            'bitcoin': [
                r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            ],
        }

    def add_entity(self, entity: Entity) -> str:
        """Add an entity to the linker"""
        self.entities[entity.id] = entity
        self.entity_groups[entity.type].add(entity.id)
        return entity.id

    def create_entity(self, entity_type: str, value: str,
                     source: str = None, metadata: Dict = None) -> Entity:
        """Create and add a new entity"""
        entity_id = self._generate_entity_id(entity_type, value)
        entity = Entity(entity_id, entity_type, value, source, metadata)
        self.add_entity(entity)
        return entity

    def _generate_entity_id(self, entity_type: str, value: str) -> str:
        """Generate a unique entity ID"""
        hash_input = f"{entity_type}:{value}".encode('utf-8')
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def extract_entities(self, text: str, source: str = None) -> List[Entity]:
        """Extract entities from text using pattern matching"""
        entities = []

        for entity_type, patterns in self.linking_rules.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    value = match.group(0)
                    entity = self.create_entity(
                        entity_type=entity_type,
                        value=value,
                        source=source,
                        metadata={'position': match.span()}
                    )
                    entities.append(entity)

        return entities

    def link_entities(self, entity1_id: str, entity2_id: str,
                     confidence: float = 1.0, link_type: str = "related") -> bool:
        """Create a link between two entities"""
        if entity1_id not in self.entities or entity2_id not in self.entities:
            return False

        entity1 = self.entities[entity1_id]
        entity2 = self.entities[entity2_id]

        entity1.linked_entities.add(entity2_id)
        entity2.linked_entities.add(entity1_id)

        entity1.confidence_scores[entity2_id] = confidence
        entity2.confidence_scores[entity1_id] = confidence

        entity1.metadata[f'link_type_{entity2_id}'] = link_type
        entity2.metadata[f'link_type_{entity1_id}'] = link_type

        return True

    def find_similar_entities(self, entity_id: str,
                            similarity_threshold: float = 0.8) -> List[Tuple[Entity, float]]:
        """Find entities similar to the given entity"""
        if entity_id not in self.entities:
            return []

        entity = self.entities[entity_id]
        similar = []

        # Check entities of the same type
        for other_id in self.entity_groups[entity.type]:
            if other_id == entity_id:
                continue

            other = self.entities[other_id]
            similarity = self._calculate_similarity(entity, other)

            if similarity >= similarity_threshold:
                similar.append((other, similarity))

        # Sort by similarity (descending)
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar

    def _calculate_similarity(self, entity1: Entity, entity2: Entity) -> float:
        """Calculate similarity score between two entities"""
        if entity1.type != entity2.type:
            return 0.0

        # Exact match
        if entity1.value == entity2.value:
            return 1.0

        # Levenshtein-like similarity for strings
        val1 = entity1.value.lower()
        val2 = entity2.value.lower()

        # Simple character overlap similarity
        set1 = set(val1)
        set2 = set(val2)

        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def get_entity_cluster(self, entity_id: str) -> Set[str]:
        """Get all entities linked to the given entity (transitive closure)"""
        if entity_id not in self.entities:
            return set()

        visited = set()
        to_visit = {entity_id}

        while to_visit:
            current_id = to_visit.pop()
            if current_id in visited:
                continue

            visited.add(current_id)
            current_entity = self.entities[current_id]
            to_visit.update(current_entity.linked_entities - visited)

        return visited

    def auto_link_entities(self, confidence_threshold: float = 0.8) -> int:
        """Automatically link similar entities across all data"""
        links_created = 0

        for entity_type, entity_ids in self.entity_groups.items():
            entity_list = [self.entities[eid] for eid in entity_ids]

            for i, entity1 in enumerate(entity_list):
                for entity2 in entity_list[i+1:]:
                    similarity = self._calculate_similarity(entity1, entity2)

                    if similarity >= confidence_threshold:
                        if self.link_entities(entity1.id, entity2.id,
                                            confidence=similarity,
                                            link_type="auto_similar"):
                            links_created += 1

        return links_created

    def get_linked_entities(self, entity_id: str) -> List[Tuple[Entity, float, str]]:
        """Get all entities directly linked to the given entity"""
        if entity_id not in self.entities:
            return []

        entity = self.entities[entity_id]
        linked = []

        for linked_id in entity.linked_entities:
            if linked_id in self.entities:
                linked_entity = self.entities[linked_id]
                confidence = entity.confidence_scores.get(linked_id, 0.0)
                link_type = entity.metadata.get(f'link_type_{linked_id}', 'unknown')
                linked.append((linked_entity, confidence, link_type))

        return linked

    def export_entities(self) -> List[Dict]:
        """Export all entities to a list of dictionaries"""
        return [
            {
                'id': entity.id,
                'type': entity.type,
                'value': entity.value,
                'source': entity.source,
                'metadata': entity.metadata,
                'linked_entities': list(entity.linked_entities),
                'confidence_scores': entity.confidence_scores
            }
            for entity in self.entities.values()
        ]

    def get_statistics(self) -> Dict:
        """Get statistics about the entity graph"""
        total_entities = len(self.entities)
        total_links = sum(len(e.linked_entities) for e in self.entities.values()) // 2

        entity_counts = {
            entity_type: len(entity_ids)
            for entity_type, entity_ids in self.entity_groups.items()
        }

        # Find largest cluster
        clusters = []
        visited = set()
        for entity_id in self.entities:
            if entity_id not in visited:
                cluster = self.get_entity_cluster(entity_id)
                clusters.append(len(cluster))
                visited.update(cluster)

        return {
            'total_entities': total_entities,
            'total_links': total_links,
            'entity_types': entity_counts,
            'num_clusters': len(clusters),
            'largest_cluster_size': max(clusters) if clusters else 0,
            'average_cluster_size': sum(clusters) / len(clusters) if clusters else 0
        }
