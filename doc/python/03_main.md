# 3. 主程式與報表生成

[< 上一章](02_analysis.md) | [回目錄](../../learning_guide_for_python.md)

## 3.1 主程式 (`main.py`)

主程式負責整合流程：
1.  解析命令列參數 (`argparse`)。
2.  讀取設定檔 (`config/sta_config.json`)。
3.  呼叫 `VerilogParser` 建立圖形。
4.  呼叫 `TimingAnalyzer` 進行分析。
5.  輸出結果。

```python
# 整合流程範例
vparser = VerilogParser(config['library'])
graph = vparser.parse(args.design)

analyzer = TimingAnalyzer(graph, config['timing_constraints'], config['library'])
worst_slack, worst_node, results = analyzer.run_analysis()
```

## 3.2 報表生成 (`sta_engine/report.py`)

為了產生專業的 Markdown 報告，我們建立了一個 `ReportGenerator` 類別。

它會遍歷分析結果，並格式化為 Markdown 表格。

```python
class ReportGenerator:
    def generate(self, output_path="sta_report.md"):
        with open(output_path, 'w') as f:
            # 寫入標題與摘要
            f.write(f"# STA Analysis Report\n\n")
            
            # ... (省略) ...
            
            # 產生路徑表格
            f.write("| Node | AT (ns) | RT (ns) | Slack (ns) | Status |\n")
            f.write("| :--- | :---: | :---: | :---: | :---: |\n")
            
            # 依 Slack 排序 (由小到大，顯示最嚴重的 Violation)
            sorted_results = sorted(self.results, key=lambda x: x['slack'])
            
            for res in sorted_results[:20]:
                # 使用 emoji 與粗體強調
                icon = "✅" if res['slack'] >= 0 else "❌"
                f.write(f"| `{res['node']}` | {res['at']:.4f} | ... | {icon} ... |\n")
```
