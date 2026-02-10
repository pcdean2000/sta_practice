#ifndef GRAPH_HPP
#define GRAPH_HPP

#include <string>
#include <vector>
#include <map>
#include <iostream>

struct Node;

struct Edge {
    Node* target;
    double delay;
    std::string type; // "internal", "net", etc.
};

struct Node {
    std::string name;
    std::string type; // "port", "pin", "net" (maybe?)
    std::vector<Edge> edges;
    
    // STA attributes
    double at = -1.0;
    double rt = 999.0;
    double slack = 0.0;

    Node(std::string n, std::string t) : name(n), type(t) {}
    
    void addEdge(Node* target, double delay, std::string type);
};

class Graph {
private:
    std::map<std::string, Node*> nodes;

public:
    ~Graph(); 
    Node* getOrCreateNode(const std::string& name, const std::string& type = "pin");
    Node* getNode(const std::string& name);
    std::vector<Node*> getAllNodes();
    
    // For debugging
    void printSummary();
};

#endif // GRAPH_HPP
