#!/bin/bash
# Show code as binary file
# This is anobject file?

./ASMCompiler.py

cd build

nasm -f bin -o test out.asm
#gcc -o asmTrailer nasmFrame64Trailer.o
#rm nasmFrame64Trailer.o
xxd test
rm out.asm
rm -f test
echo Done
