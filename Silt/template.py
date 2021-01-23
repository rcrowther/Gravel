#!/usr/bin/env python3

import nasmFrames
import architecture
from tpl_types import *

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
# independant of architecture
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
bytesToASMName = {v.byteCount:v.ASMName for k,v in WidthInfoMap.items()}


# Aritecture data
arch = architecture.architectureSolve(architecture.x64)
    
def byteSize(bitsize):
    return bitsize >> 3


# Render data style
#! should be e.g. 'codeblock' : {'indent_step': 2} etc.
baseStyle = {
    'indent': 4,
    'indent_step'  : 2,
}


## Builder
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

def indent_inc(indent_step, current_indent):
    current_indent += indent_step    
    return current_indent
    
def indent_dec(indent_base, indent_step, current_indent):
    current_indent -= indent_step
    if(current_indent < indent_base):
        current_indent = indent_base
    return current_indent
         
def builderCode(style, code):
    '''
    Return a string of code data, inflected by style
    '''
    indent_base = style['indent']
    indent_step = style['indent_step']
    current_indent = indent_base
    b = []
    for line in code:
        #indent + joinIndent.join(b._code)
        if line.startswith('codeblock'):
            current_indent = indent_inc(indent_step, current_indent)
        if line.startswith('end'):
            current_indent = indent_dec(indent_base, indent_step, current_indent)
        b.append('\n') 
        b.append(" " * current_indent) 
        b.append(line) 
    return ''.join(b)
    
def builderPrint(frame, b, style):
    indent = style['indent']
    indent_str = " " * indent
    joinIndent = '\n' + indent_str
    styledBuilder = {
        'externs' : '\n'.join(b._externs), 
        'data' : indent_str + joinIndent.join(b._data), 
        'rodata'  : indent_str + joinIndent.join(b._rodata), 
        'bss'  : indent_str + joinIndent.join(b._bss), 
        'text' : '\n'.join(b._text),
        'code' : builderCode(style, b._code),
    }
    return frame(**styledBuilder)
     
     
     

## Builder Utilities
class Labels():
    '''
    Generate data labels
    '''
    def __init__(self):
        self.idx = - 1

    def __call__(self):
        '''
        return 
            a new label
        '''
        self.idx += 1
        return self.prefix + str(self.idx)

    def __repr__(self):
        return "Labels(self.prefix:'{}', idx: {})".format(self.prefix , self.idx)
    
    
class LabelsROData(Labels):
    prefix = 'ROData'
    
class LabelsLoop(Labels):
    prefix = '.loop'
 
    def exit(self):
        '''
        return 
            an 'exit' label for the current id.
        '''
        return self.prefix + str(self.idx) + 'Exit'

class LabelGen():
    '''
    Generate data labels
    '''
    # Not for globals?
    def __init__(self):
        self.prefixes = {}

    def __call__(self, prefix):
        '''
        return 
            a new label
        '''
        if (prefix in self.prefixes):
            idx = self.prefixes[prefix]
            idx += 1
        else:
            idx = 0
        self.prefixes[prefix] = idx
        return prefix + str(idx)

    def __repr__(self):
        return "LabelGen(self.prefixs:'{}')".format(self.prefixs)
        
def writeLable(b, label):
    b += label + ':'
    
## Model utilities
class StackIndex():
    '''
    A stack for local indexes
    Works in whole stackwidths. Relative, not absolute. Can provide an 
    offset generated from an index. 
    initialOffset
        provide an initial offset. 
    '''
    def __init__(self, initialOffset):
        self.stackByteSize = arch['bitsize']
        self.idx = initialOffset - 1

    def __call__(self):
        '''
        return a new index on the stack
        '''
        self.idx += 1
        #b += "push {}".format(addressLocation))
        return self.idx
    
    def __repr__(self):
        return "StackIndex(idx: {})".format(self.idx)
    
class StackIndexAllocated():
    '''
    A stack for local indexes
    Works in whole stackwidths. Relative, not absolute. Can provide an 
    offset generated from an index. 
    initialOffset
        provide an initial offset. 
    '''
    def __init__(self, b, elemByteSize, size):
        self.elemByteSize = elemByteSize
        self.size = size
        self.byteSize = elemByteSize * size
        b += "sub rsp - " + self.byteSize
        
        #b += "push {}".format(addressLocation))
        self.idxSum = - 1

    def __call__(self, idx):
        '''
        Offset of given index
        '''
        if (idx >= self.size):
            raise  ValueError('StackIndexAllocated: Given index too large for space. size:{}, index: {}'.format(self.size, index))
        return idx * self.elemByteSize
    
    def __repr__(self):
        return "StackIndexAlloc(size: {})".format(self.size)


            
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
    
def stringROdefine(b, stackIndex, dataLabels, string):
    '''
    Define a static string
    A Bytestring.
    Is placed in the ROData section.
    '''
    label = dataLabels()
    rodata = label + ': db "' + string + '", 0'
    b.rodataAdd(rodata)
    return Pointer(b, stackIndex, label)


def stringDefine(b, stackIndex, string):
    '''
    Allocate and define a malloced string
    UTF-8
    '''
    byteSize = byteSize(elemByteSize) * size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return Pointer(b, stackIndex, 'rax')        
        
        
class Print64():
    #def __init__(self, b):
    #    self.b = b
        
    def dispatch(self, b, tpe, source):
        if(tpe == Bit8):
            self.i8(b, source)
        elif(tpe == Bit16):
            self.i16(b, source)
        elif(tpe == Bit32):
            self.i32(b, source)
        elif(tpe == Bit64):
            self.i64(b, source)
        elif(tpe == Bit128):
            self.i128(b, source)
        elif(tpe == Bit32F):
            self.f32(b, source)
        elif(tpe == Bit64F):
            self.f64(b, source)
        elif(tpe == StrASCII):
            self.ascii(b, source)
        #elif(tpe == StrUTF8):
        #    self.utf8(b, source)
        #elif(tpe == Pointer):
        #    self.pointer(b, tpe, source)
        #elif(tpe == Array):
        #    self.array(b, tpe, source)
        else:
            raise NotImplementedError('Print: unrecognised type. tpe:()'.format(tpe));

    def pointer(self, b, tpe, location):
        self.dispatch(b, tpe, base + offset)
        
    def array(self, b, tpe, location):
        byteSize = tpe.elementType.byteSize
        base = location()
        for offset in (0..tpe.size):
            self.dispatch(b, tpe, base + offset)

            
    def protect(self, source):
        if (source in ['rdi', 'rsi' ]):
            raise ValueError('Printing clobbers RDI and RSI. address: {}'.format(source))

    def extern(self, b):
        self.b.externsAdd("extern printf")
 
    def flush(self, b):
        b.externsAdd("extern fflush")
        b += "mov rdi, 0"
        b += "call fflush"
            
    def generic(self, b, form, source):
        self.protect(source)
        self.extern(b)
        b += "mov rdi, " + form
        b += "mov rsi, " + source
        b += "call printf"

    def newline(self, b):
        self.extern(b)
        b.rodataAdd('printNewLine: db 10, 0')
        b += "mov rdi, printNewLine"
        b += "call printf"

    def char(self, b, source):
        b.rodataAdd('printCharFmt: db "%c", 0')
        self.generic('printCharFmt', source)
            
    def ascii(self, b, pointer):
        '''
        pointer
            an instance of a pointer
        '''
        self.protect(pointer.location.address)
        self.extern(b)
        b += "mov rdi, " + pointer.address()
        b += "call printf"

    def i8(self, b, source):
        b.rodataAdd('print8Fmt: db "%hhi", 0')
        self.generic('print8Fmt', source) 

    def i16(self, b, source):
        b.rodataAdd('print16Fmt: db "%hi", 0')
        self.generic('print16Fmt', source) 
                        
    def i32(self, b, source):
        b.rodataAdd('print32Fmt: db "%i", 0')
        self.generic('print32Fmt', source) 

    def i64(self, b, source):
        b.rodataAdd('print64Fmt: db "%li", 0')
        self.generic('print64Fmt', source)

    def i128(self, b, source):
        b.rodataAdd('print128Fmt: db "%lli", 0')
        self.generic('print128Fmt', source)
        
    def f32(self, b, form, source):
        self.protect(source)
        self.extern(b)
        b.rodataAdd('printFloatFmt: db "%g", 0')
        b += "movsd xmm0, printlnFloatFmt"
        b += "mov rdi, " + source
        b += "call printf"

    # 32f usually promoted to 64f anyhow
    def f64(self, b, form, source):
        self.protect(source)
        self.extern(b)
        b.rodataAdd('printFloatFmt: db "%g", 0')
        b += "movsd xmm0, printlnFloatFmt"
        b += "mov rdi, " + source
        b += "call printf"
           
    def stringln(self, b, pointer):
        '''
        pointer
            an instance of a pointer
        '''
        self.protect(pointer.location.address)
        b.rodataAdd('printlnStrFmt: db "%s", 10, 0')
        self.generic('printlnStrFmt', pointer.address()) 

Print = Print64()




## builders
class Frame():
    '''
    Write a basic frame.
    '''
    def __init__(self, b):
        b += "push rbp"
        b += "mov rbp, rsp"
        self.stackIndex = StackIndex(0)
    
    def close(self, b):
        b += "mov rsp, rbp"
        b += "pop rbp"

    def __repr__(self):
        return "Frame(stackIndex:{})".format(self.stackIndex)


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



from collections import namedtuple
JumpLabels = namedtuple('JumpLabels', ['codeblock', 'end'])

class BooleanOp():
    def buildAft(self, b, jumpToEnd, jumpLabels):          
        raise NotImplementedError('BooleanOp:  buildAft func class:{}'.format(self.__class__.__name__))

    def buildFore(self, b, jumpToEnd, jumpLabels):
        raise NotImplementedError('BooleanOp:  buildFore func class:{}'.format(self.__class__.__name__))

    def __repr__(self):
        return self.__class__.__name__
        
class BooleanCondition(BooleanOp):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def negate(self):
        pass

    def buildAft(self, b, jumpToEnd, jumpLabels):          
        self.buildFore(b, jumpToEnd, jumpLabels);
            
    def buildFore(self, b, jumpToEnd, jumpLabels):          
        b += "cmp {}, {}".format(self.a, self.b)
        jmp = self.jumpCommand + " "
        if(jumpToEnd):
            jmp += jumpLabels.end 
        else:
            jmp += jumpLabels.codeblock
        b += jmp

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self.a,
            self.b
        )
                
class GT(BooleanCondition):
    jumpCommand = "jg"

    def negate(self):
        return LTE(self.a, self.b)
        
class GTE(BooleanCondition):
    jumpCommand = "jge"

    def negate(self):
        return LT(self.a, self.b)
        
class LT(BooleanCondition):
    jumpCommand = "jl"

    def negate(self):
        return GTE(self.a, self.b)
        
class LTE(BooleanCondition):
    jumpCommand = "le"

    def negate(self):
        return GT(self.a, self.b)
        
class EQ(BooleanCondition):
    jumpCommand = "je"
    
    def negate(self):
        return NEQ(self.a, self.b)
        
class NEQ(BooleanCondition):
    jumpCommand = "jne"

    def negate(self):
        return EQ(self.a, self.b)
        
        
        
class BooleanLogic(BooleanOp):
    def __init__(self, args):
        self.args = args

    def negate(self):
        pass
        
            
# jumpLabels = {
# "jl",
# "je",
# "jg",
# "jne",
# "je",
# "NOT"
# }
class AND(BooleanLogic):
    def negate(self):
        # De Morgans law
        return AND([arg.negate() for arg in self.args])
        
    def buildAft(self, b, jumpToEnd, jumpLabels):
        tailArg = self.args.pop()
        print(self.args)
        for arg in self.args:
            arg1 = arg.negate()
            arg1.buildAft(b, True, jumpLabels)
        tailArg.buildAft(b, False, jumpLabels)
                
    def buildFore(self, b, jumpToEnd, jumpLabels):
        for arg in self.args:
            arg1 = arg.negate()
            arg1.buildFore(b, True, jumpLabels)

    def __repr__(self):
        return "AND({})".format(
          ", ".join(self.args)
        )            
        
class OR(BooleanLogic):
    def negate(self):
        # De Morgans law
        return OR([arg.negate() for arg in self.args])

    def buildAft(self, b, jumpToEnd, jumpLabels):
        for arg in self.args:
            arg.buildAft(b, False, jumpLabels)
                    
    def buildFore(self, b, jumpToEnd, jumpLabels):
        tailArg = self.args.pop()
        for arg in self.args:
            arg.buildFore(b, False, jumpLabels)
        tailArg.negate().buildFore(b, True, jumpLabels)
            
    def __repr__(self):
        return "OR({})".format(
          ", ".join(self.args)
        ) 

class NOT(BooleanLogic):    
    def __init__(self, arg):
        self.arg = arg

    def negate(self):
        return self.arg

    def buildAft(self, b, jumpToEnd, jumpLabels):
        negated = self.arg.negate()
        negated.buildAft(b, jumpToEnd, jumpLabels)
        
    def buildFore(self, b, jumpToEnd, jumpLabels):
        negated = self.arg.negate()
        negated.buildFore(b, jumpToEnd, jumpLabels)

    def __repr__(self):
        return "NOT({})".format(
          ", ".join(self.arg)
        ) 

# To do a comparison assignment, we start with var = false, put true in the if block
# Or can it be simpler?

# This I think is not how to do it. What we should do is flatten the 
# structure first, resolve the equation, to make it linear.
# Then can run builder through it? But does it make any difference, 
# besides optimisation?
class If():
    def __init__(self, b, labels, comparison):
        trueLabel = labels('codeblock')
        self.failLabel = labels('endif')
        # BooleanLogic will look after itself, but BooleanCondition
        # needs negating and a jump to the end
        c = comparison
        if (isinstance(comparison, BooleanCondition) or isinstance(comparison, NOT)):
            #print('init negate')
            # Any BooleanLogic will do, they all negate then direct to 
            # end. NOT is simply convenient.
            c = NOT(comparison)
        c.buildFore(b, True, JumpLabels(trueLabel, self.failLabel))
        b += trueLabel + ":"
    
    def close(self, b):
        b += self.failLabel + ":"

class While():
    def __init__(self, b, labels, comparison):
        self.startLabel = labels('codeblock')
        self.exitLabel = labels('endwhile')
        self.entryLabel = labels('entry')
        self.comparison = comparison
        b += "jmp " + self.entryLabel
        b += self.startLabel + ":"
    
    def close(self, b):
        b += self.entryLabel + ":"
        c = self.comparison
        c.buildAft(b, None, JumpLabels(self.startLabel, self.exitLabel))        
        b += self.exitLabel + ":"

# foreaches
#? Multi-dimentional
class ForEach():
    def clutch(b, clutchData, f):
        '''
        foreach a clutch
        Passes the element offset to the supplied function.
        Code is constructed statically, the loop is unrolled, creating
        multiple functions calls.
        f
            a function, given parameter is the element offset in bytes
        '''
        stepNum = clutchData.stepCount
        stepByteSize = clutchData.byteSize
        while stepNum > 0:
            f(stepByteSize)
            stepByteSize -= clutchData.step[stepNum]
            stepNum -= 1
            
    #! isn't this a utility loop function, not array specific?
    def array(b, ptrRegister, countRegister, stepCount, stepSize, f):
        '''
        foreach an array
        Makes no attempt at access, but passes the correct offset to the 
        supplied function.
        Code is constructed dynamically, the loop written to code, 
        creating one function call
        f
            a function, given parameter is the element offset in bytes
        '''
        b += "mov " + countRegister + ", " + str(stepCount * stepSize)
        b += ".loop1"
        b += "cmp "	+ countRegister + ", 0"
        b += "jle "	+ ".loop1Exit"
        f(countRegister)
        # could be a shift?
        b += "sub "  + countRegister + ", " + stepSize
        b += "jmp" +  ".loop1"
        b += ".loop1Exit"


    
class LocationRelative():
    '''
    Model of relative/effective addressing.
    The model is,
    Base + (Index * Scale) + Displacement
    Base is any register used as address
    Index - second register for offset
    Displacement - a small offset (32Bit)
    '''
    # see https://blog.yossarian.net/2020/06/13/How-x86_64-addresses-memory
    def __init__(self, stackByteSize, address):
        self.stackByteSize = stackByteSize
        self.base = ''
        self.index = ''
        self.scale = ''
        self.displacement = ''

    #! deprecate this, see funcs below
    def canRelativeAddress(self, pointerCount, arrayCount, structCount):
        return (
            pointerCount <= 1 and arrayCount <= 1 and structCount <=1 and
            (arrayCount == 0 or structCount == 0)
        )
        
    def __call__(self):
        '''
        Code to represent the value at the location.
        If a pointer, this is the pointer address
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        index = ''
        if (self.index):
            index = '+' + self.index
        scale =''
        if (self.scale):
            scale = '*' + str(self.scale)
        displacement = ''
        if (self.displacement):
            displacement = '+' + self.displacement 
        return self.base + index + scale + displacement
                
    def set_base(self, base):
        if (not base in GeneralPurposeRegisters):
            raise ValueError('Base must be a general-purpose register. index:{}'.format(base))
        self.base = base
        
    def set_index(self, index):
        if (not (self.base or self.scale)):
            raise ValueError('No index without base or scale. index:{}'.format(index))
        if (not index in GeneralPurposeRegisters):
            raise ValueError('Index must be a general-purpose register. index:{}'.format(index))
        self.index = index
        
    def set_scale(self, scale):
        if (not self.index):
            raise ValueError('No scale without index. scale:{}'.format(scale))
        if (not (scale in [1, 2, 4, 8])):
            raise ValueError('Scale must be one of [1, 2, 4, 8]. scale:{}'.format(scale))
        self.scale = scale
                      
    def set_displacement(self, displacement):
        #? just a number - 32bit. test?
        self.displacement = displacement 
        
def isRelativeGettable(tpe):
    # Base + (Index * Scale) + Displacement
    #! relative addresses can manage more than this, they can do
    # Base + Index = Array[] 
    # The clutch is not traversable
    # Base + Index + Displacement = Array[Clutch[]]
    # 
    # Base + (Index * Scale) = Array[Pointer[]]
    # Base + (Index * Scale) + Displacement = Array[Array[]]
    # It can go down three Pointers. The second can be an array/struct
    r = False
    if isinstance(tpe, TypeContainer):
        r = ((tpe.countType() <= 3) and (tpe.countTypesOffset() < 1))
    return r

def isRelativeTraversable(tpe):
    r = False
    if isinstance(tpe, TypeContainer):
        # can only traverse two indirections with relative addresses
        r = ((tpe.countType() <= 2) and (tpe.countTypesOffset() < 2))
    return r
                
class LocationRoot():
    '''
    Location of some data
    Location is a register name, a stack offset, or label to segment data
    # It can be used as a source of values, or as source of adresses to
    # values (a pointer)
    ''' 
    def __init__(self, stackByteSize, address):
        self.stackByteSize = stackByteSize
        self.address = address

    def __call__(self):
        '''
        Code to represent the value at the location.
        If a pointer, this is the pointer address
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        pass


        
    def __repr__(self):
        return "Location(address: {})".format(self.address)
        
    def __str__(self):
        return str(self.address)


            
class LocationStack(LocationRoot):
    def __init__(self, stackByteSize, address):
        if (not (type(address) == int)):
            raise TypeError('Parameter must be class int. address: {}'.format(type(address)))
        super().__init__( stackByteSize, address)    

    def __call__(self):
        return 'rbp - {}'.format(self.address * self.stackByteSize)



class LocationRegister(LocationRoot):
    def __init__(self, stackByteSize, address):
        if (not (address in arch['registers'])):
            raise ValueError('Parameter must be in registers. address: {} registers:"{}"'.format(
            type(address),
            ", ".join(registers)
            ))
        super().__init__(stackByteSize, address)    

    def __call__(self):
        return self.address



class LocationROData(LocationRoot):
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

#? do we need this? Perhaps for making width sizes perhaps for 
# rodata numbers etc.
class Literal():
    def __init__(self, b, tpe, value):
        self.tpe = tpe
        self.b = b  
        self.value = value  
        
    def valprint(self):
        #? Widthwords?
        b += value

    def __repr__(self):
        return value
  
class Var():
    def valprint(self):
        raise NotImplementedError('This var has no valprint representation');

    def __repr__(self):
        raise NotImplementedError('This var has no __repr__ representation');
        
class VarPointer:
    # Treat a location as an address of a value
    # Can free stash-allocated pointer data, but not allocate. This is 
    # because an allocation could be to a section header, a stack,
    # a stack block, or stash.
    #? is this mutable or immutable on update?
    def __init__(self, b, stackIndex, rawLocation):
        self.tpe = Pointer(Bit64)
        self.b = b
        self.stackIndex = stackIndex
        self.stackByteSize = stackIndex.stackByteSize
        if (rawLocation in arch['registers']):
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
        #! this push not working
        self.b += "push {}".format(self.location())
        self.location = LocationStack(self.stackByteSize, self.stackIndex())
        
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

    #! somwhere this logic needs to be captured, but not in the 
    # current Print()
    def addrprint(self):
        self.b.externsAdd("extern printf")
        self.b.rodataAdd('print64Fmt: db "%lli", 0')
        self.b += "mov rdi, print64Fmt"
        #? Can we do this for labels?
        #! Works for registers but not other addresses?
        if (type(self.location) == LocationStack):
            self.b += "lea rsi, [" + self.location() + "]"
        if (type(self.location) != LocationStack):
            self.b += "mov rsi, " + self.location()
        self.b += "call printf"   
        
    def valprint(self):
        # self.b.externsAdd("extern printf")
        # # surely this needs to come from the type?
        # self.b.rodataAbdd('print64Fmt: db "%lli", 0')
        # self.b += "mov rdi, print64Fmt"
        # #if (type(self.location) != LocationRegister):
        # #    self.b += "mov rsi,  [" + self.location() + "]"
        # #if (type(self.location) == LocationRegister):
        # #?? Can we do this for labels?
        # self.b += "mov rsi, [" + self.location() + "]"        
        # self.b += "call printf" 
        Print(self.tpe, self.location)
                            
    def __repr__(self):
        return "VarPointer(stackIndex: {}, location: {})".format(
            self.stackIndex,
            self.location
        )
        
      
class VarArrayPointer(VarPointer):
    '''
    A Pointer with some extensions for basic handling.
    The displacement is varisized up to 32bit.
    (except freeing) All The location must be RAX or a subregister.
    The retrieval is 64bit (???) 
    '''
    def __init__(self, b, tpe, stackIndex, rawLocation):
        self.tpe = Array(Bit64)

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



def arrayPointerAllocate(b, stackIndex, size):
    '''
    Allocate an array of pointers.
    The size is of elemByteSize
    '''
    byteSize = architecture['bytesize'] * size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return VarArrayPointer(b, stackIndex, 'rax')        

      
class VarClutchPointer(VarPointer):
    '''
    A Pointer with some extensions for basic handling.
    The displacement is varisized up to 32bit.
    (except freeing) All The location must be RAX or a subregister.
    The retrieval is 64bit (???) 
    '''
    def __init__(self, b, stackIndex, rawLocation, keyData):
        super().__init__(b, stackIndex, rawLocation)
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


                
def clutchAllocate(b,  stackIndex, elements):
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
    return VarClutchPointer(b, stackIndex, 'rax', keyData)        

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
        

