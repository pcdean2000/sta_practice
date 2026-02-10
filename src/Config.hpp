#ifndef CONFIG_HPP
#define CONFIG_HPP

#include <string>
#include <fstream>
#include <iostream>
#include "json.hpp"

using json = nlohmann::json;

class Config {
public:
    json data;

    bool load(const std::string& path) {
        std::ifstream f(path);
        if (!f.is_open()) {
            std::cerr << "Error: Could not open config file " << path << std::endl;
            return false;
        }
        try {
            f >> data;
        } catch (json::parse_error& e) {
            std::cerr << "Error: Parse error in " << path << ": " << e.what() << std::endl;
            return false;
        }
        return true;
    }

    double getClockPeriod() {
        return data["timing_constraints"]["clock_period"];
    }

    double getClockUncertainty() {
        return data["timing_constraints"]["clock_uncertainty"];
    }

    double getInputDelay() {
        return data["timing_constraints"]["input_delay"];
    }
    
    double getOutputDelay() {
        return data["timing_constraints"]["output_delay"];
    }

    json getLibrary() {
        return data["library"];
    }
};

#endif // CONFIG_HPP
