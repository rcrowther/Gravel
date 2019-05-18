#!/usr/bin/env python3

from opCodeTemplate import x86ASM
from assembly import assemble

#! Not building this correctly?
#! try something smaller.
def program(b):

    # print a number
    #! think we need storage space in .bss for this
    #! hence, the elf file builder needs extending.
    #x86ASM.build(cb, 100, [99])

    #x86ASM.build(b, 1020, [])

    # mov rax, 60
    #x86ASM.build(b, 3, [60])
    # mov rdi, 42
    #x86ASM.build(b, 8, [52])  
    # syscall
    #x86ASM.build(b, 64, [])   

    # printInt
    #x86ASM.build(b, 1020, ['asciiMinus'])  
    # printlnStr 
    x86ASM.build(b, 1025, ['msg'])   

    # ret - simple as it gets...
    #x86ASM.build(cb, 100, [42])
    #print('codes printed:')
    #print(code)

b = []
program(b)
code = '\n'.join(b)
# if verbose:
print(str(code))
fileBaseStr = "frameASMTest"
assemble.frameAssemble(code, fileBaseStr, False)
