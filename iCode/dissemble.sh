#!/bin/bash
# Print some NASM code with detail

./ASMCompiler.py

cd build

nasm -f elf64 -F stabs -o test.o out.asm
gcc -Wall -fPIC -o test  test.o

rm test.o

# -d execuatable sections
# intel intel syntax (not AT&T)
objdump -Mintel -d test

rm out.asm
rm test
