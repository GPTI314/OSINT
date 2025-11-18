"""
Relationship Mapper - Builds and analyzes relationship graphs between entities
"""

import networkx as nx
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict
from datetime import datetime
import json


class Relationship:
    """Represents a relationship between two entities"""

    def __init__(self, source_id: str, target_id: str, rel_type: str,
                 weight: float = 1.0, timestamp: datetime = None,
                 metadata: Dict = None):
        self.source_id = source_id
        self.target_id = target_id
        self.type = rel_type
        self.weight = weight
        self.timestamp = timestamp or datetime.now()
        self.metadata = metadata or {}

    def __repr__(self):
        return f"Relationship({self.source_id} --[{self.type}]--> {self.target_id})"


class RelationshipMapper:
    """
    Builds and analyzes relationship graphs between entities:
    - Create directed/undirected graphs
    - Analyze graph structure (centrality, communities, paths)
    - Query relationships
    - Export graph data
    """

    def __init__(self, directed: bool = True):
        self.directed = directed
        if directed:
            self.graph = nx.DiGraph()
        else:
            self.graph = nx.Graph()

        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.entity_attributes: Dict[str, Dict] = defaultdict(dict)

    def add_entity(self, entity_id: str, attributes: Dict = None) -> None:
        """Add an entity node to the graph"""
        self.graph.add_node(entity_id)
        if attributes:
            self.entity_attributes[entity_id].update(attributes)
            nx.set_node_attributes(self.graph, {entity_id: attributes})

    def add_relationship(self, relationship: Relationship) -> bool:
        """Add a relationship edge to the graph"""
        try:
            # Add nodes if they don't exist
            if not self.graph.has_node(relationship.source_id):
                self.add_entity(relationship.source_id)
            if not self.graph.has_node(relationship.target_id):
                self.add_entity(relationship.target_id)

            # Add edge
            self.graph.add_edge(
                relationship.source_id,
                relationship.target_id,
                type=relationship.type,
                weight=relationship.weight,
                timestamp=relationship.timestamp,
                **relationship.metadata
            )

            # Store relationship
            key = (relationship.source_id, relationship.target_id)
            self.relationships[key] = relationship

            return True
        except Exception as e:
            print(f"Error adding relationship: {e}")
            return False

    def create_relationship(self, source_id: str, target_id: str, rel_type: str,
                          weight: float = 1.0, timestamp: datetime = None,
                          metadata: Dict = None) -> Relationship:
        """Create and add a new relationship"""
        relationship = Relationship(source_id, target_id, rel_type, weight, timestamp, metadata)
        self.add_relationship(relationship)
        return relationship

    def get_relationships(self, entity_id: str, direction: str = "both") -> List[Relationship]:
        """
        Get all relationships for an entity
        direction: 'in', 'out', or 'both'
        """
        relationships = []

        if direction in ["out", "both"]:
            for target_id in self.graph.successors(entity_id):
                key = (entity_id, target_id)
                if key in self.relationships:
                    relationships.append(self.relationships[key])

        if direction in ["in", "both"]:
            for source_id in self.graph.predecessors(entity_id):
                key = (source_id, entity_id)
                if key in self.relationships:
                    relationships.append(self.relationships[key])

        return relationships

    def find_paths(self, source_id: str, target_id: str,
                  max_length: int = 5) -> List[List[str]]:
        """Find all paths between two entities up to max_length"""
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return []

        try:
            paths = nx.all_simple_paths(
                self.graph,
                source_id,
                target_id,
                cutoff=max_length
            )
            return list(paths)
        except nx.NetworkXNoPath:
            return []

    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """Find the shortest path between two entities"""
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return None

        try:
            return nx.shortest_path(self.graph, source_id, target_id)
        except nx.NetworkXNoPath:
            return None

    def get_neighbors(self, entity_id: str, depth: int = 1) -> Set[str]:
        """Get all neighbors within a certain depth"""
        if not self.graph.has_node(entity_id):
            return set()

        neighbors = {entity_id}
        current_level = {entity_id}

        for _ in range(depth):
            next_level = set()
            for node in current_level:
                # Get successors and predecessors
                next_level.update(self.graph.successors(node))
                next_level.update(self.graph.predecessors(node))
            neighbors.update(next_level)
            current_level = next_level - neighbors

        neighbors.remove(entity_id)  # Remove the original entity
        return neighbors

    def calculate_centrality(self) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality measures for all nodes"""
        centrality_scores = {}

        try:
            centrality_scores['degree'] = dict(self.graph.degree())
            centrality_scores['betweenness'] = nx.betweenness_centrality(self.graph)
            centrality_scores['closeness'] = nx.closeness_centrality(self.graph)
            centrality_scores['pagerank'] = nx.pagerank(self.graph)

            if not self.directed:
                centrality_scores['eigenvector'] = nx.eigenvector_centrality(
                    self.graph, max_iter=1000
                )
        except Exception as e:
            print(f"Error calculating centrality: {e}")

        return centrality_scores

    def get_top_entities(self, metric: str = 'degree', top_n: int = 10) -> List[Tuple[str, float]]:
        """Get top N entities by a centrality metric"""
        centrality = self.calculate_centrality()

        if metric not in centrality:
            return []

        scores = centrality[metric]
        sorted_entities = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_entities[:top_n]

    def detect_communities(self, method: str = 'louvain') -> Dict[str, int]:
        """
        Detect communities in the graph
        method: 'louvain', 'label_propagation', or 'greedy_modularity'
        """
        if self.directed:
            # Convert to undirected for community detection
            G = self.graph.to_undirected()
        else:
            G = self.graph

        try:
            if method == 'louvain':
                # Note: requires python-louvain package
                try:
                    import community as community_louvain
                    partition = community_louvain.best_partition(G)
                    return partition
                except ImportError:
                    print("python-louvain not installed, falling back to greedy_modularity")
                    method = 'greedy_modularity'

            if method == 'label_propagation':
                communities = nx.community.label_propagation_communities(G)
            elif method == 'greedy_modularity':
                communities = nx.community.greedy_modularity_communities(G)
            else:
                return {}

            # Convert to dict format
            partition = {}
            for idx, community in enumerate(communities):
                for node in community:
                    partition[node] = idx

            return partition

        except Exception as e:
            print(f"Error detecting communities: {e}")
            return {}

    def get_subgraph(self, entity_ids: List[str]) -> 'RelationshipMapper':
        """Create a subgraph containing only the specified entities"""
        subgraph = RelationshipMapper(directed=self.directed)

        # Add nodes
        for entity_id in entity_ids:
            if self.graph.has_node(entity_id):
                attrs = dict(self.graph.nodes[entity_id])
                subgraph.add_entity(entity_id, attrs)

        # Add edges
        for source_id in entity_ids:
            for target_id in entity_ids:
                if self.graph.has_edge(source_id, target_id):
                    edge_data = self.graph[source_id][target_id]
                    relationship = Relationship(
                        source_id,
                        target_id,
                        edge_data.get('type', 'unknown'),
                        edge_data.get('weight', 1.0),
                        edge_data.get('timestamp'),
                        {k: v for k, v in edge_data.items()
                         if k not in ['type', 'weight', 'timestamp']}
                    )
                    subgraph.add_relationship(relationship)

        return subgraph

    def find_cliques(self, min_size: int = 3) -> List[Set[str]]:
        """Find cliques (fully connected subgraphs) of minimum size"""
        if self.directed:
            G = self.graph.to_undirected()
        else:
            G = self.graph

        try:
            cliques = list(nx.find_cliques(G))
            return [set(clique) for clique in cliques if len(clique) >= min_size]
        except Exception as e:
            print(f"Error finding cliques: {e}")
            return []

    def calculate_graph_metrics(self) -> Dict[str, Any]:
        """Calculate overall graph metrics"""
        metrics = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph) if self.directed
                          else nx.is_connected(self.graph),
        }

        try:
            if self.directed:
                metrics['num_strongly_connected_components'] = \
                    nx.number_strongly_connected_components(self.graph)
                metrics['num_weakly_connected_components'] = \
                    nx.number_weakly_connected_components(self.graph)
            else:
                metrics['num_connected_components'] = \
                    nx.number_connected_components(self.graph)

            # Average clustering coefficient
            metrics['avg_clustering'] = nx.average_clustering(
                self.graph.to_undirected() if self.directed else self.graph
            )

            # Diameter (if connected)
            if metrics['is_connected']:
                if self.directed:
                    metrics['diameter'] = nx.diameter(self.graph.to_undirected())
                else:
                    metrics['diameter'] = nx.diameter(self.graph)

        except Exception as e:
            print(f"Error calculating some graph metrics: {e}")

        return metrics

    def export_to_dict(self) -> Dict:
        """Export graph to dictionary format"""
        return {
            'nodes': [
                {
                    'id': node,
                    'attributes': dict(self.graph.nodes[node])
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'source': edge[0],
                    'target': edge[1],
                    'attributes': dict(self.graph[edge[0]][edge[1]])
                }
                for edge in self.graph.edges()
            ],
            'directed': self.directed
        }

    def export_to_json(self, filepath: str) -> bool:
        """Export graph to JSON file"""
        try:
            data = self.export_to_dict()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    def import_from_dict(self, data: Dict) -> bool:
        """Import graph from dictionary format"""
        try:
            # Clear existing graph
            self.graph.clear()
            self.relationships.clear()
            self.entity_attributes.clear()

            # Add nodes
            for node_data in data['nodes']:
                self.add_entity(node_data['id'], node_data.get('attributes', {}))

            # Add edges
            for edge_data in data['edges']:
                attrs = edge_data.get('attributes', {})
                relationship = Relationship(
                    edge_data['source'],
                    edge_data['target'],
                    attrs.get('type', 'unknown'),
                    attrs.get('weight', 1.0),
                    attrs.get('timestamp'),
                    {k: v for k, v in attrs.items()
                     if k not in ['type', 'weight', 'timestamp']}
                )
                self.add_relationship(relationship)

            return True
        except Exception as e:
            print(f"Error importing from dict: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get comprehensive statistics about the relationship graph"""
        metrics = self.calculate_graph_metrics()
        centrality = self.calculate_centrality()

        # Get top entities by different metrics
        top_entities = {}
        for metric in ['degree', 'betweenness', 'pagerank']:
            if metric in centrality:
                top_entities[metric] = self.get_top_entities(metric, 5)

        # Relationship type distribution
        rel_types = defaultdict(int)
        for rel in self.relationships.values():
            rel_types[rel.type] += 1

        return {
            'graph_metrics': metrics,
            'top_entities': top_entities,
            'relationship_types': dict(rel_types),
            'total_relationships': len(self.relationships)
        }
