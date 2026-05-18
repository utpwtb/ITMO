.data
cnt: 100

.text
_start:
    cycle:
        push cnt
        load
        jz exit
        dec
        store
        pop
        pop

        input 8
        output 1
        pop

        jmp cycle
    exit:
        pop
        pop
        halt
