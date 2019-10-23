
BITS 64
; DEFAULT REL
    
; malloc/free
; import <stdio.h>
; stdOut, printf, etc.
; import <stdio.h>
extern printf
extern malloc
extern free

    
SECTION .data
    
SECTION .bss
    
SECTION .rodata
    

SECTION .text
    
    global main
main:
    ;??? Why only working with the bp push pop wrap?
    push rbp ; Push stack
    
    pop rbp ; Pop stack
    mov rax, 60
    mov rdi, 42
    syscall
    