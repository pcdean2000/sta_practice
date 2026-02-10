import os
from datetime import datetime

class ReportGenerator:
    """Generates a Markdown report for STA analysis results."""

    def __init__(self, design_path, config, worst_slack, worst_node, results):
        self.design_path = design_path
        self.config = config
        self.worst_slack = worst_slack
        self.worst_node = worst_node
        self.results = results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(self, output_path="sta_report.md"):
        """Generates the Markdown report."""
        
        with open(output_path, 'w') as f:
            f.write(f"# STA Analysis Report\n\n")
            f.write(f"**Generated on:** {self.timestamp}\n\n")
            
            f.write("## 1. Executive Summary\n\n")
            status = "MET" if self.worst_slack >= 0 else "VIOLATED"
            status_icon = "✅" if status == "MET" else "❌"
            
            f.write(f"- **Design:** `{self.design_path}`\n")
            f.write(f"- **Timing Status:** {status_icon} **{status}**\n")
            f.write(f"- **Worst Slack:** `{self.worst_slack:+.4f} ns`\n")
            if self.worst_node:
                f.write(f"- **Critical Node:** `{self.worst_node}`\n")
            f.write("\n")

            f.write("## 2. Configuration\n\n")
            f.write("| Parameter | Value |\n")
            f.write("| :--- | :--- |\n")
            f.write(f"| Clock Period | `{self.config['timing_constraints']['clock_period']} ns` |\n")
            f.write(f"| Clock Uncertainty | `{self.config['timing_constraints']['clock_uncertainty']} ns` |\n")
            f.write(f"| Input Delay | `{self.config['timing_constraints']['input_delay']} ns` |\n")
            f.write(f"| Output Delay | `{self.config['timing_constraints']['output_delay']} ns` |\n")
            f.write("\n")

            f.write("## 3. Top Critical Paths\n\n")
            f.write("The following table shows the top timing paths (up to 10 worst violations) or all paths if fewer than 10.\n\n")
            
            # Sort results by slack (ascending) to show worst paths first
            sorted_results = sorted(self.results, key=lambda x: x['slack'])
            top_results = sorted_results[:20] 

            f.write("| Node | AT (ns) | RT (ns) | Slack (ns) | Status |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: |\n")
            
            for res in top_results:
                status_str = "MET" if res['slack'] >= 0 else "VIOLATED"
                row_style = "" 
                # Note: Markdown doesn't support row color natively without HTML, 
                # but we can use emoji or bolding.
                icon = "✅" if res['slack'] >= 0 else "❌"
                
                f.write(f"| `{res['node']}` | {res['at']:.4f} | {res['rt']:.4f} | **{res['slack']:+.4f}** | {icon} {status_str} |\n")
            
            f.write("\n")
            f.write("---\n")
            f.write("*End of Report*\n")

        print(f"Report generated at: {os.path.abspath(output_path)}")
