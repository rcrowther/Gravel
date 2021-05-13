import math
from exceptions import TypePathError
from collections import OrderedDict
from tpl_offset_iterators import OffsetIteratorIndexedGenerator
import architecture

arch = architecture.architectureSolve(architecture.x64)


'''
Far as I can see, we have two implementation alternatives with types:
Use Pythons facilities, replicated in many languages, to make a type as 
a class,
Con: 
- Needs metaclasses from the off. 
- To get the type of a constructed container, we must use type()
- Can not autogenerate new types easily
Or make types an instance,
Con:
- All types need a instance representation someplace. r.g I want a 
VarArray(Bit8). If type is needed, say for further construction, it 
must construct an Array (type) instance with Bit8 instance embedded.
So collections must be a class, though types without variable contents 
can have cannonical representation.
- Will raise problems of equality between types
I'm favouring the instance solution. 
'''
'''
Types
A type is the common, immutable aspects of the basic data (so far, not
fuctions). 
No, it's largely a categorisation of declared data? By encoding and 
organisation? 
Somettimes we need to refer to types themselves. For example, in an 
array, we do not need to know the type of every element, only that 
every element has a type of X. To do this, we refer to the class itself,
which can in Python be passed about and compared.
The base types do not exist as individual instances i.e. are not mapped 
to data. Niether do they work if they are instances (they should not be 
instanced). They only refer to data when they are put in a container.
One of the containers is a Literal/Constant container.
Any type put in a container creates a new type, which take the name of  
the container as type. Again, the class is used to refer to the type.
Since the process is circular (type in type in type...), from these 
elements, arbitary types can be built.
'''
'''
# Rationale for types
We were storing bit sizes anyway, because they are neceassary for 
clutches. That comes close, as commonly understood, to type info. To add
an encoding more or less defines a type. It also expands the system from
perhaps 5 ''types' (bit sizes) to perhaps sixteen ''types'. This is 
till managable. What it will do is give is give advantages for defining
general, semi-polymorphic, instructions, for example, forfloat types, 
and for prints.
What we will not do is introduce any feature that relies on the types,
such as auto-polymorphic functions.
We will not type symbols???
We will not store mutable data like string lengths.
'''


        
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


#?x
#from collections import namedtuple
#TypepathItem = namedtuple('TypepathItem', ['tpe', 'offset'])




class Type():
    #NB this used to contain extensive type analysis code. for example,
    # children(), depth() etc. However, that kind of self-knowledge
    # has been abandonded for tests and builders outside the type classes
    # themselves. Ad-hoc the tests may be, but they are better informed
    # about surrounding possibilities, such as relative address 
    # construction, than the types alone can be.
    '''
    Bytesize of root of the type
    Never larger than bytesize of the bus, but may be smaller. 
    If the type is not on a pointer, this is set to the bytecount of 
    the type.
    If the top type iss a pointer, this is set to buswidth.
    If the type is a container, it has an implicit pointer, and is set
    to buswidth.
    The value is used to provide hints to the assembler.  
    return
        the bytesize of the root type.
    '''    
    byteSizeRoot = None
    
    '''
    The type contained by this type.
    return
        The contained type. If the type is not a container, None 
    '''
    elementType = None


    '''
    Encoding of the data
    Different encodings produce different types e.g. of string or float 
    data.
    '''
    encoding = None
    
    #def __init__(self):
    #    self.children = []
    #    raise NotImplementedError('A base Type can not be instanciated')
            
    @property
    def byteSize(self):
        '''
        Bytesize of this type.
        If the type is a container, also includes the bytes needed
        for the pointer.
        return
            the bytesize in full, including descendant types.
        '''    
        raise NotImplementedError()

            
    def equals(self, other):
        '''
        Test if this type matches another.
        If there are contents, they should be checked too. 
        '''
        raise NotImplementedError('Bad!! This type has no equals function');

    def __repr__(self):
        raise NotImplementedError('This type has no __repr__ representation');
        #return "{}".format(self.__class__.__name__) #+ ('instance')




'''
A type of no substance.
Useful if a Type is required, but never want to interact with it. 
For example, a currently unknown type. Or empty return.
'''
class _NoType(Type):
    def __repr__(self):
        return "NoType"
        
NoType = _NoType()




class TypeSingular(Type):
    
    def equals(self, other):
        # singular types are instances, so all we need to know is this
        # reference to the same object as that reference?
        return self is other
        
        
class TypeNumeric(TypeSingular):
    @property
    def byteSize(self):
        return self.byteSizeRoot

# char
class _Bit8(TypeNumeric):
    encoding = Signed
    byteSizeRoot = 1
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit8 = _Bit8()

# No C equivalent
#! is this an encoding?
Bool = _Bit8()

# short int
class _Bit16(TypeNumeric):
    encoding = Signed
    byteSizeRoot = 2
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit16"
Bit16 = _Bit16()

# int
class _Bit32(TypeNumeric):
    encoding = Signed
    byteSizeRoot = 4
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit32"
Bit32 = _Bit32()

# long int
class _Bit64(TypeNumeric):
    encoding = Signed
    byteSizeRoot = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit64"
Bit64 = _Bit64()    

# long long int
class _Bit128(TypeNumeric):
    encoding = Signed
    byteSizeRoot = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit128"
Bit128 = _Bit128()    

# float
class _Bit32F(TypeNumeric):
    '''
    A 32bit float
    in C ''float'
    '''
    encoding = Float
    byteSizeRoot = 4
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit32F"
Bit32F = _Bit32F()

# double
class _Bit64F(TypeNumeric):
    '''
    A 32bit float
    in C ''double'
    '''
    encoding = Float
    byteSizeRoot = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit64F"
Bit64F = _Bit64F()

#! ignoring long double (128ish)


#! not sure if these are singular. Better as Array[Codepoint]?
#! Array[Byte]?
class TypeString(TypeSingular):
    @property
    def byteSize(self):
        return None

class _StrASCII(TypeString):
    encoding = ASCII
    byteSizeRoot = arch['bytesize']

    #def print(self):
    #    pass
    def __repr__(self):
        return "StrASCII"
StrASCII = _StrASCII() 
 
class _StrUTF8(TypeString):
    encoding = UTF8
    byteSizeRoot = arch['bytesize']

    #def print(self):
    #    pass
    def __repr__(self):
        return "StrUTF8"
StrUTF8 = _StrUTF8() 



class TypeContainer(Type):
    '''
    In this system a container must be instanciated to make a type.
    Containers have no encoding
    '''
    size = 0
    isLabeled = False
    byteSizeRoot = arch['bytesize']

    def __init__(self, elementType):
        self.elementType = elementType

    def equals(self, other):
        # Since these have many, not one instance, we need to check
        # against classes, not for object equality.
        # Also, must test element type too
        # Also, element types can be arrays of elements.        
        #? Not concerned with label names
        #NB Works for pointers and arrays, but not the more general case 
        # of clutches, which contain lists of types
        return (type(self) == type(other)) and self.elementType.equals(other.elementType)
        
    def __repr__(self):
        return "{}(elementType:{})".format(self.__class__.__name__, self.elementType)

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self.elementType)
        

            
# The big issue here is we can't get bytesize in, it's architecture dependant.
# All containers imply a pointer?
class Pointer(TypeContainer):
    '''
    A pointer to data
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        a list with one element, the contained type
    '''
    size = 1

    byteSizeRoot = arch['bytesize']

    @property
    def byteSize(self):
        return self.byteSizeRoot + self.elementType.byteSize
            
    def __init__(self, args):
        assert (len(args) == 1), 'Pointer: args should be array of 1. args: {}'.format(args)
        elementType = args[0]
        assert (isinstance(elementType, Type)), 'Pointer: elementType not a Type. elementType: {}'.format(type(elementType))
        super().__init__(elementType)
        #self.byteSize = 8
        
        

class TypeContainerOffset(TypeContainer):
    #? Consider generalising offset methods through all types.
    #? Should they be NotImplemented (means a catch), or return zero 
    # (spurious code)?
        
    def offsetTypePair(self, lid):
        '''
        Get the offet of a contained element
        Only works on the top level type.
        lid
            a locating value (either int or label)
        '''
        raise NotImplementedError()

    def offsetIt(self):
        '''
        Iterate the offets of contained elements
        Only works on the top level type.
        lid
            a locating value (either int or label)
        '''
        raise NotImplementedError()
        
        
        
        
#! There is situations when cluch data is aligned. Acccount for that
class Clutch(TypeContainerOffset):
    '''
    Collection of non-similar data.
    This can return bytesize. And cumulative offsets.
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        [type1, type2 ...]
    '''
    def __init__(self, args):
        # a cumulative list of byte index
        offsetTypePairs = []
        offsetSum = 0
        #? what if the type bytesize is None? That would be the case
        # for dynamic arrays...
        for tpe in args:
            assert isinstance(tpe, Type), "Clutch: an arg is not a Type. args:{}, arg: '{}'".format(args, tpe)
            offsetTypePairs.append((offsetSum, tpe,))
            offsetSum += tpe.byteSize
        self.offsetTypePairs = offsetTypePairs 
        # self.byteSize = offsetSum
        super().__init__(args)
        self.size = len(args)

    #! DRY
    def equals(self, other):
        # compare two clutches.
        # I think the zip() simply exhausts, but as long as other can
        # match this, lets duck type and say it will work
        r = (type(self) == type(other))
        
        #NB Any functional language has a collate function, but Python
        # isn't a functional language. Or I don't know?
        if (r):
            for sTpe, oTpe in zip(self.elementType, other.elementType): 
                r = sTpe.equals(oTpe)
                if (not(r)):
                    break
        return r

    @property
    def byteSize(self):
        byteSize = 0
        for tpe in self.elementType:
            byteSize += tpe.byteSize
        return byteSize
        
    def offsetTypePair(self, lid):
        return self.offsetTypePairs[lid]

    def offsetIt(self):
        return iter(self.offsetTypePairs)
        
    def subTypes(self):
        return self.elementType
        
        
                
#! There is situations when cluch data is aligned. Acccount for that
class ClutchLabeled(TypeContainerOffset):
    '''
    Collection of non-similar data.
    This can return bytesize. And cumulative offsets.
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        A list of of [label1, type1, label2, type2 ...]
    '''
    isLabeled = True

    def __init__(self, args):
        #NB Yes, I can do it faster and tidier. I have reasons
        assert(len(args) % 2 == 0), 'ClutchLabeled: supplied args not even number? args:{}'.format(
                args
            )

        # map(label, offset)
        # and
        # list(offset, type)
        labelToPairMap = {}
        offsetTypePairs = []
        offsetSum = 0
        typeList = []
        for i in range(0, len(args), 2):
            label = args[i]
            tpe = args[i + 1]
            assert isinstance(tpe, Type), 'ClutchLabeled: arg not a Type. args:{}, arg: {}'.format(args, tpe)
            pair = (offsetSum, tpe,)
            labelToPairMap[label] = pair
            offsetTypePairs.append(pair)            
            typeList.append(tpe)
            offsetSum += tpe.byteSize
        self.labelToPairMap = labelToPairMap
        self.offsetTypePairs = offsetTypePairs 
        #self.byteSize = offsetSum
        super().__init__(typeList)
        self.size = len(typeList)

    #! DRY
    def equals(self, other):
        '''
        Compare two clutches for equality
        '''
        #? Not concerned with label names
        # I think the zip() simply exhausts, but as long as other can
        # match this, lets duck type and say it will work
        r = (type(self) == type(other))
        
        #NB Any functional language has a collate function, but Python
        # isn't a functional language. Or I don't know?
        if (r):
            for sTpe, oTpe in zip(self.elementType, other.elementType): 
                r = sTpe.equals(oTpe)
                if (not(r)):
                    break
        return r

    @property
    def byteSize(self):
        byteSize = 0
        for tpe in self.elementType:
            byteSize += tpe.byteSize
        return byteSize
                
    def offsetTypePair(self, lid):
        return self.labelToPairMap[lid]        

    def offsetIt(self):
        return iter(self.offsetTypePairs)

    def subTypes(self):
        return self.elementType.values()
        
    def labels(self):
        return self.elementType.keys()



        
class Array(TypeContainerOffset):
    '''
    An array of data
    A fixed length. So the type can return it's bytesize
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        [containedType, size]
    '''
    def __init__(self, args):
        assert (len(args) == 2), 'Array: args should be array of 2. args: {}'.format(args)
        elementType = args[0]
        assert isinstance(elementType, Type), 'Array: first arg not a Type. args: {}'.format(args)
        super().__init__(elementType)
        self.size = args[1]
        #self.byteSize =  elementType.byteSize * self.size

    @property
    def byteSize(self):
        return self.elementType.byteSize * self.size
        
    def offsetTypePair(self, lid):
        '''
        Get the offset of a contained element
        lid
            an integer
        '''
        #? Humm. Could precalculate these...
        return (self.elementType.byteSize * lid, self.elementType,)

    def offsetIt(self):
        return OffsetIteratorIndexedGenerator(
            self.size,
            self.elementType,
        )

#? Labels can be either in a type, in which
# case they do refer to an array
# or can be builtin to the data i.e. a hash table
# perhaps they shouldn't be in Rubble?
# Ada solution:
#https://learn.adacore.com/courses/intro-to-ada/chapters/arrays.html
class ArrayLabeled(TypeContainerOffset):
    '''
    An array of data
    A fixed length. So the type can return it's bytesize
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        [containedType, label1, label2...]
    '''
    isLabeled = True

    def __init__(self, args):
        elementType = args.pop(0)
        assert isinstance(elementType, Type), 'ArrayLabeled: first arg not a Type. args: {}'.format(args)
        self.size = len(args)
        super().__init__(elementType)
        
        # map(label, offset)
        # and
        # list(offset, type)
        labelToPairMap = {}
        offsetTypePairs = []
        elemByteSize = elementType.byteSize
        offsetSum = 0
        for label in args:
            pair = (offsetSum, self.elementType,)
            labelToPairMap[label] = pair
            offsetTypePairs.append(pair)
            offsetSum += elemByteSize
        self.labelToPairMap = labelToPairMap
        self.offsetTypePairs = offsetTypePairs 
        #self.byteSize = offsetSum

    @property
    def byteSize(self):
        return self.elementType.byteSize * self.size
                
    def offsetTypePair(self, lid):
        '''
        Get the offset of a contained element
        lid
            a label
        '''
        return self.labelToPairMap[lid]        
        
    def offsetIt(self):
        return iter(self.offsetTypePairs)
        
        

#x see also tpl_vars
# Gonna rethink all this
# def accessSnippet(b, tpe, path):
    # #! protrect against path type error
    # currTpe = tpe
    # for lid in path:
        # b += "+" 
        # b += str(currTpe.offset(lid))
        # currTpe = currTpe.elemType(lid)
    # return b
        
typeNames = [
    'Bit8',
    'Bit16',
    'Bit32',
    'Bit64',
    'Bit128',
    'Bit32F',
    'Bit64F',
    'StrASCII',
    'StrUTF8',
    'Pointer',
    'Array',
    'Clutch',
]

typeNameSingularToType = {
    'Bit8': Bit8,
    'Bit16': Bit16,
    'Bit32': Bit32,
    'Bit64': Bit64,
    'Bit128': Bit128,
    'Bit32F': Bit32F,
    'Bit64F': Bit64F,
    'StrASCII': StrASCII,
    'StrUTF8': StrUTF8,
}

typeNameContainerToType = {
    'Pointer': Pointer,
    'Array': Array,
    'ArrayLabeled': ArrayLabeled,
    'Clutch': Clutch,
    'ClutchLabeled' : ClutchLabeled,
}
