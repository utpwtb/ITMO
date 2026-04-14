    .data

input_addr:      .word  0x80               
output_addr:     .word  0x84               

    .text

_start:
    lui      t0, %hi(input_addr)
    addi     t0, t0, %lo(input_addr)
    lw       t0, 0(t0)                 
    lw       t1, 0(t0)                   
    addi     t2, zero, 32              
    beqz     t1, store_result          
    addi     t2, zero, 0                
    addi     t3, zero, 1                 

loop:
    and      t4, t1, t3                   
    bnez     t4, store_result             
    addi     t2, t2, 1                    
    srl      t1, t1, t3                  
    j        loop

store_result:
    lui      t0, %hi(output_addr)
    addi     t0, t0, %lo(output_addr)
    lw       t0, 0(t0)                   
    sw       t2, 0(t0)                     

    halt
