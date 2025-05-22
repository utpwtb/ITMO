; 数据定义段

ORG 0x000

; 状态控制
STATE:      WORD 0      ; 0=输入第一个数, 1=输入第二个数

; 输入存储
DIGIT:      WORD 0      ; 当前输入键值
NUM1:       WORD 0      ; 第一个操作数
SIGN1:      WORD 0      ; 第一个数符号
NUM2:       WORD 0      ; 第二个操作数
SIGN2:      WORD 0      ; 第二个数符号

; 计算结果
RESULT:     WORD 0      ; 乘积绝对值
SIGN_RES:   WORD 0      ; 结果符号


; 主程序段

START:
    CALL INIT_SYSTEM      ; 系统初始化
    JUMP MAIN_LOOP         ; 进入主循环

INIT_SYSTEM:
    CLA
    ST NUM1               ; 初始化所有变量
    ST NUM2
    ST SIGN1
    ST SIGN2
    ST STATE
    ST RESULT
    ST SIGN_RES
    RET

MAIN_LOOP:
    CALL READ_FIRST_NUM
    CALL READ_SECOND_NUM
    CALL PERFORM_MULT
    CALL SHOW_RESULT
    HLT


; 输入处理模块

READ_FIRST_NUM:
    LD #0x0
    ST STATE              ; 设置为第一个数输入模式
    CALL PROCESS_INPUT
    RET

READ_SECOND_NUM:
    LD #0x1
    ST STATE              ; 设置为第二个数输入模式
    CALL PROCESS_INPUT
    RET

PROCESS_INPUT:
    IN 0x1C           ; 读取键盘输入
    ST DIGIT
    CMP #0xA              ; 检查负号
    BEQ HANDLE_SIGN
    CMP #0xD              ; 检查乘号
    BEQ HANDLE_MULT
    CMP #0xF              ; 检查等号
    BEQ HANDLE_EQUAL    
    CMP #10               ; 检查数字范围
    BLO PROCESS_DIGIT     ; 合法数字处理
    JUMP PROCESS_INPUT     ; 忽略无效输入

HANDLE_MULT:
    RET

HANDLE_EQUAL:
    RET                 ; 返回到CALCULATE流程

WAIT_MULT_SYMBOL:
    IN 0x1C
    CMP #0xD
    BNE WAIT_MULT_SYMBOL
    RET

HANDLE_SIGN:
    LD STATE
    BNE SET_SIGN2
    LD #0x1                ; 设置第一个数符号
    ST SIGN1
    JUMP PROCESS_INPUT
SET_SIGN2:
    LD #0x1                ; 设置第二个数符号
    ST SIGN2
    JUMP PROCESS_INPUT

PROCESS_DIGIT:
    LD #0x1
    SUB STATE
    BNE UPDATE_NUM2
    ; 更新第一个数
    LD NUM1
    CALL MULTIPLY_10
    ADD DIGIT
    ST NUM1
    JUMP PROCESS_INPUT
UPDATE_NUM2:
    ; 更新第二个数
    LD NUM2
    CALL MULTIPLY_10
    ADD DIGIT
    ST NUM2
    JUMP PROCESS_INPUT

MULTIPLY_10:              ; 通用×10子程序
    ASL                   ; ×2
    ST TEMP
    ASL                   ; ×4
    ASL                   ; ×8
    ADD TEMP              ; 8x + 2x = 10x
    RET


; 计算模块

PERFORM_MULT:
    ; 符号计算
    LD SIGN1
    CMP SIGN2
    BEQ SIGN_EQUAL
    LD #0x1                ; 符号不同结果为负
    ST SIGN_RES
    JUMP DO_CALC
SIGN_EQUAL:
    LD #0x0               ; 符号相同结果为正
    ST SIGN_RES

DO_CALC:                 ; 绝对值乘法
    CLA
    ST RESULT            ; 结果清零
    LD NUM2
MULT_LOOP:
    CMP #0x0
    BEQ MULT_END
    LD RESULT
    ADD NUM1
    ST RESULT
    LD NUM2
    DEC
    ST NUM2
    JUMP MULT_LOOP
MULT_END:
    RET


; 显示模块

SHOW_RESULT:
    CALL CONVERT_DECIMAL  ; 十进制转换
    ; 显示符号
    LD SIGN_RES
    CMP #0x0
    BEQ SHOW_DIGITS
    LD #0xA              ; '-'符号代码
    ADD #0x70            ; 位置7
    OUT 0x14

SHOW_DIGITS:
    ; 个位（位置0）
    LD DIGIT0
    OUT 0x14
    ; 十位（位置1）
    LD DIGIT1
    ADD #0x10
    OUT 0x14
    ; 百位（位置2）
    LD DIGIT2
    ADD #0x20
    OUT 0x14
    ; 千位（位置3）
    LD DIGIT3
    ADD #0x30
    OUT 0x14
     
    RET

CONVERT_DECIMAL:         ; 十进制转换
    LD RESULT
    ST CURRENT_NUM
    ; 提取个位
    LD CURRENT_NUM
    CALL DIV10
    ST CURRENT_NUM
    LD M_REMAINDER
    ST DIGIT0
    ; 提取十位
    LD CURRENT_NUM
    CALL DIV10
    ST CURRENT_NUM
    LD M_REMAINDER
    ST DIGIT1
    ; 提取百位
    LD CURRENT_NUM
    CALL DIV10
    ST CURRENT_NUM
    LD M_REMAINDER
    ST DIGIT2
    ; 提取千位
    LD CURRENT_NUM
    CALL DIV10
    ST CURRENT_NUM
    LD M_REMAINDER
    ST DIGIT3
    RET

DIV10:                   ; 除以10子程序
    ST TEMP_DIVIDEND
    LD #0x0
    ST TEMP_QUOTIENT
DIV_LOOP:
    LD TEMP_DIVIDEND
    ST TEMP
    SUB #0xA
    BMI DIV_EXIT
    ST TEMP_DIVIDEND
    LD TEMP_QUOTIENT
    INC
    ST TEMP_QUOTIENT
    JUMP DIV_LOOP
DIV_EXIT:
    LD TEMP
    ST M_REMAINDER
    LD TEMP_QUOTIENT
    RET



; 十进制转换
DIGIT0:     WORD 0      ; 个位
DIGIT1:     WORD 0      ; 十位  
DIGIT2:     WORD 0      ; 百位
DIGIT3:     WORD 0      ; 千位
CURRENT_NUM:WORD 0      ; 转换中间值


; 临时变量
TEMP:       WORD 0      ; 通用临时存储
TEMP_DIVIDEND: WORD 0   ; 除法被除数
TEMP_QUOTIENT: WORD 0   ; 除法商
M_REMAINDER: WORD 0     ; 除法余数