# Simple frameworks for NASM compiling.

#def frame64(code, bss, data, rodata):
#    return "BITS 64\nDEFAULT REL\n\nSECTION .data\n{}\n\nSECTION .bss{}\n\nSECTION .rodata{}\nSECTION .text\n\nglobal main\nmain:\n{}\nmov    rax, 60\nmov   rdi, 42\nsyscall".format(data, bss, rodata, code)

def frame64test(code, bss, data, rodata):
    return """
BITS 64
; DEFAULT REL
    
extern printf
    
SECTION .data
    msg: db 'Hi! ', 0h
    ;msg db 'Hello, world!' ;string to be printed
    {}
    
SECTION .bss{}
    
SECTION .rodata{}
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
    ;??? Why only working with the bp push pop wrap?
    push rbp ; Push stack
    {}
    pop rbp ; Pop stack
    mov rax, 60
    mov rdi, 42
    syscall
    """.format(data, bss, rodata, code)


Frame64 = """
BITS 64
; DEFAULT REL
    
; malloc/free
; import <stdio.h>
; stdOut, printf, etc.
; import <stdio.h>
extern printf
extern malloc
extern free
{}
    
SECTION .data
    {}
SECTION .bss
    {}
SECTION .rodata
    {}

SECTION .text
    
    global main
main:
    ;??? Why only working with the bp push pop wrap?
    push rbp ; Push stack
    {}
    pop rbp ; Pop stack
    mov rax, 60
    mov rdi, 42
    syscall
    """
