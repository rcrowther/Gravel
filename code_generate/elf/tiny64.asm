BITS 64
GLOBAL main
SECTION .text
main:

    ; your program here
    ; mov     bl, 42
    ; xor     eax, eax
    ; inc     eax
    ; int     0x80

    mov     rax, 1
    mov     rbx, 42  
    int     0x80
                
