#ifndef ANALYSIS_HPP
#define ANALYSIS_HPP

#include "Graph.hpp"
#include "Config.hpp"
#include <vector>
#include <map>

struct AnalysisResult {
    std::string node;
    double at;
    double rt;
    double slack;
    std::string status;
};

class Analysis {
private:
    Graph& graph;
    Config& config;
    json library;
    
    void propagateArrivalTimes();
    void calculateRequiredTimes();
    std::vector<AnalysisResult> calculateSlack(double& worstSlack, std::string& worstNode);

public:
    Analysis(Graph& g, Config& c);
    std::vector<AnalysisResult> run(double& worstSlack, std::string& worstNode);
};

#endif // ANALYSIS_HPP
