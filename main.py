import argparse
import json
import sys
import os
from sta_engine.parser import VerilogParser
from sta_engine.analysis import TimingAnalyzer

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Static Timing Analysis (STA) Engine")
    parser.add_argument("--design", required=True, help="Path to Verilog design file")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    parser.add_argument("--verbose", action="store_true", help="Print detailed node information")
    parser.add_argument("--report", help="Path to output Markdown report file")

    args = parser.parse_args()

    # 1. Load Config
    try:
        config = load_config(args.config)
        print(f"Loaded configuration from {args.config}")
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

    # 2. Parse Design & Build Graph
    try:
        vparser = VerilogParser(config['library'])
        graph = vparser.parse(args.design)
        print(f"Graph built successfully: {graph.summary()}")
    except Exception as e:
        if "No such file or directory: 'iverilog'" in str(e):
            print("\nError: 'iverilog' (Icarus Verilog) is not installed or not in PATH.")
            print("Pyverilog requires Icarus Verilog to parse designs.")
            print("Please install it using:")
            print("  - Linux (Debian/Ubuntu): sudo apt-get install iverilog")
            print("  - Windows: Install from https://bleyer.org/icarus/")
            print("  - macOS: brew install icarus-verilog")
        else:
            print(f"Error parsing design: {e}")
        sys.exit(1)

    # 3. Running Analysis
    analyzer = TimingAnalyzer(graph, config['timing_constraints'], config['library'])
    worst_slack, worst_node, results = analyzer.run_analysis() # Assuming this method exists and returns these

    # 4. Report
    print("\n--- Timing Analysis Report ---")
    print(f"Design: {args.design}")
    print(f"Clock Period: {config['timing_constraints']['clock_period']} ns")
    
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

    # 5. Generate Markdown Report
    if args.report:
        from sta_engine.report import ReportGenerator
        generator = ReportGenerator(args.design, config, worst_slack, worst_node, results)
        generator.generate(args.report)

if __name__ == "__main__":
    main()
