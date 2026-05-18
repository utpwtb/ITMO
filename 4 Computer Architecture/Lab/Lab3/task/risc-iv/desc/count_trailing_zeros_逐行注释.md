# `count_trailing_zeros.s` 逐行注释

```assembly
    .data

input_addr:      .word  0x80               ; 在内存 0x00 处定义一个常量 0x80（输入端口地址）
output_addr:     .word  0x84               ; 在内存 0x04 处定义一个常量 0x84（输出端口地址）

    .text
    .org     0x200                         ; 代码段从地址 0x200 开始（避开 I/O 端口 0x80-0x87）

_start:
    lui      sp, %hi(0x1000)               ; 取 0x1000 的高 20 位放入 sp
    addi     sp, sp, %lo(0x1000)            ; 加 0x1000 的低 12 位，sp = 0x1000（栈顶）

    lui      t0, %hi(input_addr)           ; 取 input_addr 标签地址的高 20 位
    addi     t0, t0, %lo(input_addr)        ; 加低 12 位，t0 = &input_addr（即 0x00）
    lw       t0, 0(t0)                     ; t0 = *t0 = 0x80（取出输入端口地址）
    lw       a0, 0(t0)                     ; a0 = *0x80 = n（读入输入值，放入参数寄存器）

    jal      ra, count_trailing_zeros       ; ra = 下一条指令地址，跳转到 count_trailing_zeros

    lui      t0, %hi(output_addr)          ; 取 output_addr 标签地址的高 20 位
    addi     t0, t0, %lo(output_addr)       ; 加低 12 位，t0 = &output_addr（即 0x04）
    lw       t0, 0(t0)                     ; t0 = *t0 = 0x84（取出输出端口地址）
    sw       a0, 0(t0)                     ; *0x84 = a0（将返回值写入输出端口）

    halt                                   ; 停止执行


count_trailing_zeros:
    addi     sp, sp, -12                   ; sp 减 12，在栈上分配 12 字节空间
    sw       ra, 0(sp)                     ; 保存返回地址 ra 到栈 [sp+0]
    sw       s0, 4(sp)                     ; 保存计数器 s0 到栈 [sp+4]
    sw       s1, 8(sp)                     ; 保存 n 的副本 s1 到栈 [sp+8]

    beqz     a0, ctz_return_32             ; 如果 n == 0，跳转到 ctz_return_32

    mv       s1, a0                        ; s1 = n（将 n 复制到 callee-saved 寄存器）
    addi     s0, zero, 0                   ; s0 = 0（初始化计数器）

ctz_loop:
    mv       a0, s1                        ; a0 = s1 = n（准备第 1 个参数）
    addi     a1, zero, 0                   ; a1 = 0（准备第 2 个参数：位号 = 0）
    jal      ra, is_bit_set                ; 调用 is_bit_set(n, 0)，检查最低位

    bnez     a0, ctz_done                  ; 如果返回值 a0 != 0（最低位是 1），结束循环

    addi     s0, s0, 1                     ; count++（计数器加 1）
    addi     t0, zero, 1                   ; t0 = 1
    srl      s1, s1, t0                    ; s1 = s1 >> 1（n 逻辑右移 1 位）
    j        ctz_loop                      ; 跳回循环开始，继续检查

ctz_return_32:
    addi     s0, zero, 32                  ; s0 = 32（n==0 时直接返回 32）

ctz_done:
    mv       a0, s0                        ; a0 = s0 = count（将计数结果放入返回值寄存器）

    lw       s1, 8(sp)                     ; 从栈 [sp+8] 恢复 s1 的原值
    lw       s0, 4(sp)                     ; 从栈 [sp+4] 恢复 s0 的原值
    lw       ra, 0(sp)                     ; 从栈 [sp+0] 恢复 ra 的原值
    addi     sp, sp, 12                    ; sp 加 12（释放栈帧）
    jr       ra                            ; 跳回 ra 指向的地址（返回 _start）


is_bit_set:
    srl      t0, a0, a1                    ; t0 = n >> bit（将目标位右移到最低位）
    addi     t1, zero, 1                   ; t1 = 1
    and      a0, t0, t1                    ; a0 = t0 & 1（取最低位，0 或 1）
    jr       ra                            ; 返回调用者（ra 未被覆盖，直接跳回）
```