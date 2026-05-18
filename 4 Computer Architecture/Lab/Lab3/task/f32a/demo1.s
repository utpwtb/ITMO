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
    @p input_addr b!
    @b

    dup
    lit 1
    sub
    dup
    -if check_one
    drop drop
    lit -1
    @p output_addr b!
    !b
    halt

check_one:
    drop
    dup
    lit 1
    sub
    dup
    if not_one
    drop
    loop_start ;

not_one:
    drop drop
    lit 0
    @p output_addr b!
    !b
    halt

loop_start:
    !p n_store

    lit 2
    loop_i ;

loop_i:
    !p i_store

    @p i_store
    dup
    a!
    mul
    @p n_store
    sub
    dup
    if check_equal
    dup
    -if is_prime
    drop

    @p n_store
    @p i_store
    a!
    mod

    dup
    if not_prime

    drop
    @p i_store
    lit 1
    +
    loop_i ;

check_equal:
    drop
    lit 0
    @p output_addr b!
    !b
    halt

not_prime:
    drop
    lit 0
    @p output_addr b!
    !b
    halt

is_prime:
    lit 1
    @p output_addr b!
    !b
    halt

sub:
    inv
    lit 1
    +
    +
    ;

mul:
    dup
    a!
    lit 0
    
    +* +* +* +* +* +* +* +*
    +* +* +* +* +* +* +* +*
    +* +* +* +* +* +* +* +*
    +* +* +* +* +* +* +* +*
    
    drop drop
    a
    ;

mod:
    a
    lit divisor b!
    !b
    
    a!
    
    lit 0
    lit 0
    
    +/ +/ +/ +/ +/ +/ +/ +/
    +/ +/ +/ +/ +/ +/ +/ +/
    +/ +/ +/ +/ +/ +/ +/ +/
    +/ +/ +/ +/ +/ +/ +/ +/
    
    drop
    ;
