; Simple frame for NASM testing.
; Trial compile easily using the script trailer.
; The script will not link, outly output a bin compile. Short, often 
; not working.
BITS 64

global main


;outputLine:
;    ret

main:

    ;mov ebx,  dword [0xffffffff]
    add rax,  qword [0xffffffff]
    ;and     rax,  qword [0xfffffff]
    ;sub     rax,  qword [0xfffffff]
    ;dec     rax  

    ;call outputLine
    ;cmp rax, qword [0xfffffff]
    ;jne else
    ;xor rax, qword [0xfffffff]
    ;xor rax, qword [0xfffffff]
    ;jmp skip
;else:
    ;xor rax, qword [0xfffffff]
    ;xor rax, qword [0xfffffff]    
;skip:
    ;xor rax, qword [0xfffffff]
;    ret
