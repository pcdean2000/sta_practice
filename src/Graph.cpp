#include "Graph.hpp"

void Node::addEdge(Node* target, double delay, std::string type) {
    edges.push_back({target, delay, type});
}

Graph::~Graph() {
    for (auto const& [name, node] : nodes) {
        delete node;
    }
}

Node* Graph::getOrCreateNode(const std::string& name, const std::string& type) {
    if (nodes.find(name) == nodes.end()) {
        nodes[name] = new Node(name, type);
    }
    return nodes[name];
}

Node* Graph::getNode(const std::string& name) {
    if (nodes.find(name) != nodes.end()) {
        return nodes[name];
    }
    return nullptr;
}

std::vector<Node*> Graph::getAllNodes() {
    std::vector<Node*> all_nodes;
    for (auto const& [name, node] : nodes) {
        all_nodes.push_back(node);
    }
    return all_nodes;
}

void Graph::printSummary() {
    std::cout << "Graph Summary: Total Nodes = " << nodes.size() << std::endl;
}
