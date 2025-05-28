ORG 0x000
V0: WORD    $default, 0x180 ; задаются вектора прерываний
V1: WORD    $int1, 0x180
V2: WORD    $default, 0x180
V3: WORD    $int3, 0x180
V4: WORD    $default, 0x180
V5: WORD    $default, 0x180
V6: WORD    $default, 0x180
V7: WORD    $default, 0x180

ORG 0x3D
X:  WORD    ?   ; переменная х

max:    WORD    0x0029   ; 41,  максимальное значение Х
min:    WORD    0xFFD5   ; -43, минимальное значение Х  
default:    IRET

START:      DI
            CLA
            OUT 0x1  ; запрет прерываний для неиспользуемых устройств
            OUT 0x5
            OUT 0xB
            OUT 0xD
            OUT 0x11
            OUT 0x15
            OUT 0x19
            OUT 0x1D
            LD #0x9 ; загрузка в аккумулятор MR (1000|0001=1001)
            OUT 3   ; разрешение прерываний для ВУ-1
            LD #0xB ; загрузка в аккумулятор MR (1000|0011=1011)
            OUT 7   ; разрешение прерываний для ВУ-3
            EI
main:       DI
            LD  X
            DEC
            DEC
            DEC
            CALL check
            ST  X
            EI
            JUMP  main
int1:       DI
            LD  X
            NOP
            ASL
            ASL
            SUB X
            ADD #3
            NOP
            OUT 2
            EI
            IRET
int3:       DI
            IN  6
            NOP
            AND $X
            ST  X
            LD  #0x1F
            AND $X
            ST  X
            NOP
            EI
            IRET
check:
check_max:  CMP max
            BMI check_min
            JUMP ld_max
check_min:  CMP min
            BPL return
ld_max:     LD max
return:     RET