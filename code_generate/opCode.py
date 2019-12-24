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
    # result goes on the x memory location
    b.append("add {}, {}".format(x, y))

def inc(b, reg):
    b.append("inc {}".format(reg))

def dec(b, reg):
    b.append("dec {}".format(reg))
        
def shiftL(b, reg, dist):
    #? or is this unsigned shl
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
def _cParamSet(idx, src):
    # Set a parameter register from a source.
    # @src any memory or immediate
    if (idx < 6):
        return "mov {}, {}".format(cParameterRegisters[idx], src)
    return "push {}".format(v)

def cParamSet(b, idx, src):
    # Set a parameter register from a source.
    # @src any memory or immediate
    b.append(_cParamSet(idx, src))
    
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
LocalData = collections.namedtuple('LocalData', 'size, location')

# currently only safe registers that must be preserved.
cRegisters = [
    #param registers
    #"rdi",
    #"rsi",
    #"rdx",
    #"rcx",
    #"r8",
    #"r9",
    # non-param rigisters
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
        self.regPnt = 0
        # offsets are positive summed
        self.offset = 0
        # idx, size, isReg, loc (offset/reg)
        self.data = []
        self.stackData = []
        # bulk vars data with parameter data
        #for idx, p in enumerate(range(0, paramCount)):
        #    self.data.append(LocalData(byteSpace.bit64, True, cRegisters[idx]))
    #?x
    def alloc(self, size):
        idx = len(self.data)
        isReg = ((size <= byteSpace.bit64) and (self.regPnt < len(cRegisters)))
        if (isReg):
            self.regAlloc(size)
        if (not isReg):
            self.stackAlloc(size)

    def regAlloc(self, size):
        idx = len(self.data)
        if (size > byteSpace.bit64):
            raise IndexError("Local regvar request exceeds regvar size. size:{}".format(size))
        if (self.regPnt >= len(cRegisters)):
            raise IndexError("Local regvar request exceeds available. vars allocated:{}".format(len(self.data)))
        location = cRegisters[self.regPnt]
        self.regPnt += 1
        self.data.append(LocalData(size, location))
            
    def stackAlloc(self, size):
        location = self.offset
        self.offset += size
        self.stackData.append(LocalData(size, location))

    def __call__(self, idx):
        # returns a register, or exception
        #nonParamIdx = self.paramCount + idx
        if (idx >= len(self.data)):
            raise IndexError("Local regvar index exceeds available. vars allocated:{}, idx requested: {}".format(len(self.data), idx))
        d = self.data[idx]
        return d.location

    def stackLocation(self, idx):
        if (idx >= len(self.stackData)):
            raise IndexError("Local stackvar index exceeds available. vars allocated:{}, idx requested: {}".format(len(self.data), idx))
        d = self.stackData[idx]
        return d.location

    def __repr__(self):
        return "Local(regPnt:{}, offset:{}, data:{}, stackData:{})".format(
            self.regPnt, self.offset, self.data, self.stackData
            )

# Nothing else needed? I hope so.
def localStackToReg(local, b, stackIdx, regIdx):
    b.append("mov {}, [bpr-{}]".format(local(regIdx), local.stackLocation(stackIdx)))
    
def localOpen(local, b):
    # stack pointer over any stack allocation
    if (local.offset != 0):
        b.append("add rsp {}".format(local.offset))
    for d in local.data:
        # push protect
        b.append("push {}".format(d.location))

def localClose(local, b):
    for d in reversed(local.data):
        # pop restore
        b.append("pop {}".format(d.location)) 
    # stack looks after itself.
        
###
# General
#
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
    return "qword [{}]".format(local)
        
def localOffsetVisit(local, offset):
    # format a local and offset as an address to set/get
    return "qword [{}+{}]".format(local, offset)

# x
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
        _cParamSet(0, byteSize),
        "call malloc",
        #cReturnGet(dst)
        ]

def _realloc(ptr, byteSize):
    return [
        _cParamSet(0, ptr),
        _cParamSet(1, byteSize),
        "call realloc",
        ]
        
def _free(addr):        
    return [
        _cParamSet(0, addr),
        "call free"
        ]

def heapFree(b, addr):
    # General free statement
    b += _free(addr)
    
    
def memmove(b, src, dst, size):
    #@src pointer to memory
    #@dst pointer to memory
    #@size in bytes
    cParamSet(b, 0, dst)
    cParamSet(b, 1, src)
    cParamSet(b, 2, size)
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
     local = Local()
     local.alloc(byteSpace.bit64)
     local.alloc(byteSpace.bit64)
     local.stackAlloc(byteSpace.bit64)
     print(local(0))
     # error
     #print(local(3))
     print(str(local))
     print("sample build:")
     b = []
     localOpen(local, b)
     localStackToReg(local, b, 0, 1)
     localClose(local, b)
     print(b)

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
    ## reg0 clutch
    l.regAlloc(byteSpace.bit64)
    ## reg1 tmp
    l.regAlloc(byteSpace.bit64)
    localOpen(l, b)
    clutchSB.alloc(b)
    localSet(b, l(0), cReturnSrc())
    ## string to clutch
    StrAlloc(b, StringBuilder_sizeMin)
    localSet(b, clutchSB.visit(l(0), 0), cReturnSrc())
    ## String start is further visit
    localSet(b, l(1), clutchSB.visit(l(0), 0))
    localSet(b, visit(l(1)), "\"\\0\"")
    #! localSet(b, visit(l(1)), 0)
    # set the allocsize to sizeMin
    localSet(b, clutchSB.visit(l(0), 1), StringBuilder_sizeMin)
    # set the size to 0
    localSet(b, clutchSB.visit(l(0), 2), "0")
    cReturnSet(b, l(0))
    localClose(l, b)
    funcClose(b)
    
    funcOpen(b, "StringBuilder_destroy")
    l = Local()
    ## reg0 clutch
    l.alloc(byteSpace.bit64)
    localOpen(l, b)
    localSet(b, l(0), cParamSrc(0))
    heapFree(b, clutchSB.visit(l(0), 0))
    heapFree(b, l(0))
    localClose(l, b)
    funcClose(b)
    

    #? not sure if working
    # am _ensureSpace(sb: StrBuilder, extralen: int)
    funcOpen(b, "StringBuilder__ensureSpace")
    l = Local()
    # reg0 sb
    l.regAlloc(byteSpace.bit64)
    # reg1 newSize
    l.regAlloc(byteSpace.bit64)
    localOpen(l, b)

    localSet(b, l(0), cParamSrc(0))
    
    # dc newsize = sb.size+add_len+1
    localSet(b, l(1), clutchSB.visit(l(0), 2))
    add(b, l(1), cParamSrc(1))
    inc(b, l(1))
    
    # if (sb.allocSize >= newSize)
    ifOpen(b, 'if1', clutchSB.visit(l(0), 1), l(0), 'gte')
    # # ???
    localClose(l, b)
    funcClose(b)
    ifClose(b, 'if1')

    whileOpen(b, "Loop1")
    # sb.allocSize <<= 1;
    shiftL(b, clutchSB.visit(l(0), 1), 1)
    ifOpen(b, 'if2', clutchSB.visit(l(0), 1), 0, 'eq')
    dec(b, clutchSB.visit(l(0), 1))
    ifClose(b, 'if2')
    # while (sb.allocSize < newsize)
    whileClose(b, "Loop1", l(1), clutchSB.visit(l(0), 1), 'lt')


    # sb.str = realloc(sb.str, sb.allocSize)
    StrRealloc(
        b, 
        clutchSB.visit(l(0), 0), 
        clutchSB.visit(l(0), 1)
        )
    localSet(b, clutchSB.visit(l(0), 0), cReturnSrc())
    
    localClose(l, b)
    funcClose(b)


    
    #am +=(sb: StringBuilder, str : string)
    funcOpen(b, "StringBuilder_append")
    l = Local()
    ## reg0 sb
    l.regAlloc(byteSpace.bit64)
    ## reg1 str
    l.regAlloc(byteSpace.bit64)
    ## reg2 given str size
    l.regAlloc(byteSpace.bit64)
    ## reg3 tmp
    l.regAlloc(byteSpace.bit64)
    localOpen(l, b)
        
    localSet(b, l(0), cParamSrc(0))
    localSet(b, l(1), cParamSrc(1))
    cParamSet(b, 0, l(1))
    funcCall(b, "strlen")
    localSet(b, l(2), cReturnSrc())
    # ensure space
    cParamSet(b, 0, l(0))
    cParamSet(b, 1, l(2))
    funcCall(b, "StringBuilder__ensureSpace")
    # memmove(sb.str+sb->len, str, len)
    localSet(b, l(3), clutchSB.visit(l(0), 0))
    add(b, l(3), clutchSB.visit(l(0), 2))
    memmove(b, l(1), l(3), l(2))
    # sb.size += len
    localSet(b, l(3), clutchSB.visit(l(0), 2))
    add(b, l(3), l(2))
    localSet(b, clutchSB.visit(l(0), 2), l(3))
    # sb.str(sb.size) = '\0'
    localSet(b, l(3), clutchSB.visit(l(0), 0))
    add(b, l(3), clutchSB.visit(l(0), 2))
    #localSet(b, visit(l(3)), "\"\\0\"")
    localSet(b, visit(l(3)), 0)
    localClose(l, b)
    funcClose(b)
    
    funcOpen(b, "StringBuilder_clear")
    l = Local()
    ## reg0 str ptr
    l.alloc(byteSpace.bit64)
    localOpen(l, b)
    # sb.size = 0
    localSet(b, clutchSB.visit(cParamSrc(0), 1), 0)
    # sb.str(0) = '\0'
    localSet(b, l(0), clutchSB.visit(cParamSrc(0), 0))
    #localSet(b, visit(l(0)),  '\"\\0\"')
    localSet(b, visit(l(0)),  0)
    localClose(l, b)
    funcClose(b)

    funcOpen(b, "StringBuilder_size")
    cReturnSet(b, clutchSB.visit(cParamSrc(0), 2))
    funcClose(b)

    funcOpen(b, "StringBuilder_allocSize")
    cReturnSet(b, clutchSB.visit(cParamSrc(0), 1))
    funcClose(b)

    funcOpen(b, "StringBuilder_str")
    cReturnSet(b, clutchSB.visit(cParamSrc(0), 0))
    funcClose(b)
        
    funcOpen(b, "StringBuilder_result")
    l = Local()
    ## reg0 sb
    l.alloc(byteSpace.bit64)
    localOpen(l, b)
    localSet(b, l(0), cParamSrc(0))
    # out = malloc(sb.size+1)
    StrAlloc(b, clutchSB.visit(l(0), 2))
    # memcpy(out, sb.str, sb.size+1)
    memmove(b, clutchSB.visit(l(0), 0), cReturnSrc(), clutchSB.visit(l(0), 1))
    #cReturnSet(b, cReturnSrc())
    localClose(l, b)
    funcClose(b)
    
    return b


    
def main():
    #testLocalAlloc()
    #o = testClutchCode()
    #print("\n".join(o))
    #print("\n".join(r))
    
if __name__== "__main__":
    main()
