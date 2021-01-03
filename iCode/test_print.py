#!/usr/bin/env python3

from template import *

        
stackByteSize = 8
dataLabels = DataLabels()
# start a localstack
localStack = LocalStack(stackByteSize, 1)
b = Builder()
outerFrame = Frame(b) 
raw(b, 'mov rax, 99')
str1 = stringROdefine(b, dataLabels, "The value in register RAX is:")
#callFrame = Frame(b)
#callFrame = VolatileProtectFrame(b)
#callFrame = RegisterProtectedFrame(b, ['rsi', 'rbi'])
#callProtect = RegisterProtect(b, ['rsi', 'rdi'])
#callProtect = RegistersVolatileProtect(b)
#Print().i64(b, 'rax')
#Print().string(b, str1)
#Print().newLine(b)
Print().stringln(b, str1)
Print().flush(b)
#callProtect.close(b)
#callFrame.close(b)
outerFrame.close(b)
sysExit(b, 0)

write(b, baseStyle)

