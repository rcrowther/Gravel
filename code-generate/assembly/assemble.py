#!/usr/bin/env python3

import subprocess
import sys
from assembly import nasmFrames
import os

#! add filehandling
#! sort out errors
def subprocessRun(args, errorMsg):
    try:
        subprocess.run(
            args, 
            stdin=None, input=None, stdout=None, 
            stderr=subprocess.PIPE, 
            universal_newlines=True, 
            shell=False, 
            timeout=None, 
            check=True
            )
    except subprocess.CalledProcessError  as e:
        # Non-zero oputput
        print("[Error] {}".format(errorMsg))
        #print("    {}".format(e.stderr.decode("utf-8") ))
        print("    {}".format(e.stderr))
        #! wont exit?
        sys.exit()
        


def assemble(inputFStr, outputFStr):
    # Run tools to convert an assembly file into an executable.
    
    # assemble
    compilerArgs = "nasm -f elf64 -F stabs -o nasm64.o".split()
    #compilerArgs = "nasm -f elf64 -F stabs".split()
    args = compilerArgs.append(inputFStr)
    subprocessRun(compilerArgs, "Assembler returned non-zero!")
    
    # link
    #! -nostdlib
    #!  -s, --strip-all  Strip all symbols
    #! fPIC position independant code
    linkGenerateArgs = "gcc -Wall -no-pie ".split()
    # add targets
    linkGenerateArgs.extend(['-o', outputFStr, "nasm64.o"])
    #print(str(linkGenerateArgs))
    subprocessRun(linkGenerateArgs, "Link and generate (GCC) returned non-zero!")
    
    # tidy
    args = ["rm", "nasm64.o"]
    subprocessRun(args, "Remove .o returned non-zero!")
    
    print('done')

def frameAssemble(code, fileBaseStr, deleteAssemblyFile):
    # Wrap given code in a NASM framework then assemble.
    # Writes out the assembly code to an intermediate file, then runs 
    # the tools to create an executable.
    # 
    # fileBaseStr: has asm appended for the assembly file path
    
    # nasmFrame(code, bss, data, rodata)
    framedCode = nasmFrames.frame64(code, bss="", data="", rodata="")
    outF = fileBaseStr + ".asm"
    with open(outF, "w") as f:
        f.write(framedCode)
    assemble(outF, fileBaseStr)
    if (deleteAssemblyFile):
        os.remove(outF)
#nasm -f elf64 -F stabs -o nasm64Trailer.o nasmUnlinkedTrailer.asm
##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
#gcc -Wall -fPIC  -s -nostdlib -o nasm64Trailer  nasm64Trailer.o
#ld -s -o nasm64Trailer  nasm64Trailer.o

#rm nasm64Trailer.o

#./nasm64Trailer ; echo $?

#rm nasm64Trailer



fileBaseStr = "nasmFrame64"

# wrap input in frame
frameAssemble("", fileBaseStr, False)
