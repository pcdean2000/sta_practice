# 3. 時序分析引擎

[< 上一章](02_parser_graph.md) | [回目錄](../../learning_guide_for_cpp.md)

本章節介紹 `src/Analysis.cpp` 中的時序分析演算法。

## 3.1 拓排排序 (Topological Sort)

為了正確傳播 Arrival Time，我們使用拓排排序。C++ 實作使用了 `std::queue` 與 `inDegree` 映射表。

```cpp
void Analysis::propagateArrivalTimes() {
    // 1. 計算 In-Degree
    std::map<Node*, int> inDegree;
    for (Node* n : nodes) {
        for (auto& edge : n->edges) {
            inDegree[edge.target]++;
        }
    }

    // 2. 將 In-Degree 為 0 的節點加入 Queue
    std::queue<Node*> q;
    for (Node* n : nodes) {
        if (inDegree[n] == 0) q.push(n);
    }
    
    // ... 迴圈處理 ...
}
```

## 3.2 傳播 Arrival Time

在拓排順序中，我們確保處理某個節點時，其所有前驅節點的 AT 都已計算完畢。

```cpp
// 傳播邏輯
for (Node* u : topoOrder) {
    if (u->at == -1.0) continue; // Skip 未初始化的節點

    for (auto& edge : u->edges) {
        Node* v = edge.target;
        double newAt = u->at + edge.delay;
        
        // Max (Latest) Arrival Time
        if (newAt > v->at) {
            v->at = newAt;
        }
    }
}
```

## 3.3 計算與回報

最後計算 Slack 並收集結果。

```cpp
std::vector<AnalysisResult> Analysis::calculateSlack(double& worstSlack, std::string& worstNode) {
    // ...
    double slack = n->rt - n->at;
    
    // 使用結構體儲存結果，方便排序與回報
    results.push_back({n->name, n->at, n->rt, slack, status});
    // ...
}
```

這些結果隨後會被傳遞給 `Report` 類別進行輸出。
