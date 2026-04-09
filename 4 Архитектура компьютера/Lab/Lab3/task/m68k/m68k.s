    .data
.org 0x200

input_addr:   .word 0x80
output_addr:  .word 0x84
divisor:      .word 0
n_store:      .word 0
i_store:      .word 0 
 
    .text
.org 0x400

_start:
    @p input_addr b!   \ B = 0x80 (input address)
    @b                 \ read n from input, stack: [n]

    \ check if n < 1
    dup                \ [n, n]
    lit 1              \ [n, n, 1]
    sub                \ [n, n-1]
    dup                \ [n, n-1, n-1]
    -if check_one      \ if n-1 >= 0 jump, pop top
    \ n < 1, return -1
    drop drop          \ []
    lit -1             \ [-1]
    @p output_addr b!  \ B = 0x84 (output address)
    !b                 \ mem[0x84] = -1
    halt

check_one:
    \ stack: [n, n-1]
    drop               \ [n]
    dup                \ [n, n]
    lit 1              \ [n, n, 1]
    sub                \ [n, n-1]
    dup                \ [n, n-1, n-1]
    if not_one         \ if n-1 == 0 jump, pop top
    \ n != 1, continue to loop
    drop               \ [n]
    loop_start ;

not_one:
    \ stack: [n, n-1], n-1 == 0
    drop drop          \ []
    lit 0
    @p output_addr b!
    !b
    halt

loop_start:
    \ stack: [n]
    !p n_store         \ store n

    lit 2              \ [2] i = 2
    loop_i ;

loop_i:
    \ stack: [i]
    !p i_store         \ store i

    \ check if i >= n
    @p i_store         \ [i]
    @p n_store         \ [i, n]
    sub                \ [i-n]
    -if is_prime       \ if i-n >= 0 jump (i >= n), pop top

    \ i < n, compute n % i
    @p n_store         \ [n]
    @p i_store         \ [n, i]
    !p divisor         \ [n], store i to divisor
    lit divisor b!     \ B points to divisor B = i
    a!                 \ A = n
    mod                \ [n % i]

    dup                \ [n%i, n%i]
    if not_prime       \ if n%i == 0, return 0 (not prime)

    \ n % i != 0, continue
    drop               \ []
    @p i_store         \ [i]
    lit 1              \ [i, 1]
    +                  \ [i+1]
    loop_i ;           \ continue loop

not_prime:
    drop               \ []
    lit 0
    @p output_addr b!
    !b
    halt

is_prime:
    \ stack is empty
    lit 1
    @p output_addr b!
    !b
    halt

\ =====================
\ Subroutines
\ =====================

\ Subtraction: S - T -> S-T
\ stack: [..., S, T] -> [..., S-T]
sub:
    inv
    lit 1
    +
    +
    ;

\ Modulo: A = dividend, mem[B] = divisor
\ Result: top of stack is remainder
mod:
    lit 0              \ [0] T = 0
    lit 0              \ [0, 0] S = 0
    @p n_store                 \ [0, 0, n]
    >r                 \ [0, 0], R = [n]
div_step:
    +/
    next div_step      \ R--, if R != 0 jump to div_step
    over               \ 
    drop               \ [remainder]
    ;
