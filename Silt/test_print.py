#!/usr/bin/env python3

from template import *
import architecture

        
stackByteSize = 8
globalLabels = LabelGen()
#dataLabelsRO = LabelsROData()
# start a localstack
stackIndex = StackIndex(1)
b = Builder()

extern(b, 'malloc')
extern(b, 'calloc')
extern(b, 'realloc')
extern(b, 'free')


lr1 = stringROdefine(b, globalLabels.roData(), "In a Silent Way")

# funcStart(b, 'testFunc')
# frameStart(b)
# raw(b, 'mov rbx, 99')
# lr = mkLocationRoot('rbx')
# frameEnd(b)
# funcReturn(b, lr) 

funcStart(b, 'main')
frameStart(b)
stackAlloc(b, 4)
lr2 = lr1.toRegister(b, 'rbx')
# raw(b, 'mov rbx, 99')
Println(b, StrASCII, lr2)
# PrintFlush(b)

#outerFrame = Frame(b)
#p = Print(b) 
# raw(b, 'mov rax, 99')
# vp = VarPointer(b, stackIndex, 'rax')
# vp.toStack()
# vp.addrprint()
#strP = stringROdefine(b, stackIndex, dataLabelsRO, "The value in register RAX is:")
#strP = stringROdefine(b, stackIndex, dataLabelsRO, "True")
#strP.toRegister('rax')
#callFrame = VolatileProtectFrame(b)
#callFrame = RegisterProtectedFrame(b, ['rsi', 'rbi'])
#callProtect = RegisterProtect(b, ['rsi', 'rdi'])
#callProtect = RegistersVolatileProtect(b)
#Print().i64(b, 'rax')
#Print().string(b, str1)
#Print().newLine(b)
# aPtr = arrayPointerAllocate(b, stackIndex, 3)
# aPtr.toRegister('rbx')
# aPtr.update(3, 99999)
# aPtr.update(2, 77777)
# aPtr(2, 'rcx')
#cPtr = clutchAllocate(b, stackIndex, {'flat':2, 'house':4})
#cPtr.update('flat', 32764)
#cPtr.update('house', 256)
#cPtr('house', 'rcx')
#cPtr('flat', 'rcx')
#p.i64('rcx')
#p.newline()
#p.i64('rbx')
#p.newline()
#p.i64('rsi')

#raw(b, 'mov rax, 99')
#if1 = If(b, labels, LT('rax', 5))
#if1 = If(b, labels, NOT(LT('a', 5)))
#if1 = If(b, labels, AND([LT('a', 5), LT('b', 7), LT('c', 9)  ]))
#if1 = If(b, labels, OR([LT('a', 5), LT('b', 7), LT('c', 9)  ]))
#if1 = If(b, labels, AND([LT('a', 5), LT('b', 7), NOT(LT('c', 9))  ]))
#if1 = If(b, labels, AND([LT('a', 5), OR([LT('b', 7), LT('c', 9)]) ]))
#while1 = While(b, labels, LT('rax', 5))
#while1 = While(b, labels, NOT(LT('rax', 5)))
#while1 = While(b, labels, AND([LT('rax', 5), LT('b', 7), LT('c', 9)  ]))
#while1 = While(b, labels, OR([LT('rax', 5), LT('b', 7), LT('c', 9)  ]))
#raw(b, ';  ifblock')
#raw(b, ';  whileblock')
#Print().stringln(b, strP)
#Print.flush(b)
#if1.close(b)
#while1.close(b)
#callProtect.close(b)

     

frameEnd(b)
sysExit(b, 0)

funcEnd(b, False)      

write(b, baseStyle)

