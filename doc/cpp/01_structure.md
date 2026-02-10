# 1. 專案架構與建置

[< 回目錄](../../learning_guide_for_cpp.md) | [下一章 >](02_parser_graph.md)

本章節介紹 C++ 專案的建置系統與基本架構。

## 1.1 編譯系統 (`Makefile`)

我們使用標準的 `Makefile` 來管理編譯流程。

```makefile
CXX = g++
# 使用 C++17 標準，並加入 include 目錄
CXXFLAGS = -std=c++17 -Wall -Iinclude -O2

# 自動搜尋 src/ 下的所有 cpp 檔案
SRCS = $(wildcard $(SRC_DIR)/*.cpp)
# 將 .cpp 替換為 .o，並放在 obj/ 目錄下
OBJS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))

# 連結目標執行檔
$(TARGET): $(OBJS)
    $(CXX) $(OBJS) -o $@ $(LDFLAGS)
```

-   `make`: 編譯專案。
-   `make run`: 執行程式。
-   `make clean`: 清除暫存檔。

## 1.2 相依套件 (`include/json.hpp`)

本專案使用 `nlohmann/json` 程式庫來解析 JSON 設定檔。這是一個 Single-header library，只需將 `json.hpp` 放入 `include/` 目錄即可使用，無需額外的連結 (Link) 步驟。

## 1.3 報表生成 (`src/Report.cpp`)

C++ 版本的報表生成邏輯與 Python 版本類似，使用 `std::ofstream` 寫入 Markdown 檔案。

```cpp
void Report::generate(const std::string& outputPath) {
    std::ofstream f(outputPath);
    
    // 使用 std::setprecision 控制浮點數輸出精度
    f << "| Node | AT (ns) | ... |\n";
    f << std::fixed << std::setprecision(4);
    
    for (const auto& res : results) {
        // ...
        f << "| `" << res.node << "` | " << res.at << " | ... \n";
    }
}
```

這展示了如何在 C++ 中進行格式化的檔案輸出。
