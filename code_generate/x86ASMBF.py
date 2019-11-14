#!/usr/bin/env python3
import sys
import math

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

    
cParemeterRegisters = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
cParemeterFloatRegisters = [
    "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6"
    ]
    
cReturn = ["rax", "rdx"]

####
# Build helpers
#
class SectionBuilder():
    def __init__(self):
        self.initDeclarations = []
        self.declarations = []


class StrInit():
    # Helper to create an initialised string.
    # Works by breaking the string into chunks. These chunks (
    # essentially bit-width numbers) can be declared as 
    # ''mov' commands to an appropriate space.
    # The size the space needs to be is returned by byteSize().
    
    def __init__(self, s, chunkSize):
        # helper to form initialised strings for assembly
        # @chunksize is usually byteSpace.bit64 
        self.chunkSize = chunkSize
        self.chunkString = self._strChunk(s)
        
    def _strChunk(self, s):
        # chunk a string into a given bytesize
        # @return is an array of chunks, with the last padded with zeros
        # to the chunksize
        
        # convert this python str
        #sBytes = toBytes(s)         
        sBytes = s         
        # chunk...
        l = len(sBytes)
        k, m = divmod(l, self.chunkSize)
        # chunk what is chunkable by chunkSize
        ret = [sBytes[(i * self.chunkSize):((i * self.chunkSize) + self.chunkSize)] for i in range(k)]
        # pad the last chunk
        #last = bytearray(sBytes[l - m:])
        #last.extend(bytearray(self.chunkSize - len(last)) )
        last = sBytes[l - m:]
        ext = '\0' * (self.chunkSize - m)
        last += ext
        ret.append(last)
        return ret
    
    def byteSize(self):
        # length of chunked string in bytes
        # Will be a multiple of chunkSize
        return len(self.chunkString) * self.chunkSize
    
    def initDecs(self, b, basePtr, startOffset):
        # Append a string of instructions to initialise a string
        # @s the string
        # @basePtr a register containing a pointer to some allocated space
        # @startOffset offset from basePointer to start from 
        print(self)
        topPtr = startOffset
        for chunk in self.chunkString:
            # s = ''.join( for b in chunk)
            #strOut = ''.join(str(c) for c in chunk)
            #strOut = str(chunk)
            #strOut = '"{}"'.format(chunk.decode("ascii"))
            strOut = chunk.__repr__()[1:-1]
            #b.declarations.append('"{}"'.format(strOut))
            b.declarations.append('mov qword [{}+{}], "{}"'.format(basePtr, topPtr, strOut))
            topPtr += self.chunkSize
            
    def __repr__(self):
        return "StrInit(chunkSize:{}, chunkString:{})".format(
            self.chunkSize, self.chunkString
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

## Printers
#! What about returns
def headerIO(b):
    print(str(b ))
    b.headers.append("extern printf")
    b.headers.append("extern snprintf")
    b.sections['rodata'].append('io_fmt_str8: db "%s", 0')
    b.sections['rodata'].append('io_fmt_str8_NL: db "%s", 10, 0')
    #b.headers.rodata.append('io_fmt_utf8: db "%s"', 10, 0)
    b.sections['rodata'].append('io_fmt_int: db "%d", 0')
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

#! need fresh varnames
def printStr(b, msg):
    b.sections['rodata'].append('testStr: db "{}", 0'.format(msg))
    b.declarations.append(cParameter(0, "io_fmt_str8", False))
    b.declarations.append(cParameter(1, "testStr", False))    
    b.declarations.append("call printf")

def printStrPtr(b, ptrCode):
    b.declarations.append(cParameter(0, "io_fmt_str8", False))
    b.declarations.append(cParameter(1, ptrCode, False))    
    b.declarations.append("call printf")
    
def printlnStr(b, msg):
    b.sections['rodata'].append('testStr2: db "{}", 0'.format(msg))
    b.declarations.append(cParameter(0, "io_fmt_str8_NL", False))
    b.declarations.append(cParameter(1, "testStr2", False))    
    b.declarations.append("call printf")
        
def printNL(b):
    b.declarations.append(cParameter(0, "io_fmt_nl", False))
    b.declarations.append("call printf")

#     "rdi", "rsi", "rdx", "rcx", "r8", "r9"
PrintableRegisters = ['rax', 'rbx', 'rcx', 'rdx', 'rsp', 'rbp', 'r9' 'r10',]
def printReg(b, reg):
    # cant do rdi, rsi?
    # Clobbers rdi, rsi
    if(reg not in PrintableRegisters):
        print("[Error] given register name not printable: {}\n    allowed registers {}".format(reg, PrintableRegisters))
        sys.exit()
    b.declarations.append(cParameter(0, "io_fmt_reg_{}".format(reg), False))
    b.declarations.append(cParameter(1, reg, False))
    b.declarations.append("call printf")

def printRegGen(b):
    # Clobbers rdi, rsi, rdx, rcx, r8
    # set rdx before params clobber it
    b.declarations.append(cParameter(4,  "rdx", False))    
    b.declarations.append(cParameter(0, "io_fmt_reg_gen", False))
    b.declarations.append(cParameter(1, "rax", False))     
    b.declarations.append(cParameter(2,  "rbx", False))     
    b.declarations.append(cParameter(3,  "rcx", False))     
    b.declarations.append("call printf")  

    
def printRegStack(b):
    # Clobbers rdi, rsi, rdx
    b.declarations.append(cParameter(0, "io_fmt_reg_stack", False))
    b.declarations.append(cParameter(1, "rbp", False))     
    b.declarations.append(cParameter(2,  "rsp", False)) 
    b.declarations.append("call printf")
 
def printRegStr(b):
    # Clobbers rdi, rdx
    b.declarations.append(cParameter(0, "io_fmt_reg_str", False))
    # param 1 is rsi :)
    b.declarations.append(cParameter(2,  "rdi", False)) 
    b.declarations.append("call printf")  

    
def printRegExt1(b):
    # Clobbers rdi, rsi, rdx, rcx, r8
    b.declarations.append(cParameter(0, "io_fmt_reg_64_1", False))
    b.declarations.append(cParameter(1, "r8", False))     
    b.declarations.append(cParameter(2, "r9", False))     
    b.declarations.append(cParameter(3, "r10", False))     
    b.declarations.append(cParameter(4, "r11", False))         
    b.declarations.append("call printf")


def printRegExt2(b):
    # Clobbers rdi, rsi, rdx, rcx, r8
    b.declarations.append(cParameter(0, "io_fmt_reg_64_2", False))
    b.declarations.append(cParameter(1, "r12", False))     
    b.declarations.append(cParameter(2, "r13", False))     
    b.declarations.append(cParameter(3, "r14", False))     
    b.declarations.append(cParameter(4, "r15", False))         
    b.declarations.append("call printf")


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

def commonStr(b, name, v):
    b.sections['data'].append('{}: db "{}"'.format(name, v))
        
def commonBuffer(b, name):
    b.sections['data'].append("{}: dq 2048")


    
####
# Stack
#
class StackAlloc():
    # Can be used per call
    def __init__(self):
        self.topPtr = 0
        self.nameOffset = {}
        self.declarations = []
                
    def declareData(self, name):
        self.topPtr += 8
        self.nameOffset[name] = math.floor(self.topPtr/8)

    def initData(self, name, v):
        self.declareData(name)
        self.declarations.append("mov [bpr+{}*8], {}".format(self.nameOffset[name], v))
        
    #! replace with strInit()
    def _strChunk(self, s, chunkSize):
        #
        l = len(s)
        k, m = divmod(l, chunkSize)
        #return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(chunkSize))
        ret = [s[(i * chunkSize):(i * chunkSize + chunkSize)] for i in range(k)]
        last = s[l - m:]
        #lastIdx = len(ret)-1
        while (len(last) < chunkSize):
           last += '\0'
        ret.append(last)
        return ret
        
    #! replace with strInit()
    def declareStr(self, name, s):
        # set a pointer to next val
        self.initData(name, self.topPtr+8)
        # add string after
        # chop up and move in,
        ss = self._strChunk(s, 8)
        #ptr = self.topPtr
        for chunk in ss:
            self.topPtr += 8
            self.declarations.append("mov [bpr+{}], {}".format(self.topPtr, chunk))

    def visit(self, name):
        return "[bpr+{}*8]".format(self.nameOffset[name])

    def build(self, b):
        alignedSpace = math.ceil(self.topPtr/16) * 16 
        b.declarations.append("sub rsp, {}".format(alignedSpace))
        b.declarations.extend(self.declarations)

    def __repr__(self):
        return "StackAlloc(topPtr:{}, nameOffset:{})".format(
            self.topPtr, self.nameOffset
            )
    
class HeapData():
    # Alloc(), then use utility functions to get manipulation code.
    # use build() in final code, before data is manipulated, to write 
    # declarations. 
    def __init__(self, addrReg):
        self.size = 0           
        self.addrReg = addrReg
        self.namedOffset = {}

    def alloc(self, name, sz):
        self.namedOffset[name] = self.size 
        self.size += sz
        
    def initStr(self, b, name, s):
        # make helper
        si = StrInit(s, byteSpace.bit64)

        # Alloc space
        self.alloc(name, si.byteSize())
         
        # add init declarations
        #! this is writing out wrong
        si.initDecs(b, self.addrReg, self.namedOffset[name])

    def set(self, b, name, v):
        b.declarations.append("mov qword [{}+{}*8], {}".format(self.addrReg, self.namedOffset[name], v))
        
    def get(self, b, name, to):
        b.declarations.append("mov {}, [{}+{}*8]".format(to, self.addrReg, self.namedOffset[name]))

    def build(self, sb):
        # set the malloc
        sb.initDeclarations.append(cParameter(0, self.size, False))
        sb.initDeclarations.append("call malloc")
        sb.initDeclarations.append(cReturn(self.addrReg, False))
        
    def free(self, b):
        b.declarations.append(cParameter(0, self.addrReg, False))
        b.declarations.append("call free")
            
    def __repr__(self):
        return "HeapData(size:{}, addrReg:{}, namedOffset:{})".format(
            self.size, self.addrReg, self.namedOffset
            )


# No, what you need to do is add the declarations as they arrive?
# or stack them in a frame? Needsas the frames....
#! do something about string encoding                    
# class HeapAlloc():
    # # Can be used per call
    # # uses a pool?
    # def __init__(self):
        # # Malloc for vars
        # # 8 addresses
        # self.varSpace = self.namespaceAllocData(64, 64, 'r11')
        # self.declarations = []
        
    # def alloc(b, sizeInBytes, reg):
        # b.declarations.append(cParameter(0, self.varSpace, False))
        # b.declarations.append("call malloc")
        # b.declarations.append(cReturn("r11", True))
                
    # def declareData(self, name, size, v):
        # self.varSpace.data(name, size)
        # #self.namedVarOffset[name] = math.floor(self.varTopPtr/8)    

    # def initData(self, name, v):
        # self.declareData(name)
        # self.declarations.append("mov [bpr+{}*8], {}".format(self.namedVarOffset[name], v))

    # def build(self, b):
        # #  set the now-sized malloc
        # alignedSpace = math.ceil(self.size/16) * 16 
        # b.declarations.append(cParameter(0, alignedSpace, False))
        # b.declarations.append("call malloc")
        # b.declarations.append(cReturn(self.varSpace.addrReg, True))
        # # add the declarations
        

    # def __repr__(self):
        # return "HeapAlloc(varSpace:{}, declarations:{})".format(
            # self.varSpace, self.declarations,
            # )
            
###
# Malloc
#
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

##
# loop
#
def whileNotZero(b, countValue, body):
    loopName = "loop1"
    b.declarations.append("mov rcx, {}".format(countValue))
    b.declarations.append("{}:".format(loopName))
    body(b)
    b.declarations.append("dec rcx\ncmp rcx, 0\njg {}".format(loopName))


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
"whileNotZero" : whileNotZero,
}

# def resolveBuilders(externalB, sectionB, declarationB):
    # externalB.append("data:")
    # externalB.append("\n".join(sectionB["data"]))
    # externalB.append("rodata:")
    # externalB.append("\n".join(sectionB["rodata"]))
    # externalB.append("bss:")
    # externalB.append("\n    ".join(sectionB["bss"]))
    # externalB.append("text:")
    # externalB.append("\n    ".join(declarationB))
    # return "\n".join(externalB)
    
    
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
    printlnStr(b, "doner")
    
def testPrintDebug(b):
    headerIO(b)
    printReg(b, 'rbp')
    printReg(b, 'rsp')
    printReg(b, 'rsp')
    b.declarations.append('mov rax, 363')
    printReg(b, 'rax')
    printRegStr(b)
    b.declarations.append('mov rcx, 757')
    printRegGen(b)
    printRegStr(b)

def testStackAlloc():
    a = StackAlloc()
    a.declareData("testVar1")
    print(a.visit("testVar1"))
    a.initData("initVar", 674)
    print(a.visit("initVar"))
    a.declareStr("sampleString", "cool*as*ice")
    print(a.visit("sampleString"))
    a.initData("after", 674)
    print(a.visit("after"))
    print(str(a))
    print("\n".join(a.declarations))
    
def testStaticAlloc(b):
    headerIO(b)
    commonNum(b, "commonNum1", 1212)
    commonStr(b, "commonStr1", "insane drift")
    b.declarations.append("mov rax, [commonNum1]")
    printReg(b, 'rax')
    printNL(b)

def testStackString(b):
    pass
        
def testHeapData(b):
    headerIO(b)
    a = HeapData('r11')
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

def testHeapStr(b):
    headerIO(b)
    a = HeapData('r11')    
    sb = SectionBuilder()
    a.initStr(sb, "testStr", "wikkyfoobar")
    print(a)
    a.build(sb)
    b.appendSection(sb)
    printStrPtr(b, "r11+{}".format(a.namedOffset["testStr"]))
    printNL(b)

def testWhile(b):
    pass   
     
def testArray(b):
    headerIO(b)
    ASM["Array"](b, 64, "paving")
    arrayInc(b, 'paving', 3)
    arrayInc(b, 'paving', 3)
    arrayInc(b, 'paving', 3)
    arrayWrite(b, 'paving', 3)
    stdoutNewLine(b)
    ASM["free"](b, "paving")
   
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
