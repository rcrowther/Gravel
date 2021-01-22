#!/usr/bin/env python3

import nasmFrames
import architecture
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
bytesToASMName = {v.byteCount:v.ASMName for k,v in WidthInfoMap.items()}


# Aritecture data
arch = architecture.architectureSolve(architecture.x64)
    
def byteSize(bitsize):
    return bitsize >> 3

## Types
'''
# Rationale for types
We were storing bit sizes anyway, because they are neceassary for 
clutches That comes close to type info. To add an encoding more or 
less defines a type. It also expands the system from perhaps 5 
''types' (bit sizes) to perhaps sixteen ''types (with the addition
of encoding). This is still managable. What it will do is give is
many advantages of defining special instructions, for example, for
float types, and for prints.
What we will not do is introduce any feature that relies on the types,
such as polymorphic functions.
We will not type symbols???
We will not store non coded data like string lengths.
'''
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

# class TypeMeta(type):
    # def __repr__(self):
        # return str(self.__name__)
        
#class Type(metaclass=TypeMeta):
class Type():
    encoding = None
    elementType = None
    '''
    A bytesize of None means, don't know, or variable
    '''
    byteSize = None
    
    #def __init__(self):
    #    raise NotImplementedError('A base Type can not be instanciated')
            
    # @property
    # def byteSize(self):
        # return self._byteSize
        
    def canEqual(self, other):
        return isinstance(other, Type)
        
    def equals(self, other):
        #return self.canEqual(other) and self.elementType.equals(other)
        return (self == other)

    def foreach(self, f):
        tpe = self
        while(tpe):
            f(tpe)
            tpe = tpe.elementType
    
    def list(self):
        '''
        List the types outer-in.
        To go inner-out, can be reversed(list())
        '''
        tpe = self
        b = []
        while(tpe):
            b.append(tpe)
            tpe = tpe.elementType
        return b
                
    def valprint(self):
        raise NotImplementedError('This type has no print representation');
        
    def __repr__(self):
        raise NotImplementedError('This type has no __repr__ representation');
        #return "{}".format(self.__class__.__name__) #+ ('instance')

'''
Far as I can see, we have two alternatives with types:
Use Pythons facilities, replicated in many languages, to make a type as 
a class,
Con: 
- Needs metaclasses from the off. 
- To get the type of a constructed container, we must use type()
- Can not autogenerate new types easily
Or make types an instance,
Con:
- All types need a instance representation someplace. I make a 
VarArray(Bit8). If type is needed, say for further construction, it 
must construct an Array (type) instance with Bit8 instance embedded.
- Will raise problems of equality between types 
'''
'''
Types
A type is the common, immutable aspeects of the basic data (so far, not
fuctions). 
Somettimes we need to refer to types themselves. For example, in an 
array, we do not need to know the type of every element, only that 
every element has a type of X. To do this, we refer to the class itself,
which can in Python be passed about and compared.
The base types do not exist as individual instances i.e. are not mapped 
to data. Niether do they work if they are instances (they should not be 
instanced). They onlyy refer to data when they are put in a container.
One of the containers is a Literal/Constant container.
Any type put in a containeer creates a new type, which take the name of  
the container as type. Again, the class is used to refer to the type.
Since the process is circular (type in type in type...), from these 
elements, arbitary types can be built.
'''
# char
class _Bit8(Type):
    encoding = Signed
    byteSize = 1
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit8 = _Bit8()

# short int
class _Bit16(Type):
    encoding = Signed
    byteSize = 2
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit16 = _Bit16()

# int
class _Bit32(Type):
    encoding = Signed
    byteSize = 4
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit32"
Bit32 = _Bit32()

# long int
class _Bit64(Type):
    encoding = Signed
    byteSize = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit64"
Bit64 = _Bit64()    

# long long int
class _Bit128(Type):
    encoding = Signed
    byteSize = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit128"
Bit128 = _Bit128()    

# float
class _Bit32F(Type):
    '''
    A 32bit float
    in C ''float'
    '''
    encoding = Float
    byteSize = 4
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit32F = _Bit32F()

# double
class _Bit64F(Type):
    '''
    A 32bit float
    in C ''double'
    '''
    encoding = Float
    byteSize = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit64F = _Bit64F()

#! ignoring long double (128ish)

class _StrASCII(Type):
    encoding = ASCII
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
StrASCII = _StrASCII() 
 
class _StrUTF8(Type):
    encoding = UTF8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
StrUTF8 = _StrUTF8() 


# Containers must be instanciated to make a type
class TypeContainer(Type):
    def __init__(self, elementType):
        self.elementType = elementType

    def equals(self, other):
        #return self.canEqual(other) and self.elementType.equals(other)
        return (type(self) == type(other)) and self.elementType.equals(other.elementType)

    def __repr__(self):
        return "{}(elementType:{})".format(self.__class__.__name__, self.elementType)

    def __str__(self):
        return "{}[{}]".format(self.__class__.__name__, self.elementType)
        
class Literal(TypeContainer):
    def __init__(self, elementType):
        if not(isinstance(elementType, Type)):
            raise ValueError('Literal elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
        self.byteSize = self.elementType.byteSize
            
class Pointer(TypeContainer):
    byteSize = arch['bytesize']
    def __init__(self, elementType):
        if not(isinstance(elementType, Type)):
            raise ValueError('Pointer elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
                            
class Array(TypeContainer):
    def __init__(self, elementType):
        if not(isinstance(elementType, Type)):
            raise ValueError('Array elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
        
    # @property
    # def byteSize(self):
        # bz = self.elementType.byteSize
        # if (bz):
            # return self.size * self.elementType.byteSize
        # return bz
        
#! There is situations when cluch data is aligned. Acccount for that
class Clutch(TypeContainer):
    def __init__(self, elementType):
        super().__init__(elementType)
        self.offsets = {}
        byteSize = 0
        #! what if the type bytesize is None
        #? that should never be. Only applies to arrays, and no array should be raw in a clutch?
        for k,tpe in elementType.items():
            if not(isinstance(tpe, Type)):
                raise ValueError('Clutch an element of elementType not instance of Type. elementType:{}, element: {}'.format(elementType, tpe))
            self.offsets[k] = byteSize
            byteSize += tpe.byteSize
        self.byteSize = byteSize

##Pointer?b

# Render data
baseStyle = {
    'indent': '    '
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
        # return a new offset on the stack
        self.idx += 1
        #b += "push {}".format(addressLocation))
        return self.idx
    
    def __repr__(self):
        return "StackIndex(idx: {})".format(self.idx)
    
    
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
    def backBuild(self, b, jumpToEnd, jumpLabels):          
        raise NotImplementedError('BooleanOp:  backBuild func class:{}'.format(self.__class__.__name__))

    def build(self, b, jumpToEnd, jumpLabels):
        raise NotImplementedError('BooleanOp:  build func class:{}'.format(self.__class__.__name__))

    def __repr__(self):
        return self.__class__.__name__
        
class BooleanCondition(BooleanOp):
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def negate(self):
        pass

    def backBuild(self, b, jumpToEnd, jumpLabels):          
        self.build(b, jumpToEnd, jumpLabels);
            
    def build(self, b, jumpToEnd, jumpLabels):          
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
        
    def backBuild(self, b, jumpToEnd, jumpLabels):
        tailArg = self.args.pop()
        print(self.args)
        for arg in self.args:
            arg1 = arg.negate()
            arg1.build(b, True, jumpLabels)
        tailArg.build(b, False, jumpLabels)
                
    def build(self, b, jumpToEnd, jumpLabels):
        for arg in self.args:
            arg1 = arg.negate()
            arg1.build(b, True, jumpLabels)

    def __repr__(self):
        return "AND({})".format(
          ", ".join(self.args)
        )            
        
class OR(BooleanLogic):
    def negate(self):
        # De Morgans law
        return OR([arg.negate() for arg in self.args])

    def backBuild(self, b, jumpToEnd, jumpLabels):
        for arg in self.args:
            arg.build(b, False, jumpLabels)
                    
    def build(self, b, jumpToEnd, jumpLabels):
        tailArg = self.args.pop()
        for arg in self.args:
            arg.build(b, False, jumpLabels)
        tailArg.negate().build(b, True, jumpLabels)
            
    def __repr__(self):
        return "OR({})".format(
          ", ".join(self.args)
        ) 

class NOT(BooleanLogic):    
    def __init__(self, arg):
        self.arg = arg

    def negate(self):
        return self.arg

    def backBuild(self, b, jumpToEnd, jumpLabels):
        negated = self.arg.negate()
        negated.build(b, jumpToEnd, jumpLabels)
        
    def build(self, b, jumpToEnd, jumpLabels):
        negated = self.arg.negate()
        negated.build(b, jumpToEnd, jumpLabels)

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
        trueLabel = labels('true')
        self.failLabel = labels('endif')
        # BooleanLogic will look after itself, but BooleanCondition
        # needs negating and a jump to the end
        c = comparison
        if (isinstance(comparison, BooleanCondition) or isinstance(comparison, NOT)):
            #print('init negate')
            # Any BooleanLogic will do, they all negate then direct to 
            # end. NOT is simply convenient.
            c = NOT(comparison)
        c.build(b, True, JumpLabels(trueLabel, self.failLabel))
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
        #if (isinstance(c, BooleanCondition) or isinstance(c, NOT)):
            #print('init negate')
            # Any BooleanLogic will do, they all negate then direct to 
            # end. NOT is simply convenient.
        #    c = NOT(c)
        c.backBuild(b, None, JumpLabels(self.startLabel, self.exitLabel))        
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
    '''
    def __init__(self, stackByteSize, address):
        self.stackByteSize = stackByteSize
        self.base = ''
        self.index = ''
        self.scale = ''
        self.displacement = ''

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
        

