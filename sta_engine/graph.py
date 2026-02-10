class Node:
    """Represents a pin or port in the timing graph."""
    def __init__(self, name, node_type):
        self.name = name # e.g., "u1.A" or "clk"
        self.type = node_type # "port", "pin"
        self.edges = [] # List of (target_node, weight, edge_type)
        self.at = -1.0 # Arrival Time
        self.rt = 999.0 # Required Time

    def add_edge(self, target, weight, edge_type):
        self.edges.append((target, weight, edge_type))

    def __repr__(self):
        return f"Node({self.name})"

class Graph:
    """Manages the graph nodes and connectivity."""
    def __init__(self):
        self.nodes = {} # name -> Node

    def get_or_create_node(self, name, node_type="pin"):
        if name not in self.nodes:
            self.nodes[name] = Node(name, node_type)
        return self.nodes[name]
    
    def get_node(self, name):
        return self.nodes.get(name)

    def get_all_nodes(self):
        return self.nodes.values()
    
    def summary(self):
        return f"Total Nodes: {len(self.nodes)}"
