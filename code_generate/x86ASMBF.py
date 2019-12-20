#!/usr/bin/env python3
import sys
import math
import collections

import CodeBuilder
from assembly.nasmFrames import Frame64

import opCode 

#! formatting issues like 'qword' whenever not usig 64bit
#! need to move towards an intermediate language
#! big needs:
# - floats
# - type conversions
# - utf8
#! can intermediate language do labelling?
#! explicit box, like Rust?
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
    

class ArrayInit():
    # Helper to create an initialised string.
    # Works by breaking the string into chunks. These chunks
    # (bit-width numbers) can be declared as 
    # ''mov' commands to an appropriate space.
    # The size the space needs to be is returned by alignedSize().
    
    def __init__(self, elemWidth, values):
        # helper to form initialised strings for assembly
        # @chunksize is usually byteSpace.bit64 = 8
        self.elemWidth = elemWidth
        # length of array
        self.length = len(values)
        self.values = values

    def byteSize(self):
        # length of array in bytes
        return (self.elemWidth * self.length)

    def alignedSize16(self):
        # @return a number of bytes rounded up to 16bits which will 
        # contain the string. For x64 assembluy, aligning the stack to 
        # 16bits is a call convention.
        return (math.ceil(self.byteSize()/16) << 4)
            
    def initDecls(self, basePtr, startOffset):
        # Return a string of instructions to initialise a string
        # @basePtr a register containing a pointer to some allocated space
        # @startOffset offset from basePointer to start from 
        topPtr = startOffset
        b = []
        for v in self.values:
            b.append('mov qword [{}+{}], {}'.format(basePtr, topPtr, v))
            topPtr += self.elemWidth
        return b
        
    def __repr__(self):
        return "ArrayInit(elemWidth:{}, values:{}, length:{})".format(
            self.elemWidth, self.values, self.length
            )          

class ClutchInit():
    # Helper to create an initialised string.
    # Works by breaking the string into chunks. These chunks
    # (bit-width numbers) can be declared as 
    # ''mov' commands to an appropriate space.
    # The size the space needs to be is returned by alignedSize().
    
    def __init__(self, elemData):
        # helper to form initialised strings for assembly
        # @elemData is List(value, widths e.g. byteSpace.bit64 = 8)
        self.elemData = elemData
        
    def elemWidths(self):
        return [e[0] for e in self.elemData]
        
    def byteSize(self):
        # length of clutch in bytes
        sz = 0
        for w in self.elemWidths():
            sz += w 
        return sz

    def alignedSize16(self):
        # @return a number of bytes rounded up to 16bits which will 
        # contain the string. For x64 assembluy, aligning the stack to 
        # 16bits is a call convention.
        return (math.ceil(self.byteSize()/16) << 4)
            
    def initDecls(self, basePtr, startOffset):
        # Return a string of instructions to initialise a string
        # @basePtr a register containing a pointer to some allocated space
        # @startOffset offset from basePointer to start from 
        topPtr = startOffset
        b = []
        for e in self.elemData:
            b.append('mov qword [{}+{}], {}'.format(basePtr, topPtr, e[0]))
            topPtr += e[1]
        return b
        
    def __repr__(self):
        return "ClutchInit(elemData:{})".format(
            self.elemData
            )              
            
class StrInit():
    # Helper to create an initialised byte-encoded string.
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

            b.append('mov qword rax, {} ;{}'.format(acc, chunk))
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
    #b.headers.append("extern snprintf")
    b.headers.append("extern putchar")
    b.headers.append("extern puts")
    b.sections['rodata'].append('io_fmt_str8: db "%s", 0')
    #?x unecessary, use puts?
    b.sections['rodata'].append('io_fmt_str8_NL: db "%s", 10, 0')
    #b.headers.rodata.append('io_fmt_utf8: db "%s"', 10, 0)
    b.sections['rodata'].append('io_fmt_int: db "%lld", 0')
    b.sections['rodata'].append('io_fmt_uint: db "%llu", 0')
    b.sections['rodata'].append('io_fmt_float: db "%g", 0')
    b.sections['rodata'].append('io_fmt_addr: db "%p", 0')
    #X?
    b.sections['rodata'].append('io_fmt_println: db "%s", 10, 0')
    b.sections['rodata'].append('io_fmt_separator: db ", ", 0')
    b.sections['data'].append("mch_str_buf: dq 2048")
    # reg print
    b.sections['rodata'].append('io_fmt_reg_rax: db 10, "= Reg rax: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rbx: db 10, "= Reg rbx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rcx: db 10, "= Reg rcx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rdx: db 10, "= Reg rdx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rsp: db 10, "= Reg rsp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rbp: db 10, "= Reg rbp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rsi: db 10, "= Reg rsi: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rdi: db 10, "= Reg rdi: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r9: db 10, "= Reg r9: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r10: db 10, "= Reg r10: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r12: db 10, "= Reg r12: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r14: db 10, "= Reg r14: %lld", 10, 0')

    b.sections['rodata'].append('io_fmt_reg_gen: db 10, "= GenReg", 10, "rax: %lld", 10, "rbx: %lld", 10, "rcx: %lld", 10, "rdx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_stack: db 10, "= StackReg", 10, "rsp: %llu", 10, "rbp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_str: db 10, "= StringReg", 10, "rsi: %lld", 10, "rdi: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_64_1: db 10, "= ExtReg1", 10, "r8: %lld", 10, "r9: %lld", 10, "r10: %lld", 10, "r11: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_64_2: db 10, "= ExtReg2", 10, "r12: %lld", 10, "r13: %lld", 10, "r14: %lld", 10, "r15: %lld", 10, 0')
    b.sections['rodata'].append("io_comma: db 44")
    b.sections['rodata'].append("io_lineFeed: db 10")
    b.sections['rodata'].append("io_space: db 32")
    b.sections['rodata'].append("io_semiColon: db 59")

    
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
            


def intPrint(b, reg, visit):
    b.append(cParameter(0, "io_fmt_int", False))
    b.append(cParameter(1, reg, visit))    
    b.append("call printf")

# def varIntPrint(b, baseReg, offset):
    # b.append(cParameter(0, "io_fmt_int", False))
    # b.append(cParameter(1, "[{}+{}]".format(baseReg, offset), False))
    # #b.append(cParameterOffset(1, offset))
    # b.append("call printf")
            
# StrPrint
# common
def commonStrAlloc(b, msgLabel, msg):
    b.sections['rodata'].append('{}: db "{}", 0'.format(msgLabel, msg))
    
def commonStrPrint(msgLabel):
    b = []
    b.append(cParameter(0, "io_fmt_str8", False))
    b.append(cParameter(1, msgLabel, False))    
    b.append("call printf")
    return b
    
def commonStrPrintln(msgLabel):
    b = []
    b.append(cParameter(0, msgLabel, False))    
    b.append("call puts")
    return b
    
# heap
# Some of this is beyond me
#? - Why can I not write past rsp
#? - if printf faffs with the stack, why is that a problem?
#? Why can printf use an above rsp address?
#! revise against compiles
#! probably a better adressing way than moving rsp
def strPrint(msg):
    si = StrInit(msg, byteSpace.bit64)
    sz = si.alignedSize16()
    b = [] 
    b.append("add rsp, {}".format(sz))
    b.extend( si.initDecls('rsp', 0))
    b.append(cParameter(0, "io_fmt_str8", False))
    b.append(cParameter(1, 'rsp', False))
    #! note the above    
    b.append("sub rsp, {}".format(sz))
    b.append("call printf")
    return b

def strPrintln(msg):
    si = StrInit(msg, byteSpace.bit64)
    sz = si.alignedSize16()
    b = [] 
    b.append("add rsp, {}".format(sz))
    b.extend( si.initDecls('rsp', 0))
    b.append(cParameter(0, 'rsp', False))
    #! note the above    
    b.append("sub rsp, {}".format(sz))
    b.append("call puts")
    return b

# stack & general
def heapStrPrint(addr):
    return [
    "push rdi",
    "push rsi",
    cParameter(0, "io_fmt_str8", False),
    cParameter(1, addr, False),    
    "call printf",
    "pop rdi",
    "pop rsi"
    ]
            
def heapStrPrintln(addr):
    return [
    "push rdi",
    cParameter(0, addr, False),    
    "call puts",
    "pop rsi"
    ]


# punctuation
def printNL():
    b = []
    b.append("mov edi, 10")
    b.append("call putchar")
    return b

def printSpace():
    b = []
    b.append("mov edi, 32")
    b.append("call putchar")
    return b

def printSeparator():
    b = []
    b.append(cParameter(0, "io_fmt_separator", False))
    b.append("call printf")
    return b
        
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
    "push rdi",
    "push rsi",
        cParameter(0, "io_fmt_reg_{}".format(reg), False),
        cParameter(1, reg, False),
        "call printf",
    "pop rsi",
    "pop rdi"
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
    # works :)
    # Clobbers rdi, rdx
    return [
        cParameter(2,  "rdi", False), 
        cParameter(0, "io_fmt_reg_str", False),
        # param 1 is rsi :)
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
        return math.ceil(self.topPtr/16) << 4
        #return (((sz >> 4) + 1) << 4)
        
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

    def declArray(self, name, elemWidth, length):
        # @elemWidth size of elements in bytes
        # @length mun of elements in array
        self.declData(name, elemWidth*length)
        print(self)
        
    def initArray(self, name, elemWidth, values):
        # elemWidth size of elements in bytes
        # @values a list
        ai = ArrayInit(elemWidth, values)
        
        # Alloc space
        self.declArray(name, elemWidth, ai.length)
         
        # add init declarations
        self.decls.extend( ai.initDecls(self.addrReg, -self.namedOffset[name]))

    def intArrayPrint(self, name, elemSz, sz):
        b = []
        i = self.namedOffset[name]
        end = i - (elemSz*sz)
        while i > end:
            b.append(cParameter(0, "io_fmt_int", False))
            b.append(cParameter(1, "[{}-{}]".format(self.addrReg, i), False))
            b.append("call printf")
            b.extend(printSeparator())
            i -= elemSz
        return b

    def declClutch(self, name, elemWidths):
        # @elemWidths list of sizes of elements in bytes
        i = 0
        for e in elemWidths:
            i += e
        self.declData(name, i)
        print(self)

    def initClutch(self, name, elemData):
        # elemWidth size of elements in bytes
        # @values a list
        ci = ClutchInit(elemData)
        
        # Alloc space
        self.declClutch(name, ci.elemWidths())
         
        # add init declarations
        self.decls.extend( ci.initDecls(self.addrReg, -self.namedOffset[name]))

    def intClutchPrint(self, name, elemWidths):
        b = []
        off = self.namedOffset[name]
        for w in elemWidths:
            b.append(cParameter(0, "io_fmt_int", False))
            b.append(cParameter(1, "[{}-{}]".format(self.addrReg, off), False))
            b.append("call printf")
            #b.extend(printComma())
            b.extend(printSeparator())
            off -= w
        return b 
                        
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

    def offset(self, name):
        return "[{}-{}]".format(self.addrReg, self.namedOffset[name])
                
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
        # used for chopping strings. Preset to 8
        self.byteWidth = byteSpace.bit64
        self.namedOffset = {}
        self.decls = []
        
    def declData(self, name, sz):
        # @sz in bytes
        self.namedOffset[name] = self.size 
        self.size += sz

    def initData(self, name, sz, initValue):
        # @sz in bytes
        self.declData(name, sz)
        self.decls.append('mov qword [{}+{}], {}'.format(self.addrReg, self.namedOffset[name], initValue))

    def intPrint(self, name):
        b = []
        b.append(cParameter(0, "io_fmt_int", False))
        b.append(cParameter(1, "[{}+{}]".format(self.addrReg, self.namedOffset[name]), False))
        b.append("call printf")
        return b

    def set(self, name, v):
        return "mov qword [{}+{}*{}], {}".format(self.addrReg, self.namedOffset[name], self.byteWidth, v)
        
    def get(self, name, to):
        return "mov {}, [{}+{}*8]".format(to, self.addrReg, self.namedOffset[name])

    def initStr(self, name, initStr):
        # make helper
        si = StrInit(initStr, self.byteWidth)
        # Alloc space
        self.declData(name, si.alignedSize())
         
        # add init declarations
        self.decls.extend( si.initDecls(self.addrReg, self.namedOffset[name]))

    def strPrint(self, name):
        b = []
        b.append(cParameter(0, "io_fmt_str8", False))
        b.append(cParameter(1, self.addrReg, False))
        b.append(cParameterOffset(1,  self.namedOffset[name]))     
        b.append("call printf")
        return b   
                
    def declArray(self, name, elemWidth, length):
        # @elemWidth size of elements in bytes
        # @length mun of elements in array
        self.declData(name, elemWidth*length)

    def initArray(self, name, elemWidth, values):
        # elemWidth size of elements in bytes
        # @values a list
        ai = ArrayInit(elemWidth, values)
        
        # Alloc space
        self.declArray(name, elemWidth, ai.length)
         
        # add init declarations
        self.decls.extend( ai.initDecls(self.addrReg, self.namedOffset[name]))
                
    def intArrayPrint(self, name, elemSz, sz):
        b = []
        start = self.namedOffset[name]
        end = start + (elemSz*sz)
        for i in range(start, end, elemSz):
            b.append(cParameter(0, "io_fmt_int", False))
            b.append(cParameter(1, "[{}+{}]".format(self.addrReg, i), False))
            b.append("call printf")
            #b.extend(printComma())
            b.extend(printSeparator())
        return b
                
    def arrayForEach(self, name, elemSz, sz, func):
        b = []
        b.append("mov rcx, {}+{}".format(self.addrReg, self.offset(name)))
        for x in range(0, sz):
            b.append("add rcx, {}".format(elemSz))
            b.append("{}".format(func))
        return b
    
    def declClutch(self, name, elemWidths):
        # @elemWidths list of sizes of elements in bytes
        i = 0
        for e in elemWidths:
            i += e
        self.declData(name, i)
        print(self)

    def initClutch(self, name, elemData):
        # elemWidth size of elements in bytes
        # @values a list
        ci = ClutchInit(elemData)
        
        # Alloc space
        self.declClutch(name, ci.elemWidths())
         
        # add init declarations
        self.decls.extend( ci.initDecls(self.addrReg, self.namedOffset[name]))

    def intClutchPrint(self, name, elemWidths):
        b = []
        off = self.namedOffset[name]
        for w in elemWidths:
            b.append(cParameter(0, "io_fmt_int", False))
            b.append(cParameter(1, "[{}+{}]".format(self.addrReg, off), False))
            b.append("call printf")
            #b.extend(printComma())
            b.extend(printSeparator())
            off += w
        return b 
                       
    def free(self):        
        b = []
        b.append(cParameter(0, self.addrReg, False))
        b.append("call free")
        return b
        
    def offset(self, name):
        return "[{}+{}]".format(self.addrReg, self.namedOffset[name])
        
    def resultOpen(self):
        b = []
        # set the malloc
        b.append(cParameter(0, self.size, False))
        b.append("call malloc")
        b.append(cReturn(self.addrReg, False))
        # add the inits
        b.extend(self.decls)
        return b
    
    def resultClose(self):
        return self.free()
            
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
#x
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

###
# blocks
#
def funcOpen(label):
    b = []
    b.append("{}: push rbp ;Push the base pointer".format(label))
    b.append("mov rbp, rsp ;Level the base pointer")
    return b
    
def funcClose():
    b = []
    #b.append("leave ;Level the stack pointer, pop the base pointer")
    # All we really need
    b.append("pop rbp ;reset the bpr")
    b.append("ret")
    return b

def funcInternCall(label):
    return ["call {}".format(label)]
        
def funcExternCall(name):
    return ["call {}".format(name)]
    
###
# switch
#
def switchOpen(cmpValLabels, cmpVal):
    # Form:
    # mov 'rbx', 2
    # switchOpen([(0, 'c0'),(1, 'c1'),(2, 'c2')], 'rbx')
    #  ... [optional default code]
    # switchOpenClose("switch1Close")
    # 
    # caseStart('c0')
    #    ...
    # caseClose('switch1Close')
    # caseStart('c1')
    #    ...
    # caseClose('switch1Close')
    # ...
    # switchClose("switch1Close")
    # Put the fiat case last and leave off the close to make it a few 
    # cycles faster.\
    b = []
    b.append("mov rax, {}".format(cmpVal))
    for cVL in cmpValLabels:
        b.append("cmp rax, {}".format(cVL[0]))
        b.append("je {}".format(cVL[1]))        
    return b
    
def switchOpenClose(closeLabel):
    b = []
    b.append("jmp {}".format(closeLabel))
    return b
    
def caseStart(openLabel):
    b = []
    b.append("{}: ".format(openLabel))
    return b

def caseClose(closeLabel):
    b = []
    b.append("jmp {}".format(closeLabel))
    return b

def switchClose(closeLabel):
    b = []
    b.append("{}: ".format(closeLabel))
    return b

###
# Namespace
#

def mangle(ext, name):
    return ext + name
    

#x
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

def testCommonStrPrint(b):
    headerIO(b)
    commonStrAlloc(b, "testStr1", "unfathomable...")
    b.extend(commonStrPrint("testStr1"))
    b.extend(commonStrPrintln("testStr1"))

def testStackStrPrint(b):
    headerIO(b)
    b.extend(stackStrPrint("beyond*comprehension"))
    b.extend(stackStrPrintln("..or*reason"))
    
def testHeapStrPrint(b):
    headerIO(b)
    hd = HeapData()
    hd.initStr("testStr1", "wikkyfoobartle")
    b.extend(hd.resultOpen())
    #! needs an additive offset
    b.extend(heapStrPrint(hd.offset("testStr1")))
    #! needs an additive offset
    b.extend(heapStrPrintln(hd.offset("testStr1")))
    b.extend(hd.resultClose())

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

def testRegPrint(b):
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
    b.extend(printNL())

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
    b.extend(printNL())
    b.extend(sd.intPrint('testData2'))
    b.extend(printNL())
    b.extend(sd.intPrint('testData3'))
    b.extend(printNL())
    
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
    b.extend(printNL())
    b.extend(sd.strPrint("testStr2"))
    b.extend(printNL())
    b.extend(sd.strPrint("testStr3"))
    b.extend(printNL())
    b.extend(sd.strPrint("testStr4"))
    b.extend(printNL())

def testStackArray(b):
    headerIO(b)
    sd = StackData()
    sd.declArray('testArray1', byteSpace.bit64, 12)
    sd.initArray('testArray2', byteSpace.bit64, [19, 445, 8, 17, 9])
    b.extend(sd.resultOpen())
    b.extend(sd.intArrayPrint("testArray1", byteSpace.bit64, 12))
    b.extend(printNL())    
    b.extend(sd.intArrayPrint("testArray2", byteSpace.bit64, 5))
    b.extend(printNL())    
    b.extend(printSeparator())
    

def testStackClutch(b):
    headerIO(b)
    sd = StackData()
    widths = [byteSpace.bit64, byteSpace.bit8, byteSpace.bit64]
    sd.declClutch('testClutch1', widths)
    data = [(22, byteSpace.bit64), (9, byteSpace.bit8), (77, byteSpace.bit64)]
    sd.initClutch('testClutch2', data)
    b.extend(sd.resultOpen())
    b.extend(sd.intClutchPrint("testClutch1", widths))
    b.extend(printNL())
    b.extend(sd.intClutchPrint("testClutch2", widths))
    b.extend(printNL()) 
#!    
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


def testHeapInt(b):
    headerIO(b)
    hd = HeapData()
    hd.initData("testData1", byteSpace.bit8, '66')
    hd.initData("testData2", byteSpace.bit8, '77')
    hd.initData("testData3", byteSpace.bit8, '99')
    print(hd)
    b.extend(hd.resultOpen())
    b.extend(hd.intPrint('testData1'))
    b.extend(printNL())
    b.extend(hd.intPrint('testData2'))
    b.extend(printNL())
    b.extend(hd.intPrint('testData3'))
    b.extend(printNL())
    b.extend(hd.resultClose())

def testHeapStr(b):
    headerIO(b)
    hd = HeapData()
    hd.initStr("testStr1", "wikkyfoobartle")
    hd.initStr("testStr2", "ghalumphev")
    hd.initStr("testStr3", "petalpeddlaring")
    hd.initStr("testStr4", "gonk")
    print(hd)
    b.extend(hd.resultOpen())
    b.extend(hd.strPrint("testStr1"))
    b.extend(printNL())
    b.extend(hd.strPrint("testStr2"))
    b.extend(printNL())
    b.extend(hd.strPrint("testStr3"))
    b.extend(printNL())
    b.extend(hd.strPrint("testStr4"))
    b.extend(printNL())
    b.extend(hd.resultClose())

def testHeapArray(b):
    headerIO(b)
    hd = HeapData()
    hd.declArray('testArray1', byteSpace.bit64, 12)
    hd.initArray('testArray2', byteSpace.bit64, [19, 445, 8, 17, 9])
    b.extend(hd.resultOpen())
    #off = hd.offset('testArray1')
    #i = 0
    #range(off, off, byteSpace.bit64)
    
    #def func():
    # "mov rcx, {}".format(i)
    #i += 1
    #hd.arrayForEach('testArray1', byteSpace.bit64, 12, func)
    #hd.arrayVisitEach('testArray1', byteSpace.bit64, 12, func)
    b.extend(hd.intArrayPrint("testArray1", byteSpace.bit64, 12))
    b.extend(printNL())    
    b.extend(hd.intArrayPrint("testArray2", byteSpace.bit64, 5))
    b.extend(printNL())    
    b.extend(hd.resultClose())


def testHeapClutch(b):
    headerIO(b)
    hd = HeapData()
    widths = [byteSpace.bit64, byteSpace.bit8, byteSpace.bit64]
    hd.declClutch('testClutch1', widths)
    
    data = [(22, byteSpace.bit64), (9, byteSpace.bit8), (77, byteSpace.bit64)]
    hd.initClutch('testClutch2', data)
    b.extend(hd.resultOpen())
    b.extend(hd.intClutchPrint("testClutch1", widths))
    b.extend(printNL())
    b.extend(hd.intClutchPrint("testClutch2", widths))
    b.extend(printNL()) 
            
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

def testIf2(b):
    headerIO(b)
    b.extend(strPrintln( "if code test?") )
    opCode.localSet(b, 'r14', '77')
    opCode.ifOpen(b, "L1", 'r14', '77', 'gte')
    b.extend( strPrintln( "gte runs success") )
    opCode.ifClose(b, "L1")
    opCode.ifOpen(b, "L2", 'r14', '77', 'lt')
    b.extend( strPrintln( "lt runs fail") )
    opCode.ifClose(b, "L2")    
    opCode.ifOpen(b, "L3", 'r14', '77', 'eq')
    b.extend( strPrintln( "eq runs success") )
    opCode.ifClose(b, "L3")  
    opCode.ifOpen(b, "L4", 'r14', '77', 'neq')
    b.extend( strPrintln( "neq runs fails") )
    opCode.ifClose(b, "L4")  
    b.extend( strPrintln("done") )
    #b.extend(sb.build())
        
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

def testWhile2(b):
    headerIO(b)
    b.append( "mov r14, 3" )
    opCode.whileOpen(b, "Loop1")
    b.extend( printReg('r14'))
    b.extend( printNL() )   
    b.append( "inc r14" )
    opCode.whileClose(b, "Loop1", 'r14', '8','gte')
    b.extend( strPrintln( "done") )

def testCallBlock(b):
    headerIO(b)
    b.extendFuncCode(funcOpen("testCall"))
    b.extendFuncCode(strPrintln("block called!"))
    b.extendFuncCode(funcClose())
    b.extend(strPrintln("block call?"))
    b.extend(funcInternCall("testCall"))
    b.extend(strPrintln("done"))
    b.extend(printNL())     
    
def testCallBlockParams(b):
    headerIO(b)
    b.extendFuncCode(x64["funcOpen"]("testCall"))
    b.extendFuncCode(printRegStr())
    b.extendFuncCode(x64["cReturnSet"](33))
    b.extendFuncCode(x64["funcClose"]())
    
    b.extend(strPrintln("block call?"))
    b.extend(x64["cParamSet"](0, 77))
    b.extend(x64["cParamSet"](1, 44))
    b.extend(x64["funcCall"]("testCall"))
    b.extend(printReg("rax"))
    b.extend(printNL())   


def testSwitch(b):
    headerIO(b)
    b.append("mov rbx, 1")
    b.extend(switchOpen([(0, 's0'),(1, 's1'),(2, 's2')], 'rbx'))
    #  [optional default code]
    b.extend(strPrintln("switch default code!"))
    b.extend(switchOpenClose("switch1Close"))
    # cases
    b.extend(caseStart('s1'))
    b.extend(strPrintln("switch to 1!"))
    b.extend(caseClose('switch1Close'))
    b.extend(caseStart('s2'))
    b.extend(strPrintln("switch to 2!"))
    b.extend(caseClose('switch1Close'))
    b.extend(caseStart('s0'))
    b.extend(strPrintln("switch to 0!"))
    # unecessary, runs on
    #b.extend(caseClose('switch1Close'))
    # close
    b.extend( switchClose("switch1Close")),
           
# def testComment(b):
    #! cant work, currently
    #autoComment(b, [ 
    #    staticVarStr(b, 'StrToPrint', 'ninechary')
    #    ])

def testClutchCode(b):
    headerIO(b)
    commonStrAlloc(b, "testStr1", "unfathomable...")
    b.extendFuncCode(opCode.testClutchCode())
    b.extendFuncCode("\n")    
    b.extend(funcInternCall("StringBuilder_create"))
    b.append("mov rbx, rax")
    
    #b.append("mov rdi, rbx")
    #b.append("mov rsi, testStr1")
    #b.extend(funcInternCall("StringBuilder_append"))
    #b.append("mov rdi, rbx")
    #b.append("mov rsi, testStr1")
    #b.extend(funcInternCall("StringBuilder_append"))
    #b.append("mov rdi, rbx")
    #b.append("mov rsi, testStr1")
    #b.extend(funcInternCall("StringBuilder_append"))

    #b.extend(heapStrPrintln('rbx'))
        
    #b.append("mov rdi, rbx")
    #b.extend(funcInternCall("StringBuilder_result"))
        
    #b.extend(heapStrPrintln('rax'))
    
    
    b.append("mov rdi, rbx")
    b.extend(funcInternCall("StringBuilder_size"))    
    b.extend(printReg('rax'))

    b.append("mov rdi, rbx")
    b.extend(funcInternCall("StringBuilder_allocSize"))    
    b.extend(printReg('rax'))
    
    b.append("mov rdi, rbx")
    b.extend(funcInternCall("StringBuilder_str"))    
    b.extend(heapStrPrintln('rax'))
    
    b.append("mov rdi, rbx")    
    b.extend(funcInternCall("StringBuilder_destroy"))
    #b.extend(printReg('rax'))

def main():
    b = CodeBuilder.Builder()
    test(b)
    print(b.frame(Frame64))
    
if __name__== "__main__":
    main()
