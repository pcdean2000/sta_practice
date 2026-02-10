# C++ STA Engine Learning Guide

這份文件旨在引導您理解 C++ 版本的靜態時序分析 (STA) 引擎實作細節。

## 章節導覽

1.  **[專案架構與建置](doc/cpp/01_structure.md)** (`Makefile`, `src/Report.cpp`)
    - 解說檔案結構、相依套件 (`nlohmann/json`)。
    - 解說 Makefile 編譯流程與報表生成。

2.  **[Regex 解析器與圖形結構](doc/cpp/02_parser_graph.md)** (`src/Parser.cpp`, `src/Graph.cpp`)
    - 解說如何使用 C++ `std::regex` 解析 Verilog 語法。
    - 解說 C++ 指標與記憶體管理在圖形結構中的應用。

3.  **[時序分析引擎](doc/cpp/03_analysis.md)** (`src/Analysis.cpp`, `src/main.cpp`)
    - 解說 Arrival Time (AT) 的傳播邏輯。
    - 解說 Required Time (RT) 的計算邏輯。
    - 解說 Slack 的計算。

## 專案架構概覽

```
.
├── [Makefile](Makefile)             # 編譯腳本
├── [include/](include)             # 第三方套件 (json.hpp)
├── src/                 # 核心原始碼
│   ├── [main.cpp](src/main.cpp)         # 程式入口
│   ├── [Graph.hpp/cpp](src/Graph.cpp)    # 圖形資料結構
│   ├── [Parser.hpp/cpp](src/Parser.cpp)   # Verilog 解析器
│   ├── [Analysis.hpp/cpp](src/Analysis.cpp) # 分析邏輯
│   ├── [Report.hpp/cpp](src/Report.cpp)   # 報表產生
│   └── [Config.hpp](src/Config.hpp)       # 設定檔讀取
```

建議您依照章節順序閱讀，並搭配原始碼進行對照。
