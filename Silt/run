#!/bin/bash
# Run some NASM code, stock

cd build
nasm -f elf64 -F stabs -o test.o out.asm

if [ $? -gt 0 ]; then
    echo "NASM: compile error"
    exit 1;
fi

##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
#gcc -Wall -fPIC -o test  test.o
gcc -no-pie -o test  test.o

if [ $? -gt 0 ]; then
    echo "GGC: link error"
    exit 1;
fi

# rm out.asm
rm test.o

./test

sysExit=$?
if [ "$sysExit" -gt 0 ]; then
    echo "BASH: executable run error"
    echo "Run exit code: $sysExit";
    rm test
    exit $?;
fi

printf "\ndone\n"

rm test
