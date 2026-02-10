module accumulator (
    input clk,
    input rst,
    input [3:0] data_in,
    output [3:0] sum_out
);
    wire [3:0] b_reg_out;
    wire [3:0] adder_out;
    wire [3:0] sum_reg_out;
    wire c0, c1, c2; // Carry bits

    // 1. Input Register (4 DFFs)
    DFF reg_b0 (.C(clk), .D(data_in[0]), .Q(b_reg_out[0]));
    DFF reg_b1 (.C(clk), .D(data_in[1]), .Q(b_reg_out[1]));
    DFF reg_b2 (.C(clk), .D(data_in[2]), .Q(b_reg_out[2]));
    DFF reg_b3 (.C(clk), .D(data_in[3]), .Q(b_reg_out[3]));

    // 2. 4-bit Adder Logic (Gate Level for STA demonstration)
    // Bit 0: Sum = A^B, Carry = A&B (assuming A is sum_reg_out)
    XOR2 x0 (.A(sum_reg_out[0]), .B(b_reg_out[0]), .Y(adder_out[0]));
    AND2 a0 (.A(sum_reg_out[0]), .B(b_reg_out[0]), .Y(c0));

    // Bit 1: Full Adder Logic
    wire sum1_half, c1_a, c1_b;
    XOR2 x1a (.A(sum_reg_out[1]), .B(b_reg_out[1]), .Y(sum1_half));
    XOR2 x1b (.A(sum1_half), .B(c0), .Y(adder_out[1]));
    AND2 a1a (.A(sum_reg_out[1]), .B(b_reg_out[1]), .Y(c1_a));
    AND2 a1b (.A(sum1_half), .B(c0), .Y(c1_b));
    OR2  o1  (.A(c1_a), .B(c1_b), .Y(c1));

    // Bit 2 & 3 (Simplified for brevity, but exist in graph) ...
    // ... Assume similar logic repeats ...

    // 3. Output Register / Accumulator State (4 DFFs)
    DFF reg_sum0 (.C(clk), .D(adder_out[0]), .Q(sum_reg_out[0]));
    DFF reg_sum1 (.C(clk), .D(adder_out[1]), .Q(sum_reg_out[1]));
    // ... reg_sum2, reg_sum3 ...

    assign sum_out = sum_reg_out;

endmodule