# STA Practice Project

一個基於 Python 與 Pyverilog 的靜態時序分析 (Static Timing Analysis) 練習專案。
本專案演示了如何將 Verilog Netlist 轉換為時序圖 (Timing Graph)，並計算 Arrival Time, Required Time 與 Slack。

## 專案架構

```
.
├── config/
│   └── sta_config.json       # 時序約束 (Clock, IO Delay) 與 元件庫 (Library) 設定
├── design/
│   └── accumulator.v         # Verilog 原始碼 (Design Under Test)
├── sta_engine/               # STA 核心引擎
│   ├── graph.py              # 圖形資料結構 (Node, Edge)
│   ├── parser.py             # 負責解析 Verilog 並建立 Graph
│   └── analysis.py           # 負責計算延遲與傳播時序 (AT, RT, Slack)
├── main.py                   # 程式執行入口
└── README.md                 # 說明文件
```

## 安裝需求

請確保已安裝以下套件：

1.  **uv**: [Install uv](https://github.com/astral-sh/uv)
2.  **Icarus Verilog**: Pyverilog 需要依賴 `iverilog` 進行預處理。
    - Windows 下請安裝 [Icarus Verilog for Windows](https://bleyer.org/icarus/) 並加入 PATH。
    - Linux: `sudo apt-get install iverilog`

安裝相依套件：

```bash
uv sync
```

## 如何執行

在專案根目錄下，使用 `uv run` 執行 `main.py`：

```bash
# 基本執行
uv run main.py --design design/accumulator.v --config config/sta_config.json

# 顯示詳細節點資訊 (Debug 用)
uv run main.py --design design/accumulator.v --config config/sta_config.json --verbose

# 產生 Markdown 報告
uv run main.py --design design/accumulator.v --config config/sta_config.json --report sta_report.md
```

## C++ 版本

本專案亦提供 C++ 實作版本 (位於 `src/` 目錄)。

### 編譯與執行

使用 `make` 進行編譯與執行：

```bash
# 編譯
make

# 執行 (預設執行 accumulator.v 分析)
make run

# 清除編譯檔案
make clean
```

執行後會產生 `sta_report_cpp.md` 報告。

## 設定說明 (`config/sta_config.json`)

此檔案控制所有的時序參數，無需修改程式碼即可調整測試條件。

-   `timing_constraints`:
    -   `clock_period`: 時脈週期 (ns)。例如設為 `0.25` 可模擬 4GHz 高頻。
    -   `clock_uncertainty`: 時脈抖動 (Jitter)。
    -   `input_delay` / `output_delay`: IO 邊界限制。
-   `library`:
    -   `cells`: 定義標準元件 (AND, OR, DFF 等) 的延遲參數。
    -   `wire_load_model`: 定義繞線延遲估算模型 (如 Fanout 係數)。

## 執行結果範例

```text
--- Timing Analysis Report ---
Design: design/accumulator.v
Clock Period: 1.0 ns

--- Final Summary ---
Timing Status: MET
Worst Slack:   +0.6750 ns
Critical Node: reg_sum1/D
```
