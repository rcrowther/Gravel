#!/usr/bin/env python3

import subprocess
import sys
#import code_generate.assembly.nasmFrames
#import nasmFrames
from . import nasmFrames
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
        
def codeFrame(headers, sectionData, code):
    return nasmFrames.frame64(headers, sectionData, code)

        
def assemble(buildPath, fileBaseStr, asmFPath, deleteObjectFile, verbose):
    # Run tools to convert an assembly file into an executable.
    # No PIC
    
    # make object
    compilerArgs = "nasm -f elf64 -F stabs".split()
    objectFPath = os.path.join(buildPath, fileBaseStr + ".o")
    compilerArgs.extend(['-o', objectFPath, asmFPath])
    if (verbose):
        print("compiler line:\n    {}".format(" ".join(compilerArgs)))
    subprocessRun(compilerArgs, "Assembler returned non-zero!")
    
    # link
    #! -nostdlib
    #!  -s, --strip-all  Strip all symbols
    #! -fPIC position independant code
    #! -no-pie not position independant code
    #! gcc -Wall -no-pie -o <outputFStr>  nasm64.o
    linkerArgs = "gcc -Wall -no-pie ".split()
    executableFPath = os.path.join(buildPath, fileBaseStr)
    linkerArgs.extend(['-o', executableFPath, objectFPath])
    if (verbose):
        print("linker line:\n    {}".format(" ".join(linkerArgs)))    
    subprocessRun(linkerArgs, "Link and generate (GCC) returned non-zero!")
    
    # tidy
    if (deleteObjectFile):
        os.remove(objectFPath)
        if (verbose):
            print("object file removed")
        
    if (verbose):
        print('done')

#! deleteObjectFile
def frameAssemble(headers, sectionData, code, buildPath, fileBaseStr, deleteAssemblyFile, verbose):
    # Wrap given code in a NASM framework then assemble.
    # Writes out the assembly code to an intermediate file, then runs 
    # the tools to create an executable.
    # No PIC
    #
    # fileBaseStr: has ''asm' appended for the assembly file path
    deleteObjectFile=True
    
    # nasmFrame(code, bss, data, rodata)
    framedCode = codeFrame(headers, sectionData, code)

    # assure build directory
    os.makedirs(buildPath, exist_ok=True)
    
    asmFPath = os.path.join(buildPath, fileBaseStr + ".asm")
    with open(asmFPath, "w") as f:
        f.write(framedCode)

    assemble(buildPath, fileBaseStr, asmFPath, deleteObjectFile, verbose)

    if (deleteAssemblyFile):
        os.remove(asmFPath)
        if (verbose):
            print("assembly file removed")
        
#nasm -f elf64 -F stabs -o nasm64Trailer.o nasmUnlinkedTrailer.asm
##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
#gcc -Wall -fPIC  -s -nostdlib -o nasm64Trailer  nasm64Trailer.o
#ld -s -o nasm64Trailer  nasm64Trailer.o

#rm nasm64Trailer.o

#./nasm64Trailer ; echo $?

#rm nasm64Trailer



########
# TEST #
########
def main():
    fileBaseStr = "nasmFrame64"
    ret = codeFrame("", {"data":"", "bss":"", "rodata": ""}, "")
    print(ret)
    
if __name__== "__main__":
    main()


