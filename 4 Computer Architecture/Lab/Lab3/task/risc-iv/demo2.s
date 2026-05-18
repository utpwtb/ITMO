    .data

input_addr:      .word  0x80               ; Input address where the number 'n' is stored
output_addr:     .word  0x84               ; Output address where the result should be stored

    .text

_start:
    lui      sp, %hi(0x1000)               ; Initialize stack pointer to top of memory
    addi     sp, sp, %lo(0x1000)

    ; Load input value into a0 (argument register)
    lui      t0, %hi(input_addr)
    addi     t0, t0, %lo(input_addr)
    lw       t0, 0(t0)                     ; t0 = &input (0x80)
    lw       a0, 0(t0)                     ; a0 = n = *input_addr

    ; Call count_trailing_zeros(n)
    jal      ra, count_trailing_zeros      ; ra <- return address, jump to function

    ; Store result from a0 to output
    lui      t0, %hi(output_addr)
    addi     t0, t0, %lo(output_addr)
    lw       t0, 0(t0)                     ; t0 = &output (0x84)
    sw       a0, 0(t0)                     ; *output_addr = result

    halt

; ---------------------------------------------------------------------------
; count_trailing_zeros(n) -> count
;   Input:  a0 = n (32-bit integer)
;   Output: a0 = number of trailing zero bits (0..32)
;   Uses stack to save return address (ra) and callee-saved register (s0)
; ---------------------------------------------------------------------------
count_trailing_zeros:
    addi     sp, sp, -8                    ; Allocate 8 bytes on stack
    sw       ra, 0(sp)                     ; Save return address
    sw       s0, 4(sp)                     ; Save callee-saved register s0

    ; if n == 0, return 32
    beqz     a0, ctz_return_32

    ; count = 0
    addi     s0, zero, 0                   ; s0 = count = 0
    addi     t0, zero, 1                   ; t0 = 1 (constant for AND and shift)

ctz_loop:
    and      t1, a0, t0                    ; t1 = n & 1
    bnez     t1, ctz_done                  ; if (n & 1) != 0, done
    addi     s0, s0, 1                     ; count++
    srl      a0, a0, t0                    ; n >>= 1
    j        ctz_loop

ctz_return_32:
    addi     s0, zero, 32                  ; result = 32

ctz_done:
    mv       a0, s0                        ; a0 = count (return value)

    lw       s0, 4(sp)                     ; Restore callee-saved register s0
    lw       ra, 0(sp)                     ; Restore return address
    addi     sp, sp, 8                     ; Deallocate stack space
    jr       ra                            ; Return to caller
