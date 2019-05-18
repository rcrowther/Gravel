#!/bin/bash
# Run some NASM code, stock

# python opCodeTrailer.py

nasm -f elf64 -F stabs -o nasm64Trailer.o nasmUnlinkedTrailer.asm
##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
#gcc -Wall -fPIC  -s -nostdlib -o nasm64Trailer  nasm64Trailer.o
ld -s -o nasm64Trailer  nasm64Trailer.o

rm nasm64Trailer.o

./nasm64Trailer ; echo $?

#rm nasm64Trailer
