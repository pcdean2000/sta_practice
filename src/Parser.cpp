#include "Parser.hpp"
#include <sstream>

Parser::Parser(Graph& g, Config& c) : graph(g), config(c) {
    library = config.getLibrary();
}

bool Parser::parse(const std::string& filePath) {
    std::ifstream file(filePath);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open design file " << filePath << std::endl;
        return false;
    }

    std::string line;
    std::smatch match;

    // Regex patterns
    // 1. Input/Output ports: input [3:0] data_in; or input clk;
    std::regex portRegex(R"((input|output)\s+(?:\[\d+:\d+\]\s+)?(\w+)\s*;)");
    
    // 2. Instance: CellType instName (.Pin(Net), ...);
    // Simple regex to catch the line. 
    // Capturing explicit pin mapping requires parsing the content inside ().
    std::regex instRegex(R"(^\s*(\w+)\s+(\w+)\s*\((.*)\)\s*;)");

    // 3. Pin connection: .Pin(Net)
    std::regex pinRegex(R"(\.(\w+)\s*\(([^)]+)\))");

    // 4. Register declaration (ignored for graph, handled via instance logic) but we might need to know if something is a wire or reg?
    // In this structural netlist, mostly wires and instances.

    std::cout << "Parsing Verilog: " << filePath << std::endl;

    while (std::getline(file, line)) {
        // Strip comments // 
        size_t commentPos = line.find("//");
        if (commentPos != std::string::npos) {
            line = line.substr(0, commentPos);
        }

        if (std::regex_search(line, match, portRegex)) {
            std::string direction = match[1];
            std::string name = match[2];
            // Note: Vector ports like [3:0] data_in are treated as single node "data_in" in this simplified parser? 
            // OR we should expand them? 
            // In the Python version: "data_in[0]" is created if referenced.
            // But the port declaration "input [3:0] data_in" creates "data_in" ???
            // Let's check Python parser. It uses Pyverilog which expands things. 
            // For simplicity here, we will create nodes lazily when we see them in instances.
            // But for PRIMARY INPUTS, we need to know they drive nets.
            // Let's defer port creation to connection phase or create generic "port" type.
            // Actually, if we see `input clk`, we know `clk` is a net driver.
            
            // For this practice, we assume scalar or vector nets are handled by name string match.
            // e.g., "data_in[0]" is a distinct name from "data_in[1]".
            // If the line says "input [3:0] data_in", we technically should expand it. 
            // But simplistic regex won't expand. 
            // *Simplification*: We'll assume the netlist uses explicit indices in instances, e.g. .D(data_in[0]).
            // So we treat "data_in[0]" as a net name.
            // We need to mark primary inputs/outputs though.
            
            // If we match "input", we can't easily expand without parsing [3:0].
            // Let's ignore this for now and handle it via `processInstance` and lazy creation, 
            // EXCEPT we need to know what are Primary Inputs for Arrival Time.
            // We can infer Primary Inputs: nodes with 0 in-degree that are not constants? 
            // Or just rely on "input_delay" constraints applied to all inputs?
            
            // Hack for now: We won't strictly validate port directions vs declaraction.
            continue; 
        }

        if (std::regex_search(line, match, instRegex)) {
            std::string cellType = match[1];
            std::string instName = match[2];
            std::string content = match[3];
            
            if (cellType == "module") continue; // Skip module declaration

            std::map<std::string, std::string> connections;
            
            // Parse pin connections .Pin(Net)
            auto pins_begin = std::sregex_iterator(content.begin(), content.end(), pinRegex);
            auto pins_end = std::sregex_iterator();
            
            for (std::sregex_iterator i = pins_begin; i != pins_end; ++i) {
                std::smatch pinMatch = *i;
                connections[pinMatch[1]] = pinMatch[2];
            }
            
            processInstance(cellType, instName, connections);
        }
    }
    
    connectNets();

    return true;
}

void Parser::processInstance(const std::string& cellType, const std::string& instName, const std::map<std::string, std::string>& connections) {
    if (!library["cells"].contains(cellType)) {
        std::cerr << "Warning: Unknown cell type " << cellType << " for instance " << instName << std::endl;
        return;
    }

    // Explicitly convert json value to object (std::map-like access)
    json cellInfo = library["cells"][cellType];
    
    // Process pins
    for (auto const& [pin, net] : connections) {
        std::string pinName = instName + "/" + pin;
        Node* pinNode = graph.getOrCreateNode(pinName, "pin");

        bool isInput = false;
        bool isOutput = false;

        // Check inputs
        for (auto& inp : cellInfo["inputs"]) {
            if (inp.get<std::string>() == pin) isInput = true;
        }
         // Check outputs
        for (auto& outp : cellInfo["outputs"]) {
            if (outp.get<std::string>() == pin) isOutput = true;
        }

        if (isInput) {
            net_loads[net].push_back(pinNode);
        } else if (isOutput) {
            net_drivers[net].push_back(pinNode);
        }
    }

    // Internal Edges
    bool isSeq = false;
    if (cellInfo.contains("is_seq") && cellInfo["is_seq"].get<bool>()) isSeq = true;

    if (!isSeq) {
        double delay = cellInfo["delay"];
        for (auto& outPin : cellInfo["outputs"]) {
            std::string outPinName = instName + "/" + outPin.get<std::string>();
            Node* outNode = graph.getOrCreateNode(outPinName, "pin");

            for (auto& inPin : cellInfo["inputs"]) {
                std::string inPinName = instName + "/" + inPin.get<std::string>();
                Node* inNode = graph.getOrCreateNode(inPinName, "pin");
                
                inNode->addEdge(outNode, delay, "internal");
            }
        }
    }
}

void Parser::connectNets() {
    double fanoutFactor = 0.0;
    if (library.contains("wire_load_model")) {
        fanoutFactor = library["wire_load_model"]["fanout_factor"];
    }

    for (auto const& [net, drivers] : net_drivers) {
        if (net_loads.find(net) != net_loads.end()) {
            std::vector<Node*>& loads = net_loads[net];
            double delay = loads.size() * fanoutFactor;

            for (Node* driver : drivers) {
                for (Node* load : loads) {
                    driver->addEdge(load, delay, "net");
                }
            }
        } else {
            // Net has drivers but no loads (maybe output port?)
            // In this parser, output ports are not explicitly nodes unless we parse "output ..."
            // Ideally we need to create a Port node and connect driver to it.
            // Let's create a "port" node for the net itself if it looks like a port.
            // Or just leave it open. STA usually checks endpoints at DFF/Ports. 
            // If the net name is "sum_out", we want to see it as an endpoint.
            // Let's create a dummy load node for the net if it's potentially an output?
            // "sum_out" is driven by register Q.
            // Let's create a node for the Net itself? No, standard graph is Pin-to-Pin.
            
            // Special handling for output ports:
            // If a generic net has no loads, we treat the net name as a "Output Port Node" 
            // and connect driver to it.
            Node* portNode = graph.getOrCreateNode(net, "port");
            for (Node* driver : drivers) {
                 driver->addEdge(portNode, 0.0, "net"); // Connect driver to output port
            }
            // Mark as port for sure
            portNode->type = "port";
        }
    }
    
    // Handle Input Ports driving loads
    for (auto const& [net, loads] : net_loads) {
        if (net_drivers.find(net) == net_drivers.end()) {
            // Net has loads but no internal drivers -> Driven by Input Port
            Node* portNode = graph.getOrCreateNode(net, "port");
            double delay = loads.size() * fanoutFactor;
            
            for (Node* load : loads) {
                portNode->addEdge(load, delay, "net");
            }
        }
    }
}
