    .data

input_addr:      .word  0x80
output_addr:     .word  0x84

    .text
    .org     0x200

_start:
    lui      sp, %hi(0x1000)
    addi     sp, sp, %lo(0x1000)

    lui      t0, %hi(input_addr)
    addi     t0, t0, %lo(input_addr)
    lw       t0, 0(t0)
    lw       a0, 0(t0)                     

    jal      ra, count_trailing_zeros

    lui      t0, %hi(output_addr)
    addi     t0, t0, %lo(output_addr)
    lw       t0, 0(t0)
    sw       a0, 0(t0)

    halt

count_trailing_zeros:
    addi     sp, sp, -12                   
    sw       ra, 0(sp)                     
    sw       s0, 4(sp)                     
    sw       s1, 8(sp)                     

    beqz     a0, ctz_return_32

    mv       s1, a0                        
    addi     s0, zero, 0                   

ctz_loop:
    mv       a0, s1                        
    addi     a1, zero, 0                   
    jal      ra, is_bit_set                

    bnez     a0, ctz_done                  

    addi     s0, s0, 1                     
    addi     t0, zero, 1
    srl      s1, s1, t0                    
    j        ctz_loop

ctz_return_32:
    addi     s0, zero, 32                  

ctz_done:
    mv       a0, s0                       

    lw       s1, 8(sp)                    
    lw       s0, 4(sp)                    
    lw       ra, 0(sp)                    
    addi     sp, sp, 12                   
    jr       ra                           

is_bit_set:
    srl      t0, a0, a1                   
    addi     t1, zero, 1
    and      a0, t0, t1                   
    jr       ra                           