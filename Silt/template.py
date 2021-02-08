#!/usr/bin/env python3

import nasmFrames
import architecture
from tpl_codeBuilder import *
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


# Architecture data
arch = architecture.architectureSolve(architecture.x64)
    
def byteSize(bitsize):
    return bitsize >> 3

## compile utilities

def warning(src, msg):
    print("[Warning] {}: {}".format(src, msg))


# builder results

def builderResolveCode(arch, b):
    '''
    Take gathered data and generate a flat linear list of code
    '''
    # Currently 
    # - constructions allocation code 
    # - resolves functions into the main list
    # but may do other actions
    # Here we gather function code to append to the root builder code 
    # block. Do not use '+='
        
    if (not 'main' in b.funcNames):
        warning('builderResolveCode', 'No main func?')

    for bFunc in b.funcs:
        # build the func data into the main builder
        ## jump label
        b._code.append( '{}:'.format(bFunc.name) )

        ## allocations
        stackAllocSize = bFunc.stackAllocSize 
        if(stackAllocSize > 0):
            b._code.append( "mov rsp, rsp - {}".format(stackAllocSize))
        heapAllocSize = bFunc.heapAllocSize 
        if(heapAllocSize > 0):
            b._code.append(  "mov {}, {}".format(arch['cParameterRegisters'][0], heapAllocSize) )
            b._code.append(  "call malloc")

        ## code body
        b._code.extend(bFunc._code)
    
        # return
        if (bFunc.returnAuto):
            b._code.append('ret')
        
        print(str(b._code))


## Render data style
#! should be e.g. 'codeblock' : {'indent_step': 2} etc.
baseStyle = {
    'indent': 4,
    'indent_step'  : 2,
    'label' : {'indent': -4},
}

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
        b.append('\n') 
        if line.endswith(':'):
            style['label']
            indent = indent_dec(indent_base, indent_step, current_indent)
            b.append(" " * indent) 
        
        if line.startswith('codeblock'):
            current_indent = indent_inc(indent_step, current_indent)
        if line.startswith('end'):
            current_indent = indent_dec(indent_base, indent_step, current_indent)
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
        
def funcStart(b, name):
    #b.funcBegin('{}:'.format(name))
    b.funcBegin(name)

def funcEnd(b, ):
    #b.funcEnd('ret')
    b.funcEnd()
    
    
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


# Needs arch
class AddressRelative():
    '''
    Model of relative/effective addressing.
    The model is,
    Base + (Index * Scale) + Displacement
    Base is any register used as address
    Index - second register for offset
    Displacement - a small offset (32Bit)
    '''
    # see https://blog.yossarian.net/2020/06/13/How-x86_64-addresses-memory
    def __init__(self):
        self._base = ''
        self._index = ''
        self._scale = ''
        self._displacement = ''

    #! deprecate this, see funcs below
    # def canRelativeAddress(self, pointerCount, arrayCount, structCount):
        # return (
            # pointerCount <= 1 and arrayCount <= 1 and structCount <=1 and
            # (arrayCount == 0 or structCount == 0)
        # )
        
    def __call__(self):
        '''
        Code to represent the value at the location.
        If a pointer, this is the pointer address
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        index = ''
        if (self._index):
            index = '+' + self._index
        scale =''
        if (self._scale):
            scale = '*' + str(self._scale)
        displacement = ''
        if (self.displacement):
            displacement = '{:+}'.format(self._displacement) 
        return self._base + index + scale + displacement
                
    def base(self, base):
        if (not base in arch['registers']):
            raise ValueError('Base must be a general-purpose register. index:{}'.format(base))
        self._base = base
        
    def index(self, index):
        if (not (self.base or self.scale)):
            raise ValueError('No index without base or scale. index:{}'.format(index))
        if (not index in arch['generalPurposeRegisters']):
            raise ValueError('Index must be a general-purpose register. index:{}'.format(index))
        self._index = index
        
    def scale(self, scale):
        if (not self._index):
            raise ValueError('No scale without index. scale:{}'.format(scale))
        if (not (scale in [1, 2, 4, 8])):
            raise ValueError('Scale must be one of [1, 2, 4, 8]. scale:{}'.format(scale))
        self._scale = scale
                      
    def displacement(self, displacement):
        #? just a number - 32bit. test?
        if (not isinstance(displacement, int)):
            raise ValueError('Displacement must be integer. displacement:{}'.format(displacement))
        self._displacement = displacement 

    def __str__(self):
        return "{}{}{}{}".format(
            self._base,
            self._index,
            self._scale,
            self._displacement
        )
        
# Needs types
#x
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

#x
def isRelativeTraversable(tpe):
    r = False
    if isinstance(tpe, TypeContainer):
        # can only traverse two indirections with relative addresses
        r = ((tpe.countType() <= 2) and (tpe.countTypesOffset() < 2))
    return r


#from collections import namedtuple
#TypeHeirachySplit = namedtuple('TypeHeirachySplit', ['loadable', 'relative'])


# This works, but is nasty stepping code and also a bit inefficient
# See also tpe.children(). The question is, is this data usable 
# cross-architecture for example, for relative address detection?
def relativeGettableSplit(tpe, offsetIndexAndLabels):
    '''
    Split a type into segments handlable by relative addressing.
    return
        Array[Array{child..parent]..] breaking at pointers
    '''
    # Get allows any number of offsets to be joined. But only one 
    # pointer
    children = tpe.typePath(offsetIndexAndLabels)
    relativeChains = []
    b = []
    # chilldren is reversed for natural termination.
    # , so count down counts in--out
    for e in reversed(children):
        b.append(e)
        # if singular or TypeContainerOffset, nothing else to do
        if (isinstance(e.tpe, Pointer)):
            relativeChains.append(b)
            b = []
    return relativeChains

# def relativeTraversableSplit(tpe, offsetIndexAndLabels):
    # '''
    # Split a type into segments handlable by relative addressing.  
    # '''
    # children = tpe.typePath(offsetIndexAndLabels)
    # relativeChains = []
    # b = []
    # regCount = 0
    # # children is reversed for natural termination.
    # # , so count down counts in--out
    # for e in reversed(children):
        # b.append(e)
        # # if singular or TypeContainerOffset, nothing else to do
        # if (isinstance(e.tpe, Pointer)):
            # relativeChains.append(b)
            # b = []
        # if (isinstance(e.tpe, TypeContainerOffset):
            # regCount += 1

    # return relativeChains
        
    
# class AddressRelativeBuilder():
    # def __init__(self):
        # self.r = AddressRelative()
        # self.registerCount = 0
        # self.offsetCount = 0
        
    # def register(self, register):
        # if(self.registerCount >= 2):
            # raise ValueError('RelaiveAdressBuilder: register count > 2. addr: {} register:"{}"'.format(
                # self.r,
                # register,
            # ))
        # if(self.registerCount == 0):
            # self.r.base(register)
        # if(self.registerCount == 1):
            # self.r.index(register)
        # self.registerCount += 1

    # def offset(self, offset):
        # if(self.offsetCount >= 1):
            # raise ValueError('RelaiveAdressBuilder: offset count > 2. addr: {} offset:"{}"'.format(
                # self.r,
                # offset,
            # ))
        # self.r.displacement(offset)
        # self.offsetCount += 1
        
    # def result(self):
        # return self.r()

class AddressRelativeBuilder():
    def __init__(self):
        self.registers = []
        self.offsets = []
        
    def registerAdd(self, register):
        if(len(self.registers) >= 2):
            raise ValueError('RelativeAdressBuilder: register count > 2. self: {} register:"{}"'.format(
                self,
                register,
            ))
        self.registers.append(register)

    def offsetAdd(self, offset):
        self.offsets.append(offset)
        
    def result(self):
        b =[]
        if self.registers:
            b.append(self.registers[0])
        if (len(self.registers) > 1):
            # Can only be plus
            b.append('+')            
            b.append(self.registers[1])            
        for offset in self.offsets:
            b.append('{:+}'.format(offset))
        return "".join(b)
        
# def getRelative(relativeTypechain, offsetIndexAndLabels):
    # olIdx = len(offsetIndexAndLabels) - 1
    # b = AddressRelativeBuilder()
    # ra = AddressRelative()
    # for tpe in relativeTypechain:
        # if (isinstance(tpe, TypeContainerOffset)):
            # print(str(olIdx))
            # print(str(tpe))
            # b.offset(tpe.offset(offsetIndexAndLabels[olIdx]))
            # olIdx -= 1
        # else:
            # #! need a supply of registers
            # b.register('rax')
    # return b.result()
    
def getRelative(relativeTypePath):
    b = AddressRelativeBuilder()
    for e in relativeTypePath:
        if (isinstance(e.tpe, TypeContainerOffset)):
            print(str(e))
            print(str(e.tpe.byteSize))
            b.offsetAdd(e.tpe.offset(e.offset))
        if (isinstance(e.tpe, Pointer)):
            #! need a supply of registers
            b.registerAdd('rax')
    return b.result()
    
    
    
class LocationRoot():
    '''
    Location of root of some data.
    This implies a pointer.
    Location is a register name, a stack offset, or label to segment data
    # It can be used as a source of values, or as source of adresses to
    # values (a pointer)
    ''' 
    def __init__(self, lid):
        self.stackByteSize = arch['bytesize']
        self.lid = lid

    def __call__(self):
        '''
        Code to represent the value at the location.
        If a pointer, this is the pointer address
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        pass

    def mkRelative(self):
        raise NotImplementedError('LocationRoot:  mkRelative. class:{}'.format(self.__class__.__name__))

    def __repr__(self):
        return "Location(lid: {})".format(self.lid)
        
    def __str__(self):
        return str(self.lid)



class LocationROData(LocationRoot):
    def __init__(self, label):
        if (label in arch['registers']):
            raise ValueError('Label id must not be in registers. lid: {} registers:"{}"'.format(
                type(label),
                ", ".join(registers)
            ))
        super().__init__(label)

    def mkRelative(self):
        raise NotImplementedError('LocationROData:  label can not be in relative address???. class:{}'.format(self.__class__.__name__))

    def __call__(self):
        return self.lid  



class LocationRegister(LocationRoot):
    def __init__(self, register):
        if (not (register in arch['registers'])):
            raise ValueError('Parameter must be in registers. lid: {} registers:"{}"'.format(
                register,
                ", ".join(arch['registers'])
            ))
        super().__init__(register)    

    def mkRelative(self):
        l = AddressRelative()
        l.base(self.lid)
        return l
        
    def __call__(self):
        return self.lid
        
        
                    
class LocationStack(LocationRoot):
    def __init__(self, index):
        if (not (type(index) == int)):
            raise TypeError('Parameter must be class int. lid: {}'.format(type(index)))
        super().__init__(index)    


    def mkRelative(self):
        l = AddressRelative()
        l.base('rbp')
        l.displacement(-(self.lid * self.stackByteSize))
        return l
        
    def __call__(self):
        return 'rbp - {}'.format(self.lid * self.stackByteSize)

def mkLocation(self, rawLocation):
    l = None
    if (rawLocation in arch['registers']):
        l = LocationRegister(rawLocation)
    elif(type(rawLocation) == str):
        l = LocationROData(rawLocation)
    elif(type(rawLocation) == int):
        l = LocationStack(rawLocation)
    else:
        raise NotImplementedError('Parameter must be class int or str. rawLocation: {}'.format(type(address)))
    return l
        
#! how are we going to keep track of stacks?
#! by depth from pointer? Which requires a global to local trace.
#! absolute address 
#! alloca 
#! etc.

#? do we need this? Perhaps for making width sizes perhaps for 
# rodata numbers etc.
class Literal():
    '''
    Define a literal
    Can be replaced with a raw description, but has 
    extra conveniences.
    '''
    def __init__(self, tpe, value):
        self.tpe = tpe
        self.value = value  
        
    def __call__(self):
        #? Widthwords?
        return str(self.value)

    def withAnnot(self):
        asmName = bytesToASMName[self.tpe.byteSize]
        return asmName + ' ' + str(self.value)
                
    def __repr__(self):
        return value

# Look, is this an all-encompassing Var, that can be broken down to relative
# addressable subclasses?
# Such a thing would not have a get and setter, as the API would not either
# e.g. Array(4)('name')
# contruct
# There is a data location, and a root location
# v1 = HeapVar(b, Array(7, Clutch(['x': Bit64, 'y':Bit64])))
# v1()
# v1(4)('name')
# The issue, We can delve for values, ''get', ''set' etc.
# But we have no syntax
# Also, offsetcollections may have pointers, may not.
# Var(rootLocation, Pointer(Array(Clutch())
# Van vars take vars as values, for reallocation? Yes.
# v1 = Var(b, rootLocation, Pointer(Array(Clutch()), [values])
# v2 = v1(3)
# v2('x')
# v1.free()

class Var():
    '''
    A var assembles a type, value acessors and root location.
    '''
    #def valprint(self):
    #    raise NotImplementedError('This var has no valprint representation');

    def __repr__(self, b, rawLocation, storeLocation, tpe, value):
        self.tpe = tpe
        self.rootLocation = mkLocation(rawLocation)
        self.value = value
        self.alloc(storeLocation, tpe, value)
    
    def alloc(self, b, storeLocation, tpe, value):
        if (isinstance(storeLocation, DefStack)):
            b.stackAllocAdd(s, tpe.byteSize)

        #elif (isinstance(storeLocation, DefGlobalRO)):
            
        #elif (isinstance(storeLocation, DefGlobalRW)):
        elif (isinstance(storeLocation, DefHeap)):
            b.heapAllocAdd(s, tpe.byteSize)
        #elif (isinstance(storeLocation, DefRegister)):

class Var():
    '''
    A var assembles a type, value acessors and root location.
    '''
    #def valprint(self):
    #    raise NotImplementedError('This var has no valprint representation');

    def __repr__(self):
        raise NotImplementedError('This var has no __repr__ representation');
          
# class ValueAccessor():
    # '''
    # Value assembles the setting and getting of a value, plus a type. 
    # '''
    # def __init__(self, tpe, refs):
        # '''
        # refs
            # indexes or labels for collections. In order of appearence.
        # '''
        # self.tpe = tpe
    # #def merge(self):    
    # def get(self):
        # # No, split type into mustLoad/relative addressable
        # if (isRelativeGettable(self.tpe)):
            # location = AddressRelative()
            # #while (not isinstance(tpe, TypeSingular)):
            # #if isinstance(tpe, TypeSingular):
            # #    r = Location()
            # #    break:
            # # if (tpe, Pointer):
                # # r = 
            # # if (tpe, Array):
            # # if (tpe, Clutch):
        
            # return'[' + location() + ']'
        # else:
            # # Bury down until can use relaive address
            # return None
        
    # #def delete(self): 

# Or is this a special kind of rootLocation?
class VarLabel(Var):
    '''
    A varlabel contains a value wich returns directly/
    It is not a literal, it is stored somewhere repeatably acessible and 
    and sometimes modifiable 
    In assembly, labels are values stored in registers. Note that the 
    addressess of registers are either inaccessible or irrelevant. 
    '''
    def __init__(self, tpe, locationRaw):
        self.tpe = tpe
        self.location = mkLocation(locationRaw)
        if (isinstance(self.location, LocationStack) or isinstance(self.location, LocationROData)):
            raise ValueError('VarLabel: a varlabel can not be on the stack or section? locationRaw:"{}"'.format(
                locationRaw,
            ))

    def get(self):
        return self.location()
        
    def set(self, b, v):
        b += "mov {}, {}".format(self.location(), v)
    # No delete, irrelevant, or zeroing?
    
    
# Problem is, an offset type may not be on a pointer if it is embedded 
# e.g. Array(Clutch())
# Can these be a simple 
        
def address_build(self, tpe, addressRelativeBuilder, offsetId):
    # Singletons, no need to do anything
    ## Pointer, are constructed with acessor ops, not here
    if isinstance(tpe, TypeContainerOffset):
        addressRelativeBuilder.offsetAdd( self.tpe.offset(index) )
      
   




class VarPointer:
    '''
    Treat a root location as the address of a value
    '''
    # Can free stash-allocated pointer data, but not allocate. This is 
    # because an allocation could be to a section header, a stack,
    # a stack block, or stash.
    #? is this mutable or immutable on update?
    def __init__(self, tpe, rawLocation):
        self.tpe = Pointer(Bit64)
        self.location = mkLocation(rawLocation)

    def addr(self):
        '''
        A snippet for accessing the address
        '''
        return self.location()

    # def indexAddress(self, index):
        # '''
        # A snippet for accessing an address offset from the pointer value.
        # '''
        # #Will not work naked? LEA?
        # return '{} + {}'.format(self.location(), index)
                
    def __call__(self):
        '''
        A snippet for accessing the value
        '''
        return '[' + self.location() + ']'

    # def indexValue(self, index):
        # '''
        # A snippet for accessing a value offset from the pointer value.
        # '''
        # return 'qword[{} + {}]'.format(self.location(), index)
                    
    def toPointerIndex(self, pointer, index):
        '''
        Copy the address to a pointer offset. 
        Leaves the pointer unchanged
        '''
        self.b += 'mov {}, {}'.format(pointer.addressIndex(index), self.location()) 
        #?? what do we do about location?             
        
    def toStack(self, index):
        '''
        Push the address to the stack. 
        records the offset
        '''
        if (type(self.location) == LocationStack):
            raise NotImplementedError('address already in stack. Pointer:{}'.format(self))
        #! this push not working
        self.b += "push {}".format(self.location())
        self.location = LocationStack(index)
        
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
        self.location = LocationRegister(targetRegisterName)

    def free(self):
        self.b += "mov {}, {}".format(cParameterRegister[0], self.location())
        self.b += "call free"

    #! somwhere this logic needs to be captured, but not in the 
    # current Print()
    # def addrprint(self):
        # self.b.externsAdd("extern printf")
        # self.b.rodataAdd('print64Fmt: db "%lli", 0')
        # self.b += "mov rdi, print64Fmt"
        # #? Can we do this for labels?
        # #! Works for registers but not other addresses?
        # if (type(self.location) == LocationStack):
            # self.b += "lea rsi, [" + self.location() + "]"
        # if (type(self.location) != LocationStack):
            # self.b += "mov rsi, " + self.location()
        # self.b += "call printf"   
        
    #def valprint(self):
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
        #Print(self.tpe, self.location)
                            
    def __repr__(self):
        return "VarPointer(location: {})".format(
            self.location
        )
        
      
class VarArrayPointer(VarPointer):
    '''
    A Pointer with some extensions for basic handling.
    The displacement is varisized up to 32bit.
    (except freeing) All The location must be RAX or a subregister.
    The retrieval is 64bit (???) 
    '''
    def __init__(self, b, rawLocation):
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



def arrayPointerAllocateStack(b, size, index):
    '''
    Allocate an array of pointers.
    The size is of elemByteSize
    '''
    byteSize = architecture['bytesize'] * size
    b +=  "mov {}, {}".format(cParameterRegister[0], byteSize)
    b += "call malloc"
    return VarArrayPointer(b, index, 'rax')        

      
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
        

