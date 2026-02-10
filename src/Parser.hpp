#ifndef PARSER_HPP
#define PARSER_HPP

#include <string>
#include <regex>
#include <iostream>
#include <fstream>
#include <set>
#include "Graph.hpp"
#include "Config.hpp"

class Parser {
private:
    Graph& graph;
    Config& config;
    json library;
    
    // Net connectivity tracking
    std::map<std::string, std::vector<Node*>> net_drivers;
    std::map<std::string, std::vector<Node*>> net_loads;

    void processInstance(const std::string& cellType, const std::string& instName, const std::map<std::string, std::string>& connections);
    void connectNets();

public:
    Parser(Graph& g, Config& c);
    bool parse(const std::string& filePath);
};

#endif // PARSER_HPP
