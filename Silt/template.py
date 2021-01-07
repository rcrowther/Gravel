#!/usr/bin/env python3

import nasmFrames

'''
A language that captures some of the common nature of
opcodes.
# It is not intended to be compressed, like Java or CL bytecode.
# It is much more sophisticated, and so would not readily become
# bytecode.
# AFAIK. It also deals with opcodes, so is not much like a Hardware 
# Definition Language, either. 
# The aim of the language is to rationalise the common nature of many
# processing instructions into higher level constructs.
# It is not the aim of the language to decide where anything goes or 
# how, Only to get it there, and be reasonably common and 
# cross-platform in it's action.
# It is easy to go wrong with the lanaguage. For example, overwrriting 
# useful values in a register.
Currently, no protection is built in.
So What does it offer?
- abracted interface to storage options
- memoised data tracking of storage
- memoised, so simplified closure on minor bodies such as loops, 
function calls, and, if possible deallocation
''' 

# general compiling data
#https://stackoverflow.com/questions/12063840/what-are-the-sizes-of-tword-oword-and-yword-operands
#BYTE, WORD, DWORD, QWORD, TWORD, OWORD, YWORD or ZWORD
class WidthInfo():
    def __init__(self, bitName, ASMName, byteCount):
        self.bitName = bitName
        self.ASMName = ASMName
        self.byteCount = byteCount
        
WidthInfoMap = {
    # 256
    8   : WidthInfo("bit8",   "byte", 1),
    # 32766
    16  : WidthInfo("bit16",  "word", 2),
    # 2,147,483,647
    32  : WidthInfo("bit32",  "dword", 4),
    64  : WidthInfo("bit64",  "qword", 8),
    128 : WidthInfo("bit128", "oword", 16),
}
alignedBitWidths = list(WidthInfoMap.keys())
alignedByteWidths = [v.byteCount for k,v in WidthInfoMap.items()]
bytesToASMName = { v.byteCount:v.ASMName for k,v in WidthInfoMap.items()}

#from collections import namedtuple
#namedtuple("Student", ["name", "age", "faculty"])
class Encoding():
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return 'Encoding(' + self.name + ')'
        
Signed = Encoding('signed')
Unsigned = Encoding('unsigned')
Float = Encoding('float')
ASCII = Encoding('ascii')
UTF8 = Encoding('UTF8')

class Type():
    encoding = None
    elementType = None

    def __init__(self):
        pass
            
    def canEqual(self, other):
        return isinstance(other, Type)
        
    def equals(self, other):
        return self.canEqual(other) and self.elementType.equals(self, other)
        
   #def print(self):
   #     raise UnimplementedError();
    def __repr__(self):
        return "{}".format(self.__class__.__name__)


                
class _Bit8(Type):
    encoding = Signed
    #def print(self):
    #    pass
Bit8 = _Bit8()

class _Bit16(Type):
    encoding = Signed

Bit16 = _Bit16()

class _Bit32(Type):
    encoding = Signed
Bit32 = _Bit32()

class _Bit64(Type):
    encoding = Signed
Bit64 = _Bit64()    

class _Bit32F(Type):
    '''
    A 32bit float
    in C ''float'
    '''
    encoding = Float
Bit32F = _Bit32F()

class _Bit64F(Type):
    '''
    A 32bit float
    in C ''double'
    '''
    encoding = Float
bit64F = _Bit64F()

class _StrASCII(Type):
    encoding = ASCII
StrASCII = _StrASCII() 
 
class _StrUTF8(Type):
    encoding = UTF8
StrUTF8 = _StrUTF8() 



class TypeContainer(Type):
    def __init__(self, elementType):
        self.elementType = elementType
        
    def __repr__(self):
        return "{}(elementType:{})".format(self.__class__.__name__, self.elementType)

    def __str__(self):
        return "{}[{}]".format(self.__class__.__name__, self.elementType)
        
        
                
class Array(TypeContainer):
    def __init__(self, elementType):
        if not(issubclass(type(elementType), Type)):
            raise ValueError('Array elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
        
        
class Clutch(TypeContainer):
    def __init__(self, elementType):
        if (type(elementType) != dict):
            #! dict values should be types
            raise ValueError('Clutch elementType not a dict. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
        
##Pointer?b

# Render data
baseStyle = {
    'indent': '    '
}


# Aritecture data
architectureX64 = {
    # bitsize of the architecture
    'bitsize' : 64,
}

def architectureResolve(architecture):
    architecture['bytesize'] = architecture['bitsize'] >> 3
    return architecture
    
architecture = architectureResolve(architectureX64)

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
    '''
    Append a codeline
    '''
    b += content

def sysExit(b, code=0):    
    b += "mov rax, 60"
    b += "mov rdi, " + str(code)
    b += "syscall"
    
def stringROdefine(b, localStack, dataLabels, string):
    '''
    Define a static string
    A Bytestring.
    Is placed in the ROData section.
    '''
    label = dataLabels.newLabel()
    rodata = label + ': db "' + string + '", 0'
    b.rodataAdd(rodata)
    return Pointer(b, localStack, label)


def stringDefine(b, localStack, dataLabels, string):
    '''
    Allocate and define a malloced string
    UTF-8
    '''
    byteSize = byteSize(elemByteSize) * size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return Pointer(b, localStack, 'rax')        
        
        
class Print():
    def __init__(self, b):
        self.b = b
        
    def protect(self, source):
        if (source in ['rdi', 'rsi' ]):
            raise ValueError('Printing clobbers RDI and RSI. address: {}'.format(source))

    def extern(self):
        self.b.externsAdd("extern printf")

    def flush(self):
        self.b.externsAdd("extern fflush")
        self.b += "mov rdi, 0"
        self.b += "call fflush"
            
    def generic(self, form, source):
        self.protect(source)
        self.extern()
        self.b += "mov rdi, " + form
        self.b += "mov rsi, " + source
        self.b += "call printf"

    def newline(self):
        self.extern()
        self.b.rodataAdd('printNewLine: db 10, 0')
        self.b += "mov rdi, printNewLine"
        self.b += "call printf"

    def char(self, source):
        self.b.rodataAdd('printCharFmt: db "%c", 0')
        self.generic('printCharFmt', source)
            
    def string(self, pointer):
        '''
        pointer
            an instance of a pointer
        '''
        self.protect(pointer.location.address)
        self.extern()
        self.b += "mov rdi, " + pointer.address()
        self.b += "call printf"
        
    def i32(self, source):
        self.b.rodataAdd('print32Fmt: db "%li", 0')
        self.generic('print32Fmt', source) 

    def i64(self, source):
        self.b.rodataAdd('print64Fmt: db "%lli", 0')
        self.generic('print64Fmt', source)

    def float(self, form, source):
        self.protect(source)
        self.extern()
        self.b.rodataAdd('printFloatFmt: db "%g", 0')
        self.b += "movsd xmm0, printlnFloatFmt"
        self.b += "mov rdi, " + source
        self.b += "call printf"
   
    def stringln(self, pointer):
        '''
        pointer
            an instance of a pointer
        '''
        self.protect(pointer.location.address)
        self.b.rodataAdd('printlnStrFmt: db "%s", 10, 0')
        self.generic('printlnStrFmt', pointer.address()) 



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
            raise TypeError('Parameter must be class int. address: {}'.format(type(address)))
        super().__init__( stackByteSize, address)    

    def __call__(self):
        return 'rbp - {}'.format(self.address * self.stackByteSize)



class LocationRegister(LocationBase):
    def __init__(self, stackByteSize, address):
        if (not (address in registers)):
            raise ValueError('Parameter must be in registers. address: {} registers:"{}"'.format(
            type(address),
            ", ".join(registers)
            ))
        super().__init__(stackByteSize, address)    

    def __call__(self):
        return self.address



class LocationROData(LocationBase):
    def __init__(self, stackByteSize, address):
        if (address in registers):
            raise ValueError('Parameter must not be in registers. address: {} registers:"{}"'.format(
            type(address),
            ", ".join(registers)
            ))
        super().__init__(stackByteSize, address)

    def __call__(self):
        return self.address        
                
                

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
        '''
        A snippet for accessing the address
        '''
        return self.location()

    def indexAddress(self, index):
        '''
        A snippet for accessing an address offset from the pointer value.
        '''
        #Will not work naked? LEA?
        return '{} + {}'.format(self.location(), index)
                
    def value(self):
        '''
        A snippet for accessing the value
        '''
        return '[' + self.location() + ']'

    def indexValue(self, index):
        '''
        A snippet for accessing a value offset from the pointer value.
        '''
        return 'qword[{} + {}]'.format(self.location(), index)
                    
    def toPointerIndex(self, pointer, index):
        '''
        Copy the address to a pointer offset. 
        Leaves the pointer unchanged
        '''
        self.b += 'mov {}, {}'.format(pointer.addressIndex(index), self.location()) 
        #?? what do we do about location?             
        
    def toStack(self):
        '''
        Push the address to the stack. 
        records the offset
        '''
        if (type(self.location) == LocationStack):
            raise NotImplementedError('address already in stack. Pointer:{}'.format(self))
        self.b += "push {}".format(self.location())
        self.location = LocationStack(self.stackByteSize, self.localStack.newOffset())
        
    def toRegister(self, targetRegisterName):
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
        
      
class ArrayPointer(Pointer):
    '''
    A Pointer with some extensions for basic handling.
    The displacement is varisized up to 32bit.
    (except freeing) All The location must be RAX or a subregister.
    The retrieval is 64bit (???) 
    '''
    def __call__(self, index, dst):
        #? movxsd
        #if (self.location.address != 'rax'):
        #    raise NotImplementedError('Accessing a pointer array must be done through RAX. address: {}'.format(type(self.location.address)))
        self.b += 'mov {}, qword [{}+8*{}]'.format(dst, self.location(), index)

    def update(self, index, value):
        #if (self.location.address != 'rax'):
        #    raise NotImplementedError('Accessing a pointer array must be done through RAX. address: {}'.format(type(self.location.address)))
        self.b += 'mov qword [{}+8*{}], {}'.format(self.location(), index, value)
        
    def delete(self):
        self.free()



def arrayPointerAllocate(b, localStack, size):
    '''
    Allocate an array of pointers.
    The size is of elemByteSize
    '''
    byteSize = architecture['bytesize'] * size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return ArrayPointer(b, localStack, 'rax')        

      
class ClutchPointer(Pointer):
    '''
    A Pointer with some extensions for basic handling.
    The displacement is varisized up to 32bit.
    (except freeing) All The location must be RAX or a subregister.
    The retrieval is 64bit (???) 
    '''
    def __init__(self, b, localStack, rawLocation, keyData):
        super().__init__(b, localStack, rawLocation)
        self.keyData = keyData
        
    def get(self, key, dst):
        '''
        Optionally return the value of the key
        '''
        try:
            return self(key, dst)
        except KeyError:
            return None
        
    def __call__(self, key, dst):
        '''
        Return the value of the key
        Throws error
        '''
        self.b += 'mov {}, {} [{}+{}]'.format(
            dst, 
            self.keyData[key][1],
            self.location(), 
            self.keyData[key][0]
        )

    def update(self, key, value):
        '''
        Update the value of the key
        '''
        self.b += 'mov {} [{}+{}], {}'.format(
            self.keyData[key][1],
            self.location(), 
            self.keyData[key][0],
            value
        )
        
    def delete(self):
        self.free()


                
def clutchAllocate(b,  localStack, elements):
    '''
    Allocate a clutch in heap.
    elements 
        a dict of labels to element type
    return 
        A ClutchPointer
    '''
    byteSize = 0
    keyData = {}
    #! should pad too, probaly to 16 etc.
    for name, size in elements.items():
        # Insist on powers of two
        if (size not in alignedByteWidths):
            raise ValueError('Key value not a pewer of 2. size: {}, key:"{}"'.format(size, name))
        # convert from individual sizes to cumulative index
        keyData[name] = (byteSize, bytesToASMName[size])
        byteSize += size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return ClutchPointer(b, localStack, 'rax', keyData)        

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
