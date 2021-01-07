#!/bin/bash
# NASM's input with detail

./ASMCompiler.py

cd build

nasm -l out.tidy out.asm
#rm nasmLinkedTrailer

rm out.asm
rm out
#rm nasm64Trailer.dis
cat out.tidy
rm out.tidy
