# Various frameworks for NASM compiling.


Frame64PIC = """
BITS 64
DEFAULT REL

; malloc/free
; import <stdlib.h>
; stdOut, printf, etc.
; import <stdio.h>
extern malloc
extern free
; additional externs
{}

SECTION .data
    msg: db 'Hi! ', 0h
    ;msg db 'Hello, world!' ;string to be printed
    {}

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

SECTION .bss
    {}
    
SECTION .text
{}
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

def frame64(
        externs, 
        data, 
        rodata, 
        bss, 
        text,
        code
    ):
    return """
BITS 64
DEFAULT ABS

; externs
{externs}
    
SECTION .data
{data}
SECTION .rodata
{rodata}
SECTION .bss
{bss}
SECTION .text
{text}
    global main

{code}
    """.format(
        externs = externs,
        data = data,
        rodata = rodata,
        bss = bss,
        text = text,
        code = code,
    )
    
def frame64Alloc(
        externs, 
        data, 
        rodata, 
        bss, 
        text,
        code
    ):
    return """
BITS 64
DEFAULT ABS
;  DEFAULT REL
    
; stdOut, printf, etc.
; import <stdio.h>
; from <stdlib.h>
extern malloc
extern calloc
extern realloc
extern free
; from <string>
extern memmove
; additional externs
{externs}
    
SECTION .data
{data}
SECTION .rodata
{rodata}
SECTION .bss
{bss}
SECTION .text
{text}
    global main

{code}
    """.format(
        externs= externs,
        data= data,
        rodata= rodata,
        bss= bss,
        text= text,
        code= code,
    )
