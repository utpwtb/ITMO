    .data

input_addr:      .word  0x80
output_addr:     .word  0x84

    .text
    .org     0x200

_start:
    lui      sp, %hi(0x1000)
    addi     sp, sp, %lo(0x1000)

    lui      t0, %hi(input_addr)
    addi     t0, t0, %lo(input_addr)
    lw       t0, 0(t0)
    lw       a0, 0(t0)                     ; a0 = n

    jal      ra, count_trailing_zeros

    lui      t0, %hi(output_addr)
    addi     t0, t0, %lo(output_addr)
    lw       t0, 0(t0)
    sw       a0, 0(t0)

    halt

; ===========================================================================
; count_trailing_zeros(n) -> count
;   输入:  a0 = n
;   输出:  a0 = trailing zero count (0..32)
;
;   这是一个非叶子函数 —— 它调用了 is_bit_set，
;   因此必须将 ra 和跨调用存活的寄存器保存到栈上。
; ===========================================================================
count_trailing_zeros:
    addi     sp, sp, -12                   ; 分配栈帧: ra + s0 + s1
    sw       ra, 0(sp)                     ; 保存返回地址（会被嵌套调用覆盖）
    sw       s0, 4(sp)                     ; 保存计数器 s0
    sw       s1, 8(sp)                     ; 保存 n 的副本 s1

    ; if n == 0, return 32
    beqz     a0, ctz_return_32

    mv       s1, a0                        ; s1 = n（跨调用保存的副本）
    addi     s0, zero, 0                   ; s0 = count = 0

ctz_loop:
    mv       a0, s1                        ; arg0 = n
    addi     a1, zero, 0                   ; arg1 = bit = 0
    jal      ra, is_bit_set                ; ★ 嵌套调用 —— ra 被覆盖！

    bnez     a0, ctz_done                  ; if bit 0 is set, we are done

    addi     s0, s0, 1                     ; count++
    addi     t0, zero, 1
    srl      s1, s1, t0                    ; n >>= 1
    j        ctz_loop

ctz_return_32:
    addi     s0, zero, 32                  ; count = 32

ctz_done:
    mv       a0, s0                        ; a0 = count（返回值）

    lw       s1, 8(sp)                     ; 恢复 s1
    lw       s0, 4(sp)                     ; 恢复 s0
    lw       ra, 0(sp)                     ; 恢复 ra
    addi     sp, sp, 12                    ; 释放栈帧
    jr       ra                            ; 返回

; ===========================================================================
; is_bit_set(n, bit) -> {0, 1}
;   输入:  a0 = n,  a1 = bit position (0..31)
;   输出:  a0 = 0  如果第 bit 位为 0
;          a0 = 1  如果第 bit 位为 1
;
;   这是一个叶子函数 —— 它不再调用任何其他函数，
;   因此 ra 不会被覆盖，无需保存到栈上。
; ===========================================================================
is_bit_set:
    srl      t0, a0, a1                    ; t0 = n >> bit
    addi     t1, zero, 1
    and      a0, t0, t1                    ; a0 = (n >> bit) & 1
    jr       ra                            ; 直接返回，ra 仍指向 count_trailing_zeros
