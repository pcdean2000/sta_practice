from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import InstanceList
import os
import sys
from .graph import Graph

class VerilogParser:
    """Parses Verilog and builds the STA Graph."""
    def __init__(self, library_config):
        self.lib = library_config
        self.graph = Graph()
        self.net_drivers = {} # NetName -> [Node]
        self.net_loads = {}   # NetName -> [Node]

    def parse(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")
            
        print(f"Parsing Verilog: {file_path}")
        ast, _ = parse([file_path])
        module = ast.description.definitions[0]
        
        # 1. Process Instances
        for item in module.items:
            if isinstance(item, InstanceList):
                for inst in item.instances:
                    self._process_instance(inst)
                    
        # 2. Process Top Ports
        self._process_ports(module)
        
        # 3. Connect Nets
        self._build_net_connections()
        
        return self.graph

    def _process_instance(self, inst):
        cell_type = inst.module
        inst_name = inst.name
        
        if cell_type not in self.lib['cells']:
            print(f"Warning: Unknown cell type {cell_type} for instance {inst_name}")
            return

        cell_info = self.lib['cells'][cell_type]
        
        # Iterate over ports to identify net connections
        for port in inst.portlist:
            pin_name = f"{inst_name}/{port.portname}"
            net_name = self._get_net_name(port.argname)
            
            pin_node = self.graph.get_or_create_node(pin_name, "pin")

            # Determine direction
            is_input = port.portname in cell_info.get('inputs', [])
            is_output = port.portname in cell_info.get('outputs', [])

            if is_input:
                if net_name not in self.net_loads: self.net_loads[net_name] = []
                self.net_loads[net_name].append(pin_node)
            elif is_output:
                if net_name not in self.net_drivers: self.net_drivers[net_name] = []
                self.net_drivers[net_name].append(pin_node)

        # Create Internal Edges (Break Logic Loops at DFF)
        if not cell_info.get('is_seq', False):
            # Combinational
            for out_pin in cell_info['outputs']:
                out_node = self.graph.get_or_create_node(f"{inst_name}/{out_pin}")
                for in_pin in cell_info['inputs']:
                    in_node = self.graph.get_or_create_node(f"{inst_name}/{in_pin}")
                    delay = cell_info['delay']
                    in_node.add_edge(out_node, delay, "internal")
        else:
            # Sequential (Loop Breaking)
            # No internal edge from D to Q
            pass

    def _process_ports(self, module):
        for port in module.portlist.ports:
            first_level = port.first
            if first_level.__class__.__name__ == 'Ioport':
                first = first_level.first
                node = self.graph.get_or_create_node(first.name, "port")
                if first.__class__.__name__ == 'Input':
                     if first.name not in self.net_drivers: self.net_drivers[first.name] = []
                     self.net_drivers[first.name].append(node)
                elif first.__class__.__name__ == 'Output':
                     if first.name not in self.net_loads: self.net_loads[first.name] = []
                     self.net_loads[first.name].append(node)

    def _build_net_connections(self):
        fanout_factor = self.lib.get('wire_load_model', {}).get('fanout_factor', 0.0)
        
        for net_name, drivers in self.net_drivers.items():
            if net_name in self.net_loads:
                loads = self.net_loads[net_name]
                fanout = len(loads)
                delay = fanout * fanout_factor
                
                for driver in drivers:
                    for load in loads:
                        driver.add_edge(load, delay, "net")

    def _get_net_name(self, argname):
        # Helper to handle Pyverilog AST types
        if argname.__class__.__name__ == 'Pointer':
             return f"{argname.var}[{argname.ptr}]"
        elif argname.__class__.__name__ == 'Identifier':
             return f"{argname.name}"
        else:
            return str(argname)
