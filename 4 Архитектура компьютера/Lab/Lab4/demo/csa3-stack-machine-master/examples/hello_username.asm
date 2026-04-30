.data
question: "> What is your name?", 10
hello_str: "> Hello, "
mark: "!"
buffer: 0


.text

_start:
    push 1
    push question
    call extand_string

    push question
    call print_string

    push buffer
    call read_string

    push hello_str
    call print_string

    push buffer
    call print_string

    push mark
    call print_string
    halt


; --- lib ---

;;; Ввод строки из IO 0
;; На вершине стека данных адрес строки, в которую будем записывать
;; > ->[address]
;; < ->[]
read_string:
  read:           ; ->[a] = address
        input 0   ; ->[char, a]
        push -1   ; ->[-1, char, a]
        cmp       ; ->[-1, char, a]
        jz ret_r  ; ->[-1, char, a]
        pop       ; ->[char, a]

        swap      ; ->[a, char]
        load      ; ->[l, a, char]
        inc       ; ->[l+1, a, char]
        store     ; ->[l+1, a, char]   -- [a] (len) <- l+1 (len++)
        pop       ; ->[a, char]
        dup       ; ->[a, a, char]
        load      ; ->[ll, a, a, char]
        add       ; ->[ll+a, a, char]
        over3     ; ->[char, ll+a, a, char]
        store     ; ->[char, ll+a, a, char] -- [ll+a] <- char
        pop       ; ->[ll+a, a, char]
        pop       ; ->[a, char]
        swap      ; ->[char, a]
        pop       ; ->[a]
        jmp read  ; ->[a]
  ret_r:
        pop       ; ->[char, a]
        pop       ; ->[a]
        pop       ; ->[]
        ret       ; ->[]


;;; Выводит строку
;; На вершине стека адрес строки
;; > ->[address]
;; < ->[]
print_string:
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


;;; Увеличивает длину строки
;; На вершине стека адрес строки, ниже - количество символов для добавления
;; > ->[address; n]
;; < ->[]
extand_string:
    load    ; ->[v, a, n]
    over3   ; ->[n, v, a, n]
    add     ; ->[n+v, a, n]
    store   ; ->[n+v, a, n]
    pop     ; ->[a, n]
    pop     ; ->[n]
    pop     ; ->[]
    ret
