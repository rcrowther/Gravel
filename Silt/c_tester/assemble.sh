#!/bin/bash

# List the assembler for the test file.
# -S compile only
gcc -masm=intel -S test.c -o test.asm
cat test.asm
rm test.asm


