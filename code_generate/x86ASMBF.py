#!/usr/bin/env python3

import CodeBuilder
from assembly.nasmFrames import Frame64

cParemeterRegisters = [
"rdi", "rsi", "rdx", "rcx", "r8", "r9"
]

def cParameter(idx, v):
    if (idx < 6):
        return "mov {}, {}".format(cParemeterRegisters[idx], v)
    return "push {}".format(v)

def cReturn(dst):
    return "mov {}, rax".format(dst)
    
def array(declarationB, sectionB, sizeInBytes, name):
    sectionB['bss'].append("{}: resq 1".format(name))
    declarationB.append(cParameter(0, sizeInBytes))
    declarationB.append("call malloc")
    declarationB.append(cReturn(':' + name))

def free(declarationB, name):
    declarationB.append(cParameter(0, ':' + name))
    declarationB.append("call free")

def arrayInc(declarationB, name, idx):
    declarationB.append('inc [:{}+8*{}]'.format(name, idx))
    
def arrayDec(declarationB, name, idx):
    declarationB.append('dec [:{}+8*{}]'.format(name, idx))

def arrayWrite(declarationB, name, idx):
    declarationB.append(cParameter(0, idxAcess(name, idx)))
    declarationB.append("call putchar")
    
def idxAcess(name, idx):
    return "[{}+8*{}]".format(name, idx)
    
def arrayRead(declarationB, name, idx):
    declarationB.append("call getchar")
    declarationB.append(cReturn(idxAcess(name, idx)))

def whileNotZero(declarationB, countValue, body):
    loopName = "loop1"
    declarationB.append("mov rcx, {}".format(countValue))
    declarationB.append("{}:".format(loopName))
    body(declarationB)
    declarationB.append("dec rcx\ncmp rcx, 0\njg {}".format(loopName))


ASM = {
"Array" : array,
"free" : free,
# int data[100];
#int *array = malloc(10 * sizeof(int));
# malloc and free probably can be used
# if you want
"Array.inc" : arrayInc,
"Array.dec" : arrayDec,
"write" : arrayWrite, 
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
def test(b):
    #externalB = [
    #declarationB = [""]

    #sectionB ={"data": [""], "bss": [""], "rodata": [""]}

    #ASM["Array"](declarationB, sectionB, 64, "paving")
    ASM["Array"](b.declarations, b.sections, 64, "paving")

    arrayInc(b.declarations, 'paving', 3)
    arrayInc(b.declarations, 'paving', 3)
    arrayInc(b.declarations, 'paving', 3)
    arrayWrite(b.declarations, 'paving', 3)
    ASM["free"](b.declarations, "paving")
    
def main():
    b = CodeBuilder.Builder()
    test(b)
    print(b.frame(Frame64))
    
if __name__== "__main__":
    main()
