try:
    from graphviz import Digraph
except ImportError:
    Digraph = None

from .graph import Graph

class GraphVisualizer:
    """Handles visualization of the STA Graph using Graphviz."""
    
    def __init__(self, graph: Graph):
        self.graph = graph

    def plot(self, output_file: str = "sta_graph"):
        """Generates a visual representation of the graph."""
        if Digraph is None:
            print("Error: graphviz not installed. Please run 'uv add graphviz'")
            return

        dot = Digraph(comment='STA Timing Graph')
        dot.attr(rankdir='LR')

        for node in self.graph.get_all_nodes():
            self._add_node_to_graph(dot, node)
            self._add_edges_to_graph(dot, node)

        try:
            dot.render(output_file, view=False, format='png')
            print(f"Graph rendered to {output_file}.png")
        except Exception as e:
            print(f"Error rendering graph: {e}")

    def _add_node_to_graph(self, dot, node):
        # Color code: Inputs (green/blue), Outputs (red), Others (white)
        if node.type == "port":
            color = 'lightblue'
        else:
            color = 'white'
            
        label = f"{node.name}\nAT: {node.at:.2f}\nSlack: {node.slack:.2f}"
        dot.node(node.name, label, style='filled', fillcolor=color)

    def _add_edges_to_graph(self, dot, node):
        for target, delay, edge_type in node.edges:
            style = 'solid' if edge_type == 'net' else 'dashed'
            dot.edge(node.name, target.name, label=f"{delay:.2f}", style=style)
