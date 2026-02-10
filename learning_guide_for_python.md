# Python STA Engine Learning Guide

這份文件旨在引導您理解 Python 版本的靜態時序分析 (STA) 引擎實作細節。

## 章節導覽

1.  **[解析器與圖形結構](doc/python/01_parser_graph.md)** (`sta_engine/parser.py`, `sta_engine/graph.py`)
    - 解說如何解析 Verilog 網表 (Netlist)。
    - 解說如何建立時序圖 (Timing Graph)。

2.  **[時序分析引擎](doc/python/02_analysis.md)** (`sta_engine/analysis.py`)
    - 解說 Arrival Time (AT) 的傳播邏輯。
    - 解說 Required Time (RT) 的計算邏輯。
    - 解說 Slack 的計算與 Critical Path 判定。

3.  **[主程式與報表生成](doc/python/03_main.md)** (`main.py`, `sta_engine/report.py`)
    - 解說程式進入點與參數處理。
    - 解說 Markdown 報表生成邏輯。

## 專案架構概覽

```
.
├── config/           # 時序約束與元件庫設定
├── design/           # Verilog 設計檔
├── sta_engine/       # 核心模組
│   ├── [graph.py](sta_engine/graph.py)      # 圖形結構
│   ├── [parser.py](sta_engine/parser.py)     # 解析器
│   ├── [analysis.py](sta_engine/analysis.py)   # 分析邏輯
│   └── [report.py](sta_engine/report.py)     # 報表產生
└── [main.py](main.py)           # 執行入口
```

建議您依照章節順序閱讀，並搭配原始碼進行對照。
