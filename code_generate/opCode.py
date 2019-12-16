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
# arithmetic
#
def add(b, x, y):
    b.append("add {}, {}".format(x, y))

def inc(b, reg):
    b.append("inc {}".format(reg))

def dec(b, reg):
    b.append("dec {}".format(reg))
        
def shiftL(b, reg, dist):
    # or is this unsigned shl
    b.append("sal {}, {}".format(reg, dist))

###
# C Params
#
cParameterRegisters = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
    
#? Need a cParamGet to cParamSet
def cParamGetToSet(getIdx, setIdx):
    src = cParamSrc(getIdx)
    dst = cParamSrc(getIdx)
    if (src != dst):
        return "mov {}, {}".format(dst, src)
    return ''
    
# keep
def cParamSet(idx, src):
    # Set a parameter register from a source.
    # @src any memory or immediate
    if (idx < 6):
        return "mov {}, {}".format(cParameterRegisters[idx], src)
    return "push {}".format(v)

#?x for src?
def cParamGet(idx, dst):
    if (idx < 6):
        return "mov {}, {}".format(dst, cParameterRegisters[idx])
    return "pop {}".format(dst)
    
# keep
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
    #param registesetrs
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
    
#x
def localAddrSet(b, local, src):
    # uses the local as an address
    # @src must be literal, label or register
    b.append("mov qword [{}], {}".format(local, src))
#x
def localAddrGet(b, local, dst):
    # treat the local as an address to retrieve from
    # @dst must be literal, label or register
    b.append("mov {}, [{}]".format(dst, local))

def visit(local):
    # treat a local as an address to set/get.
    return "[{}]".format(local)
        
def localOffsetVisit(local, offset):
    # format a local and offset as an address to set/get
    return "qword [{}+{}]".format(local, offset)

def regOffset(reg, offset):
    # Code set a register to point at offset from the register.
    # In other words, move a pointer to an offset
    # @reg a register containing an address
    # @offset to move to
    return "lea {}, [{}+{}]".format(reg, reg, offset)        

###
# Malloc
#

def _malloc(byteSize):
    return [
        cParamSet(0, byteSize),
        "call malloc",
        #cReturnGet(dst)
        ]

def _realloc(ptr, byteSize):
    return [
        cParamSet(0, ptr),
        cParamSet(1, byteSize),
        "call realloc",
        ]
        
def _free(addr):        
    return [
        cParamSet(0, addr),
        "call free"
        ]

def heapFree(b, addr):
    # General free statement
    b += _free(addr)
    
    
def memmove(b, src, dst, size):
    #@src pointer to memory
    #@dst pointer to memory
    #@size in bytes
    b.append(cParamSet(0, src))
    b.append(cParamSet(1, dst))
    b.append(cParamSet(2, size))
    funcCall(b, "memmove")
    
        
###
# String
#
def StrAlloc(b, size):
    b += _malloc(size)

def StrRealloc(b, ptr, size):
    b += _realloc(ptr, size)    
    
    
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

    def visit(self, reg, idx):
        # Code fragment returns contents of an elem.
        # Uses offset addressing, so only works for base elem size of 
        # processor.
        # the fragment can be used as source or destination.
        # Otherwise, use a pointer. 
        # @reg a reg or fixed address
        # @idx elem to return
        return localOffsetVisit(reg, self.elemOffset(idx))

    def regToElem(self, b, reg, idx):
        # Instruction moves a pointer to an elem.
        # For one offs, use the fast visit(). 
        # @reg a reg or fixed address
        # @idx elem to return
        #? must be hand-constructed as offsets add too many visiting 
        # brackets
        b.append( regOffset(reg, "{}+{}".format(reg, self.elemOffset(idx)) ))   
        
    def elemOffset(self, idx):
        return self.offsets[idx]
         
    def free(self, b, addr):
        b += _free(addr)

    def __repr__(self):
        return "ClutchTpl(offsets:{}, size:{})".format(
            self.offsets, self.size
            )
 
###
# comparison
#
CmpOps = {
    'gt':  "g",     
    'lt':  "l",
    'lte': "le",
    'gte': "ge",
    'eq':  "e", 
    'neq': "ne",      
    }
    

def cmpSet(b, local, cmpVal, cmpTyp, dst):
    # @cmpVal can be literal or a visited address (32bit?)
    # @src can be a register/offset etc.
    # @dst can be a register/offset etc.
    # @cmpTyp 'gt', 'gte' etc.
    b.append("cmp {}, {}".format(local, cmpVal))
    b.append("xor {}, {}".format(dst, dst))
    b.append("set{} {}".format(CmpOps[cmpTyp], dst))
    
###
# if
#
#? upside down
#? works for looks
JumpOps = {
    'g':  "jle",     
    'lt':  "jns",
    'lte': "jg",
    'gte': "js",
    'eq':  "jne", 
    'neq': "je",      
    }

InvCmpOps = {
    'gt':  "le",     
    'lt':  "ge",
    'lte': "g",
    'gte': "l",
    'eq':  "ne", 
    'neq': "e",
    }
        
def ifOpen(b, label, local, cmpVal, cmpTyp):
    # if value (op) cmped
    # @cmpVal can be literal or a visited address (32bit?)
    # @cmpTyp 'gt', 'gte' etc
    #! why use register? guarentee 64bit?
    b.append("cmp {}, {}".format(local, cmpVal))
    b.append("j{} {}".format(InvCmpOps[cmpTyp], label))
  
def ifClose(b, label):
    b.append("{}:".format(label))


###
# loop
#

def whileOpen(b, label):
    initJmpLabel = label + 'init' 
    b.append("jmp {}".format(initJmpLabel))
    b.append("{}:".format(label))

def whileClose(b, label, local, cmpVal, cmpTyp):
    initJmpLabel = label + 'init' 
    b.append("{}:".format(initJmpLabel))
    b.append("cmp {}, {}".format(local, cmpVal))
    b.append("j{} {}".format(InvCmpOps[cmpTyp], label))
    
    
        
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

def funcCall(b, label):
    b.append("call {}".format(label))
    


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
    # str, allocSize, size
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
    localSet(b, clutchSB.visit(l(1), 0), cReturnSrc())
    # # String start is further visit
    localSet(b, l(1), visit(l(1)))
    localSet(b, l(1), "\"\\0\"")
    localSet(b, l(1), l(0))
    localSet(b, clutchSB.visit(l(1), 1), StringBuilder_sizeMin)
    localSet(b, clutchSB.visit(l(1), 2), "0")
    cReturnSet(b, l(0))
    funcClose(b)
    
    funcOpen(b, "StringBuilder_destroy")
    l = Local()
    # L0 clutch
    l.alloc(byteSpace.bit64)
    localSet(b, l(0), cParamSrc(0))
    heapFree(b, clutchSB.visit(l(0), 0))
    heapFree(b, l(0))
    funcClose(b)
    

    #? not sure if working
    funcOpen(b, "StringBuilder__ensureSpace")
    l = Local()
    # L0 newSize
    l.alloc(byteSpace.bit64)

    localSet(b, l(0), clutchSB.visit(cParamSrc(0), 2))
    add(b, l(0), cParamSrc(1))
    inc(b, l(0))

    ifOpen(b, 'if1', clutchSB.visit(cParamSrc(0), 1), l(0), 'gte')
    # ???
    b.append("    ret")
    ifClose(b, 'if1')

    whileOpen(b, "Loop1")
    shiftL(b, clutchSB.visit(cParamSrc(0), 1), 1)
    ifOpen(b, 'if2', clutchSB.visit(cParamSrc(0), 1), 0, 'eq')
    dec(b, clutchSB.visit(cParamSrc(0), 1))
    ifClose(b, 'if2')
    whileClose(b, "Loop1", clutchSB.visit(cParamSrc(0), 1), l(0), 'lt')

    StrRealloc(
        b, 
        clutchSB.visit(cParamSrc(0), 0), 
        clutchSB.visit(cParamSrc(0), 1)
        )
    localSet(b, clutchSB.visit(l(0), 0), cReturnSrc())
    funcClose(b)


    
    #funcOpen(b, "StringBuilder_+=")
    funcOpen(b, "StringBuilder_append")
    l = Local()
    # # local 0 given str size
    l.alloc(byteSpace.bit64)
    cParamSet(0, cParamSrc(1))
    funcCall(b, "strlen")
    localSet(b, l(0), cReturnSrc())
    # stringbuiler already on param(0), but...
    cParamGetToSet(0, 0)
    cParamSet(1, l(0))
    funcCall(b, "StringBuilder__ensureSpace")
    # memmove(sb.str+sb->len, str, len)
    # local 1 end of struct str
    l.alloc(byteSpace.bit64)
    localSet(b, l(1), cParamSrc(0))
    clutchSB.regToElem(b, l(1), 0)
    # add len to the ptr
    add(b, l(1), clutchSB.visit(cParamSrc(0), 1))
    memmove(b, l(1), cParamSrc(1), l(0))
    # set the struct length
    ## current len
    localSet(b, l(1), clutchSB.visit(cParamSrc(0), 1))
    ## add str len
    add(b, l(1), l(0))
    ## save back
    localSet(b, clutchSB.visit(cParamSrc(0), 1),  l(1))
    # set the null
    ##
    localSet(b, l(1), cParamSrc(0))
    clutchSB.regToElem(b, l(1), 0)
    add(b, l(1), clutchSB.visit(cParamSrc(0), 1))
    localSet(b, l(1), "\"\\0\"")
    funcClose(b)
    
    funcOpen(b, "StringBuilder_clear")
    localSet(b, clutchSB.visit(cParamSrc(0), 1),  0)
    localSet(b, clutchSB.visit(cParamSrc(0), 0),  '\"\\0\"')
    funcClose(b)

    funcOpen(b, "StringBuilder_size")
    cReturnSet(b, clutchSB.visit(cParamSrc(0), 1))
    funcClose(b)

    funcOpen(b, "StringBuilder_result")
    l = Local()
    # # local 0 given str size
    l.alloc(byteSpace.bit64)
    localSet(b, l(0), cParamSrc(0))
    StrAlloc(b, clutchSB.visit(l(0), 1))
    memmove(b, clutchSB.visit(l(0), 0), cReturnSrc(), clutchSB.visit(l(0), 1))
    cReturnSet(b, l(0))
    funcClose(b)
    
    return b
    
def main():
    #testLocalAlloc()
    o = testClutchCode()
    print("\n".join(o))

if __name__== "__main__":
    main()