#!/bin/bash
# Run some NASM code, stock

# python opCodeTrailer.py

nasm -f elf64 -F stabs -o nasm64Trailer.o nasmLinkedTrailer.asm
##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
gcc -Wall -fPIC -o nasm64Trailer  nasm64Trailer.o

rm nasm64Trailer.o

./nasm64Trailer ; echo $?

rm nasm64Trailer
