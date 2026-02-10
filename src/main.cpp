#include <iostream>
#include <string>
#include <vector>
#include "Graph.hpp"
#include "Parser.hpp"
#include "Analysis.hpp"
#include "Report.hpp"
#include "Config.hpp"

void printUsage(const char* progName) {
    std::cout << "Usage: " << progName << " --design <verilog_file> --config <json_config> --report <output_report>\n";
}

int main(int argc, char* argv[]) {
    std::string designPath;
    std::string configPath;
    std::string reportPath = "sta_report_cpp.md";

    // Simple argument parsing
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--design" && i + 1 < argc) {
            designPath = argv[++i];
        } else if (arg == "--config" && i + 1 < argc) {
            configPath = argv[++i];
        } else if (arg == "--report" && i + 1 < argc) {
            reportPath = argv[++i];
        } else if (arg == "--help") {
            printUsage(argv[0]);
            return 0;
        }
    }

    if (designPath.empty() || configPath.empty()) {
        std::cerr << "Error: Missing required arguments.\n";
        printUsage(argv[0]);
        return 1;
    }

    std::cout << "Starting C++ STA Engine...\n";

    // 1. Load Config
    Config config;
    if (!config.load(configPath)) {
        return 1;
    }
    std::cout << "Loaded configuration from " << configPath << "\n";

    // 2. Build Graph
    Graph graph;
    Parser parser(graph, config);
    if (!parser.parse(designPath)) {
        return 1;
    }

    // 3. Run Analysis
    Analysis analysis(graph, config);
    double worstSlack;
    std::string worstNode;
    auto results = analysis.run(worstSlack, worstNode);

    // 4. Report
    std::cout << "\n--- Final Summary ---\n";
    std::string status = (worstSlack >= 0) ? "MET" : "VIOLATED";
    std::cout << "Timing Status: " << status << "\n";
    std::cout << "Worst Slack:   " << worstSlack << " ns\n";
    if (!worstNode.empty()) {
        std::cout << "Critical Node: " << worstNode << "\n";
    }

    Report report(designPath, config, worstSlack, worstNode, results);
    report.generate(reportPath);

    return 0;
}
