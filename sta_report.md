# STA Analysis Report

**Generated on:** 2026-02-10 18:10:41

## 1. Executive Summary

- **Design:** `design/accumulator.v`
- **Timing Status:** ✅ **MET**
- **Worst Slack:** `+0.6750 ns`
- **Critical Node:** `reg_sum1/D`

## 2. Configuration

| Parameter | Value |
| :--- | :--- |
| Clock Period | `1.0 ns` |
| Clock Uncertainty | `0.05 ns` |
| Input Delay | `0.2 ns` |
| Output Delay | `0.2 ns` |

## 3. Top Critical Paths

The following table shows the top timing paths (up to 10 worst violations) or all paths if fewer than 10.

| Node | AT (ns) | RT (ns) | Slack (ns) | Status |
| :--- | :---: | :---: | :---: | :---: |
| `reg_sum1/D` | 0.2250 | 0.9000 | **+0.6750** | ✅ MET |
| `reg_sum0/D` | 0.1550 | 0.9000 | **+0.7450** | ✅ MET |

---
*End of Report*
