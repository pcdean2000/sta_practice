#ifndef REPORT_HPP
#define REPORT_HPP

#include "Analysis.hpp"
#include "Config.hpp"
#include <string>
#include <vector>

class Report {
private:
    std::string designPath;
    Config& config;
    double worstSlack;
    std::string worstNode;
    std::vector<AnalysisResult> results;

    std::string getCurrentTime();

public:
    Report(std::string design, Config& c, double ws, std::string wn, std::vector<AnalysisResult> res);
    void generate(const std::string& outputPath);
};

#endif // REPORT_HPP
