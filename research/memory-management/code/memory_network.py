"""
Semantic Memory Network
Implements associative memory with spreading activation.

Based on: Hebbian assembly theory, Hopfield networks, Small-world networks
"""

import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json


@dataclass
class MemoryNode:
    """A node in the semantic memory network."""
    id: str
    content: str
    activation: float = 0.0
    connections: Dict[str, float] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.id)


class SemanticMemoryNetwork:
    """
    Implements a semantic memory network with associative retrieval.
    
    Features:
    - Spreading activation for pattern completion
    - Small-world network topology
    - Hub node identification
    - Cross-domain bridge detection
    """
    
    def __init__(self, decay_rate: float = 0.1, threshold: float = 0.01):
        self.nodes: Dict[str, MemoryNode] = {}
        self.decay_rate = decay_rate  # Activation decay per step
        self.threshold = threshold    # Minimum activation to propagate
        
    def add_node(self, node_id: str, content: str, metadata: Optional[Dict] = None) -> MemoryNode:
        """Add a new memory node."""
        if node_id not in self.nodes:
            self.nodes[node_id] = MemoryNode(
                id=node_id,
                content=content,
                metadata=metadata or {}
            )
        return self.nodes[node_id]
    
    def add_connection(self, from_id: str, to_id: str, strength: float = 1.0, bidirectional: bool = True):
        """Create a weighted connection between nodes."""
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError("Both nodes must exist in network")
        
        self.nodes[from_id].connections[to_id] = strength
        if bidirectional:
            self.nodes[to_id].connections[from_id] = strength
    
    def activate(self, node_id: str, initial_activation: float = 1.0):
        """Activate a node (simulate memory retrieval trigger)."""
        if node_id in self.nodes:
            self.nodes[node_id].activation = initial_activation
    
    def spread_activation(self, max_iterations: int = 10) -> Dict[str, float]:
        """
        Spread activation through the network (spreading activation algorithm).
        
        Returns:
            Dictionary of node_id -> final activation levels
        """
        for _ in range(max_iterations):
            new_activations = {}
            
            for node_id, node in self.nodes.items():
                if node.activation < self.threshold:
                    continue
                
                # Spread to connected nodes
                for neighbor_id, connection_strength in node.connections.items():
                    if neighbor_id not in new_activations:
                        new_activations[neighbor_id] = 0
                    
                    # Activation spreads proportional to connection strength
                    spread = node.activation * connection_strength * 0.5
                    new_activations[neighbor_id] += spread
            
            # Update activations and apply decay
            for node_id, node in self.nodes.items():
                if node_id in new_activations:
                    node.activation = node.activation * (1 - self.decay_rate) + new_activations[node_id]
                else:
                    node.activation *= (1 - self.decay_rate)
        
        return {nid: n.activation for nid, n in self.nodes.items()}
    
    def retrieve_associated(self, cue_id: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        Retrieve associated memories from a cue.
        
        Args:
            cue_id: Starting node
            top_k: Number of results to return
            
        Returns:
            List of (node_id, content, activation) tuples
        """
        # Reset all activations
        for node in self.nodes.values():
            node.activation = 0
        
        # Activate cue
        self.activate(cue_id, 1.0)
        
        # Spread activation
        activations = self.spread_activation()
        
        # Sort by activation (excluding the cue itself)
        results = [
            (nid, self.nodes[nid].content, act)
            for nid, act in activations.items()
            if nid != cue_id and act > self.threshold
        ]
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:top_k]
    
    def find_hub_nodes(self, top_k: int = 5) -> List[Tuple[str, int]]:
        """Identify hub nodes (high degree centrality)."""
        degrees = [(nid, len(node.connections)) for nid, node in self.nodes.items()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        return degrees[:top_k]
    
    def calculate_clustering_coefficient(self, node_id: str) -> float:
        """Calculate local clustering coefficient for a node."""
        if node_id not in self.nodes:
            return 0.0
        
        node = self.nodes[node_id]
        neighbors = list(node.connections.keys())
        
        if len(neighbors) < 2:
            return 0.0
        
        # Count edges between neighbors
        edges_between_neighbors = 0
        for i, n1 in enumerate(neighbors):
            for n2 in neighbors[i+1:]:
                if n2 in self.nodes[n1].connections:
                    edges_between_neighbors += 1
        
        max_possible = len(neighbors) * (len(neighbors) - 1) / 2
        return edges_between_neighbors / max_possible if max_possible > 0 else 0
    
    def find_bridges(self) -> List[Tuple[str, str, float]]:
        """
        Find bridge connections (high betweenness potential).
        Connections that link otherwise disconnected clusters.
        """
        bridges = []
        
        for node_id, node in self.nodes.items():
            node_cluster = self.calculate_clustering_coefficient(node_id)
            
            for neighbor_id, strength in node.connections.items():
                neighbor_cluster = self.calculate_clustering_coefficient(neighbor_id)
                
                # Low clustering on both ends suggests bridge
                if node_cluster < 0.3 and neighbor_cluster < 0.3 and strength > 0.5:
                    bridges.append((node_id, neighbor_id, strength))
        
        bridges.sort(key=lambda x: x[2], reverse=True)
        return bridges
    
    def save(self, filepath: str):
        """Save network to JSON."""
        data = {
            "nodes": {
                nid: {
                    "content": n.content,
                    "connections": n.connections,
                    "metadata": n.metadata
                }
                for nid, n in self.nodes.items()
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'SemanticMemoryNetwork':
        """Load network from JSON."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        network = cls()
        for nid, ndata in data["nodes"].items():
            network.add_node(nid, ndata["content"], ndata.get("metadata", {}))
        
        for nid, ndata in data["nodes"].items():
            for conn_id, strength in ndata["connections"].items():
                if conn_id in network.nodes:
                    network.nodes[nid].connections[conn_id] = strength
        
        return network


# Example: Creating a knowledge network
if __name__ == "__main__":
    print("=" * 60)
    print("SEMANTIC MEMORY NETWORK DEMO")
    print("=" * 60)
    
    # Create network
    network = SemanticMemoryNetwork()
    
    # Add nodes representing concepts
    concepts = {
        "memory": "The faculty of encoding, storing, and retrieving information",
        "encoding": "Process of converting information into memory traces",
        "storage": "Maintenance of information over time",
        "retrieval": "Accessing stored information when needed",
        "hippocampus": "Brain region critical for memory formation",
        "neuron": "Basic unit of the nervous system",
        "synapse": "Connection between neurons",
        "forgetting": "Loss of information over time",
        "rehearsal": "Repeating information to maintain it in memory",
        "association": "Linking new information to existing knowledge",
        "chunking": "Grouping information into meaningful units",
        "schema": "Mental framework for organizing knowledge",
    }
    
    for cid, content in concepts.items():
        network.add_node(cid, content)
    
    # Create semantic connections
    connections = [
        ("memory", "encoding", 0.9),
        ("memory", "storage", 0.9),
        ("memory", "retrieval", 0.9),
        ("encoding", "hippocampus", 0.8),
        ("storage", "hippocampus", 0.7),
        ("retrieval", "hippocampus", 0.7),
        ("hippocampus", "neuron", 0.6),
        ("neuron", "synapse", 0.9),
        ("storage", "synapse", 0.5),
        ("memory", "forgetting", 0.6),
        ("encoding", "rehearsal", 0.7),
        ("encoding", "association", 0.8),
        ("storage", "chunking", 0.6),
        ("storage", "schema", 0.7),
        ("association", "schema", 0.8),
        ("chunking", "schema", 0.5),
    ]
    
    for from_id, to_id, strength in connections:
        network.add_connection(from_id, to_id, strength)
    
    print(f"\nNetwork created with {len(network.nodes)} nodes")
    
    # Identify hub nodes
    print("\n" + "-" * 40)
    print("HUB NODES (High Connectivity):")
    print("-" * 40)
    hubs = network.find_hub_nodes(5)
    for node_id, degree in hubs:
        print(f"  {node_id}: {degree} connections")
    
    # Demonstrate spreading activation
    print("\n" + "-" * 40)
    print("SPREADING ACTIVATION DEMO")
    print("-" * 40)
    
    cue = "memory"
    print(f"\nActivating cue: '{cue}'")
    associated = network.retrieve_associated(cue, top_k=5)
    
    print(f"\nAssociated concepts (by activation strength):")
    for node_id, content, activation in associated:
        print(f"  {node_id:15} (activation: {activation:.3f})")
        print(f"    → {content[:50]}...")
    
    # Find bridges
    print("\n" + "-" * 40)
    print("BRIDGE CONNECTIONS (Cross-Cluster Links):")
    print("-" * 40)
    bridges = network.find_bridges()
    for n1, n2, strength in bridges[:5]:
        print(f"  {n1} ↔ {n2} (strength: {strength:.2f})")
    
    # Calculate network statistics
    print("\n" + "-" * 40)
    print("NETWORK STATISTICS:")
    print("-" * 40)
    
    avg_clustering = np.mean([
        network.calculate_clustering_coefficient(nid)
        for nid in network.nodes
    ])
    
    total_connections = sum(len(n.connections) for n in network.nodes.values()) // 2
    density = total_connections / (len(network.nodes) * (len(network.nodes) - 1) / 2)
    
    print(f"  Total nodes: {len(network.nodes)}")
    print(f"  Total connections: {total_connections}")
    print(f"  Network density: {density:.3f}")
    print(f"  Average clustering: {avg_clustering:.3f}")
