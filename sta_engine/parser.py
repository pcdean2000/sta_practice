from pyverilog.vparser.parser import parse
from pyverilog.vparser.ast import InstanceList, Description, ModuleDef, Port, Ioport, Input, Output, Pointer, Identifier
import os
from typing import Dict, List, Any, Optional
from .graph import Graph, Node

class VerilogParser:
    """Parses Verilog designs and builds the STA Graph."""
    
    def __init__(self, library_config: Dict[str, Any]):
        self.lib = library_config
        self.graph = Graph()
        self.net_drivers: Dict[str, List[Node]] = {} # NetName -> [Node]
        self.net_loads: Dict[str, List[Node]] = {}   # NetName -> [Node]

    def parse(self, file_path: str) -> Graph:
        """Parses a Verilog file and returns the constructed STA Graph."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{file_path} not found")
            
        print(f"Parsing Verilog: {file_path}")
        try:
            ast, _ = parse([file_path])
            module_def: ModuleDef = ast.description.definitions[0]
            
            self._process_instances(module_def)
            self._process_ports(module_def)
            self._build_net_connections()
            
            return self.graph
        except Exception as e:
            raise RuntimeError(f"Failed to parse Verilog file: {e}") from e

    def _process_instances(self, module_def: ModuleDef):
        """Iterates over all instances in the module and processes them."""
        for item in module_def.items:
            if isinstance(item, InstanceList):
                for inst in item.instances:
                    self._process_single_instance(inst)

    def _process_single_instance(self, inst):
        """Processes a single instance to create nodes and internal edges."""
        cell_type = inst.module
        inst_name = inst.name
        
        if cell_type not in self.lib['cells']:
            print(f"Warning: Unknown cell type {cell_type} for instance {inst_name}")
            return

        cell_info = self.lib['cells'][cell_type]
        self._create_pin_nodes(inst, inst_name, cell_info)
        self._create_internal_timing_arcs(inst_name, cell_info)

    def _create_pin_nodes(self, inst, inst_name: str, cell_info: Dict[str, Any]):
        """Creates graph nodes for instance pins and registers net connections."""
        for port in inst.portlist:
            pin_name = f"{inst_name}/{port.portname}"
            net_name = self._resolve_net_name(port.argname)
            
            pin_node = self.graph.get_or_create_node(pin_name, "pin")

            is_input = port.portname in cell_info.get('inputs', [])
            is_output = port.portname in cell_info.get('outputs', [])

            if is_input:
                self.net_loads.setdefault(net_name, []).append(pin_node)
            elif is_output:
                self.net_drivers.setdefault(net_name, []).append(pin_node)

    def _create_internal_timing_arcs(self, inst_name: str, cell_info: Dict[str, Any]):
        """Creates internal edges based on cell timing arcs."""
        is_sequential = cell_info.get('is_seq', False)
        
        if not is_sequential:
            # Combinational logic: Create arcs from all inputs to all outputs
            delay = cell_info.get('delay', 0.0)
            for out_pin in cell_info.get('outputs', []):
                out_node = self.graph.get_or_create_node(f"{inst_name}/{out_pin}")
                for in_pin in cell_info.get('inputs', []):
                    in_node = self.graph.get_or_create_node(f"{inst_name}/{in_pin}")
                    in_node.add_edge(out_node, delay, "internal")
        else:
            # Sequential logic (DFF): No internal combinational arc from D to Q
            # Timing arcs like clk->Q are handled during analysis/arrival time propagation start points
            pass

    def _process_ports(self, module_def: ModuleDef):
        """Processes top-level module ports."""
        for port in module_def.portlist.ports:
            # Pyverilog AST navigation to find the actual port details
            first_level = port.first
            if isinstance(first_level, Ioport):
                first = first_level.first
                node = self.graph.get_or_create_node(first.name, "port")
                
                if isinstance(first, Input):
                     self.net_drivers.setdefault(first.name, []).append(node)
                elif isinstance(first, Output):
                     self.net_loads.setdefault(first.name, []).append(node)

    def _build_net_connections(self):
        """Creates edges between drivers and loads on the same net."""
        fanout_factor = self.lib.get('wire_load_model', {}).get('fanout_factor', 0.0)
        
        for net_name, drivers in self.net_drivers.items():
            if net_name in self.net_loads:
                loads = self.net_loads[net_name]
                fanout = len(loads)
                delay = fanout * fanout_factor
                
                for driver in drivers:
                    for load in loads:
                        driver.add_edge(load, delay, "net")

    def _resolve_net_name(self, argname: Any) -> str:
        """Resolves the net name from Pyverilog AST nodes."""
        if isinstance(argname, Pointer):
             return f"{argname.var}[{argname.ptr}]"
        elif isinstance(argname, Identifier):
             return f"{argname.name}"
        else:
            return str(argname)
