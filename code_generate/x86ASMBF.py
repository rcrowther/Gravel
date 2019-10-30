#!/usr/bin/env python3
import sys

import CodeBuilder
from assembly.nasmFrames import Frame64

cParemeterRegisters = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
cParemeterFloatRegisters = [
    "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6"
    ]
    
cReturn = ["rax", "rdx"]

####
# func helpers
#
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
    b.sections['rodata'].append('io_fmt_reg_rdx: db 10, "= Reg rdx: %lld", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rsp: db 10, "= Reg rsp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_rbp: db 10, "= Reg rbp: %llu", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_r9: db 10, "= Reg r9: %lld", 10, 0')

    b.sections['rodata'].append('io_fmt_reg: db 10, "= GenReg", 10, "rax: %lld", 10, "rbx: %lld", 10, "rcx: %lld", 10, "rdx: %lld", 10, 0')
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

def printlnStr(b, msg):
    b.sections['rodata'].append('testStr2: db "{}", 0'.format(msg))
    b.declarations.append(cParameter(0, "io_fmt_str8_NL", False))
    b.declarations.append(cParameter(1, "testStr2", False))    
    b.declarations.append("call printf")
        
def printNL(b):
    b.declarations.append(cParameter(0, "io_fmt_nl", False))
    b.declarations.append("call printf")

#     "rdi", "rsi", "rdx", "rcx", "r8", "r9"
PrintableRegisters = ['rax', 'rdx', 'rsp', 'rbp', 'r9']
def printReg(b, reg):
    if(reg not in PrintableRegisters):
        print("[Error] given register name not printable: {}\n    allowed registers {}".format(reg, PrintableRegisters))
        sys.exit()
    b.declarations.append("sub rsp, 32")
    b.declarations.append("mov [rbp-8*1], rsi")
    b.declarations.append("mov [rbp-8*2], rdi")
    b.declarations.append("mov [rbp-8*3], {}".format(reg))
    if (reg == 'rsp'):
        b.declarations.append("add qword [rbp-8*3], 32")
    b.declarations.append(cParameter(0, "io_fmt_reg_{}".format(reg), False))
    b.declarations.append(cParameter(1, "rbp-8*3", True))     
    b.declarations.append("call printf")
    b.declarations.append("mov rsi, [rbp-8*1]")
    b.declarations.append("mov rdi, [rbp-8*2]")        
    b.declarations.append("mov {}, [rbp-8*3]".format(reg))
    if (reg != 'rsp'):
        b.declarations.append("add rsp, 32")

def printRegGen(b):
    b.declarations.append("sub rsp, 64")
    b.declarations.append("mov [rbp-8*1], rdi")
    b.declarations.append("mov [rbp-8*2], rsi")
    b.declarations.append("mov [rbp-8*3], rdx")
    b.declarations.append("mov [rbp-8*4], r8")
    b.declarations.append("mov [rbp-8*5], rax")
    b.declarations.append("mov [rbp-8*6], rbx")
    b.declarations.append("mov [rbp-8*7], rcx")
    b.declarations.append(cParameter(0, "io_fmt_reg", False))
    b.declarations.append(cParameter(1, "rbp-8*5", True))     
    b.declarations.append(cParameter(2,  "rbp-8*6", True))     
    b.declarations.append(cParameter(3,  "rbp-8*7", True))     
    b.declarations.append(cParameter(4,  "rbp-8*3", True))    
    b.declarations.append("call printf")  
    b.declarations.append("mov rdi, [rbp-8*1]")
    b.declarations.append("mov rsi, [rbp-8*2]")
    b.declarations.append("mov rdx, [rbp-8*3]")
    b.declarations.append("mov r8, [rbp-8*4]")
    b.declarations.append("mov rax, [rbp-8*5]")
    b.declarations.append("mov rbx, [rbp-8*6]")
    b.declarations.append("mov rcx, [rbp-8*7]")
    b.declarations.append("add rsp, 64")
    
def printRegStack(b):
    b.declarations.append("sub rsp, 32")
    b.declarations.append("mov [rbp-8*1], rsi")
    b.declarations.append("mov [rbp-8*2], rdi")
    b.declarations.append("mov [rbp-8*3], rdx")
    b.declarations.append("mov [rbp-8*4], rsp")
    b.declarations.append("add qword [rbp-8*4], 32")
    b.declarations.append(cParameter(0, "io_fmt_reg_stack", False))
    b.declarations.append(cParameter(1, "rbp-8*4", True))     
    b.declarations.append(cParameter(2,  "rbp", False)) 
    b.declarations.append("call printf")
    b.declarations.append("mov rsi, [rbp-8*1]")
    b.declarations.append("mov rdi, [rbp-8*2]") 
    b.declarations.append("mov rdx, [rbp-8*3]")
    b.declarations.append("add rsp, 32")
 
def printRegStr(b):
    b.declarations.append("sub rsp, 32")
    b.declarations.append("mov [rbp-8*1], rsi")
    b.declarations.append("mov [rbp-8*2], rdi")
    b.declarations.append("mov [rbp-8*3], rdx")
    b.declarations.append(cParameter(0, "io_fmt_reg_str", False))
    b.declarations.append(cParameter(1, "rbp-8*1", True))     
    b.declarations.append(cParameter(2,  "rbp-8*2", True)) 
    b.declarations.append("call printf")  
    b.declarations.append("mov rsi, [rbp-8*1]")
    b.declarations.append("mov rdi, [rbp-8*2]")
    b.declarations.append("mov rdx, [rbp-8*3]")
    b.declarations.append("add rsp, 16")
    
def printRegExt1(b):
    # Can clobber Gen registers
    b.declarations.append("sub rsp, 64")
    b.declarations.append("mov [rbp-8*1], r8")
    b.declarations.append("mov [rbp-8*2], r9")
    b.declarations.append("mov [rbp-8*3], r10")
    b.declarations.append("mov [rbp-8*4], r11")
    b.declarations.append(cParameter(0, "io_fmt_reg_64_1", False))
    b.declarations.append(cParameter(1, "rbp-8*1", True))     
    b.declarations.append(cParameter(2,  "rbp-8*2", True))     
    b.declarations.append(cParameter(3,  "rbp-8*3", True))     
    b.declarations.append(cParameter(4,  "rbp-8*4", True))         
    b.declarations.append("call printf")
    b.declarations.append("mov r8, [rbp-8*1]")
    b.declarations.append("mov r9, [rbp-8*2]")
    b.declarations.append("mov r10, [rbp-8*3]")
    b.declarations.append("mov r11, [rbp-8*4]")
    b.declarations.append("add rsp, 64")

def printRegExt2(b):
    # Can clobber Gen registers
    b.declarations.append("sub rsp, 64")
    b.declarations.append("mov [rbp-8*1], r12")
    b.declarations.append("mov [rbp-8*2], r13")
    b.declarations.append("mov [rbp-8*3], r14")
    b.declarations.append("mov [rbp-8*4], r15")
    b.declarations.append(cParameter(0, "io_fmt_reg_64_2", False))
    b.declarations.append(cParameter(1, "rbp-8*1", True))     
    b.declarations.append(cParameter(2,  "rbp-8*2", True))     
    b.declarations.append(cParameter(3,  "rbp-8*3", True))     
    b.declarations.append(cParameter(4,  "rbp-8*4", True))         
    b.declarations.append("call printf")
    b.declarations.append("mov r12, [rbp-8*1]")
    b.declarations.append("mov r13, [rbp-8*2]")
    b.declarations.append("mov r14, [rbp-8*3]")
    b.declarations.append("mov r15, [rbp-8*4]")
    b.declarations.append("add rsp, 64")
    
####
# Utility
#
def staticBuffer(b, name):
    b.sections['data'].append("{}: dq 2048")

def staticVar(b, name, v):
    b.sections['data'].append("{}: dq {}".format(name, v))

def staticVarStr(b, name, v):
    b.sections['data'].append('{}: db "{}"'.format(name, v))

def staticVal(b, name, v):
    b.sections['rodata'].append('{}: dq "{}"'.format(name, v))
        
def comment(b, msg):
    b.declarations.append("; {}".format(msg))

def mark(b):
    b.declarations.append("; *")
    
# def autoComment(b, ins):
    # for idx,iStr in enumerate(ins):
        # comment(b, "comm1" + str(idx))
        # comment(b, iStr)

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

def testPrintDebug(b):
    headerIO(b)
    printReg(b, 'rbp')
    printReg(b, 'rsp')
    printReg(b, 'rsp')
    b.declarations.append('mov rax, 363')
    printReg(b, 'rax')
    printRegStack(b)
    b.declarations.append('mov rcx, 757')
    printRegGen(b)
    printRegStr(b)
    printStr(b, "done")
    printlnStr(b, "doner")
        
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
