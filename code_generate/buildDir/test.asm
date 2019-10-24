
BITS 64
DEFAULT ABS
    
; malloc/free
; import <stdio.h>
; stdOut, printf, etc.
; import <stdio.h>
extern printf
extern malloc
extern free
extern putchar


    
SECTION .data
    paving: dq 3
SECTION .rodata
    
SECTION .bss
    


SECTION .text
    
    global main
main:
    ;??? Why only working with the bp push pop wrap?
    push rbp ; Push stack
    mov rdi, 64
    call malloc
    mov [paving], rax
    inc qword [paving+8*3]
    inc qword [paving+8*3]
    inc qword [paving+8*3]
    mov rdi, [paving+8*3]
    call putchar
    mov rdi, 10
    call putchar
    mov rdi, [paving]
    call free
    pop rbp ; Pop stack
    mov rax, 60
    mov rdi, 42
    syscall
    