"""
Link analysis and relationship mapping
"""
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict


class LinkAnalyzer:
    """Analyze links and relationships between entities"""

    def __init__(self):
        """Initialize link analyzer"""
        self.graph = defaultdict(set)
        self.nodes = set()
        self.edges = []

    def enrich(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Enrich data with link analysis

        Args:
            data: Input data
            fields: Specific fields to analyze

        Returns:
            Enriched data with link analysis
        """
        # Extract entities or items to analyze
        entities = self._extract_entities(data, fields)

        if not entities:
            return {
                'links': [],
                'nodes': [],
                'timestamp': datetime.utcnow().isoformat()
            }

        # Analyze relationships
        result = self.analyze_relationships(entities)

        return result

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text for relationships

        Args:
            text: Input text

        Returns:
            Relationship analysis results
        """
        # Extract entities from text
        entities = self._extract_entities_from_text(text)

        return self.analyze_relationships(entities)

    def add_link(self, source: str, target: str, link_type: str = 'default', weight: float = 1.0):
        """
        Add a link between two nodes

        Args:
            source: Source node
            target: Target node
            link_type: Type of link
            weight: Link weight
        """
        self.graph[source].add(target)
        self.nodes.add(source)
        self.nodes.add(target)

        self.edges.append({
            'source': source,
            'target': target,
            'type': link_type,
            'weight': weight
        })

    def analyze_relationships(self, entities: List[str]) -> Dict[str, Any]:
        """
        Analyze relationships between entities

        Args:
            entities: List of entity names

        Returns:
            Relationship analysis results
        """
        # Create co-occurrence links
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i+1:]:
                self.add_link(entity1, entity2, 'co-occurrence', 1.0)

        # Calculate metrics
        metrics = self.calculate_metrics()

        return {
            'nodes': list(self.nodes),
            'edges': self.edges,
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Calculate graph metrics

        Returns:
            Dictionary of metrics
        """
        metrics = {
            'density': self._calculate_density(),
            'centrality': self._calculate_centrality(),
            'clustering': self._calculate_clustering()
        }

        return metrics

    def _calculate_density(self) -> float:
        """Calculate graph density"""
        n = len(self.nodes)
        if n < 2:
            return 0.0

        max_edges = n * (n - 1) / 2
        actual_edges = len(self.edges)

        return actual_edges / max_edges if max_edges > 0 else 0.0

    def _calculate_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for each node"""
        centrality = {}

        for node in self.nodes:
            # Count connections
            out_degree = len(self.graph[node])
            in_degree = sum(1 for neighbors in self.graph.values() if node in neighbors)
            total_degree = out_degree + in_degree

            # Normalize by max possible degree
            max_degree = (len(self.nodes) - 1) * 2
            centrality[node] = total_degree / max_degree if max_degree > 0 else 0.0

        # Get top 10 most central nodes
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_nodes[:10])

    def _calculate_clustering(self) -> float:
        """Calculate average clustering coefficient"""
        if len(self.nodes) < 3:
            return 0.0

        clustering_scores = []

        for node in self.nodes:
            neighbors = self.graph[node]
            if len(neighbors) < 2:
                clustering_scores.append(0.0)
                continue

            # Count edges between neighbors
            edges_between_neighbors = 0
            for n1 in neighbors:
                for n2 in neighbors:
                    if n1 != n2 and n2 in self.graph[n1]:
                        edges_between_neighbors += 1

            # Calculate clustering coefficient
            max_edges = len(neighbors) * (len(neighbors) - 1)
            clustering = edges_between_neighbors / max_edges if max_edges > 0 else 0.0
            clustering_scores.append(clustering)

        return sum(clustering_scores) / len(clustering_scores) if clustering_scores else 0.0

    def find_communities(self) -> List[Set[str]]:
        """
        Find communities using simple connected components

        Returns:
            List of communities (sets of nodes)
        """
        visited = set()
        communities = []

        def dfs(node, community):
            visited.add(node)
            community.add(node)

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    dfs(neighbor, community)

        for node in self.nodes:
            if node not in visited:
                community = set()
                dfs(node, community)
                communities.append(community)

        return communities

    def get_shortest_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes using BFS

        Args:
            source: Source node
            target: Target node

        Returns:
            List of nodes in path, or None if no path exists
        """
        if source not in self.nodes or target not in self.nodes:
            return None

        queue = [(source, [source])]
        visited = {source}

        while queue:
            node, path = queue.pop(0)

            if node == target:
                return path

            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    def _extract_entities(self, data: Dict[str, Any], fields: Optional[List[str]] = None) -> List[str]:
        """Extract entities from data"""
        entities = []

        # Check if data has explicit entities field
        if 'enrichment' in data and 'results' in data['enrichment']:
            results = data['enrichment']['results']
            if 'entity_recognition' in results:
                entity_data = results['entity_recognition']
                if 'entities' in entity_data:
                    entities = [e['text'] for e in entity_data['entities']]

        # Fallback to text extraction
        if not entities and fields:
            text = ' '.join(str(data.get(field, '')) for field in fields if field in data)
            entities = self._extract_entities_from_text(text)

        return entities

    def _extract_entities_from_text(self, text: str) -> List[str]:
        """Simple entity extraction from text"""
        import re

        # Extract capitalized words/phrases as potential entities
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

        # Remove duplicates while preserving order
        seen = set()
        unique_entities = []
        for entity in entities:
            if entity not in seen:
                seen.add(entity)
                unique_entities.append(entity)

        return unique_entities

    def export_graph(self, format: str = 'json') -> Any:
        """
        Export graph in specified format

        Args:
            format: Export format ('json', 'edgelist', 'adjacency')

        Returns:
            Graph data in specified format
        """
        if format == 'json':
            return {
                'nodes': [{'id': node} for node in self.nodes],
                'edges': self.edges
            }
        elif format == 'edgelist':
            return [(e['source'], e['target'], e['weight']) for e in self.edges]
        elif format == 'adjacency':
            return {node: list(neighbors) for node, neighbors in self.graph.items()}
        else:
            raise ValueError(f"Unsupported format: {format}")

    def clear(self):
        """Clear all graph data"""
        self.graph.clear()
        self.nodes.clear()
        self.edges.clear()
