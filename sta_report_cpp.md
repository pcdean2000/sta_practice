# STA Analysis Report (C++)

**Generated on:** 2026-02-10 20:48:17

## 1. Executive Summary

- **Design:** `design/accumulator.v`
- **Timing Status:** ✅ **MET**
- **Worst Slack:** `+0.5050 ns`
- **Critical Node:** `c1`

## 2. Configuration

| Parameter | Value |
| :--- | :--- |
| Clock Period | `1.0000 ns` |
| Clock Uncertainty | `0.0500 ns` |
| Input Delay | `0.2000 ns` |
| Output Delay | `0.2000 ns` |

## 3. Top Critical Paths

The following table shows the top timing paths (up to 20 worst violations).

| Node | AT (ns) | RT (ns) | Slack (ns) | Status |
| :--- | :---: | :---: | :---: | :---: |
| `c1` | 0.2450 | 0.7500 | **+0.5050** | ✅ MET |
| `b_reg_out[2]` | +0.0800 | +0.7500 | **+0.6700** | ✅ MET |
| `b_reg_out[3]` | +0.0800 | +0.7500 | **+0.6700** | ✅ MET |
| `reg_sum1/D` | +0.2250 | +0.9000 | **+0.6750** | ✅ MET |
| `reg_b0/D` | +0.2050 | +0.9000 | **+0.6950** | ✅ MET |
| `reg_b1/D` | +0.2050 | +0.9000 | **+0.6950** | ✅ MET |
| `reg_b2/D` | +0.2050 | +0.9000 | **+0.6950** | ✅ MET |
| `reg_b3/D` | +0.2050 | +0.9000 | **+0.6950** | ✅ MET |
| `reg_sum0/D` | +0.1550 | +0.9000 | **+0.7450** | ✅ MET |

---
*End of Report*
