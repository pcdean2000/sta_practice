#include "Report.hpp"
#include <fstream>
#include <iostream>
#include <algorithm>
#include <ctime>
#include <iomanip>

Report::Report(std::string design, Config& c, double ws, std::string wn, std::vector<AnalysisResult> res)
    : designPath(design), config(c), worstSlack(ws), worstNode(wn), results(res) {}

std::string Report::getCurrentTime() {
    auto now = std::time(nullptr);
    auto tm = *std::localtime(&now);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S");
    return oss.str();
}

void Report::generate(const std::string& outputPath) {
    std::ofstream f(outputPath);
    if (!f.is_open()) {
        std::cerr << "Error: Could not open report file " << outputPath << std::endl;
        return;
    }

    f << "# STA Analysis Report (C++)\n\n";
    f << "**Generated on:** " << getCurrentTime() << "\n\n";

    f << "## 1. Executive Summary\n\n";
    std::string status = (worstSlack >= 0) ? "MET" : "VIOLATED";
    std::string icon = (worstSlack >= 0) ? "✅" : "❌";
    
    f << "- **Design:** `" << designPath << "`\n";
    f << "- **Timing Status:** " << icon << " **" << status << "**\n";
    f << "- **Worst Slack:** `" << std::showpos << std::fixed << std::setprecision(4) << worstSlack << " ns`\n";
    if (!worstNode.empty()) {
        f << "- **Critical Node:** `" << worstNode << "`\n";
    }
    f << "\n";

    f << "## 2. Configuration\n\n";
    f << "| Parameter | Value |\n";
    f << "| :--- | :--- |\n";
    f << "| Clock Period | `" << std::noshowpos << config.getClockPeriod() << " ns` |\n";
    f << "| Clock Uncertainty | `" << config.getClockUncertainty() << " ns` |\n";
    f << "| Input Delay | `" << config.getInputDelay() << " ns` |\n";
    f << "| Output Delay | `" << config.getOutputDelay() << " ns` |\n";
    f << "\n";

    f << "## 3. Top Critical Paths\n\n";
    f << "The following table shows the top timing paths (up to 20 worst violations).\n\n";

    // Sort by slack (ascending)
    std::sort(results.begin(), results.end(), [](const AnalysisResult& a, const AnalysisResult& b) {
        return a.slack < b.slack;
    });

    f << "| Node | AT (ns) | RT (ns) | Slack (ns) | Status |\n";
    f << "| :--- | :---: | :---: | :---: | :---: |\n";

    int limit = 20;
    for (const auto& res : results) {
        if (limit-- <= 0) break;
        std::string rowIcon = (res.slack >= 0) ? "✅" : "❌";
        f << "| `" << res.node << "` | " 
          << std::fixed << std::setprecision(4) << res.at << " | "
          << res.rt << " | **" << std::showpos << res.slack << "** | " 
          << rowIcon << " " << res.status << " |\n";
    }

    f << "\n---\n*End of Report*\n";
    std::cout << "Report generated at: " << outputPath << std::endl;
}
