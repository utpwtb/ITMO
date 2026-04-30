;;; ANS: 4613732

; cutoff=4000000
; first_even = 2
; second_even = 8
; even_sum = first_even + second_even
;
; while even_sum < cutoff:
;     even_fib = ((4 * second_even) + first_even)
;     even_sum += even_fib
;     first_even = second_even
;     second_even = even_fib
;
; print(even_sum)

.data
cutoff: 4000000
first_even: 2
second_even: 8
even_sum: 10

.text
load_value:
    load
    swap
    pop
    ret

_start:
calculate_sum:          ; []
    push even_sum       ; [even_sum]
    call load_value

    push cutoff         ; [even_sum, cutoff]
    call load_value

    cmp                 ; [even_sum - cutoff]
    js print_result    ; если even_sum >= cutoff, перейти к выводу результата
    pop
    pop


    ; even_fib = (4 * second_even) + first_even
    push 4
    push second_even    ; [4, second_even]
    call load_value
    mul                 ; [4 * second_even]
    push first_even     ; [4 * second_even, first_even]
    call load_value
    add                 ; [even_fib]

    ; even_sum += even_fib
    push even_sum       ; [even_fib, even_sum]
    load                ; [even_fib, even_sum_r, even_sum]
    over3               ; [even_fib, even_sum_r, even_sum, even_fib]
    add                 ; [even_fib, even_sum_r, even_sum+even_fib]
    store               ; сохранить новый even_sum
    pop
    pop                 ; [even_fib]

    ;; first_even = second_even; second_even = even_fib
    push second_even    ; [even_fib, second_even_r]
    call load_value     ; [even_fib, second_even]
    push first_even     ; [even_fib, second_even, first_even_r]
    swap                ; [even_fib, first_even_r, second_even]
    store               ; сохранить first_even <- second_even
    pop
    pop                 ; [even_fib]
    push second_even    ; [even_fib, second_even_r]
    swap                ; [second_even_r, even_fib]
    store               ; [second_even_r, even_fib]
    pop
    pop

    jmp calculate_sum    ; перейти к началу цикла

print_result:
    push even_sum
    load
    output 2             ; вывод результата
    halt
