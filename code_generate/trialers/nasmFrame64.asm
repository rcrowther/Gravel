BITS 64
DEFAULT REL

SECTION .data


SECTION .bss

SECTION .rodata
SECTION .text

global main
main:

mov    rax, 60
mov   rdi, 42
syscall