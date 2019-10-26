
BITS 64
DEFAULT REL
    
extern printf
    
SECTION .data
    msg: db 'Hi! ', 0h
    ;msg db 'Hello, world!' ;string to be printed
    
    
SECTION .bss
    
SECTION .rodata
    asciiMinus db 45
    asciiPlus db 43
    asciiLF db 10
    ; ASCII 0, 1, 2.... 
    asciiNumerics db 48, 49, 50, 51, 52, 53, 54, 55, 56, 57
    ;! Also hex...
    ; 0123456789ABCDEF
    fmtInt: db "%d", 10, 0 ; null terminated numeric format str.	
    fmtFloat: db "%g", 10, 0 ; null terminated numeric format str.	
    fmtStr: db "%s", 10, 0 ; null terminated codepoint format str.	

SECTION .text
    
    global main
main:
    push rbp ; Push stack
    
    push rdi
    push rsi
    mov rdi, fmtStr
	mov	rsi, msg
    call printf
    pop rdi
    pop rsi
    
    pop rbp ; Push stack
    mov rax, 60
    mov rdi, 42
    syscall
    