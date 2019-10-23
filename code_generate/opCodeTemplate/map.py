#!/usr/bin/python3

import collections

# Addresstype
# name code, 
addressTpe = [
? : "register", ""),
? : "memory", ""),
? : "stack", ""),
? : "heap", "" ),
#"": "",
]

# widths
# Width, SimpleName, Java name, machinecodeName
#? Should have range data too
#? What about floats
#? What about enums
#? is width plain width, or numeric data type e.g. floats
bitWidth = [
(128, "128Bit", "Huge", "ddq"),
(64, "64Bit", "Long", "dq"),
(32, "32Bit", "Int", "dd"),
(16, "16Bit", "Short", "dw"),
(8, "8Bit", "", "db"),
#(4, "4Bit", "", ""),
(1, "1Bit", "Byte", "b"),
]

# Signing
sign = [
0 : "signed"),
1 : "unsigned"),
]

# Codes
# OpName, width, operands...
# Extra suggestions (mostly multiple opcodes)
# - locks
# - safe call (with backups)
# Table needs to be expanded?
opCodes = {
# Storage
? : "mov", "width", "dstTpe"),

# arithmetic
#? Add with carry
0 : "add", "width", "dstTpe", "srcTpe"),
1 : "subtract", "width", "dstTpe", "srcTpe"),
2 : "multiply", "width", "dstTpe", "srcTpe"),
3 : "divide", "width", "dstTpe", "srcTpe"),
4 : "inc", "width", "dstTpe"),
5 : "dec", "width", "dstTpe"),
6 : "neg", "width", "dstTpe"),
7 : "shiftL", "signed?"),
8 : "shiftR", "signed?"),

# Logic
20 : "and", "width", "dstTpe"),
21 : "or", "width", "dstTpe"),
22 : "xor", "width", "dstTpe"),
23 : "not", "width", "dstTpe"),


# Type conversion
# ? : multiple instructions, but seem appropriate for basic numerics?)
# ? : full set is massive)
30 : "x2x", "width", "width"),

# Object manipulation
# ? : Java has new, newarray, putfield, sastore---store short in array. 
# Quite rum. Don't want to get into details of objects)
40 : "alloc", "size"),
41 : "free", "size"),


# stack manipulation
#? : Java swap dup. Several x84 specialities also)
50 : "pop"),
51 : "push"),

# control transfer
60 : "jmpIfEQ", "width", "dstTpe"),
61 : "jmpIfLT", "width", "dstTpe"),
62 : "jmpIfLTEq", "width", "dstTpe"),
63 : "jmpIfGT", "width", "dstTpe"),
64 : "jmpIfGTEQ", "width", "dstTpe"),
65 : "jmpIfEQ", "width", "dstTpe"),
66 : "jmpIfZero", "width", "dstTpe"),
67 : "jmpIfNotZero", "width", "dstTpe"),
68 : 'if0', 'lock'),
69 : 'if0else', 'block1', 'block2'),
#? : 'bOnX', 'blocks'), # blocks is a list of blocks

# method calling
# defend or not?
70 : "call", "dstTpe"),
71 : "ret"),
72 : "sysCall", "width", "dstTpe"),
}

