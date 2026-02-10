# 2. 時序分析引擎

[< 上一章](01_parser_graph.md) | [回目錄](../../learning_guide_for_python.md) | [下一章 >](03_main.md)

本章節介紹如何計算 Arrival Time (AT), Required Time (RT) 與 Slack。程式碼位於 `sta_engine/analysis.py`。

## 2.1 傳播 Arrival Time (AT)

AT 代表訊號到達某點的**最晚時間**。計算方式是從起點 (Startpoints) 開始，沿著邊累加延遲，取最大值 (Max Delay)。

### 步驟

1.  **初始化**: 將所有節點 AT 設為 -1。
2.  **設定起點**:
    - **Primary Inputs**: 從約束檔讀取 `input_delay`。
    - **DFF Outputs (Q)**: 設為 `clock_to_q` 延遲。

```python
# 設定起點 AT
for node in nodes:
    if node.name.endswith("/Q") and "reg_" in node.name:
        node.at = self.lib['cells']['DFF']['delay_clk_q']
        start_nodes.append(node)
```

3.  **拓排排序 (Topological Sort)**: 確保在計算節點 AT 時，其前驅節點的 AT 都已計算完成。
4.  **傳播計算**:

```python
# 依拓樸順序遊訪
for node in topo_order:
    if node.at == -1.0: continue
    for target, delay, _ in node.edges:
        new_at = node.at + delay
        # 取最大值 (Latest Arrival Time)
        if new_at > target.at:
            target.at = new_at
```

## 2.2 計算 Required Time (RT)

RT 代表訊號**必須**到達某點的最晚時間，否則會發生 Setup Violation。

### 步驟

1.  **初始化**: 將所有節點 RT 設為無限大 (999.0)。
2.  **設定終點 (Endpoints)**:
    - **Primary Outputs**: `Period - Output_Delay - Uncertainty`。
    - **DFF Inputs (D)**: `Period - Setup_Time - Uncertainty`。

```python
# 設定 DFF Input 的 RT
if node.name.endswith("/D") and "reg_" in node.name:
    setup = self.lib['cells']['DFF']['setup']
    # RT = 週期 - Setup - Jitter
    node.rt = period - setup - uncertainty
```

3.  **反向傳播 (Back-propagation)**: (本專案簡化實作省略了這一步，因為我們只關心 Endpoints 的 Slack。若是完整的 STA，需要從 RT 反推每個節點的 Required Time)。

## 2.3 計算 Slack

Slack (餘裕) = Required Time - Arrival Time。
- **Slack >= 0**: 時序滿足 (MET)。
- **Slack < 0**: 時序違規 (VIOLATED)。

```python
def _calculate_slack(self):
    # ...
    for node in self.graph.get_all_nodes():
        if node.rt != 999.0: # 只計算 Endpoints
            if node.at == -1.0: continue
            
            slack = node.rt - node.at
            # ... 記錄結果 ...
```
