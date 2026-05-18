.data
buf: 0


.text

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


;;; Добавляет символ в конец строки
;; На вершине стека адрес строки, ниже - символ для добавления
;; > ->[address; sym]
;; < ->[]
push_char:
    dup
    push 1
    swap
    call extand_string

    load
    add
    swap
    store
    pop
    pop
    ret


;;; Добавляет первод строки к строке
;; На вершине стека адрес строки
;; > ->[address]
;; < ->[]
add_new_line:
    push 10
    swap
    call push_char
    ret


_start:
    push buf
    call read_string

    push 33
    push buf
    call push_char

    push buf
    call print_string
    halt
