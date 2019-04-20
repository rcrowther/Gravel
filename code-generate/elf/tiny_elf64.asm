
; Undone. Untried. Not  enough info.

BITS 64
            ;org     0x08048000
            org     0x00400000

ehdr:                                                 ; Elf64_Ehdr
            db      0x7F, "ELF", 2, 1, 1, 0         ;   e_ident
    times 8 db      0
            dw      2                               ;   e_type
            dw      62                              ;   e_machine
            dd      1                               ;   e_version
            dq      _start                          ;   e_entry
            dq      phdr - $$                       ;   e_phoff
            dq      0                               ;   e_shoff
            dd      0                               ;   e_flags
            dw      ehdrsize                        ;   e_ehsize
            dw      phdrsize                        ;   e_phentsize
            dw      1                               ;   e_phnum
            dw      0                               ;   e_shentsize
            dw      0                               ;   e_shnum
            dw      0                               ;   e_shstrndx

ehdrsize      equ     $ - ehdr

phdr:                                                 ; Elf32_Phdr
            dd      1                               ;   p_type
            dd      5                               ;   p_flags
            dq      0                               ;   p_offset
            dq      $$                              ;   p_vaddr
            dq      $$                              ;   p_paddr
            dq      filesize                        ;   p_filesz
            dq      filesize                        ;   p_memsz
            dq      0x1000                          ;   p_align

phdrsize      equ     $ - phdr

_start:

    ; your program here
    ; mov     bl, 42
    ; xor     eax, eax
    ; inc     eax
    ; int     0x80

    mov     eax, 1
    mov     ebx, 42  
    int     0x80
    
filesize      equ     $ - $$
