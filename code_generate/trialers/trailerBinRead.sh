#!/bin/bash
# Run the trailer

# python opCodeTrailer.py
nasm -f bin -o asmTrailer nasmBinTrailer.asm
#gcc -o asmTrailer nasmFrame64Trailer.o
#rm nasmFrame64Trailer.o
xxd asmTrailer
rm -f asmTrailer
echo Done
