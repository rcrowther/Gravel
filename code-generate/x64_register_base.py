#!/usr/bin/python3

import collections


#bit_widths 
WIDTH64 = 1000
WIDTH32 = 1001
WIDTH16 = 1002
WIDTH8 = 1003


BitWidth = collections.namedtuple('BitWidth', 'width microsoft absolute') 
bit_widths = {
  # 64 bit (qword), 32 bit (dword), 16bit (word), 8bit (byte)
  # microsoft, absolute
  BitWidth(64, 'qword', '64bit'),
  BitWidth(32, 'dword', '32bit'),
  BitWidth(16, 'word', '16bit'),
  BitWidth(8, 'byte', '8bit'),
}

# tokens
RAX = 0
RBX = 1
RCX = 2
RDX = 3
RBP = 4
RSI = 5
RDI = 6
RSP = 7

# second 8 64-bit registers
R8 = 8
R9 = 9
R10 = 10
R11 = 11
R12 = 12
R13 = 13
R14 = 14
R15 = 15

# 80bit. Aliased MMX
FPR0 = 20
FPR1 = 21
FPR2 = 22
FPR3 = 23
FPR4 = 24
FPR5 = 25
FPR6 = 26
FPR7 = 27

XMM0 = 30
XMM1 = 31
XMM2 = 32
XMM3 = 33
XMM4 = 34
XMM5 = 35
XMM6 = 36
XMM7 = 37
XMM8 = 38
XMM9 = 39
XMM10 = 40
XMM11 = 41
XMM12 = 42
XMM13 = 43
XMM14 = 44
XMM15 = 45

# auto registers
RIP = 50
RFLAGS = 51

# flags
CF = 61
PF = 62
AF = 63
ZF = 64
SF = 65
OF = 66
DF = 67
ID = 68

## general register aliases
# 32bit
EAX = 100
EBX = 101
ECX = 102
EDX = 103
EBP = 104
ESI = 105
EDI = 106
ESP = 107
R8D = 108
R9D = 109
R10D = 110
R11D = 111
R12D = 112
R13D = 113
R14D = 114
R15D = 115

# 16bit
AX = 200
BX = 201
CX = 202
DX = 203
R8W = 204
R9W = 205
R10W = 206
R11W = 207
R12W = 208
R13W = 209
R14W = 210
R15W = 211

# 8bit low
AL = 301
BL = 302
CL = 303
DL = 304
R8B = 305
R9B = 306
R10B = 307
R11B = 308
R12B = 309
R13B = 310
R14B = 311
R15B = 312

# 8 bit high
AH= 400
BH= 401
CH= 402
DH= 403

## floating point aliases
MMX0 = 500
MMX1 = 501
MMX2 = 502
MMX3 = 503
MMX4 = 504
MMX5 = 505
MMX6 = 506
MMX7 = 507
 
 
## Register groups  
GR = collections.namedtuple('GeneralRegister', 'sym name description')
general_registers = {
    # first 8 64-bit registers
    RAX : GR('RAX', 'GenA', 'General Register (accumulator)'), 
    RBX: GR('RBX', 'GenB','General Register B (index and offsets)'), 
    RCX: GR('RCX', 'GenC', 'General Register Counter'), 
    RDX: GR('RDX', 'GenD', 'General Register D (port addressing)'), 
    RBP: GR('RBP', 'BasePointer', 'Stack Base Pointer '), 
    RSI: GR('RSI', 'GenSI', 'General Register (source in streams and strings)'), 
    RDI: GR('RDI', 'GenDI', 'General Register (destination in streams and strings)'), 
    RSP: GR('RSP', 'StackPointer', 'Stack pointer'),
    
    # second 8 64-bit registers
    R8: GR('R8', 'Gen8', 'General Register 8'),
    R9: GR('R9', 'Gen9', 'General Register 9'),
    R10: GR('R10', 'Gen10', 'General Register 10'),
    R11: GR('R11', 'Gen11', 'General Register 11'),
    R12: GR('R12', 'Gen12', 'General Register 12'),
    R13: GR('R13', 'Gen13', 'General Register 13'),
    R14: GR('R14', 'Gen14', 'General Register 14'),
    R15: GR('R15', 'Gen15', 'General Register 15'),
}


GRA = collections.namedtuple('GeneralRegisterAlias', 'Width64 Width32 Width16 Width8L Width8H')
general_purpose_aliases = {
    # first 8 64-bit registers
    # 64 bit (qword), 32 bit (dword), 16bit (word), 8bit (byte)
    RAX : GRA(RAX, EAX, AX, AL, AH),
    RBX: GRA(RBX, EBX, BX, BL, BH),
    RCX: GRA(RCX, ECX, CX, CL, CH),
    RDX: GRA(RDX, EDX, DX, DL, DH),
    RBP: GRA(RBP, EBP, None, None, None),
    RSI: GRA(RSI, ESI, None, None, None),
    RDI: GRA(RDI, EDI, None, None, None),
    RSP: GRA(RSP, ESP, None, None, None),
    R8: GRA(R8, R8D, R8W, R8B, None),
    R9: GRA(R9, R9D, R9W, R9B, None),
    R10: GRA(R10, R10D, R10W, R10B, None),
    R11: GRA(R11, R11D, R11W, R11B, None),
    R12: GRA(R12, R12D, R12W, R12B, None),
    R13: GRA(R13, R13D, R13W, R13B, None),
    R14: GRA(R14, R14D, R14W, R14B, None),
    R15: GRA(R15, R15D, R15W, R15B, None),
}



FR = collections.namedtuple('FloatingPointRegister', 'sym name description')
floating_point_registers = {
    # 80bit. Aliased MMX
    FPR0: FR('FPR0', 'Float0', 'FP Register 0'),
    FPR1: FR('FPR1', 'Float1', 'FP Register 1'),
    FPR2: FR('FPR2', 'Float2', 'FP Register 2'),
    FPR3: FR('FPR3', 'Float3', 'FP Register 3'),
    FPR4: FR('FPR4', 'Float4', 'FP Register 4'),
    FPR5: FR('FPR5', 'Float5', 'FP Register 5'),
    FPR6: FR('FPR6', 'Float6', 'FP Register 6'), 
    FPR7: FR('FPR7', 'Float7', 'FP Register 7'),
}

FA = collections.namedtuple('FloatRegisterAlias', 'MMX')
floating_point_aliases = {
    FPR0: FA(MMX0),
    FPR1: FA(MMX1),
    FPR2: FA(MMX2),
    FPR3: FA(MMX3),
    FPR4: FA(MMX4),
    FPR5: FA(MMX5),
    FPR6: FA(MMX6),
    FPR7: FA(MMX7),
}

SR = collections.namedtuple('SSERegister', 'sym name description') 
mmx_registers = {
    # 128bit SSE
    XMM0: SR('XMM0', 'SSE0', 'SSE Register 1'),
    XMM1: SR('XMM1', 'SSE1', 'SSE Register 2'),
    XMM2: SR('XMM2', 'SSE2', 'SSE Register 3'),
    XMM3: SR('XMM3', 'SSE3', 'SSE Register 4'),
    XMM4: SR('XMM4', 'SSE4', 'SSE Register 5'),
    XMM5: SR('XMM5', 'SSE5', 'SSE Register 6'),
    XMM6: SR('XMM6', 'SSE6', 'SSE Register 7'),
    XMM7: SR('XMM7', 'SSE7', 'SSE Register 8'),
    XMM8: SR('XMM8', 'SSE8', 'SSE Register 9'),
    XMM9: SR('XMM9', 'SSE9', 'SSE Register 10'),
    XMM10: SR('XMM10', 'SSE10', 'SSE Register 11'),
    XMM11: SR('XMM11', 'SSE12', 'SSE Register 12'),
    XMM12: SR('XMM12', 'SSE12', 'SSE Register 13'),
    XMM13: SR('XMM13', 'SSE13', 'SSE Register 14'),
    XMM14: SR('XMM14', 'SSE14', 'SSE Register 15'),
    XMM15: SR('XMM15', 'SSE15', 'SSE Register 16'),
}

AR = collections.namedtuple('AutoRegister', 'sym name description') 
auto_registers = { 
    RIP: AR('RIP', 'InsPtr', 'Instruction pointer'),
    RFLAGS: AR('RFLAGS', 'Flags', 'Flag register'),
}

FD = collections.namedtuple('FlagData', 'offset sym name description') 
flags = {
    #token, bit offset, common name, description
    CF: FD(0, 'CF',	'Carry', 'Operation generated a carry or borrow'),
    PF: FD(2, 'PF',	'Parity', "Last byte has even number of 1's, else 0"),
    AF: FD(4, 'AF',	'Adjust', 'Denotes Binary Coded Decimal in-byte carry'),
    ZF: FD(6, 'ZF',	'Zero', 'Result was 0'),
    SF: FD(7, 'SF',	'Sign', 'Most significant bit of result is 1'),
    OF: FD(11, 'OF',	'Overflow', 'Overflow on signed operation'),
    DF: FD(10, 'DF',		'Direction', 'Direction string instructions operate (increment or decrement)'),
    ID: FD(21, 'ID',	'Identification', 'Changeability denotes presence of CPUID instruction'),
}
