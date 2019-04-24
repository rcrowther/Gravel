#!/usr/bin/python3

import collections

# Addresstype
# name code, 
addressTpe = [
("register", ""),
("memory", ""),
("stack", ""),
("heap", "" ),
#"": "",
]

# widths
# Width, SimpleName, Java name, machinecodeName
#? Should have range data too
#? What about floats
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
("signed"),
("unsigned"),
]

# Codes
# OpName, width, operands...
# Extra suggestions (mostly multiple opcodes)
# - locks
# - safe call (with backups)
opCodes = [
# Storage
("mov", "width", "dstTpe"),

# arithmetic
#? Add with carry
("add", "width", "dstTpe", "srcTpe"),
("subtract", "width", "dstTpe", "srcTpe"),
("multiply", "width", "dstTpe", "srcTpe"),
("divide", "width", "dstTpe", "srcTpe"),
("inc", "width", "dstTpe"),
("dec", "width", "dstTpe"),
("neg", "width", "dstTpe"),
("shiftL", "signed?"),
("shiftR", "signed?"),

# logic
("and", "width", "dstTpe"),
("or", "width", "dstTpe"),
("xor", "width", "dstTpe"),
("not", "width", "dstTpe"),


# Type conversion
# (multiple instructions, but seem appropriate for basic numerics?)
# (full set is massive)
("x2x", "width", "width"),

# Object manipulation
# (Java has new, newarray, putfield, sastore---store short in array. 
# Quite rum. Don't want to get into details of objects)
("alloc", "size"),
("free", "size"),


# stack manipulation
#(Java swap dup. Several x84 specialities also)
("pop"),
("push"),

# control transfer
("jmpIfEQ", "width", "dstTpe"),
("jmpIfLT", "width", "dstTpe"),
("jmpIfLTEq", "width", "dstTpe"),
("jmpIfGT", "width", "dstTpe"),
("jmpIfGTEQ", "width", "dstTpe"),
("jmpIfEQ", "width", "dstTpe"),
("jmpIfZero", "width", "dstTpe"),
("jmpIfNotZero", "width", "dstTpe"),

# method calling
# defend or not?
("call", "dstTpe"),
("ret"),
("sysCall", "width", "dstTpe"),
]

