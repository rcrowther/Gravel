import tpl_types as Type

# Strictly speaking, this is NASM database, but I belive it would be 
# useful for MASM. Anyhow, I only intend to use NASM. Enough is enough, 
# and no more.

# DB, DW, DD, DQ, DT, DO, DY and DZ
#NB "do" will not take an integer?

class WidthInfo():
    def __init__(self, bitName, ASMName, ASMAbreviation, byteCount):
        self.bitName = bitName
        self.ASMName = ASMName
        self.ASMAbv = ASMAbreviation
        self.byteCount = byteCount

WidthInfoMap = {
    # 256
    Type.Bit8   : WidthInfo("bit8",   "byte", "db", 1),
    # 32766
    Type.Bit16  : WidthInfo("bit16",  "word", "dw", 2),
    # 2,147,483,647
    Type.Bit32  : WidthInfo("bit32",  "dword", "dd", 4),
    Type.Bit64  : WidthInfo("bit64",  "qword", "dq", 8),
    Type.Bit128 : WidthInfo("bit128", "oword", "do", 16),
    Type.Bit32F  : WidthInfo("bit32 float",  "dword", "dd", 4),
    Type.Bit64F  : WidthInfo("bit64 float",  "qword", "dq", 8),
}

TypesToASMName = {tpe:v.ASMName for tpe,v in WidthInfoMap.items()}
TypesToASMAbv = {tpe:v.ASMAbv for tpe,v in WidthInfoMap.items()}
