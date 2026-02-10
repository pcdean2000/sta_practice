import argparse
import json
import sys
import os
from typing import Dict, Any

from sta_engine.parser import VerilogParser
from sta_engine.analysis import TimingAnalyzer
from sta_engine.report import ReportGenerator
from sta_engine.visualizer import GraphVisualizer

def load_config(config_path: str) -> Dict[str, Any]:
    """Loads JSON configuration from the given path."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse configuration file '{config_path}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Static Timing Analysis (STA) Engine")
    parser.add_argument("--design", required=True, help="Path to Verilog design file")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    parser.add_argument("--verbose", action="store_true", help="Print detailed node information")
    parser.add_argument("--report", help="Output Markdown report file")
    parser.add_argument("--plot", help="Output Graph visualization file (PNG)", default=None)

    args = parser.parse_args()

    # 1. Load Config
    config = load_config(args.config)
    print(f"Loaded configuration from {args.config}")

    # 2. Parse Design & Build Graph
    try:
        vparser = VerilogParser(config['library'])
        graph = vparser.parse(args.design)
        print(f"Graph built successfully: {graph.summary()}")
    except Exception as e:
        print(f"Error during parsing: {e}")
        # Hint for common Icarus Verilog missing error
        if "No such file or directory: 'iverilog'" in str(e):
             print("\nHint: 'iverilog' (Icarus Verilog) seems to be missing. It is required for parsing.")
        sys.exit(1)

    # 3. Plot Graph if requested
    if args.plot:
        visualizer = GraphVisualizer(graph)
        visualizer.plot(args.plot)

    # 4. Run Analysis
    try:
        analyzer = TimingAnalyzer(graph, config['timing_constraints'], config['library'])
        worst_slack, worst_node, results = analyzer.run_analysis()
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

    # 5. Console Output
    print("\n--- Timing Analysis Report ---")
    print(f"Design: {args.design}")
    print(f"Clock Period: {config['timing_constraints'].get('clock_period', 'N/A')} ns")
    
    if args.verbose:
        print("\n{:<20} {:<10} {:<10} {:<10} {:<10}".format("Node", "AT", "RT", "Slack", "Status"))
        print("-" * 65)
        for res in results:
            print(f"{res['node']:<20} {res['at']:<10.4f} {res['rt']:<10.4f} {res['slack']:<10.4f} {res['status']}")

    print("\n--- Final Summary ---")
    status = "MET" if worst_slack >= 0 else "VIOLATED"
    print(f"Timing Status: {status}")
    print(f"Worst Slack:   {worst_slack:+.4f} ns")
    if worst_node:
        print(f"Critical Node: {worst_node}")

    # 6. Generate Markdown Report
    if args.report:
        generator = ReportGenerator(args.design, config, worst_slack, worst_node, results)
        generator.generate(args.report)

if __name__ == "__main__":
    main()
