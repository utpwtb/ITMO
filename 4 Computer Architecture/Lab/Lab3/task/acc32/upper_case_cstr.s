.data

buffer:         .byte '__________________________________'
input_addr:     .word   0x80      
output_addr:    .word   0x84    
buf_ptr:        .word   0x00        

current_sym:    .word   0       
count_sym:      .word   0

const_a:        .word   0x61    ; 'a'
const_z:        .word   0x7A    ; 'z'
const_hex_DF:   .word   0xDF
const_hex_FF:   .word   0xFF

const_buf_err:  .word   0xCCCCCCCC
const_1:        .word   0x1                     
line_feed:      .word   0xA     ; '\n'
size_buf:       .word   0x20          
space:          .byte   ' '       
const_inital:   .byte   '\0\0__'

.text
.org 137

_start:
    load_addr    buf_ptr
    xor          size_buf
    beqz         error

    load_addr   input_addr
    load_acc
    store_addr  current_sym  
    jmp         check_line_feed     

check_line_feed:
    load_addr   current_sym      
    xor         line_feed          
    beqz        clear_ptr         
    jmp         check_lower

check_lower:
    load_addr   current_sym
    sub         const_a
    ble         input_buffer

    load_addr   current_sym   
    sub         const_z
    beqz        to_upper
    ble         to_upper
    bgt         input_buffer

to_upper:
    load_addr    current_sym    
    and          const_hex_DF   ;0100  0110 1101
    store_addr   current_sym

    jmp          input_buffer

input_buffer:
    load_addr    current_sym
    add          const_inital
    store_ind    buf_ptr       

    load_addr    buf_ptr
    add          const_1
    store_addr   buf_ptr

    load_addr    count_sym
    add          const_1
    store_addr   count_sym

    jmp          _start

error:
    load_addr   const_buf_err
    store_ind   output_addr 
    jmp         end

clear_ptr:
    load_addr   buf_ptr 
	xor         buf_ptr
	store_addr  buf_ptr

output_buffer:
    load_addr   count_sym
    beqz        end

    load_addr   buf_ptr
    load_acc
    store_addr  current_sym

    and         const_hex_FF
    beqz        end

    load_addr   current_sym   
    and         const_hex_FF  
    store_ind   output_addr    

    load_addr   buf_ptr       
    add const_1
    store_addr  buf_ptr

    load_addr   count_sym
    sub         const_1
    store_addr  count_sym

    jmp         output_buffer

end:
    halt