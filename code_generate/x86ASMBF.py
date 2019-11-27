#!/usr/bin/env python3
import sys
import math
import collections

import CodeBuilder
from assembly.nasmFrames import Frame64

class ByteSpace:
    bit8 = 1
    bit16 = 2
    bit32 = 4
    bit64 = 8
    bit128 = 16
    
byteSpace = ByteSpace()

#https://stackoverflow.com/questions/12063840/what-are-the-sizes-of-tword-oword-and-yword-operands
#BYTE, WORD, DWORD, QWORD, TWORD, OWORD, YWORD or ZWORD
class SpaceAnnotation:
    bit8 = "BYTE"
    bit16 = "WORD"
    bit32 = "DWORD"
    bit64 = "QWORD"
    bit128 = "OWORD"
    
spaceAnnotation = SpaceAnnotation()

#   %ebp, %ebx, %edi and %esi must be preserved   
# clobbers r10, r11 and any parameter registers 
cParemeterRegisters = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
cParemeterFloatRegisters = [
    "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6"
    ]
    
cReturn = ["rax", "rdx"]

class GType:
    int8 = 0
    int16 = 1
    int32 = 2
    int64 = 3
    float32 = 8
    float64 = 9
    stringASCII = 12
    array = 20
    struct = 21 
    

####
# Build helpers
#
LabelAcc = 0

def newLabel():
    global LabelAcc
    LabelAcc += 1
    return "L" + str(LabelAcc)
    
class StrInit():
    # Helper to create an initialised string.
    # Works by breaking the string into chunks. These chunks
    # (bit-width numbers) can be declared as 
    # ''mov' commands to an appropriate space.
    # The size the space needs to be is returned by alignedSize().
    
    def __init__(self, s, chunkSize):
        # helper to form initialised strings for assembly
        # @chunksize is usually byteSpace.bit64 = 8
        self.chunkSize = chunkSize
        # length, in bytes
        self.len = 0
        self.chunkString = self._strChunk(s)

    def _strChunk(self, s):
        # chunk a string into a given bytesize
        # @return is an array of chunks of chunksize, with the last
        # chunk possibly short
        
        # convert this python str
        #s if it blows,, it blows        
        sBytes = s.encode("ascii", "ignore")
        
        # set len
        l = len(sBytes)
        self.len = l

        # chunk...
        k, m = divmod(l, self.chunkSize)

        # chunk what is chunkable by chunkSize
        ret = [sBytes[(i * self.chunkSize):((i * self.chunkSize) + self.chunkSize)] for i in range(k)]            

        # add last chunk (possibly odd sized, or empty)
        if (m != 0):
            last = sBytes[l - m:]
            ret.append(last)
        return ret
            
    def size(self):
        # length of chunked string in bytes
        return self.len

    def alignedSize(self):
        # @return a number of bytes rounded up to chunksize which will 
        # contain the string
        return (len(self.chunkString)) * self.chunkSize

    def alignedSize16(self):
        # @return a number of bytes rounded up to 16bits which will 
        # contain the string. For x64 assembluy, aligning the stack to 
        # 16bits is a call convention.
        return (((self.len >> 4) + 1) << 4)
            
    def initDecls(self, basePtr, startOffset):
        # Append a string of instructions to initialise a string
        # @s the string
        # @basePtr a register containing a pointer to some allocated space
        # @startOffset offset from basePointer to start from 
        print(self)
        topPtr = startOffset
        b = []
        for chunk in self.chunkString:
            # make a number
            #? Endian dependant, etc.
            acc = 0
            for i, byt in enumerate(chunk):
                acc += byt << (8*i)

            b.append('mov qword rax, {}'.format(acc))
            b.append('mov qword [{}+{}], rax'.format(basePtr, topPtr))
            topPtr += self.chunkSize
            
        # stamp in the null terminator
        b.append('mov byte [{}+{}], 0'.format(basePtr, startOffset + (self.len)))        
        return b
        
    def __repr__(self):
        return "StrInit(chunkSize:{}, chunkString:{}, len:{})".format(
            self.chunkSize, self.chunkString, self.len
            )          
            
            
####
# func helpers
#
def toBytes(s):
    return bytes( s, 'ascii')

def cParameter(idx, v, visitV):
    if (idx < 6):
        if (visitV):
            return "mov {}, [{}]".format(cParemeterRegisters[idx], v)
        return "mov {}, {}".format(cParemeterRegisters[idx], v)
    if (visitV):
        return "murk!!! [{}]".format(v)
    return "murk!!! {}".format(v)

def cParameterOffset(idx, v):
    return "add {}, {}".format(cParemeterRegisters[idx], v)

def cParameterOffsetNeg(idx, offset):
    return "sub {}, {}".format(cParemeterRegisters[idx], offset)    

# e.g. xmmo
def cParameterFloat(idx, v, visitV):
    if (idx < 6):
        if (visitV):
            return "movq {}, [{}]".format(cParemeterFloatRegisters[idx], v)
        return "movq {}, {}".format(cParemeterFloatRegisters[idx], v)
    #??? overflow is errror???
    if (visitV):
        return "push [{}]".format(v)
    return "push {}".format(v)

def cReturn(dst, targetIsAddress):
    #! address only if a label?
    if (targetIsAddress):
        return "mov [{}], rax".format(dst)
    return "mov {}, rax".format(dst)

def cReturnToStack():
    return "push rax"
        
def visit(v):
    return "[{}]".format(v)

##
def frameOpen(b):
    b.append("push rbp ; frame open")
    b.append("mov rbp, rsp")
    
def frameClose(b):
    b.append("mov rsp, rbp")
    b.append("pop rbp ; frame close")
    
## Printers
#! What about returns
    
def headerIO(b):
    print(str(b ))
    b.headers.append("extern printf")
    b.headers.append("extern snprintf")
    b.sections['rodata'].append('io_fmt_str8: db "%s", 0')
    b.sections['rodata'].append('io_fmt_str8_NL: db "%s", 10, 0')
    #b.headers.rodata.append('io_fmt_utf8: db "%s"', 10, 0)
    b.sections['rodata'].append('io_fmt_int: db "%lld", 0')
    b.sections['rodata'].append('io_fmt_uint: db "%llu", 0')
    b.sections['rodata'].append('io_fmt_float: db "%g", 0')
    b.sections['rodata'].append('io_fmt_addr: db "%p", 0')
    b.sections['rodata'].append('io_fmt_println: db "%s", 10, 0')
    b.sections['rodata'].append('io_fmt_nl: db "", 10, 0')
    b.sections['data'].append("mch_str_buf: dq 2048")
    # reg print
    b.sections['rodata'].append('io_fmt_reg_rax: db 10, "= Reg rax: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rbx: db 10, "= Reg rbx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rcx: db 10, "= Reg rcx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rdx: db 10, "= Reg rdx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rsp: db 10, "= Reg rsp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rbp: db 10, "= Reg rbp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r9: db 10, "= Reg r9: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r10: db 10, "= Reg r10: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r12: db 10, "= Reg r12: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r14: db 10, "= Reg r14: %lld", 10, 0')

    b.sections['rodata'].append('io_fmt_reg_gen: db 10, "= GenReg", 10, "rax: %lld", 10, "rbx: %lld", 10, "rcx: %lld", 10, "rdx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_stack: db 10, "= StackReg", 10, "rsp: %llu", 10, "rbp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_str: db 10, "= StringReg", 10, "rsi: %lld", 10, "rdi: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_64_1: db 10, "= ExtReg1", 10, "r8: %lld", 10, "r9: %lld", 10, "r10: %lld", 10, "r11: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_64_2: db 10, "= ExtReg2", 10, "r12: %lld", 10, "r13: %lld", 10, "r14: %lld", 10, "r15: %lld", 10, 0')


# def arrayWrite(b, name, idx):
    # b.declarations.append(cParameter(0, idxAcess(name, idx), False))
    # b.declarations.append("call putchar")
    
#! what to do with returns, if anything?
def intToStr(b, src, dst, visitSrc):
    b.declarations.append(cParameter(0, dst, False))    
    b.declarations.append(cParameter(1, 2048, False))    
    b.declarations.append(cParameter(2, "io_fmt_int", False))
    b.declarations.append(cParameter(3, src, visitSrc))
    b.declarations.append("call snprintf")
    #b.declarations.append(cReturn(dst, True))

def uintToStr(b, src, dst, visitSrc):
    b.declarations.append(cParameter(0, dst, False))    
    b.declarations.append(cParameter(1, 2048, False))    
    b.declarations.append(cParameter(2, "io_fmt_uint", False))
    b.declarations.append(cParameter(3, src, visitSrc))
    b.declarations.append("call snprintf")
    
def floatToStr(b, src, dst, visitSrc):
    b.declarations.append(cParameter(0, dst, False))    
    b.declarations.append(cParameter(1, 2048, False))    
    b.declarations.append(cParameter(2, "io_fmt_float", False))
    b.declarations.append(cParameterFloat(0, src, visitSrc))
    b.declarations.append("call snprintf")
    #b.declarations.append(cReturn(dst, True))

def addrToStr(b, src, dst):
    b.declarations.append(cParameter(0, dst, False))    
    b.declarations.append(cParameter(1, 2048, False))    
    b.declarations.append(cParameter(2, "io_fmt_addr", False))
    b.declarations.append(cParameter(3, src, False))
    b.declarations.append("call snprintf")
    #b.declarations.append(cReturn(dst, True))
            
def printo(b, addr):
    b.declarations.append(cParameter(0, "io_fmt_str8", False))
    b.declarations.append(cParameter(1, addr, False))    
    b.declarations.append("call printf")
        
def println(b, addr):
    b.declarations.append(cParameter(0, "io_fmt_println", False))
    b.declarations.append(cParameter(1, addr, False))    
    b.declarations.append("call printf")

def intPrint(b, reg, visit):
    b.append(cParameter(0, "io_fmt_int", False))
    b.append(cParameter(1, reg, visit))    
    b.append("call printf")

# def varIntPrint(b, baseReg, offset):
    # b.append(cParameter(0, "io_fmt_int", False))
    # b.append(cParameter(1, "[{}+{}]".format(baseReg, offset), False))
    # #b.append(cParameterOffset(1, offset))
    # b.append("call printf")
            
#! need fresh varnames
def printStr(b, msg):
    b.sections['rodata'].append('testStr: db "{}", 0'.format(msg))
    b.declarations.append(cParameter(0, "io_fmt_str8", False))
    b.declarations.append(cParameter(1, "testStr", False))    
    b.declarations.append("call printf")

def printlnStr(msg):
    si = StrInit(msg, byteSpace.bit64)
    sz = si.alignedSize16()
    b = [] 
    b.append("add rsp, {}".format(sz))
    b.extend( si.initDecls('rsp', 0))
    b.append(cParameter(0, "io_fmt_str8_NL", False))
    b.append(cParameter(1, 'rsp', False))    
    b.append("call printf")
    b.append("sub rsp, {}".format(sz))
    return b
    
def printStrPtr(b, ptrReg, offset):
    b.append(cParameter(0, "io_fmt_str8", False))
    b.append(cParameter(1, ptrReg, False))
    b.append(cParameterOffset(1, offset))     
    b.append("call printf")
    
# def printlnStr(b, msg):
    # b.sections['rodata'].append('testStr2: db "{}", 0'.format(msg))
    # b.declarations.append(cParameter(0, "io_fmt_str8_NL", False))
    # b.declarations.append(cParameter(1, "testStr2", False))    
    # b.declarations.append("call printf")

def printlnCommonStr(msgLabel):
    b = []
    b.append(cParameter(0, "io_fmt_str8_NL", False))
    b.append(cParameter(1, msgLabel, False))    
    b.append("call printf")
    return b
    
def printNL(b):
    b.append(cParameter(0, "io_fmt_nl", False))
    b.append("call printf")

#     "rdi", "rsi", "rdx", "rcx", "r8", "r9"
PrintableRegisters = ['rax', 'rbx', 'rcx', 'rdx', 'rsp', 'rbp', 'r9' 'r10', 'r12', 'r14']
# def printReg(b, reg):
    # # cant do rdi, rsi?
    # # Clobbers rdi, rsi
    # if(reg not in PrintableRegisters):
        # print("[Error] given register name not printable: {}\n    allowed registers {}".format(reg, PrintableRegisters))
        # sys.exit()
    # b.append(cParameter(0, "io_fmt_reg_{}".format(reg), False))
    # b.append(cParameter(1, reg, False))
    # b.append("call printf")

def printReg(reg):
    # cant do rdi, rsi?
    # Clobbers rdi, rsi
    if(reg not in PrintableRegisters):
        print("[Error] given register name not printable: {}\n    allowed registers {}".format(reg, PrintableRegisters))
        sys.exit()
    return [
        cParameter(0, "io_fmt_reg_{}".format(reg), False),
        cParameter(1, reg, False),
        "call printf",
        ]
        
def printRegGen():
    # Clobbers rdi, rsi, rdx, rcx, r8
    # set rdx before params clobber it
    return [
        cParameter(4,  "rdx", False),
        cParameter(0, "io_fmt_reg_gen", False),
        cParameter(1, "rax", False),     
        cParameter(2,  "rbx", False),     
        cParameter(3,  "rcx", False),   
        "call printf",
        ]
        
def printRegStack():
    # Clobbers rdi, rsi, rdx
    return [
        cParameter(0, "io_fmt_reg_stack", False),
        cParameter(1, "rbp", False),     
        cParameter(2,  "rsp", False), 
        "call printf",
        ]
       
def printRegStr():
    # Clobbers rdi, rdx
    return [
        cParameter(0, "io_fmt_reg_str", False),
        # param 1 is rsi :)
        cParameter(2,  "rdi", False), 
        "call printf",
        ]
       
def printRegExt1():
    # Clobbers rdi, rsi, rdx, rcx, r8
    return [
        cParameter(0, "io_fmt_reg_64_1", False),
        cParameter(1, "r8", False),     
        cParameter(2, "r9", False),     
        cParameter(3, "r10", False),     
        cParameter(4, "r11", False),         
        "call printf",
        ]

def printRegExt2():
    # Clobbers rdi, rsi, rdx, rcx, r8
    return [
        cParameter(0, "io_fmt_reg_64_2", False),
        cParameter(1, "r12", False),     
        cParameter(2, "r13", False),     
        cParameter(3, "r14", False),     
        cParameter(4, "r15", False),         
        "call printf",
        ]
       


###
# Comment
#
def comment(b, msg):
    b.declarations.append("; {}".format(msg))

def mark(b):
    b.declarations.append("; *")
    
# def autoComment(b, ins):
    # for idx,iStr in enumerate(ins):
        # comment(b, "comm1" + str(idx))
        # comment(b, iStr)

    
####
# Common
#
def commonNum(b, name, v):
    b.sections['data'].append("{}: dq {}".format(name, v))

def commonStr(b, name, msg, newLine):
    nl = ''
    if newLine:
        nl = '10,' 
    b.sections['data'].append('{}: db "{}", {} 0'.format(name, msg, nl))
        
def commonBuffer(b, name):
    b.sections['data'].append("{}: dq 2048")


    
####
# Stack
#
class StackData():
    # Allocate and set data on the stack.
    # Don't do anything outside it until result() has been handled.
    # Does not assume it will reset the stack pointer. If you want
    # that, wrap the class in store/reset code. 
    def __init__(self):
        # topPtr moves by bits
        # grows in size. These are offsets, to be removed from rbp
        self.topPtr = 0
        # an anchor register. Preset to 'bpr'
        self.addrReg = 'rbp'
        # used for chopping strings. Preset to 8
        self.byteWidth = byteSpace.bit64
        self.namedOffset = {}
        self.decls = []
                
    def alignedSize16(self, sz):
        # @return a number of bytes rounded up to 16bits which will 
        # contain the string. For x64 assembluy, aligning the stack to 
        # 16bits is a call convention.
        #! slower, more efficient
        #alignedSpace = math.ceil(self.topPtr/16) << 4
        return (((sz >> 4) + 1) << 4)
        
    def declData(self, name, sz):
        # @sz in bytes
        self.topPtr += sz
        self.namedOffset[name] = self.topPtr
        
    def initData(self, name, sz, initValue):
        # @sz in bytes
        self.declData(name, sz)
        self.decls.append("mov qword [{}-{}], {}".format(
            self.addrReg, 
            self.namedOffset[name], 
            initValue
            ))
        
    def initStr(self, name, initStr):
        # make helper
        si = StrInit(initStr, self.byteWidth)

        # Alloc space
        self.declData(name, si.alignedSize())
         
        # add init declarations
        #??? what about minus signs?
        self.decls.extend( si.initDecls(self.addrReg, -self.namedOffset[name]))
        
    def visit(self, name):
        return "[bpr-{}*8]".format(self.namedOffset[name])

    def intPrint(self, name):
        b = []
        b.append(cParameter(0, "io_fmt_int", False))
        b.append(cParameter(1, "[{}-{}]".format(self.addrReg, self.namedOffset[name]), False))
        b.append("call printf")
        return b

    def strPrint(self, name):
        b = []
        b.append(cParameter(0, "io_fmt_str8", False))
        b.append(cParameter(1, self.addrReg, False))
        b.append(cParameterOffsetNeg(1, self.namedOffset[name]))     
        b.append("call printf")
        return b
         
    def resultOpen(self):
        b = []
        alignedSpace = self.alignedSize16(self.topPtr)
        b.append("sub rsp, {} ; alloc aligned space".format(alignedSpace))
        b.extend(self.decls)
        return b
        
    def __repr__(self):
        return "StackData(topPtr:{}, namedOffset:{}, decls:{})".format(
            self.topPtr, self.namedOffset, self.decls
            )
                
class HeapData():
    # Allocate and set data on the heap.
    # Use alloc() or init...() funcs, 
    # Use buildOpen() to build initcode (place before data manipulation) 
    # Utility functions will build access code.
    # declarations. 
    def __init__(self):
        # in bits
        self.size = 0           
        # an anchor register. Preset to 'r12'
        self.addrReg = 'r12'
        # used for aligning. Preset to 8
        self.byteWidth = byteSpace.bit64
        self.namedOffset = {}
        self.decls = []
        
    def declData(self, name, sz):
        # @sz in bytes
        self.namedOffset[name] = self.size 
        self.size += (sz*self.byteWidth)

    def initData(self, name, sz, initValue):
        # @sz in bytes
        self.declData(name, sz)
        self.decls.append('mov qword [{}+{}], {}'.format(self.addrReg, self.namedOffset[name], initValue))
        
    def initStr(self, name, initStr):
        # make helper
        si = StrInit(initStr, self.byteWidth)

        # Alloc space
        self.declData(name, si.alignedSize())
         
        # add init declarations
        self.decls.extend( si.initDecls(self.addrReg, self.namedOffset[name]))
        
    def declArray(self, b, name, elemSz, sz):
        # elemSz size of elements in bytes
        # @sz mun of elements in array
        self.declData(name, elemSz*sz)
        
    def set(self, b, name, v):
        b.append( "mov qword [{}+{}*{}], {}".format(self.addrReg, self.namedOffset[name], self.byteWidth, v))
        
    def get(self, b, name, to):
        b.append( "mov {}, [{}+{}*8]".format(to, self.addrReg, self.namedOffset[name]))

    def intPrint(self, b, name):
        b.append(cParameter(0, "io_fmt_int", False))
        b.append(cParameter(1, "[{}+{}]".format(self.addrReg, self.namedOffset[name]), False))
        b.append("call printf")

    def strPrint(self, b, name):
        b.append(cParameter(0, "io_fmt_str8", False))
        b.append(cParameter(1, self.addrReg, False))
        b.append(cParameterOffset(1,  self.namedOffset[name]))     
        b.append("call printf")
                    
    def buildOpen(self, b):
        # set the malloc
        b.append(cParameter(0, self.size, False))
        b.append("call malloc")
        b.append(cReturn(self.addrReg, False))
        # add the inits
        b.extend(self.decls)
    
    def buildClose(self, b):
        self._free(b)

    def _free(self, b):
        b.append(cParameter(0, self.addrReg, False))
        b.append("call free")
            
    def __repr__(self):
        return "HeapData(byteWidth:{}, size:{}, addrReg:{}, namedOffset:{}, decls:{})".format(
            self.byteWidth, self.size, self.addrReg, self.namedOffset, self.decls
            )


class SectionBuilder():
    def __init__(self, heapData, stackData):
        self.initDecls = []
        self.decls = []
        self.heap = heapData
        self.stack = stackData

    def append(self, v):
        self.decls.append(v)

    def extend(self, v):
        self.decls.extend(v)  
              
    # def build(self, b):
        # if (self.heap):
            # self.heap.buildOpen(self.decls) 
        # if (self.stack):
            # self.stack.buildOpen(self.decls) 
        # b.extend(self.initDecls)
        # if (self.heap):
            # self.heap.buildClose(self.decls)         
        # b.extend(self.decls)

    def build(self):
        b = []
        if (self.heap):
            self.heap.buildOpen(b) 
        if (self.stack):
            self.stack.buildOpen(b) 
        b.extend(self.decls)
        if (self.heap):
            self.heap.buildClose(b)         
        return b            
###
# Malloc
#
#!
def alloc(b, sizeInBytes, name):
    #b.sections['bss'].append("{}: resq 1".format(name))
    b.sections['data'].append("{}: dq 3".format(name))
    b.declarations.append(cParameter(0, sizeInBytes, False))
    b.declarations.append("call malloc")
    b.declarations.append(cReturn(name, True))

def allocThenStack(b, sizeInBytes):
    b.declarations.append(cParameter(0, sizeInBytes, False))
    b.declarations.append("call malloc")
    b.declarations.append(cReturnToStack())
    
def free(b, name):
    b.declarations.append(cParameter(0, name, True))
    b.declarations.append("call free")

def allocAddrSpace(b, addrCount, name):
    alloc(b, addrCount*8, name)

def allocAddrSpaceThenStack(b, addrCount):
    allocThenStack(b, addrCount*8)    

####
# Heap
#



##
# Struct
#
def clutch(b, addrCount):
    allocAddrSpaceThenStack(b, addrCount)
        
#! top of stack
#! need to visit again?
def clt_set(b, idx, dataAddr):
    b.declarations.append('mov qword [rsp+8*{}], {}'.format(idx, dataAddr))

def clt_get(b, idx, dst):
    b.declarations.append('mov {}, qword [rsp+8*{}]'.format(dst, idx))

##
#  Array
#
def arrayInc(b, name, idx):
    b.declarations.append('inc qword [{}+8*{}]'.format(name, idx))
    
def arrayDec(b, name, idx):
    b.declarations.append('dec [{}+8*{}]'.format(name, idx))

def idxAcess(name, idx):
    return "[{}+8*{}]".format(name, idx)
    
def arrayRead(b, name, idx):
    b.declarations.append("call getchar")
    b.declarations.append(cReturn(idxAcess(name, idx)))

###
# if
# 
#? upside down
#? works for looks
JumpOps = {
    'gt':  "jle",     
    'lt':  "jns",
    'lte': "jg",
    'gte': "js",
    'eq':  "jne", 
    'neq': "je",      
    }
    
IfStack = []    
def ifOpen(b, value, cmped, typ):
    # if value (op) cmped
    # @value can be literal or a visited address (32bit?)
    # @cmped can be literal or a visited address (32bit?)
    # @typ 'gt', 'gte' etc
    jLabel = newLabel()
    IfStack.append(jLabel)
    #! why use register? guarentee 64bit?
    b.append("mov r14, {}".format(value))
    b.append("cmp r14, {}".format(cmped))
    op = JumpOps[typ]
    b.append("{} .{}".format(op, jLabel)) 
            
def ifClose(b):
    jLabel = IfStack.pop()
    b.append(".{}".format(jLabel))
 
        
##
# loop
#
LoopOps = {
    'gt':  "jg",     
    'lt':  "js",
    'lte': "jle",
    'gte': "jns",
    'eq':  "je", 
    'neq': "jne",      
    }
    
LoopStack = []
CountLoopData = collections.namedtuple('CountLoopData', 'initLabel, jLabel, reg')

def countLoopOpen(b, count, reg):
    d = CountLoopData(newLabel(), newLabel(), reg)
    LoopStack.append( d )
    b.append("mov {}, {}".format(reg, count))
    b.append("jmp .{}".format(d.initLabel))
    b.append(".{}".format(d.jLabel))

def countLoopClose(b):
    d = LoopStack.pop()
    b.append("dec {}".format(d.reg))
    b.append(".{}".format(d.initLabel))
    b.append("cmp {}, 0".format(d.reg))
    b.append("jnle .{}".format(d.jLabel)) 

def countLoop0Open(b, count, reg):
    d = CountLoopData(newLabel(), newLabel(), reg)
    LoopStack.append( d )
    b.append("mov {}, {}".format(reg, count))
    b.append("jmp .{}".format(d.initLabel))
    b.append(".{}".format(d.jLabel))

def countLoop0Close(b):
    d = LoopStack.pop()
    b.append(".{}".format(d.initLabel))
    b.append("dec {}".format(d.reg))
    b.append("cmp {}, 0".format(d.reg))
    b.append("jnl .{}".format(d.jLabel)) 

#! backwards range?
#! with zero?
RangeLoopData = collections.namedtuple('RangeLoopData', 'until, inc, initLabel, jLabel, reg')

def rangeLoopOpen(b, start, until, reg):
    d = RangeLoopData(until, (start < until), newLabel(), newLabel(), reg)
    LoopStack.append( d )
    b.append("mov {}, {}".format(reg, start))
    b.append("jmp .{}".format(d.initLabel))
    b.append(".{}".format(d.jLabel))

def rangeLoopClose(b):
    d = LoopStack.pop()
    incdec  = 'dec'
    if d.inc:
        incdec = 'inc'
    b.append("{} {}".format(incdec, d.reg))
    b.append(".{}".format(d.initLabel))
    b.append("cmp {}, {}".format(d.reg, d.until))
    cmpOp = 'jnle'
    if d.inc:
       cmpOp = 'jnge'   
    b.append("{} .{}".format(cmpOp, d.jLabel)) 
    
# WhileData = collections.namedtuple('WhileData', 'typ, cmped, initLabel, jLabel, reg')
            
# def whileOpen(b, count,  typ, cmped, reg):
    # # while count (op) cmped {}
    # # @value can be literal or a visited address (32bit?)
    # # @cmped can be literal or a visited address (32bit?)
    # # @typ 'gt', 'gte' etc
    # d = WhileData(typ, cmped, newLabel(), newLabel(), reg)
    # LoopStack.append( d )
    # b.append("mov {}, {}".format(reg, count))
    # b.append("jmp .{}".format(d.initLabel))
    # b.append(".{}".format(d.jLabel))
            
# def whileClose(b):
    # d = LoopStack.pop()
    # b.append(".{}".format(d.initLabel))
    # #! why use register? guarentee 64bit?
    # b.append("cmp {}, {}".format(d.reg, d.cmped))
    # b.append("{} .{}".format(LoopOps[d.typ], d.jLabel)) 



ASM = {
"alloc" : alloc,
"free" : free,
# int data[100];
#int *array = malloc(10 * sizeof(int));
# malloc and free probably can be used
# if you want
"Array.inc" : arrayInc,
"Array.dec" : arrayDec,
#"write" : arrayWrite, 
"read" : arrayRead,
}


#######
# Test #
######
#! can add comment stretches?
def testPrint(b):
    headerIO(b)
    #staticVarStr(b, 'StrToPrint', 'ninechar')
    #comment(b, 'intToStr')
    staticVar(b, 'IntToPrint', 101)
    intToStr(b, 'IntToPrint', 'mch_str_buf', True)
    println(b, 'mch_str_buf')
    #comment(b, 'floatToStr')
    staticVar(b, 'FloatToPrint', 192.7)
    floatToStr(b, 'FloatToPrint', 'mch_str_buf', True)
    println(b, 'mch_str_buf')
    addrToStr(b, 'IntToPrint', 'mch_str_buf')
    println(b, 'mch_str_buf')
    printStr(b, "done")
    #printlnStr(b, "doner")

def testPrintReg(b):
    headerIO(b)  
    #b.extend(printReg('rbp'))
    #b.extend(printReg('rsp'))
    #b.extend(printReg('rsp'))
    b.append("mov rax, 77")  
    b.extend(printReg('rax'))
    
def testPrintStr(b):
    headerIO(b)
    r = printlnStr("Maybe*those words*should*go*uunspoken")
    b.extend(r)
    
def testPrintRegGroups(b):
    headerIO(b)
    b.append('mov rax, 363')
    b.append('mov rcx, 757')
    b.extend(printRegGen())
    b.extend(printRegStack())
    b.extend(printRegStr())
    b.extend(printRegExt1())
    b.extend(printRegExt2())

        
def testStaticAlloc(b):
    headerIO(b)
    commonNum(b, "commonNum1", 1212)
    commonStr(b, "commonStr1", "insane drift")
    b.declarations.append("mov rax, [commonNum1]")
    #printReg(b, 'rax')
    b.extend(printReg('rax'))
    printNL(b)

def testStaticArray(b):
    headerIO(b)
    ASM["Array"](b, 64, "paving")
    arrayInc(b, 'paving', 3)
    arrayInc(b, 'paving', 3)
    arrayInc(b, 'paving', 3)
    arrayWrite(b, 'paving', 3)
    stdoutNewLine(b)
    ASM["free"](b, "paving")
        

def testStackInt(b):
    headerIO(b)
    sd = StackData()
    sd.initData("testData1", byteSpace.bit64, '66')
    sd.initData("testData2", byteSpace.bit64, '77')
    sd.initData("testData3", byteSpace.bit64, '99')
    print(sd)
    b.extend(sd.resultOpen())
    b.extend(sd.intPrint('testData1'))
    printNL(b)
    b.extend(sd.intPrint('testData2'))
    printNL(b)
    b.extend(sd.intPrint('testData3'))
    printNL(b)
    
# def testStackString(b):
    # headerIO(b)
    # sb = SectionBuilder(None, StackData())
    # sb.stack.initStr("testStr1", "wikkyfoobartle")
    # sb.stack.initStr("testStr2", "ghalumphev")
    # sb.stack.initStr("testStr3", "petalpeddlaring")
    # sb.stack.initStr("testStr4", "gonk")
    # print(sb.stack)
    # sb.stack.strPrint(sb.decls, "testStr1")
    # printNL(sb.decls)
    # sb.stack.strPrint(sb.decls, "testStr2")
    # printNL(sb.decls)
    # sb.stack.strPrint(sb.decls, "testStr3")
    # printNL(sb.decls)
    # sb.stack.strPrint(sb.decls, "testStr4")
    # printNL(sb.decls)
    # b.extend(sb.build())

def testStackString(b):
    headerIO(b)
    sd = StackData()
    sd.initStr("testStr1", "wikkyfoobartle")
    sd.initStr("testStr2", "ghalumphev")
    sd.initStr("testStr3", "petalpeddlaring")
    sd.initStr("testStr4", "gonk")
    print(sd)
    b.extend(sd.resultOpen())
    b.extend(sd.strPrint("testStr1"))
    printNL(b)
    b.extend(sd.strPrint("testStr2"))
    printNL(b)
    b.extend(sd.strPrint("testStr3"))
    printNL(b)
    b.extend(sd.strPrint("testStr4"))
    printNL(b)
    
def testStackData():
    a = StackData()
    a.declData("testVar1")
    print(a.visit("testVar1"))
    a.initData("initVar", 674)
    print(a.visit("initVar"))
    a.declareStr("sampleString", "cool*as*ice")
    print(a.visit("sampleString"))
    a.initData("after", 674)
    print(a.visit("after"))
    print(str(a))
    print("\n".join(a.declarations))

        
def testHeapData(b):
    headerIO(b)
    a = HeapData()
    # a.alloc('stonk', byteSpace.bit64)
    # a.alloc('blimey', byteSpace.bit64)
    #a.build(b)
    # a.set(b, 'stonk', '44')
    # a.set(b, 'blimey', '777')
    # print(a)
    # a.get(b, 'stonk', 'rax')
    # a.get(b, 'blimey', 'rbx')
    # printRegGen(b)
    ##printReg(b, 'rax')

def testHeapInt(b):
    headerIO(b)
    sb = SectionBuilder(HeapData(), None)
    sb.heap.initData("testData1", byteSpace.bit8, '66')
    sb.heap.initData("testData2", byteSpace.bit8, '77')
    sb.heap.initData("testData3", byteSpace.bit8, '99')
    print(sb.heap)
    sb.heap.intPrint(sb.decls, 'testData1')
    sb.heap.intPrint(sb.decls, 'testData2')
    sb.heap.intPrint(sb.decls, 'testData3')
    printNL(sb.decls)
    b.extend(sb.build())

def testHeapStr(b):
    headerIO(b)
    sb = SectionBuilder(HeapData(), None)
    #! why cut-off on first one?
    sb.heap.initStr("testStr1", "wikkyfoobartle")
    sb.heap.initStr("testStr2", "ghalumphev")
    sb.heap.initStr("testStr3", "petalpeddlaring")
    sb.heap.initStr("testStr4", "gonk")
    print(sb.heap)
    sb.heap.strPrint(sb.decls, "testStr1")
    printNL(sb.decls)
    sb.heap.strPrint(sb.decls, "testStr2")
    printNL(sb.decls)
    sb.heap.strPrint(sb.decls, "testStr3")
    printNL(sb.decls)
    sb.heap.strPrint(sb.decls, "testStr4")
    printNL(sb.decls)
    b.extend(sb.build())

def testHeapArray(b):
    headerIO(b)
    sb = SectionBuilder(HeapData(), None)
    sb.heap.declArray(sb.decls, 'testArray1', byteSpace.bit64, 12)
    sb.heap.intArrayPrint(sb.decls, "testArray1")
    printNL(sb.decls)    
    b.extend(sb.build())



        
def testIf(b):
    headerIO(b)
    commonStr(b, "ind",  "if code runs", True)
    commonStr(b, "done", "done", False)
    sb = SectionBuilder(HeapData(), None)
    sb.heap.initData("testData1", byteSpace.bit64, '66')
    sb.heap.initData("testData2", byteSpace.bit64, '-7')
    ifOpen(sb.decls, '-7', '0', 'gt')
    #ifOpen(sb.decls, '4499', '0', 'gt')
    sb.extend( printlnCommonStr("ind") )
    ifClose(sb.decls)
    sb.extend( printlnCommonStr("done") )
    b.extend(sb.build())
    
def testCountLoop(b):
    headerIO(b)
    sb = SectionBuilder(None, None)
    countLoop0Open(sb.decls, '7', 'r14')
    #printReg(sb.decls, 'r14')
    sb.extend(printReg('r14'))
    countLoop0Close(sb.decls)
    printNL(sb.decls)    
    b.extend(sb.build())

def testRangeLoop(b):
    headerIO(b)
    sb = SectionBuilder(None, None)
    rangeLoopOpen(sb.decls, '7', '4', 'r14')
    #printReg(sb.decls, 'r14')
    sb.extend(printReg('r14'))
    rangeLoopClose(sb.decls)
    rangeLoopOpen(sb.decls, '4', '7', 'r14')
    #printReg(sb.decls, 'r14')
    sb.extend(printReg('r14'))
    rangeLoopClose(sb.decls)
    printNL(sb.decls)    
    b.extend(sb.build())


    
# def testWhile(b):
    # headerIO(b)
    # sb = SectionBuilder(None, None)
    # #def whileOpen(b, count, typ, cmped, reg):
    # whileOpen(sb.decls, '8', 'gt', 4, 'r14')
    # sb.append( "dec r14" )
    # printReg(sb.decls, 'r14')
    # whileClose(sb.decls)
    # printNL(sb.decls)    
    # b.extend(sb.build())

       
# def testComment(b):
    #! cant work, currently
    #autoComment(b, [ 
    #    staticVarStr(b, 'StrToPrint', 'ninechary')
    #    ])

def testStruct(b):
    headerIO(b)
    clutch(b, 3)
    printRegStack(b)
    printReg(b)
    printNL(b)
    printReg(b)
    printNL(b)
    #! top of stack
    clt_set(b, 0, 333)
    clt_set(b, 1, 101)
    clt_set(b, 2, 48)
    clt_get(b, 0, "rax")
    intToStr(b, 'rax', 'mch_str_buf', False)
    println(b, 'mch_str_buf')
    # clt_get(b, 1, "rax")
    # intToStr(b, 'rax', 'mch_str_buf', False)
    # println(b, 'mch_str_buf')
    # clt_get(b, 2, "rax")
    # intToStr(b, 'rax', 'mch_str_buf', False)
    # println(b, 'mch_str_buf')
        
def testLoop(b):
    whileNotZero(b, countValue, body)
    
def main():
    b = CodeBuilder.Builder()
    test(b)
    print(b.frame(Frame64))
    
if __name__== "__main__":
    main()
