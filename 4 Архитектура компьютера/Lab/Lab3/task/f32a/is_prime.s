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
    subtract
    dup
    -if check_one
    drop drop
    lit -1
    
    end ;

check_one:
    drop
    dup
    lit 1
    subtract
    dup
    if is_one
    drop
    
    dup
    lit 2
    subtract
    dup
    if is_two
    drop
    
    dup
    lit 1
    and
    if is_even
    
    loop_start ;

is_one:
    drop drop
    lit 0

    end ;

is_two:
    drop drop
    lit 1

    end ;

is_even:
    drop
    lit 0

    end ;

loop_start:
    !p n_store
    
    lit 3
    loop_i ;

loop_i:
    !p i_store
    
    @p i_store
    dup
    a!
    mul
    @p n_store
    subtract
    dup
    if not_prime
    -if is_prime
    
    @p n_store
    @p i_store
    a!
    mod
    
    dup
    if not_prime
    
    drop
    @p i_store
    lit 2
    +
    loop_i ;

not_prime:
    drop
    lit 0

    end ;

is_prime:
    lit 1

    end ;

subtract:
    inv
    lit 1
    +
    +
    ;

mul:
    dup
    a!
    lit 0
    
    lit 31
    >r
    
mul_loop:
    +*
    next mul_loop
    
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
    
    lit 31
    >r
    
mod_loop:
    +/
    next mod_loop
    
    drop
    ;

end:
    @p output_addr b!
    !b
    halt