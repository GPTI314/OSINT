"""
Network Graph Visualizer - Visualizes entity relationships as network graphs
"""

import networkx as nx
from typing import Dict, List, Optional, Tuple, Any
import json


class NetworkGraphVisualizer:
    """
    Creates interactive network graph visualizations:
    - Force-directed graphs
    - Hierarchical layouts
    - Circular layouts
    - Community detection visualizations
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self.node_styles: Dict[str, Dict] = {}
        self.edge_styles: Dict[Tuple[str, str], Dict] = {}
        self.layout = None

    def add_node(self, node_id: str, label: str = None,
                node_type: str = None, size: float = 10,
                color: str = '#3498db',
                metadata: Dict = None) -> None:
        """Add a node to the graph"""
        self.graph.add_node(node_id)

        self.node_styles[node_id] = {
            'label': label or node_id,
            'type': node_type,
            'size': size,
            'color': color,
            'metadata': metadata or {}
        }

    def add_edge(self, source: str, target: str, label: str = None,
                weight: float = 1.0, color: str = '#95a5a6',
                style: str = 'solid', metadata: Dict = None) -> None:
        """Add an edge to the graph"""
        self.graph.add_edge(source, target, weight=weight)

        self.edge_styles[(source, target)] = {
            'label': label,
            'weight': weight,
            'color': color,
            'style': style,
            'metadata': metadata or {}
        }

    def add_nodes_from_list(self, nodes: List[Dict]) -> None:
        """Add multiple nodes from a list"""
        for node in nodes:
            self.add_node(
                node['id'],
                node.get('label'),
                node.get('type'),
                node.get('size', 10),
                node.get('color', '#3498db'),
                node.get('metadata')
            )

    def add_edges_from_list(self, edges: List[Dict]) -> None:
        """Add multiple edges from a list"""
        for edge in edges:
            self.add_edge(
                edge['source'],
                edge['target'],
                edge.get('label'),
                edge.get('weight', 1.0),
                edge.get('color', '#95a5a6'),
                edge.get('style', 'solid'),
                edge.get('metadata')
            )

    def calculate_layout(self, layout_type: str = 'force') -> Dict[str, Tuple[float, float]]:
        """
        Calculate node positions using specified layout algorithm
        layout_type: 'force', 'circular', 'hierarchical', 'spring', 'kamada_kawai'
        """
        if layout_type == 'force' or layout_type == 'spring':
            self.layout = nx.spring_layout(self.graph, k=1, iterations=50)
        elif layout_type == 'circular':
            self.layout = nx.circular_layout(self.graph)
        elif layout_type == 'hierarchical':
            # Use graphviz hierarchical layout if available
            try:
                self.layout = nx.nx_agraph.graphviz_layout(self.graph, prog='dot')
            except:
                # Fallback to spring layout
                self.layout = nx.spring_layout(self.graph)
        elif layout_type == 'kamada_kawai':
            self.layout = nx.kamada_kawai_layout(self.graph)
        elif layout_type == 'shell':
            self.layout = nx.shell_layout(self.graph)
        else:
            self.layout = nx.spring_layout(self.graph)

        return self.layout

    def style_by_centrality(self, centrality_type: str = 'degree',
                          min_size: float = 5, max_size: float = 30) -> None:
        """Style nodes based on centrality measures"""
        if centrality_type == 'degree':
            centrality = dict(self.graph.degree())
        elif centrality_type == 'betweenness':
            centrality = nx.betweenness_centrality(self.graph)
        elif centrality_type == 'closeness':
            centrality = nx.closeness_centrality(self.graph)
        elif centrality_type == 'pagerank':
            centrality = nx.pagerank(self.graph)
        else:
            return

        # Normalize centrality to size range
        if centrality:
            min_cent = min(centrality.values())
            max_cent = max(centrality.values())
            cent_range = max_cent - min_cent if max_cent > min_cent else 1

            for node_id, cent_value in centrality.items():
                if node_id in self.node_styles:
                    normalized = (cent_value - min_cent) / cent_range
                    size = min_size + (max_size - min_size) * normalized
                    self.node_styles[node_id]['size'] = size

    def color_by_community(self, method: str = 'louvain') -> None:
        """Color nodes by detected communities"""
        # Convert to undirected for community detection
        G_undirected = self.graph.to_undirected()

        if method == 'louvain':
            try:
                import community as community_louvain
                communities = community_louvain.best_partition(G_undirected)
            except ImportError:
                # Fallback to greedy modularity
                communities_list = nx.community.greedy_modularity_communities(G_undirected)
                communities = {}
                for idx, comm in enumerate(communities_list):
                    for node in comm:
                        communities[node] = idx
        else:
            communities_list = nx.community.greedy_modularity_communities(G_undirected)
            communities = {}
            for idx, comm in enumerate(communities_list):
                for node in comm:
                    communities[node] = idx

        # Color palette
        colors = [
            '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
            '#1abc9c', '#34495e', '#e67e22', '#95a5a6', '#d35400'
        ]

        for node_id, community_id in communities.items():
            if node_id in self.node_styles:
                color = colors[community_id % len(colors)]
                self.node_styles[node_id]['color'] = color
                self.node_styles[node_id]['community'] = community_id

    def generate_plotly_graph(self, layout_type: str = 'force',
                            title: str = "Network Graph") -> Dict:
        """Generate Plotly-compatible graph data"""
        # Calculate layout
        if self.layout is None:
            self.calculate_layout(layout_type)

        # Prepare edge traces
        edge_traces = []
        for edge in self.graph.edges():
            x0, y0 = self.layout[edge[0]]
            x1, y1 = self.layout[edge[1]]

            edge_style = self.edge_styles.get(edge, {})

            edge_trace = {
                'x': [x0, x1, None],
                'y': [y0, y1, None],
                'mode': 'lines',
                'line': {
                    'width': edge_style.get('weight', 1) * 2,
                    'color': edge_style.get('color', '#95a5a6')
                },
                'hoverinfo': 'text',
                'text': edge_style.get('label', ''),
                'showlegend': False
            }
            edge_traces.append(edge_trace)

        # Prepare node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []

        for node in self.graph.nodes():
            x, y = self.layout[node]
            node_x.append(x)
            node_y.append(y)

            style = self.node_styles.get(node, {})
            node_size.append(style.get('size', 10))
            node_color.append(style.get('color', '#3498db'))

            label = style.get('label', node)
            node_type = style.get('type', 'unknown')
            node_text.append(f"{label}<br>Type: {node_type}")

        node_trace = {
            'x': node_x,
            'y': node_y,
            'mode': 'markers+text',
            'marker': {
                'size': node_size,
                'color': node_color,
                'line': {'width': 2, 'color': 'white'}
            },
            'text': [self.node_styles.get(n, {}).get('label', n) for n in self.graph.nodes()],
            'textposition': 'top center',
            'hovertext': node_text,
            'hoverinfo': 'text',
            'showlegend': False
        }

        # Combine traces
        data = edge_traces + [node_trace]

        layout = {
            'title': title,
            'showlegend': False,
            'hovermode': 'closest',
            'xaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False},
            'yaxis': {'showgrid': False, 'zeroline': False, 'showticklabels': False},
            'plot_bgcolor': '#f8f9fa',
            'paper_bgcolor': '#ffffff'
        }

        return {'data': data, 'layout': layout}

    def generate_cytoscape_json(self) -> Dict:
        """Generate Cytoscape.js compatible JSON"""
        elements = []

        # Add nodes
        for node in self.graph.nodes():
            style = self.node_styles.get(node, {})
            elements.append({
                'group': 'nodes',
                'data': {
                    'id': node,
                    'label': style.get('label', node),
                    'type': style.get('type', 'unknown')
                },
                'style': {
                    'width': style.get('size', 10),
                    'height': style.get('size', 10),
                    'background-color': style.get('color', '#3498db')
                }
            })

        # Add edges
        for edge in self.graph.edges():
            style = self.edge_styles.get(edge, {})
            elements.append({
                'group': 'edges',
                'data': {
                    'id': f"{edge[0]}-{edge[1]}",
                    'source': edge[0],
                    'target': edge[1],
                    'label': style.get('label', '')
                },
                'style': {
                    'width': style.get('weight', 1) * 2,
                    'line-color': style.get('color', '#95a5a6'),
                    'line-style': style.get('style', 'solid')
                }
            })

        return {'elements': elements}

    def export_to_gexf(self, filepath: str) -> bool:
        """Export graph to GEXF format (Gephi-compatible)"""
        try:
            nx.write_gexf(self.graph, filepath)
            return True
        except Exception as e:
            print(f"Error exporting to GEXF: {e}")
            return False

    def export_to_graphml(self, filepath: str) -> bool:
        """Export graph to GraphML format"""
        try:
            nx.write_graphml(self.graph, filepath)
            return True
        except Exception as e:
            print(f"Error exporting to GraphML: {e}")
            return False

    def export_to_json(self, filepath: str) -> bool:
        """Export graph to JSON format"""
        try:
            data = {
                'nodes': [
                    {
                        'id': node,
                        **self.node_styles.get(node, {})
                    }
                    for node in self.graph.nodes()
                ],
                'edges': [
                    {
                        'source': edge[0],
                        'target': edge[1],
                        **self.edge_styles.get(edge, {})
                    }
                    for edge in self.graph.edges()
                ]
            }

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        return {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_weakly_connected(self.graph),
            'num_components': nx.number_weakly_connected_components(self.graph)
        }

    def clear(self) -> None:
        """Clear the graph"""
        self.graph.clear()
        self.node_styles.clear()
        self.edge_styles.clear()
        self.layout = None
