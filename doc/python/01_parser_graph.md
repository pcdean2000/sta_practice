# 1. 解析器與圖形結構

[< 回目錄](../../learning_guide_for_python.md) | [下一章 >](02_analysis.md)

本章節介紹如何將 Verilog 轉換為時序圖 (Timing Graph)。

## 1.1 圖形資料結構 (`sta_engine/graph.py`)

時序圖由 **節點 (Node)** 與 **邊 (Edge)** 組成。

```python
class Node:
    def __init__(self, name, node_type):
        self.name = name       # 節點名稱 (例如: "u1/A")
        self.type = node_type  # 類型 ("pin" 或 "port")
        self.edges = []        # 輸出的邊 (Adjacency List)
        
        # STA 屬性
        self.at = -1.0         # Arrival Time
        self.rt = 999.0        # Required Time
```

`edges` 列表儲存了連向其他節點的資訊，包含 `delay` (延遲) 與 `edge_type` (連線類型：或是內部延遲 `internal` 或繞線延遲 `net`)。

## 1.2 Verilog 解析器 (`sta_engine/parser.py`)

解析器使用 `pyverilog` 套件來讀取 Verilog AST (抽象語法樹)。

### 處理流程

1.  **解析實例 (Instances)**: 走訪 AST 中的所有實例化元件 (如 `DFF`, `AND2`)。
2.  **建立節點**: 為每個實例的 Pin (如 `.A`, `.Y`) 建立 `Node`。
3.  **連接網線 (Nets)**: 根據 Pin 所連接的 net 名稱，將 Driver Pin 連接到 Load Pin。

### 關鍵程式碼：處理實例與內部延遲

在 `_process_instance` 方法中，會根據元件庫 (`library`) 定義，建立元件內部的時序弧 (Timing Arc)。

```python
def _process_instance(self, inst):
    # ... 省略 ...
    cell_info = self.lib['cells'][cell_type]

    # 建立內部邊 (Internal Edges)
    # 組合邏輯元件 (如 XOR, AND) 會有從 Input 到 Output 的延遲
    if not cell_info.get('is_seq', False): # 如果不是循序元件(DFF)
        for out_pin in cell_info['outputs']:
            out_node = self.graph.get_or_create_node(f"{inst_name}/{out_pin}")
            for in_pin in cell_info['inputs']:
                in_node = self.graph.get_or_create_node(f"{inst_name}/{in_pin}")
                delay = cell_info['delay']
                # 建立邊：Input Pin -> Output Pin
                in_node.add_edge(out_node, delay, "internal")
```

**重點**: 對於 DFF (循序元件)，我們**不會**建立從 D 到 Q 的邊，因為時序路徑在此斷開 (Timing Break)，這是 STA 的基本原則。D 端是路徑終點 (Endpoint)，Q 端是新路徑的起點 (Startpoint)。

### 關鍵程式碼：建立網線連接

在 `_build_net_connections` 方法中，會將同一個 Net 的 Driver 連接到所有的 Loads。

```python
def _build_net_connections(self):
    fanout_factor = self.lib.get('wire_load_model', {}).get('fanout_factor', 0.0)
    
    for net_name, drivers in self.net_drivers.items():
        if net_name in self.net_loads:
            loads = self.net_loads[net_name]
            # 簡單的線延遲模型：延遲與 Fanout 成正比
            delay = len(loads) * fanout_factor
            
            for driver in drivers:
                for load in loads:
                    # 建立邊：Driver Pin -> Load Pin
                    driver.add_edge(load, delay, "net")
```
