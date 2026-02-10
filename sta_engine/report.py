import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class ReportGenerator:
    """Generates a Markdown report for STA analysis results."""

    def __init__(self, design_path: str, config: Dict[str, Any], worst_slack: float, worst_node: Optional[str], results: List[Dict[str, Any]]):
        self.design_path = design_path
        self.config = config
        self.worst_slack = worst_slack
        self.worst_node = worst_node
        self.results = results
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate(self, output_path: str = "sta_report.md"):
        """Generates the Markdown report at the specified path."""
        try:
            with open(output_path, 'w') as f:
                f.write(self._generate_header())
                f.write(self._generate_executive_summary())
                f.write(self._generate_configuration_section())
                f.write(self._generate_critical_paths_section())
                f.write(self._generate_footer())
            
            print(f"Report generated at: {os.path.abspath(output_path)}")
        except IOError as e:
            print(f"Error writing report to {output_path}: {e}")

    def _generate_header(self) -> str:
        return (
            f"# STA Analysis Report\n\n"
            f"**Generated on:** {self.timestamp}\n\n"
        )

    def _generate_executive_summary(self) -> str:
        status = "MET" if self.worst_slack >= 0 else "VIOLATED"
        status_icon = "✅" if status == "MET" else "❌"
        
        summary = (
            "## 1. Executive Summary\n\n"
            f"- **Design:** `{self.design_path}`\n"
            f"- **Timing Status:** {status_icon} **{status}**\n"
            f"- **Worst Slack:** `{self.worst_slack:+.4f} ns`\n"
        )
        
        if self.worst_node:
            summary += f"- **Critical Node:** `{self.worst_node}`\n"
        
        return summary + "\n"

    def _generate_configuration_section(self) -> str:
        constraints = self.config.get('timing_constraints', {})
        return (
            "## 2. Configuration\n\n"
            "| Parameter | Value |\n"
            "| :--- | :--- |\n"
            f"| Clock Period | `{constraints.get('clock_period', 'N/A')} ns` |\n"
            f"| Clock Uncertainty | `{constraints.get('clock_uncertainty', 'N/A')} ns` |\n"
            f"| Input Delay | `{constraints.get('input_delay', 'N/A')} ns` |\n"
            f"| Output Delay | `{constraints.get('output_delay', 'N/A')} ns` |\n"
            "\n"
        )

    def _generate_critical_paths_section(self) -> str:
        content = (
            "## 3. Top Critical Paths\n\n"
            "The following table shows the top timing paths (up to 20 worst violations).\n\n"
            "| Node | AT (ns) | RT (ns) | Slack (ns) | Status |\n"
            "| :--- | :---: | :---: | :---: | :---: |\n"
        )
        
        # Sort results by slack (ascending) to show worst paths first
        sorted_results = sorted(self.results, key=lambda x: x['slack'])
        top_results = sorted_results[:20]

        for res in top_results:
            status_str = "MET" if res['slack'] >= 0 else "VIOLATED"
            icon = "✅" if res['slack'] >= 0 else "❌"
            
            # Highlight slack in bold
            content += (
                f"| `{res['node']}` | "
                f"{res['at']:.4f} | "
                f"{res['rt']:.4f} | "
                f"**{res['slack']:+.4f}** | "
                f"{icon} {status_str} |\n"
            )
            
        return content + "\n"

    def _generate_footer(self) -> str:
        return "---\n*End of Report*\n"
