# C++ STA Engine Learning Guide

這份文件旨在引導您理解 C++ 版本的靜態時序分析 (STA) 引擎實作細節。

## 範例設計: 4-bit Accumulator

本專案使用一個簡單的 4-bit 累加器 (`accumulator.v`) 作為範例。
以下是該設計的時序圖 (Timing Graph) 結構，對於理解 C++ 解析與分析邏輯至關重要。

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

## C++ 專案架構概覽

C++ 版本的實作著重於高效能與記憶體管理。

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
