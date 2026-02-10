# Python STA Engine Learning Guide

這份文件旨在引導您理解 Python 版本的靜態時序分析 (STA) 引擎實作細節。我們將以 `clean code` 原則重構後的程式碼為基礎進行解說。

## 範例設計: 4-bit Accumulator

本專案使用一個簡單的 4-bit 累加器 (`accumulator.v`) 作為範例。
以下是該設計的時序圖 (Timing Graph) 結構：

```mermaid
graph LR
    subgraph Inputs
        clk((clk))
        rst((rst))
        data_in_0((data_in[0]))
        data_in_1((data_in[1]))
        data_in_2((data_in[2]))
        data_in_3((data_in[3]))
    end

    subgraph "Input Registers (Reg B)"
        reg_b0_D[reg_b0/D]
        reg_b0_Q[reg_b0/Q]
        reg_b1_D[reg_b1/D]
        reg_b1_Q[reg_b1/Q]
        reg_b2_D[reg_b2/D]
        reg_b2_Q[reg_b2/Q]
        reg_b3_D[reg_b3/D]
        reg_b3_Q[reg_b3/Q]
    end

    subgraph "Adder Logic (Bit 0)"
        x0_A[x0/A]
        x0_B[x0/B]
        x0_Y[x0/Y]
        a0_A[a0/A]
        a0_B[a0/B]
        a0_Y[a0/Y]
    end

    subgraph "Accumulator Registers (Reg Sum)"
        reg_sum0_D[reg_sum0/D]
        reg_sum0_Q[reg_sum0/Q]
        reg_sum1_D[reg_sum1/D]
        reg_sum1_Q[reg_sum1/Q]
        reg_sum2_D[reg_sum2/D]
        reg_sum2_Q[reg_sum2/Q]
        reg_sum3_D[reg_sum3/D]
        reg_sum3_Q[reg_sum3/Q]
    end
    
    subgraph Outputs
        sum_out_0((sum_out[0]))
        sum_out_1((sum_out[1]))
        sum_out_2((sum_out[2]))
        sum_out_3((sum_out[3]))
    end

    %% Connections for Bit 0
    data_in_0 --> reg_b0_D
    
    %% Reg B -> Adder
    reg_b0_Q --> x0_B
    reg_b0_Q --> a0_B
    
    %% Reg Sum -> Adder (Feedback)
    reg_sum0_Q --> x0_A
    reg_sum0_Q --> a0_A
    reg_sum0_Q --> sum_out_0

    %% Adder Logic
    x0_Y --> reg_sum0_D
    a0_Y --> c0((Carry 0))

    %% Connections for other bits (Simplified)
    data_in_1 --> reg_b1_D
    data_in_2 --> reg_b2_D
    data_in_3 --> reg_b3_D
    
    reg_b1_Q --> |Logic| reg_sum1_D
    reg_b2_Q --> |Logic| reg_sum2_D
    reg_b3_Q --> |Logic| reg_sum3_D
    
    c0 --> |Carry| reg_sum1_D
    
    reg_sum1_Q --> sum_out_1
    reg_sum2_Q --> sum_out_2
    reg_sum3_Q --> sum_out_3

    classDef reg fill:#f9f,stroke:#333,stroke-width:2px;
    class reg_b0_D,reg_b0_Q,reg_sum0_D,reg_sum0_Q,reg_b1_D,reg_b1_Q,reg_sum1_D,reg_sum1_Q reg;
```

---

## 程式架構 (Clean Code Refactored)

本專案經過重構，將不同的職責分離到獨立的模組中，以符合單一職責原則 (SRP)。

1.  **[解析與建模](doc/python/01_parser_graph.md)**
    -   `sta_engine/graph.py`: 定義圖形結構。
        -   **`Node` (Dataclass)**: 代表電路中的 Pin 或 Port。使用 `dataclass` 讓程式碼更簡潔，並具備型別提示。
        -   **`Graph`**: 管理所有的節點與連線。
    -   `sta_engine/parser.py`: 負責解析 Verilog 檔案。
        -   **`VerilogParser`**: 封裝了解析邏輯，將 Pyverilog 的 AST 轉換為我們的 `Graph` 結構。

2.  **[視覺化](doc/python/04_visualizer.md)** (New!)
    -   `sta_engine/visualizer.py`: 專門負責將時序圖繪製出來。
        -   **`GraphVisualizer`**: 使用 `graphviz` 函式庫產生 PNG 圖檔。這將繪圖邏輯從 `Graph` 類別中分離出來，使 `Graph` 保持單純。

3.  **[時序分析](doc/python/02_analysis.md)**
    -   `sta_engine/analysis.py`: 核心分析引擎。
        -   **`TimingAnalyzer`**: 
            -   `_propagate_arrival_times()`: 計算訊號到達時間 (AT)。
            -   `_calculate_required_times()`: 計算訊號需求時間 (RT)。
            -   `_calculate_slack()`: 計算 Slack 並判斷是否違反時序 (Timing Violation)。

4.  **[報表生成](doc/python/03_main.md)**
    -   `sta_engine/report.py`: 負責產生易讀的 Markdown 報告。
        -   **`ReportGenerator`**: 將分析結果格式化，包含摘要、設定值與 Critical Paths 列表。

5.  **主程式**
    -   `main.py`: 程式進入點。
        -   負責協調上述模組：讀取設定 -> 解析 -> 繪圖 (可選) -> 分析 -> 產生報告。

## 專案目錄結構

```
.
├── config/             # 時序約束與元件庫設定
├── design/             # Verilog 設計檔
├── sta_engine/         # 核心模組
│   ├── graph.py        # 圖形資料結構 (Dataclasses)
│   ├── parser.py       # Verilog 解析器
│   ├── analysis.py     # 時序分析邏輯
│   ├── report.py       # 文字報表產生器
│   └── visualizer.py   # [New] 圖形視覺化
└── main.py             # 執行入口
```

建議您依照上述順序閱讀原始碼，並嘗試修改 `design/accumulator.v` 或 `config/sta_config.json` 來觀察分析結果的變化。
