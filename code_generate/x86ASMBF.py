#!/usr/bin/env python3

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
    #b.headers.rodata.append('io_fmt_utf8: db "%s"', 10, 0)
    b.sections['rodata'].append('io_fmt_int: db "%d", 0')
    b.sections['rodata'].append('io_fmt_float: db "%g", 0')
    b.sections['rodata'].append('io_fmt_addr: db "%p", 0')
    b.sections['rodata'].append('io_fmt_println: db "%s", 10, 0')
    b.sections['rodata'].append('io_fmt_nl: db "", 10, 0')
    b.sections['data'].append("mch_str_buf: dq 2048")
    # reg print
    b.sections['rodata'].append('io_fmt_reg: db 10, "= GenReg", 10, "rax: %d", 10, "rbx: %d", 10, "rcx: %d", 10, "rdx: %d", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_stack: db 10, "= StackReg", 10, "rsp: %d", 10, "rbp: %d", 10, "diff: %d", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_str: db 10, "= StringReg", 10, "rsi: %d", 10, "rdi: %d", 10, 0')
    b.sections['rodata'].append('io_fmt_reg_64: db 10, "= ExtReg", 10, "r8: %d", 10, "r9: %d", 10, "r10: %d", 10, 0')


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

#def printStr(b, s):
    
def printNL(b):
    b.declarations.append(cParameter(0, "io_fmt_nl", False))
    b.declarations.append("call printf")
    
def printReg(b):
    b.declarations.append("mov r10, rax")
    b.declarations.append("mov r11, rbx")
    b.declarations.append("mov r12, rcx")
    b.declarations.append("mov r13, rdx")
    b.declarations.append(cParameter(0, "io_fmt_reg", False))
    b.declarations.append(cParameter(1, "r10", False))    
    b.declarations.append(cParameter(2, "r11", False))
    b.declarations.append(cParameter(3, "r12", False))
    b.declarations.append(cParameter(4, "r13", False))
    #if (reg != 'rsi'):
    #    b.declarations.append(cParameter(1, reg, False))    
    b.declarations.append("call printf")    

def printRegStack(b):
    # calc diff    
    b.declarations.append("mov rax, rsp")
    b.declarations.append("sub rax, rbp")
    b.declarations.append("mov r13, rax")
    # print
    b.declarations.append("mov r10, rsp")
    b.declarations.append("mov r11, rbp")
    b.declarations.append(cParameter(0, "io_fmt_reg_stack", False))
    b.declarations.append(cParameter(1, "r10", False))    
    b.declarations.append(cParameter(2, "r11", False))
    b.declarations.append(cParameter(3, "r13", False))
    b.declarations.append("call printf")  

 
def printRegStr(b):
    b.declarations.append("mov r10, rsi")
    b.declarations.append("mov r11, rdi")
    b.declarations.append(cParameter(0, "io_fmt_reg_str", False))
    b.declarations.append(cParameter(1, "r10", False))    
    b.declarations.append(cParameter(2, "r11", False))   
    b.declarations.append("call printf")  

def printReg64(b):
    #! something wrong with pushing
    b.declarations.append("push r8")
    b.declarations.append("push r9")
    b.declarations.append("push r10")
    b.declarations.append(cParameter(0, "io_fmt_reg_64", False))
    b.declarations.append(cParameter(1, "rsp", True))    
    b.declarations.append(cParameter(2, "rsp+8*1", True))     
    b.declarations.append(cParameter(3, "rsp+8*2", True))     
    b.declarations.append("call printf")  
    
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
    printRegStack(b)
    printRegStr(b)
    printReg(b)
    printNL(b)
    b.declarations.append('mov rdx, 78787')
    printReg(b)
    printReg64(b)
        
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
