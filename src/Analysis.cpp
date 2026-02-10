#include "Analysis.hpp"
#include <queue>
#include <algorithm>
#include <iostream>

Analysis::Analysis(Graph& g, Config& c) : graph(g), config(c) {
    library = config.getLibrary();
}

std::vector<AnalysisResult> Analysis::run(double& worstSlack, std::string& worstNode) {
    propagateArrivalTimes();
    calculateRequiredTimes();
    return calculateSlack(worstSlack, worstNode);
}

void Analysis::propagateArrivalTimes() {
    std::cout << "Propagating Arrival Times..." << std::endl;
    auto nodes = graph.getAllNodes();
    
    // Reset AT
    for (Node* n : nodes) n->at = -1.0;

    std::queue<Node*> q;
    std::map<Node*, int> inDegree;

    // Calculate in-degree for topo sort
    // Only count edges that matter for propagation? Graph includes internal and net edges.
    for (Node* n : nodes) inDegree[n] = 0;
    
    for (Node* n : nodes) {
        for (auto& edge : n->edges) {
            inDegree[edge.target]++;
        }
    }

    // Identify start points and seed queue
    for (Node* n : nodes) {
        bool isStartPoint = false;
        
        // DFF Outputs (Q) - Simple heuristic matching Python
        if (n->name.find("/Q") != std::string::npos && n->name.find("reg_") != std::string::npos) {
            n->at = library["cells"]["DFF"]["delay_clk_q"];
            isStartPoint = true;
        }
        
        // Input Ports (checking if type is "port" and no incoming edges or explicitly named)
        // Since my parser sets type="port" for inputs, let's use that.
        // Also check if node is "rst" or "data_in" based on Python logic?
        if (n->type == "port" && inDegree[n] == 0) {
             n->at = config.getInputDelay();
             isStartPoint = true;
        }

        if (isStartPoint) {
            // If it's a start point, it should have initial AT.
            // But for Topo sort, we start with nodes having in-degree 0.
            // Wait, DFF/Q is *internally* a start point but it might not have in-degree 0 in the full graph?
            // Actually DFF/Q has NO incoming edges in our graph because we break loops at DFF!
            // So DFF/Q should have inDegree 0.
        }
    }

    // Topological Sort Queue
    for (Node* n : nodes) {
        if (inDegree[n] == 0) {
            q.push(n);
        }
    }

    std::vector<Node*> topoOrder;
    while (!q.empty()) {
        Node* u = q.front();
        q.pop();
        topoOrder.push_back(u);

        for (auto& edge : u->edges) {
            Node* v = edge.target;
            inDegree[v]--;
            if (inDegree[v] == 0) {
                q.push(v);
            }
        }
    }

    // Propagate
    for (Node* u : topoOrder) {
        if (u->at == -1.0) continue;

        for (auto& edge : u->edges) {
            Node* v = edge.target;
            double newAt = u->at + edge.delay;
            if (newAt > v->at) {
                v->at = newAt;
            }
        }
    }
}

void Analysis::calculateRequiredTimes() {
    std::cout << "Calculating Required Times..." << std::endl;
    double period = config.getClockPeriod();
    double uncertainty = config.getClockUncertainty();
    double outputDelay = config.getOutputDelay();
    double setup = library["cells"]["DFF"]["setup"];

    for (Node* n : graph.getAllNodes()) {
        n->rt = 999.0;
        
        // DFF Inputs (D)
        if (n->name.find("/D") != std::string::npos && n->name.find("reg_") != std::string::npos) {
            n->rt = period - setup - uncertainty;
        }
        
        // Output Ports
        // In Python it checked `n.name == "sum_out"`.
        // In C++ Parser, output ports might be `sum_reg_out[0]` etc. OR explicitly `sum_out` if mapped.
        // My parser logic was: if net has drivers but no loads, make it a port.
        // So `sum_reg_out[0]` would be a port.
        if (n->type == "port") {
             // Heuristic: if it's not an input port (which we set AT for), it's an output port?
             // Or check if it has incoming edges? 
             // Output ports (endpoints) usually have incoming edges and no outgoing (in this graph).
             // But DFF/D also has incoming edges.
             
             // Check if it's an output port by name or just assume all ports that are not inputs?
             // If AT is -1 (was not set as input), treat as output?
             // BUT propagation runs before RT calc. So AT should be valid.
             
             // Let's use name check "sum_" or just apply to all "port" types with valid AT?
             // Actually, apply to all designated output ports.
             // Given limitations, let's just check if it's "port" and not an input (implied by not having valid AT set by propagated inputs... wait).
             
             // Simple: If `n->edges.empty()` (no outgoing edges) and it's a port?
             if (n->edges.empty() && n->type == "port") {
                 n->rt = period - outputDelay - uncertainty;
             }
        }
    }
}

std::vector<AnalysisResult> Analysis::calculateSlack(double& worstSlack, std::string& worstNode) {
    std::cout << "Calculating Slack..." << std::endl;
    worstSlack = 999.0;
    worstNode = "";
    std::vector<AnalysisResult> results;

    for (Node* n : graph.getAllNodes()) {
        if (n->rt != 999.0 && n->at != -1.0) {
            double slack = n->rt - n->at;
            n->slack = slack;
            
            std::string status = (slack >= 0) ? "MET" : "VIOLATED";
            results.push_back({n->name, n->at, n->rt, slack, status});

            if (slack < worstSlack) {
                worstSlack = slack;
                worstNode = n->name;
            }
        }
    }
    return results;
}
