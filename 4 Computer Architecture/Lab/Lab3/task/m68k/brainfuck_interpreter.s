    .data
    .org    0x100

input_addr:      .word 0x80
output_addr:     .word 0x84

bf_memory:       .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
bracket_fwd:     .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
bracket_back:    .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
bracket_stack:   .word 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
code_buffer:     .byte 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0

    .text

_start:
    movea.l input_addr, A0
    movea.l (A0), A0
    movea.l output_addr, A1
    movea.l (A1), A1

    move.l  0, D2
    move.l  0, D5
    move.l  0, D7
    movea.l code_buffer, A4
    movea.l bf_memory, A5

read_loop:
    move.l  (A0), D0
    cmp.l   0, D0
    beq     read_done
    cmp.b   0x0A, D0
    beq     read_done
    cmp.l   63, D5
    bge     line_overflow_error
    move.b  D0, 0(A4,D5)
    add.l   1, D5
    jmp     read_loop

read_done:
    move.b  0, 0(A4,D5)

validate_brackets:
    move.l  0, D4
    move.l  0, D6

val_bracket_loop:
    move.b  0(A4,D4), D0
    beq     val_brackets_done
    cmp.b   '[', D0
    bne     val_check_close
    add.l   1, D6
    jmp     val_adv_index

val_check_close:
    cmp.b   ']', D0
    bne     val_adv_index
    sub.l   1, D6
    blt     error_unmatched_close

val_adv_index:
    add.l   1, D4
    jmp     val_bracket_loop

val_brackets_done:
    cmp.l   0, D6
    bne     error_unmatched_open

fill_bracket_jumps:
    movea.l bracket_stack, A3
    move.l  0, D4
    move.l  0, D1

fill_bfj_loop:
    move.b  0(A4,D4), D0
    beq     fill_bfj_done
    cmp.b   '[', D0
    bne     fill_bfj_check_close
    cmp.l   64, D1
    bge     error_unmatched_open
    move.l  D1, D3
    lsl.l   2, D3
    move.l  D4, 0(A3,D3)
    add.l   1, D1
    jmp     fill_bfj_adv

fill_bfj_check_close:
    cmp.b   ']', D0
    bne     fill_bfj_adv
    sub.l   1, D1
    blt     error_unmatched_close
    move.l  D1, D3
    lsl.l   2, D3
    move.l  0(A3,D3), D6
    move.l  D6, D3
    lsl.l   2, D3
    movea.l bracket_fwd, A6
    move.l  D4, D0
    add.l   1, D0
    move.l  D0, 0(A6,D3)
    move.l  D4, D3
    lsl.l   2, D3
    movea.l bracket_back, A6
    move.l  D6, D0
    add.l   1, D0
    move.l  D0, 0(A6,D3)

fill_bfj_adv:
    add.l   1, D4
    jmp     fill_bfj_loop

fill_bfj_done:
    jmp     main_loop

main_loop:
    move.b  0(A4,D2), D0
    beq     program_end
    cmp.b   '+', D0
    beq     cmd_inc
    cmp.b   '-', D0
    beq     cmd_dec
    cmp.b   '.', D0
    beq     cmd_output
    cmp.b   ',', D0
    beq     cmd_input
    cmp.b   '>', D0
    beq     cmd_right
    cmp.b   '<', D0
    beq     cmd_left
    cmp.b   '[', D0
    beq     cmd_loop_start
    cmp.b   ']', D0
    beq     cmd_loop_end
    cmp.b   ' ', D0
    beq     main_next
    cmp.b   9, D0
    beq     main_next
    cmp.b   13, D0
    beq     main_next
    jmp     error_invalid_cmd

cmd_right:
    add.l   1, D7
    cmp.l   30, D7
    bge     error_ptr_out
    jmp     main_next

cmd_left:
    sub.l   1, D7
    blt     error_ptr_out
    jmp     main_next

cmd_inc:
    move.l  D7, D3
    lsl.l   2, D3
    add.l   1, 0(A5,D3)
    bvs     overflow_error
    jmp     main_next

cmd_dec:
    move.l  D7, D3
    lsl.l   2, D3
    sub.l   1, 0(A5,D3)
    bvs     overflow_error
    jmp     main_next

cmd_output:
    move.l  D7, D3
    lsl.l   2, D3
    move.l  0(A5,D3), D0
    and.l   0xFF, D0
    move.l  D0, (A1)
    jmp     main_next

cmd_input:
    move.l  (A0), D0
    cmp.l   0, D0
    beq     input_eof
    move.l  D7, D3
    lsl.l   2, D3
    move.l  0(A5,D3), D1
    and.l   0xFFFFFF00, D1
    or.l    D0, D1
    move.l  D1, 0(A5,D3)
    jmp     main_next

input_eof:
    move.l  D7, D3
    lsl.l   2, D3
    move.l  0(A5,D3), D0
    and.l   0xFFFFFF00, D0
    move.l  D0, 0(A5,D3)
    jmp     main_next

cmd_loop_start:
    move.l  D7, D3
    lsl.l   2, D3
    move.l  0(A5,D3), D0
    bne     main_next
    move.l  D2, D3
    lsl.l   2, D3
    movea.l bracket_fwd, A6
    move.l  0(A6,D3), D2
    jmp     main_loop

cmd_loop_end:
    move.l  D7, D3
    lsl.l   2, D3
    move.l  0(A5,D3), D0
    beq     main_next
    move.l  D2, D3
    lsl.l   2, D3
    movea.l bracket_back, A6
    move.l  0(A6,D3), D2
    jmp     main_loop

main_next:
    add.l   1, D2
    jmp     main_loop

program_end:
    halt

error_ptr_out:
    move.l  -1, (A1)
    halt

error_unmatched_close:
    move.l  -1, (A1)
    halt

error_unmatched_open:
    move.l  -1, (A1)
    halt

overflow_error:
    move.l  0xCCCCCCCC, (A1)
    halt

line_overflow_error:
    move.l  0xCCCCCCCC, (A1)
    halt

error_invalid_cmd:
    move.l  -1, (A1)
    halt
