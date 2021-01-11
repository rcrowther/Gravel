#!/usr/bin/env python3

from template import *

        
stackByteSize = 8
dataLabels = DataLabels()
# start a localstack
localStack = LocalStack(stackByteSize, 1)
b = Builder()
#outerFrame = Frame(b)
#p = Print(b) 
raw(b, 'mov rax, 99')
vp = VarPointer(b, localStack, 'rax')
vp.toStack()
vp.addrprint()
#strP = stringROdefine(b, localStack, dataLabels, "The value in register RAX is:")
#strP.toRegister('rax')
#callFrame = Frame(b)
#callFrame = VolatileProtectFrame(b)
#callFrame = RegisterProtectedFrame(b, ['rsi', 'rbi'])
#callProtect = RegisterProtect(b, ['rsi', 'rdi'])
#callProtect = RegistersVolatileProtect(b)
#Print().i64(b, 'rax')
#Print().string(b, str1)
#Print().newLine(b)
# aPtr = arrayPointerAllocate(b, localStack, 3)
# aPtr.toRegister('rbx')
# aPtr.update(3, 99999)
# aPtr.update(2, 77777)
# aPtr(2, 'rcx')
#cPtr = clutchAllocate(b, localStack, {'flat':2, 'house':4})
#cPtr.update('flat', 32764)
#cPtr.update('house', 256)
#cPtr('house', 'rcx')
#cPtr('flat', 'rcx')
#p.i64('rcx')
#p.newline()
#p.i64('rbx')
#p.newline()
#p.i64('rsi')

#Print().stringln(b, strP)
Print.flush(b)
#callProtect.close(b)
#callFrame.close(b)
#outerFrame.close(b)
sysExit(b, 0)

write(b, baseStyle)

