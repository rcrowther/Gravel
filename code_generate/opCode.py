#!/usr/bin/env python3

import collections

from Common import byteSpace

# summoning bytecode
#? These sit at under than the full instructions.
#? machine code nuggets.
#? Looking at them to see how the fuller instructions need flexing.
#? Also, assumes knows what it is doing with regs vs. stack

CodeData = {
# code      params                 NB
# allocNum  size/representation    reg or stack
# offsets/reg, isReg, size stored in index table
    "localAlloc": "localData, size",
    "localSet" : "localData, idx",
    "localGet" : "localData, idx",
    #"localFree": "",

# "stackFrame",
# "stackUnframe",

# "heapAlloc",
# "heapFree",


# # initNum   size/representation    reg or stack
# # Common
# "NumLabelSet",
# # offset
# "NumSet",

# # Strings
# "strSetStack",
# "strSetCommon",

# # Arrays
# # set as space?

# # Clutches
# # set as space?


# # Compares NB include null?
# "gt",
# "gte",
# "lt",
# "lte",
# "eq",
# "neq",

# # Conversion


# # Arithmetic    NB includes special float etc.
# "add",
# "sub",
# "mult",
# "div",
# "dec",
# "inc",
# "neg",

# # Bit logic
# "and",
# "or",
# "nor",
# "not",

# # Jumps
# "jmpGt",
# "jmpLt",
# "jmpGte",
# "jmpLte",
# "jmpEq",
# "jmpNe",
# "jmp",

# Calls
    "cParamSet": "idx, src",
    "cParamGet": "idx, dst", 
    "cParamSrc": "idx",
    "cReturnSet": "src",
    "cReturnGet": "dst",
    "cReturnSrc": "",
    "funcOpen": "label",
    "funcClose": "",
    "funcCall": "label",
}

IdToName = [ data for data in enumerate(CodeData)]

###
# C Params
#
cParameterRegisters = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
    
def cParamSet(idx, src):
    if (idx < 6):
        return "mov {}, {}".format(cParameterRegisters[idx], src)
    return "push {}".format(v)

def cParamGet(idx, dst):
    if (idx < 6):
        return "mov {}, {}".format(dst, cParameterRegisters[idx])
    return "pop {}".format(dst)
    
def cParamSrc(idx):
    if (idx < 6):
        return "{}".format(cParameterRegisters[idx])
    return "[rsp+8*{}]".format(idx-6)
    
def cReturnSet(b, src):
    b.append("mov rax, {}".format(src))

def cReturnGet(dst):
    return "mov {}, rax".format(dst)

def cReturnSrc():
    return "rax"

###
# Local
#
LocalData = collections.namedtuple('LocalData', 'size, isReg, location')

cRegisters = [
    #param registers
    #"rdi",
    #"rsi",
    #"rdx",
    #"rcx",
    #"r8",
    #"r9",
    # other usable rigisters
    # ok rax-rbx
    #"rax",
    "rbx",
    #"r10",
    #"r11",
    # ok r12-15
    "r12",
    # stack ptr
    "r13",
    "r14",
    "r15",
    ]

###
# Local
#
#? Note the param count must nt only clear
    # provided params, but any params used in calls within the 
    # callblock.
class Local:
    # Manage local variables
    # The class treats params as a local vaiable too, hence the param 
    # count required on init(). Note the param count must nt only clear
    # provided params, but any params used in calls within the 
    # callblock.
    # The only rreturn is the register name of the local, or an error
    # if the local is not on a regiater. From there on you need to use 
    # other methods.
    # Takes a var width, currently unused.
    def __init__(self):
        # @paramCount number of parameters passed by register to this 
        # callBlock
        #self.paramCount = paramCount
        self.regPnt = 0
        self.offset = 0
        # idx, size, isReg, loc (offset/reg)
        self.data = []
        # bulk vars data with parameter data
        #for idx, p in enumerate(range(0, paramCount)):
        #    self.data.append(LocalData(byteSpace.bit64, True, cRegisters[idx]))
            
    def alloc(self, size):
        idx = len(self.data)
        isReg = ((size <= byteSpace.bit64) and (self.regPnt < len(cRegisters)))
        
        if (isReg):
            location = cRegisters[self.regPnt]
            self.regPnt += 1
        if (not isReg):
            self.offset -= size
            location = self.offset
        self.data.append(LocalData(size, isReg, location))

    def __call__(self, idx):
        # returns a register, or exception
        #nonParamIdx = self.paramCount + idx
        if (idx >= len(self.data)):
            raise IndexError("Local var index exceeds available. vars allocated:{}, idx requested: {}".format(len(self.data), idx))
        d = self.data[idx]
        if (not d.isReg):
           raise ValueError("Local var is not on a register, but on stack (needs a swap for location usage) idx:{}; data:{}".format(idx,d))
        return d.location
        
    def __repr__(self):
        return "Local(regPnt:{}, offset:{}, data:{})".format(
            self.regPnt, self.offset, self.data
            )


def localSet(b, local, src):
    # @src can be a register/offset etc.
    b.append("mov {}, {}".format(local, src))
    
def localAddrSet(b, local, src):
    # uses the local as an address
    # @src must be literal, label or register
    b.append("mov qword [{}], {}".format(local, src))

def localAddrGet(b, local, dst):
    # treat the local as an address to retrieve from
    # @dst must be literal, label or register
    b.append("mov {}, [{}]".format(dst, local))

def localAddrSrc(local):
    # treat the local as an address to retrieve from
    return "[{}]".format(local)
        
def localOffset(local, offset):
    # format an offset fragment
    return "qword [{}+{}]".format(local, offset)
        
###
# Malloc
#

def _malloc(byteSize):
    return [
        cParamSet(0, byteSize),
        "call malloc",
        #cReturnGet(dst)
        ]

def _free(addr):        
    return [
        cParamSet(0, addr),
        "call free"
        ]

def heapFree(b, addr):
    # General free statement
    b += _free(addr)
    
    
    
###
# String
#
def StrAlloc(b, size):
    b += _malloc(size)
    
    
    
###
# Clutch
#

# class Str:
    # def __init__(self, s):
        # # in bytes        
        # self.size = len(s)
        
    # def alloc(self, dst):
        # return _malloc(self.size, dst)

    # #def __call__(self, idx):
    # #    return self.offsets[idx]
         
    # def free(self, addr):
        # return _free(addr)

    # def __repr__(self):
        # return "Str(offsets:{}, size:{})".format(
            # self.offsets, self.size
            # )
                
class ClutchTpl:
    #@elemWidths list of byteWidths
    def __init__(self, elemWidths):
        self.offsets = []
        i = 0
        for e in elemWidths:
            self.offsets.append(i)
            i += e
        # in bytes
        self.size = i
        
    def alloc(self, b):
        b += _malloc(self.size)

    def __call__(self, idx):
        return self.offsets[idx]
         
    def free(self, b, addr):
        b += _free(addr)

    def __repr__(self):
        return "ClutchTpl(offsets:{}, size:{})".format(
            self.offsets, self.size
            )
 
            
###
# func
#
def funcOpen(b, label):
    b.extend([
        "",
        "{}:".format(label),
        "push rbp ;Push the base pointer",
        "mov rbp, rsp ;Level the base pointer"
        ])
    
def funcClose(b):
    #b.append("leave ;Level the stack pointer, pop the base pointer")
    # All we really need
    b.extend([
        "pop rbp ;reset the bpr",
        "ret"
        ])

def funcCall(label):
    return ["call {}".format(label)]
    

###
# tests
#
def testLocalAlloc():
     local = Local(2)
     local.alloc(byteSpace.bit64)
     local.alloc(byteSpace.bit64)
     print(local(0))
     print(local(3))
     print(str(local))
     local(7)

def testClutch():
    c  = ClutchTpl([byteSpace.bit64, byteSpace.bit8, byteSpace.bit64])
    print(str(c.alloc('rax')))
    print(str(c(2)))
    print(str(c.free('rax')))
    print(str(c))

def testClutchCode():
    clutchSB = ClutchTpl([byteSpace.bit64, byteSpace.bit64, byteSpace.bit64])
    # strCommonInit("StringBuilder_sizeMin", 32)
    StringBuilder_sizeMin = 32

    b = []
    funcOpen(b, "StringBuilder_create")
    # clear the malloc params also
    l = Local()
    # # local 0 clutch
    l.alloc(byteSpace.bit64)
    # # local 1 tmp
    l.alloc(byteSpace.bit64)
    clutchSB.alloc(b)
    localSet(b, l(0), cReturnSrc())
    # # string to clutch
    StrAlloc(b, StringBuilder_sizeMin)
    localSet(b, l(1), l(0))
    localSet(b, localOffset(l(1), clutchSB(0)),  cReturnSrc())
    # # String start is further visit
    localSet(b, l(1), localAddrSrc(l(1)))
    localSet(b, l(1), "\"\\0\"")
    localSet(b, l(1), l(0))
    localSet(b, localOffset(l(1), clutchSB(1)), StringBuilder_sizeMin)
    localSet(b, localOffset(l(1), clutchSB(2)), "0")
    cReturnSet(b, l(0))
    funcClose(b)
    
    funcOpen(b, "StringBuilder_destroy")
    l = Local()
    # L0 clutch
    l.alloc(byteSpace.bit64)
    localSet(b, l(0), cParamSrc(0))
    heapFree(b, localOffset(l(0), clutchSB(0)))
    heapFree(b, l(0))
    funcClose(b)
    return b
    #print("\n".join(b))
    
def main():
    #testLocalAlloc()
    testClutchCode()
    
if __name__== "__main__":
    main()
