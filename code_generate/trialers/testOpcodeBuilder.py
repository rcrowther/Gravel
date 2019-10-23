#!/usr/bin/env python3

from opCodeTemplate import x86
from elf.elfLib import mkElf

#! Not building this correctly?
#! try something smaller.
def program(b):
    cb = []

    # print a number
    #! think we need storage space in .bss for this
    #! hence, the elf file builder needs extending.
    x86.build(cb, 100, [99])

    # mov rax, 60
    x86.build(cb, 3, [60])
    # mov rdi, 42
    x86.build(cb, 8, [42])  
    # syscall
    x86.build(cb, 64, [])   

    # ret - simple as it gets...
    #x86.build(cb, 100, [42])
    code = x86.builderToBytes(cb)
    #print('codes printed:')
    #print(code)
    b.extend(code)


mkElf(
    outpath='opCodeTemplateTest', 
    bits='64', etype='exec', 
    sections=None, 
    code=program,
    verbose=True
    )
