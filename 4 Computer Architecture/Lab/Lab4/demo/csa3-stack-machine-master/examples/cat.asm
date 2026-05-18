.data
buf: 0

.text
read_to_buf:
  read:
        input 0   ; ch      считать с порта 0

        push -1   ; -1, ch
        cmp       ; -1, ch
        jz ret_r  ; -1, ch
        pop       ; ch

        push buf  ; s_r, ch
        load      ; s_val, s_r, ch
        inc       ; s_val+1, s_r, ch
        store     ; s_val+1, s_r, ch   -- [s_r] = s_val+1
        pop       ; s_r, ch
        load      ; s_val, s_r, ch
        add       ; s_val+s_r, ch
        swap      ; ch, s_val+s_r
        store     ; ch, s_val+s_r      -- [s_r] (now s_val+1) = ch
        pop       ; s_val+s_r
        pop       ; []
        jmp read  ; []
  ret_r:
        pop
        pop
        ret


write_from_buf:   ; Дальше то же, что и в hello_world.asm
        push buf
        load
  cycle:
        jz ret_w
        swap
        inc
        load
        output 1
        pop
        swap
        dec
        jmp cycle
  ret_w:
        pop
        pop
        ret


_start:
        call read_to_buf
        call write_from_buf
        halt
