# 2. Regex 解析器與圖形結構

[< 上一章](01_structure.md) | [回目錄](../../learning_guide_for_cpp.md) | [下一章 >](03_analysis.md)

本章節介紹如何使用 C++ 解析 Verilog 並建立時序圖。

## 2.1 記憶體管理 (`src/Graph.cpp`)

C++ 需要手動管理記憶體。我們在 `Graph` 類別中使用 `std::map<string, Node*>` 儲存節點指標，並在解構子 (Destructor) 中釋放記憶體。

```cpp
Graph::~Graph() {
    for (auto const& [name, node] : nodes) {
        delete node; // 釋放 Node 物件
    }
}
```

`Node` 結構體使用 `std::vector<Edge>` 儲存邊，這裡 `Edge` 是值類型 (Value Type)，但它包含指向目標節點的指標 `Node* target`。

## 2.2 正則表達式解析 (`src/Parser.cpp`)

不同於 Python 版本使用完整的 Parser，C++ 版本針對本專案的 Verilog 子集，使用了 `std::regex` 進行快速解析。

### 解析實例 (Instance)

```cpp
// 匹配模式：CellType instName (.Pin(Net), ...);
std::regex instRegex(R"(^\s*(\w+)\s+(\w+)\s*\((.*)\)\s*;)");

if (std::regex_search(line, match, instRegex)) {
    std::string cellType = match[1];
    std::string instName = match[2];
    std::string content = match[3]; # 括號內的內容
    
    // 進一步解析 Pin 連接：.Pin(Net)
    std::regex pinRegex(R"(\.(\w+)\s*\(([^)]+)\))");
    // 使用 sregex_iterator 迭代所有匹配的 Pin
    auto pins_begin = std::sregex_iterator(content.begin(), content.end(), pinRegex);
    // ...
}
```

### 處理連接

邏輯與 Python 版本一致：
1.  讀取 Library 資訊。
2.  建立 Pin Node。
3.  根據 `is_input` / `is_output` 將 Pin 加入 `net_loads` 或 `net_drivers`。
4.  建立內部時序弧 (Internal Edges)。

```cpp
// 連接 Net delay
for (auto const& [net, drivers] : net_drivers) {
    // ... 計算 Fanout Delay ...
    for (Node* driver : drivers) {
        for (Node* load : loads) {
            driver->addEdge(load, delay, "net");
        }
    }
}
```
