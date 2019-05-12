#!/bin/bash
# Run some NASM code, for dissembly

nasm -l nasm64Trailer.dis nasmLinkedTrailer.asm
#rm nasmLinkedTrailer


#rm nasm64Trailer.dis
echo look in nasm64Trailer.dis
