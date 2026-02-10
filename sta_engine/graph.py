from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

@dataclass
class Node:
    """Represents a pin or port in the timing graph."""
    name: str
    type: str  # "port", "pin"
    edges: List[Tuple['Node', float, str]] = field(default_factory=list) # (target_node, weight, edge_type)
    at: float = -1.0  # Arrival Time
    rt: float = 999.0  # Required Time
    slack: float = 0.0  # Slack

    def add_edge(self, target: 'Node', weight: float, edge_type: str):
        self.edges.append((target, weight, edge_type))

    def __repr__(self):
        return f"Node({self.name})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name

class Graph:
    """Manages the graph nodes and connectivity."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {} # name -> Node

    def get_or_create_node(self, name: str, node_type: str = "pin") -> Node:
        if name not in self.nodes:
            self.nodes[name] = Node(name, node_type)
        return self.nodes[name]
    
    def get_node(self, name: str) -> Optional[Node]:
        return self.nodes.get(name)

    def get_all_nodes(self) -> List[Node]:
        return list(self.nodes.values())

    def summary(self) -> str:
        return f"Total Nodes: {len(self.nodes)}"
