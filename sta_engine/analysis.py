from typing import Dict, List, Any, Tuple, Optional
from collections import deque, defaultdict
from .graph import Graph, Node

class TimingAnalyzer:
    """Performs Static Timing Analysis (STA) on the graph."""
    
    def __init__(self, graph: Graph, constraints: Dict[str, float], library: Dict[str, Any]):
        self.graph = graph
        self.constraints = constraints
        self.lib = library

    def run_analysis(self) -> Tuple[float, Optional[str], List[Dict[str, Any]]]:
        """Runs the full timing analysis pipeline."""
        self._propagate_arrival_times()
        self._calculate_required_times()
        return self._calculate_slack()

    def _propagate_arrival_times(self):
        """Propagates Arrival Times (AT) through the graph using topological traversal."""
        print("Propagating Arrival Times...")
        nodes = self.graph.get_all_nodes()
        
        # 1. Initialize and Set Start Points
        self._reset_at(nodes)
        self._apply_input_delays(nodes)
        
        # 2. Topological Sort
        topo_order = self._topological_sort(nodes)
        
        # 3. Propagate Delays
        for node in topo_order:
            if node.at == -1.0: 
                continue
                
            for target_node, delay, _ in node.edges:
                new_at = node.at + delay
                if new_at > target_node.at:
                    target_node.at = new_at

    def _reset_at(self, nodes: List[Node]):
        for node in nodes:
            node.at = -1.0

    def _apply_input_delays(self, nodes: List[Node]):
        """Sets initial arrival times for start points (Inputs, Flip-Flops)."""
        input_delay = self.constraints.get('input_delay', 0.0)
        dff_clk_q = self.lib['cells']['DFF']['delay_clk_q']

        for node in nodes:
            # Start Point: DFF Outputs (Q pin)
            if self._is_dff_output(node):
                node.at = dff_clk_q
            
            # Start Point: Primary Inputs
            # Heuristic: Known input names or simple ports
            if node.type == "port" and node.name in ["rst", "clk"]:
                 # Clock and Reset paths usually handled differently or have 0 specific delay in basic STA
                 # For data path STA, we often care about data inputs
                 pass 
            
            if "data_in" in node.name or node.name == "rst": # Heuristic from original code
                node.at = input_delay

    def _is_dff_output(self, node: Node) -> bool:
        return node.name.endswith("/Q") and "reg_" in node.name

    def _topological_sort(self, nodes: List[Node]) -> List[Node]:
        """Performs consistent topological sort for traversal."""
        in_degree = defaultdict(int)
        for node in nodes:
            for target, _, _ in node.edges:
                in_degree[target] += 1
        
        queue = deque([n for n in nodes if in_degree[n] == 0])
        topo_order = []
        
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            for target, _, _ in node.edges:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
        return topo_order

    def _calculate_required_times(self):
        """Calculates Required Times (RT) based on clock period and constraints."""
        print("Calculating Required Times...")
        period = self.constraints['clock_period']
        uncertainty = self.constraints['clock_uncertainty']
        output_delay = self.constraints['output_delay']
        dff_setup = self.lib['cells']['DFF']['setup']
        
        for node in self.graph.get_all_nodes():
            # End Point: DFF Inputs (D pin)
            if self._is_dff_input(node):
                node.rt = period - dff_setup - uncertainty
            
            # End Point: Primary Outputs
            if node.name == "sum_out": # Specific to example design, should be generalized
                node.rt = period - output_delay - uncertainty

    def _is_dff_input(self, node: Node) -> bool:
         return node.name.endswith("/D") and "reg_" in node.name

    def _calculate_slack(self) -> Tuple[float, Optional[str], List[Dict[str, Any]]]:
        """Calculates slack for valid timing points."""
        print("Calculating Slack...")
        worst_slack = float('inf')
        worst_node = None
        results = []
        
        for node in self.graph.get_all_nodes():
            # Only calculate slack for constrained nodes (where RT is set)
            if node.rt == 999.0 or node.at == -1.0:
                continue
            
            slack = node.rt - node.at
            results.append({
                "node": node.name,
                "at": node.at,
                "rt": node.rt,
                "slack": slack,
                "status": "MET" if slack >= 0 else "VIOLATED"
            })
            
            if slack < worst_slack:
                worst_slack = slack
                worst_node = node.name
                    
        return worst_slack, worst_node, results
