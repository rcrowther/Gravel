# teDisassemble the object file
# Useful, as dissassembles code linked from libraries.
# Terribly verbose, and I've not so for cut it down.

gcc -Wall -o test test.c
# -d execuatable sections
# intel intel syntax (not AT&T)
objdump -Mintel -S test
rm test
