#!/usr/bin/env python3

import nasmFrames

externs = ""
data = ""
rodata = ""
bss = ""
text = ""
code = """
    mov rsi, print64Fmt
    mov rdi, rax
    call printf
"""
o = nasmFrames.frame64CAlloc(
        externs, 
        data, 
        rodata, 
        bss, 
        text,
        code
    )

with open('build/out.asm', 'w') as f:
    f.write(o)
