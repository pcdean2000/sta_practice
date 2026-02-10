import collections

class TimingAnalyzer:
    """Performs STA on the graph."""
    def __init__(self, graph, constraints, library):
        self.graph = graph
        self.constraints = constraints
        self.lib = library

    def run_analysis(self):
        self._propagate_arrival_times()
        self._calculate_required_times()
        return self._calculate_slack()

    def _propagate_arrival_times(self):
        print("Propagating Arrival Times...")
        nodes = self.graph.get_all_nodes()
        
        # Initialize
        for node in nodes:
            node.at = -1.0
            
        # Set Start Points
        start_nodes = []
        for node in nodes:
            # DFF Outputs (Q)
            if node.name.endswith("/Q") and "reg_" in node.name: # Simple heuristic
                node.at = self.lib['cells']['DFF']['delay_clk_q']
                start_nodes.append(node)
            
            # Primary Inputs
            # In a robust tool, we'd check if node type is 'port' and is a driver
            # Here we assume ports with input delay
            if node.type == "port" and not node.edges: # Rough check for input port (it drives, doesn't receive)
                 # Actually, input ports drive nets, so they HAVE edges. 
                 # Let's rely on name/config or explicit list if available.
                 # For now, if it's in net_drivers but NOT in any destination of edges? No.
                 # Let's use the explicit list from constraints if possible, or simple heuristic
                 pass
            if node.name in ["rst"] or "data_in" in node.name:
                node.at = self.constraints['input_delay']
                start_nodes.append(node)

        # Topological Sort
        in_degree = collections.defaultdict(int)
        for node in nodes:
            for target, _, _ in node.edges:
                in_degree[target] += 1
        
        queue = collections.deque([n for n in nodes if in_degree[n] == 0])
        topo_order = []
        
        while queue:
            node = queue.popleft()
            topo_order.append(node)
            for target, delay, _ in node.edges:
                in_degree[target] -= 1
                if in_degree[target] == 0:
                    queue.append(target)
                    
        # Propagate
        for node in topo_order:
            if node.at == -1.0: continue
            for target, delay, _ in node.edges:
                new_at = node.at + delay
                if new_at > target.at:
                    target.at = new_at

    def _calculate_required_times(self):
        print("Calculating Required Times...")
        period = self.constraints['clock_period']
        uncertainty = self.constraints['clock_uncertainty']
        output_delay = self.constraints['output_delay']
        
        for node in self.graph.get_all_nodes():
            # DFF Inputs (D)
            if node.name.endswith("/D") and "reg_" in node.name:
                setup = self.lib['cells']['DFF']['setup']
                node.rt = period - setup - uncertainty
            
            # Primary Outputs
            if node.name == "sum_out":
                node.rt = period - output_delay - uncertainty

    def _calculate_slack(self):
        print("Calculating Slack...")
        worst_slack = 999.0
        worst_node = None
        results = []
        
        for node in self.graph.get_all_nodes():
            if node.rt != 999.0:
                if node.at == -1.0:
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
