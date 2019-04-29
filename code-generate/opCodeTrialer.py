#!/usr/bin/env python3

from elf.elfLib import mkElf

def addReturnProgram(b):
    # From Tiny. 
    # Close, or close enough, to the (working) 64bit a.out
    #00000000 B801000000                  mov     rax, 1
    #00000005 BB2A000000                  mov     rbx, 42  
    #0000000A CD80                        int     0x80
    # NASM
    # b801 000000
    # bb2a 000000 
    # cd80

    # Parameter to command 'exit'
    # B801000000                  mov     rax, 1
    b.append(int('B8', 16))
    b.extend(int(1).to_bytes(4, byteorder='little'))
    
    # Return numeric code to exit with
    # BB2A000000                  mov     rbx, 42  
    b.append(int('BB', 16))
    b.extend(int('2A', 16).to_bytes(4, byteorder='little'))
    
    # Make system call---to exit
    #CD80                        int     0x80
    b.append(int('CD', 16))
    b.append(int('80', 16))

mkElf(
    outpath='opCodeTrial', 
    bits='64', etype='exec', 
    sections=None, 
    code=addReturnProgram,
    verbose=True
    )
