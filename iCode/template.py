#!/usr/bin/env python3

import nasmFrames


# An intermediate code that captures some of the generic nature of
# opcodes.
# It is not intended to be compressed, like Java or CL bytecode.
# It is much more sophisticated, and so would not readily become
# bytecode.
# AFAIK. It also deals with opcodes, so is not much like a Hardware 
# Definition Language, either. 
# The aim of the language is to rationalise the generic nature of many
# processing instructions into higher level constrructs.
# It is not the aim of the language to decide where anything goes or 
# how, Only to get it there, and be reasonably generic and 
# cross-platform in it's action.
# It is easy to go wrong with the lanaguage. For example, overwrriting 
# useful values in a register.
# Currently, no protection is built in.
baseStyle = {
    'indent': '    '
}

architectureX64 = {
#!
}

registers = [
    "rax", 
    "rbx",
    "rcx",
    "rdx",
    "rbp",
    "rsi",
    "rdi"
    "rsp",
]

#   %ebp, %ebx, %edi and %esi must be preserved   
# clobbers r10, r11 and any parameter registers 
cParameterRegister = [
    "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ]
cParemeterFloatRegister = [
    "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6"
    ]
    
    
def byteSize(bitsize):
    return bitsize >> 3


class Builder():
    def __init__(self):
        self._externs = set()
        self._data = set()
        self._rodata = set()
        self._bss = set()
        self._text = []
        self._code = []
        
    def externsAdd(self, s):
        self._externs.add(s)
        
    def dataAdd(self, s):
        self._data.add(s)
     
    def rodataAdd(self, s):
        self._rodata.add(s)
             
    def bssAdd(self, s):
        self._bss.add(s)
  
    def textAdd(self, s):
        self._text.append(s)
        
    ## For code, defaults to class implementation
    def __iadd__(self, s):
       self._code.append(s)
       return self
         
    def __repr__(self):
        return "Builder()"


def builderPrint(frame, b, style):
    indent = style['indent']
    joinIndent = '\n' + indent
    styledBuilder = {
        'externs' : '\n'.join(b._externs), 
        'data' : indent + joinIndent.join(b._data), 
        'rodata'  : indent + joinIndent.join(b._rodata), 
        'bss'  : indent + joinIndent.join(b._bss), 
        'text' : '\n'.join(b._text),
        'code' : indent + joinIndent.join(b._code),
    }
    return frame(**styledBuilder)
     
     
     
## Builder handlers
def raw(b, content):
    b += content

def sysExit(b, code=0):    
    b += "mov rax, 60"
    b += "mov rdi, " + str(code)
    b += "syscall"
    
def stringROdefine(b, dataLabels, string):
    label = dataLabels.newLabel()
    rodata = label + ': db "' + string + '", 0'
    b.rodataAdd(rodata)
    return label
        
        
        
class Print():
    def extern(self, b):
        b.externsAdd("extern fflush")
        b.externsAdd("extern printf")

    def flush(self, b):
        b += "mov rdi, 0"
        b += "call fflush"
            
    def generic(self, b, form, source):
        self.extern(b)
        b += "mov rdi, " + form
        b += "mov rsi, " + source
        b += "call printf"

    def newLine(self, b):
        self.extern(b)
        b.rodataAdd('printNewLine: db 10, 0')
        b += "mov rdi, printNewLine"
        b += "call printf"

    def char(self, b, source):
        b.rodataAdd('printCharFmt: db "%c", 0')
        self.generic(b, 'printCharFmt', source)
            
    def string(self, b, source):
        self.extern(b)
        b += "mov rdi, " + source
        b += "call printf"
        
    def i32(self, b, source):
        b.rodataAdd('print32Fmt: db "%li", 0')
        self.generic(b, 'print32Fmt', source) 

    def i64(self, b, source):
        b.rodataAdd('print64Fmt: db "%lli", 0')
        self.generic(b, 'print64Fmt', source)

    def float(self, b, form, source):
        self.extern(b)
        b.rodataAdd('printFloatFmt: db "%g", 0')
        b += "movsd xmm0, printlnFloatFmt"
        b += "mov rdi, " + source
        b += "call printf"
   
    def stringln(self, b, source):
        b.rodataAdd('printlnStrFmt: db "%s", 10, 0')
        self.generic(b, 'printlnStrFmt', source) 



class Frame():
    '''
    Write a basic frame.
    '''
    def __init__(self, b):
        b += "push rbp"
        b += "mov rbp, rsp"

    
    def close(self, b):
        b += "mov rsp, rbp"
        b += "pop rbp"


class RegistersProtect():
    '''
    Protect selected registers.
    '''
    def __init__(self, b, registerList):
        self.registerList = registerList
        for r in  registerList:
            b += 'push ' + r

    def close(self, b):
        for r in reversed(self.registerList):
            b += 'pop ' + r
                                
class RegistersVolatileProtect(RegistersProtect):
    '''
    Protect the volatile registers 
    i.e. those used for parameter passing.
    '''
    def __init__(self, b):
        super().__init__(b, cParameterRegister.copy()) 
        
                           
class LocalStack():
    # A stack for local positions
    # provides offsets and carries the stackByteSize
    def __init__(self, stackByteSize, initialOffset):
        self.stackByteSize = stackByteSize
        self.idx = initialOffset - 1

    def newOffset(self):
        # return a new offset on the stack
        self.idx += 1
        #b += "push {}".format(addressLocation))
        return self.idx
    
    def __repr__(self):
        return "LocalStack(stackByteSize: {})".format(self.stackByteSize)
    
                        
class DataLabels():
    '''
    Generate data labels
    '''
    def __init__(self):
        self.idx = - 1

    def newLabel(self):
        '''
        return 
            a new label
        '''
        self.idx += 1
        return 'ROData' + str(self.idx)

    def __repr__(self):
        return "DataLabels(idx: {})".format(self.idx)
    
    
class LocationBase():
    # location is either a register name or a stack offset
    # It can be used as a source of values, or as source of adresses to
    # values (a pointer) 
    def __init__(self, stackByteSize, address):
        self.stackByteSize = stackByteSize
        self.address = address

    def __call__(self):
        '''
        Code to retrive the value at the location.
        If a pointer, this is the pointer address
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        pass
            
    def __repr__(self):
        return "Location(address: {})".format(self.address)
        
    def __str__(self):
        return str(self.address)
            
class LocationStack(LocationBase):
    def __init__(self, stackByteSize, address):
        if (not (type(address) == int)):
            raise NotImplementedError('Parameter must be class int. address: {}'.format(type(address)))
        super.__init__(self,  stackByteSize, address)    

    def __call__(self):
        return 'rbp - {}'.format(self.address * self.stackByteSize)

class LocationRegister(LocationBase):
    def __init__(self, stackByteSize, address):
        if (not (address in registers)):
            raise NotImplementedError('Parameter must be in registers. address: {} registers:"{}"'.format(
            type(address),
            ", ".join(registers)
            ))
        super.__init__(self,  stackByteSize, address)    

    def __call__(self):
        return self.address

class LocationROData(LocationBase):
    def __init__(self, stackByteSize, address):
        if (address in registers):
            raise NotImplementedError('Parameter must not be in registers. address: {} registers:"{}"'.format(
            type(address),
            ", ".join(registers)
            ))
        super.__init__(self,  stackByteSize, address)

    def __call__(self):
        return self.address        
                
                
                
class Location():
    # location is either a register name or a stack offset
    # It can be used as a source of values, or as source of adresses to
    # values (a pointer) 
    def __init__(self, stackByteSize, address):
        self.stackByteSize = stackByteSize
        if (not (type(address) == str or type(address) == int)):
            raise NotImplementedError('Parameter must be class int or str. addess: {}'.format(type(address)))
        self.address = address

    def inStack(self):
        return (type(address) == str)
        
    def inRegister(self):
        return (type(address) == int)
        
    def __call__(self):
        # Code to retrive the value at the location.
        # If a pointer, this is npt the value from a pointer
        # it is the address of the pointer address
        # return
        #    register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        if (type(self.address) == int):
            # currently a stack index
            return 'rbp - {}'.format(self.address * self.stackByteSize)
        else:
            # currently a register
            return self.address
            
    def __repr__(self):
        return "Location(address: {})".format(self.address)
        
    def __str__(self):
        return str(self.address)
    
        
#! how are we going to keep track of stacks?
#! by depth from pointer? Which requires a global to local trace.
#! absolute address 
#! alloca 
#! etc.
class Pointer:
    # Treat a location as an address of a value
    # Can free stash-allocated pointer data, but not allocate. This is 
    # because an allocation could be to a section header, a stack,
    # a stack block, or stash.
    #? is this mutable or immutable on update?
    def __init__(self, b, localStack, rawLocation):
        self.b = b
        self.localStack = localStack
        self.stackByteSize = localStack.stackByteSize
        if (rawLocation in registers):
            self.location = LocationRegister(self.stackByteSize, rawLocation)
        elif(type(rawLocation) == str):
            self.location = LocationROData(self.stackByteSize, rawLocation)
        elif(type(rawLocation) == int):
            self.location = LocationStack(self.stackByteSize, rawLocation)
        else:
            raise NotImplementedError('Parameter must be class int or str. rawLocation: {}'.format(type(address)))
    
    def address(self):
        # return a snippet for acessing the address
        return self.location()
        
    def value(self):
        # return a snippet for acessing the value
        return '[' + self.location() + ']'
            
    def moveToStack(self):
        # push the address to the stack, record the offset
        if (type(self.location) == LocationStack):
            raise NotImplementedError('address already in stack. Pointer:{}'.format(self))
        self.b += "push {}".format(self.location())
        self.location = LocationStack(self.stackByteSize, self.localStack.newOffset())
        
    def moveToRegister(self, targetRegisterName):
        '''
        Move the address to a register
        Push the address to the stack, record the offset
        If on stack, stack remains unchanged
        '''
        if (not(targetRegisterName in registers)):
            raise NotImplementedError('targetRegisterName not a register')
        if (self.location.address == targetRegisterName):
            raise NotImplementedError('address already in given register. Pointer:{}'.format(self))
        self.b += 'mov {}, {}'.format(targetRegisterName, self.location())              
        self.location = LocationRegister(self.stackByteSize, targetRegisterName)

    def free(self):
        self.b += "mov {}, {}".format(cParameterRegister[0], self.location())
        self.b += "call free"
            
    def __repr__(self):
        return "Pointer(localStack: {}, location: {})".format(
            self.localStack,
            self.location
        )
        
        
        
# Reason for caching params is for printouts
class Array:
    # ...of reference sizes (8/15/32/64)
    # create
    def __init__(self, b, elemByteSize, size):
        self.b = b
        self.elemByteSize = elemByteSize
        self.size = size
        self.byteSize = byteSize(elemByteSize) * size
        b +=  "mov {}, {}".format(cParameterRegister[0], self.byteSize)
        b += "call malloc"
          
    def free(self):
        b += "mov {}, {}".format(cParameterRegister[0], 'rax')
        b += "call free"
        

# read reference from array (place where?)
# update array reference
# array length

# class Var
# ...of reference sizes (8/15/32/64)
# create var 1/2/3... size=
# read var 1/2/3... (place where?)
# update var

# class Stack
# Stack pop
# stack push

# class String:
# ...of UTF8 and 8bit
# create string
# read string (place where?)
# update string reference

# class Number:
# ...of reference sizes (8/15/32/64)
# arithmetic +, -, *, \, ++, --
# shift >>

# class Coerce:
# all numbers to all other numbers

# class Compare:
# ...of reference sizes (8/15/32/64)
# all numbers

# class Boolean:
# ...of reference sizes (8/15/32/64)???
# AND/OR/XOR/NOT

# class BranchIf:
# On references or numbrers?
# <, >, ==, !
# if ()

# call intern/extern
#print
# clutch


# Currently lacking a parser. This little hack allows us to build-on-run
# any file of icode. iport icode, write code, call this.
def write(b, style):
    # o = nasmFrames.frame64CAlloc(
            # externs = b.externs, 
            # data = b.data, 
            # rodata = b.rodata, 
            # bss = b.bss, 
            # text = b.text,
            # code = b.code,
        # )
    o = builderPrint(nasmFrames.frame64CAlloc, b, style)
    with open('build/out.asm', 'w') as f:
        f.write(o)
        
# stackByteSize = 8
# # start a localstack
# localStack = LocalStack(stackByteSize, 1)
# b = Builder()
# a1 = Array(b, 32, 7)
# #Pointer(b, localStack, 'rax').moveToRegister('rbx')
# p = Pointer(b, localStack, 'rax')
# p.moveToStack()
# #print(p.value())
# Print().i64(b, 'rax')
# p.free()
# o = b.code

# print(b.rodata)
# print(o)

