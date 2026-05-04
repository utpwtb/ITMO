    .data

input_addr:      .word  0x80               ; Input address where the number 'n' is stored
output_addr:     .word  0x84               ; Output address where the result should be stored

    .text

_start:
    ; Load input value
    lui      t0, %hi(input_addr)
    addi     t0, t0, %lo(input_addr)
    lw       t0, 0(t0)                     ; t0 = &input (0x80)
    lw       t1, 0(t0)                     ; t1 = n = *input_addr

    ; if n == 0, return 32
    addi     t2, zero, 32                  ; t2 = 32 (result for n==0)
    beqz     t1, store_result              ; if n == 0, jump to store

    ; count = 0
    addi     t2, zero, 0                   ; t2 = count = 0
    addi     t3, zero, 1                   ; t3 = 1 (constant for AND and shift)

loop:
    and      t4, t1, t3                    ; t4 = n & 1
    bnez     t4, store_result              ; if (n & 1) != 0, done
    addi     t2, t2, 1                     ; count++
    srl      t1, t1, t3                    ; n >>= 1
    j        loop

store_result:
    lui      t0, %hi(output_addr)
    addi     t0, t0, %lo(output_addr)
    lw       t0, 0(t0)                     ; t0 = &output (0x84)
    sw       t2, 0(t0)                     ; *output_addr = count

    halt
