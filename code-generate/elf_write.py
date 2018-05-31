


# http://www.muppetlabs.com/~breadbox/software/tiny/teensy.html
#def write_file(filename="tiny.asm", code = ''):
  ##org     0x08048000
    #code = """
                #mov     bl, 42
                #xor     eax, eax
                #inc     eax
                #int     0x80
                #"""
                
    #d = """BITS 64
  

                #org     0x08048000                      ;? necessary 

  #ehdr:                                                 ; Elf64_Ehdr
                #db      0x7F, "ELF", 2, 1, 1, 0         ;   e_ident (64-bit)
        #times 8 db      0
                #dw      2                               ;   e_type 
                #dw      0x3E                            ;   e_machine (64-bit)
                #dd      1                               ;   e_version
                #dq      _start                          ;   e_entry 0x8048054
                #dq      phdr - $$                       ;   e_phoff 64
                #dq      0                               ;   e_shoff
                #dd      0                               ;   e_flags
                #dw      ehdrsize                        ;   e_ehsize 64
                #dw      phdrsize                        ;   e_phentsize 56
                #dw      1                               ;   e_phnum
                #dw      0                               ;   e_shentsize
                #dw      0                               ;   e_shnum
                #dw      0                               ;   e_shstrndx
  
  #ehdrsize      equ     $ - ehdr
  
  #phdr:                                                 ; Elf64_Phdr
                #dd      1                               ;   p_type (PT_LOAD)
                #dd      5                               ;   p_flags
                #dq      0                               ;   p_offset
                #dq      $$                              ;   p_vaddr 0x0000000008048000 0x0000000000000080
                #dq      $$                              ;   p_paddr 0x08048000
                #dq      filesize                        ;   p_filesz 0x0005b
                #dq      filesize                        ;   p_memsz 0x0005b
                #dq      0x1000                          ;   p_align
  
  #phdrsize      equ     $ - phdr
  

  #_start:
         #{program}

  #filesize      equ     $ - $$
  #""".format(program=code)
  
    #with open(filename, "w") as f:
        #f.write(d)


import subprocess
import os

#def compile(code, filename = "tiny"):
    #asm_filename = filename + '.asm'
    #write_file(asm_filename)
    #subprocess.call(["nasm", "-f", "bin", "-o", filename, asm_filename])
    #os.remove(asm_filename)
    #subprocess.call(["chmod", "+x", filename])


def write_file(filename="tiny.asm", code = ''):
    code = """
                mov     bl, 42
                xor     eax, eax
                inc     eax
                int     0x80
                """
    d = """
    BITS 64
    
    
    SECTION .data
        {data}
        
    SECTION .bss
        
    SECTION .text
        
    global main
    main:
    
       {program}
    """.format(
        data = '',
        program=code
        )

  
    with open(filename, "w") as f:
        f.write(d)


def compile(code, filename = "tiny"):
    asm_filename = filename + '.asm'
    write_file(asm_filename)
    subprocess.call(["nasm", "-f", "elf64", asm_filename])
    os.remove(asm_filename)
    obj_filename = filename + '.o'
    subprocess.call(["gcc", "-o", filename, obj_filename])
    os.remove(obj_filename)
