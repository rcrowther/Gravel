#!/usr/bin/env python3

# Commandline invokation of ElfLib

# debian ''elfutils' contains eu-readelf, and eu-elflint, among others.
# Tiny ELF discussion on linking and tables,
# http://www.muppetlabs.com/~breadbox/software/tiny/somewhat.html
#import subprocess
#import os
import sys
import stat
import argparse
from elfLib import mkElf, ETypeToCode

#? Some consistency checks e.g. only shared data has a section header 
# file
# From Spec:
# Files used to build a process image (execute a program) must have a 
# program header table; relocatable files do not need one. 
# Files used during linking must have a section header table; other 
# object files may or may not have one

#? Now up to 32Bit header adjustments...
#? and need to test on Intel machines

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
    
    

parser = argparse.ArgumentParser(description='A runner for ELFWrite.')
parser.add_argument('-addCode', 
    action="store_true",
    dest="addCode",
    help='Add a snippet of code to the ELF to return 42.'
    )
    
parser.add_argument('-bits', 
    choices=['64', '32'], 
    default='64',  
    help='Choose a bit-width (default=64).'
    )

parser.add_argument('-type',
    choices=ETypeToCode.keys(), 
    default = 'exec',
    dest= 'etype',
    #choices=['rel', 'exec', 'dyn', 'core'], 
    help='Type (or intended usage) of the file.',
    )

parser.add_argument('-verbose', 
    action="store_true",
    help='Print data on the process.'
    )
        
# Only needed for shared objects.
# Do not implement yet? 
parser.add_argument('-sections',
    choices=['rodata', 'lrodata', 'data', 'ldata', 'bss', 'tdata', 'tbss', 'lbss', 'debug', 'comment'], 
    nargs='*',
    help='Add sections to the ELF.',
    )
    
parser.add_argument('-outfile', 
    type=argparse.FileType('wb'),
    nargs='?', 
    default='elfTest'
    )

args = parser.parse_args()
#print (args.verbose)

# Do this all the time until valid alternatives.
givenCode = addReturnProgram
if (args.addCode):
    givenCode=addReturnProgram
    
mkElf(
    args.outfile, 
    args.bits, 
    args.etype, 
    args.sections, 
    givenCode, 
    args.verbose
    )
