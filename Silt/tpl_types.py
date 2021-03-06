import math
from exceptions import TypePathError


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
A type is the common, immutable aspeects of the basic data (so far, not
fuctions). 
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
clutches. That comes close to type info. To add an encoding more or 
less defines a type. It also expands the system from perhaps 5 
''types' (bit sizes) to perhaps sixteen ''types' (with the addition
of encoding). This is still managable. What it will do is give is
many advantages of defining special instructions, for example, for
float types, and for prints.
What we will not do is introduce any feature that relies on the types,
such as polymorphic functions.
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


from collections import namedtuple
TypepathItem = namedtuple('TypepathItem', ['tpe', 'offset'])

class Type():
    '''
    Bytesize of this type.
    return
        the bytesize. If the bytesize is varible then None.
    '''
    byteSize = None

    
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
            
    # @property
    # def byteSize(self):
        # return self._byteSize
    
    def canEqual(self, other):
        return isinstance(other, Type)
        
    def equals(self, other):
        #return self.canEqual(other) and self.elementType.equals(other)
        return (self == other)

    #! Not work on clutch, or clutch renders a bit useless
    # def foreach(self, f):
        # '''
        # Do some action f for the type and subtypes.
        # '''
        # tpe = self
        # while(tpe):
            # f(tpe)
            # tpe = tpe.elementType

    
    # def list(self):
        # '''
        # List the type and subtypes.
        # Order is outer-in. To go inner-out, can be reversed(list())
        # '''
        # tpe = self
        # b = []
        # while(tpe):
            # b.append(tpe)
            # tpe = tpe.elementType
        # return b
    # This works, but is nasty stepping code and inefficient
    # The data could be gathered on build, at the cost of a kind of 
    # repetition. The question is, is this data usable 
    # cross-architecture for example, for relative address detection?
    #! may abandon this for something else
    def children(self, offsetIndexAndLabels):
        '''
        List the children/contained types.
        Includes the initial type (self).
        offsetIndextAndLabels
            [] of indexes and labels for arrays and clutches. Only 
            labels are used, to trace down types parented/contained in a
            clutch.
        return
            A list of the types. Since they types are pointer to the 
            type, the first outer type will contain all the contained 
            types, the next will include all the types it contains, etc. 
            The types are in order out..in.
        '''
        typeMem = []
        tpe = self
        olIdx = 0
        while(tpe):
            if (not isinstance(tpe, TypeContainerOffset)):
                typeMem.append(tpe)
                tpe = tpe.elementType
            else:
                if (olIdx >= len(offsetIndexAndLabels)):
                    raise ValueError('Not enough data in path. tpe:{}, offsetIndexAndLabels:{}'.format(
                        tpe,
                        offsetIndexAndLabels
                    ))
                offsetOrLabel = offsetIndexAndLabels[olIdx]
                olIdx += 1
                if (isinstance(tpe, Array)):
                    typeMem.append(tpe)
                    tpe = tpe.elementType
                elif (isinstance(tpe, Clutch)):
                    typeMem.append(tpe)
                    if (not (offsetOrLabel in tpe.elementType)):
                        raise ValueError('Given label not in Clutch. label:"{}", clutch:{}'.format(
                            offsetOrLabel,
                            tpe
                        ))
                    tpe = tpe.elementType[offsetOrLabel]
        #print('typeMem')
        #print(str(typeMem))
        return typeMem
                    

    def typePath(self, offsetIndexAndLabels):
        '''
        List the children/contained types.
        Includes the initial type (self).
        offsetIndextAndLabels
            [] of indexes and labels for arrays and clutches. Only 
            labels are used, to trace down types parented/contained in a
            clutch.
        return
            A list of the types. Since they types are pointer to the 
            type, the first outer type will contain all the contained 
            types, the next will include all the types it contains, etc. 
            The types are in order out..in.
        '''
        typeMem = []
        tpe = self
        olIdx = 0
        while(tpe):
            if (not isinstance(tpe, TypeContainerOffset)):
                typeMem.append(TypepathItem(tpe, None))
                tpe = tpe.elementType
            else:
                if (olIdx >= len(offsetIndexAndLabels)):
                    raise ValueError('Not enough data in path. tpe:{}, offsetIndexAndLabels:{}'.format(
                        tpe,
                        offsetIndexAndLabels
                    ))
                offsetOrLabel = offsetIndexAndLabels[olIdx]
                olIdx += 1
                typeMem.append(TypepathItem(tpe, offsetOrLabel))
                if (isinstance(tpe, Array)):
                    tpe = tpe.elementType
                elif (isinstance(tpe, Clutch)):
                    if (not (offsetOrLabel in tpe.elementType)):
                        raise ValueError('Given label not in Clutch. label:"{}", clutch:{}'.format(
                            offsetOrLabel,
                            tpe
                        ))
                    tpe = tpe.elementType[offsetOrLabel]
        #print('typeMem')
        #print(str(typeMem))
        return typeMem

    def typeDepth(self):
        '''
        Return the depth of this type i,e, number of subtypes
        When this function encounters a clutch, it chooses the maximum
        depth from the available types.
        '''
        raise NotImplementedError('This type has no typeDepth implementation');
        
    def __repr__(self):
        raise NotImplementedError('This type has no __repr__ representation');
        #return "{}".format(self.__class__.__name__) #+ ('instance')


class TypeSingular(Type):
    #def foreach(self, f):
    #    f(self)
    
    #def list(self):
    #    return [self]
        
    def typeDepth(self):
        return 1
        
# char
class _Bit8(TypeSingular):
    encoding = Signed
    byteSize = 1
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit8 = _Bit8()

# short int
class _Bit16(TypeSingular):
    encoding = Signed
    byteSize = 2
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
Bit16 = _Bit16()

# int
class _Bit32(TypeSingular):
    encoding = Signed
    byteSize = 4
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit32"
Bit32 = _Bit32()

# long int
class _Bit64(TypeSingular):
    encoding = Signed
    byteSize = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit64"
Bit64 = _Bit64()    

# long long int
class _Bit128(TypeSingular):
    encoding = Signed
    byteSize = 8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit128"
Bit128 = _Bit128()    

# float
class _Bit32F(TypeSingular):
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
class _Bit64F(TypeSingular):
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

class _StrASCII(TypeSingular):
    encoding = ASCII
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
StrASCII = _StrASCII() 
 
class _StrUTF8(TypeSingular):
    encoding = UTF8
    #def print(self):
    #    pass
    def __repr__(self):
        return "Bit8"
StrUTF8 = _StrUTF8() 


class TypeContainer(Type):
    '''
    In this system a container must be instanciated to make a type.
    Containers have no encoding
    '''
    size = 0
    isLabeled = False
        
    def __init__(self, elementType):
        self.elementType = elementType
    
    def elemType(self, lid):
        '''
        The type of a contained element
        '''
        raise NotImplementedError()
    
    def equals(self, other):
        #return self.canEqual(other) and self.elementType.equals(other)
        return (type(self) == type(other)) and self.elementType.equals(other.elementType)
        
    def containsTypeSingular(self):
        '''
        Are all child types TypeSingular?
        '''
        raise NotImplementedError('This type has no __repr__ representation')
        
    # def countTypesOffset(self):
        # i = 0
        # for tpe in self.list():
            # if (isinstance(tpe, TypeContainerOffset)):
                # i += 1
        # return i
        
    def __repr__(self):
        return "{}(elementType:{})".format(self.__class__.__name__, self.elementType)

    def __str__(self):
        return "{}[{}]".format(self.__class__.__name__, self.elementType)
        
# A literal is not a type, is it? its a variable... It has a location.
# class Literal(TypeContainer):
    # '''
    # A piece of data that exists existentially.
    # Existentiallyy meaning, it stands as itself. Though a container, no identity exists elsewhere.
    # '''
    # def __init__(self, elementType):
        # if not(isinstance(elementType, Type)):
            # raise ValueError('Literal elementType not a Type. elementType: {}'.format(type(elementType)))
        # super().__init__(elementType)
        # self.byteSize = self.elementType.byteSize
            
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
    #byteSize = arch['bytesize']
    #byteSize = 8
    def __init__(self, args):
        assert (len(args) == 1), 'Pointer: trying to build with wrong number of args (should be 1). args: {}'.format(args)
        elementType = args[0]
        assert (isinstance(elementType, Type)), 'Pointer: elementType not a Type. elementType: {}'.format(type(elementType))
        super().__init__(elementType)
        self.byteSize = 8
           
    def elemType(self, lid):
        return self.elementType
        
        
    def containsTypeSingular(self):
        return isinstance(self.elementType, TypeSingular)            
                            
    def typeDepth(self):
        return self.elementType.typeDepth() + 1
        
        
        
class TypeContainerOffset(TypeContainer):
    #? Consider generalising offset methods through all types.
    #? Should they be NotImplemented (means a catch), or return zero 
    # (spurious code)?
    def offset(self, lid):
        '''
        Get the offet of a contained element
        Only works on the top level type.
        lid
            a locating value (either int or label)
        '''
        raise NotImplementedError()

    def _typeIsContainer(self, tpe, path):
            print(str(tpe))
            if (not isinstance(tpe, TypeContainer)):
                raise TypePathError('Path accesses type element which is not a container. type:{}, path:{}'.format(
                    tpe,
                    path
                ))
            return True
                
    def _pathElementTypeMatch(self, tpe, lid, path):
            if (tpe.isLabeled):
                if (type(lid)!= str):
                    raise TypePathError('Path element for labeled type is not str. type:{}, path:{}'.format(
                        tpe,
                        path
                    ))  
            else:
                if (type(lid)!= int):
                    raise TypePathError('Path element for unlabeled type is not int. type:{}, path:{}'.format(
                        tpe,
                        path
                    ))           
            return True
        
    def offsetDeep(self, path):
        '''
        Use a path to get the offet of a contained element
        Can work into a type tree. See offset.
        path
            [locationValue1,  locationValue2, ...]
        '''
        currTpe = self
        offset = 0
        for lid in path:
            assert self._typeIsContainer(currTpe, path)
            assert self._pathElementTypeMatch(currTpe, lid, path)
            offset += currTpe.offset(lid)
            currTpe = currTpe.elemType(lid)
        return offset
        
        
class Array(TypeContainerOffset):
    '''
    An array of data
    A fixed length. So the type can return it's bytesize
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        the contained type, size
    '''
    def __init__(self, args):
        # assertions?
        assert (len(args) == 2), 'Array: number of args should be 2. args: {}'.format(args)
        elementType = args[0]
        assert isinstance(elementType, Type), 'Array: first arg not a Type. args: {}'.format(args)
        super().__init__(elementType)
        self.size = args[1]
        self.byteSize =  elementType.byteSize * self.size

    def elemType(self, lid):
        return self.elementType
                
    def offset(self, lid):
        '''
        Get the offset of a contained element
        lid
            an integer
        '''
        #? Humm. Could precalculate these...
        return self.elementType.byteSize * lid
                
    def containsTypeSingular(self):
        return isinstance(self.elementType, TypeSingular)

    def typeDepth(self):
        return self.elementType.typeDepth() + 1        



class ArrayLabeled(TypeContainerOffset):
    '''
    An array of data
    A fixed length. So the type can return it's bytesize
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        the contained type, label1, label2...]
    '''
    isLabeled = True

    def __init__(self, args):
        elementType = args.pop(0)
        assert isinstance(elementType, Type), 'ArrayLabeled: first arg not a Type. args: {}'.format(args)
        self.size = len(args)
        super().__init__(elementType)
        # a cumulative list of byte index.
        offsets = {}
        elemByteSize = elementType.byteSize
        i = 0
        for label in args:
            offsets[label] = i
            i += elemByteSize
        self.offsets = offsets
        self.byteSize = i

    def elemType(self, lid):
        return self.elementType
        
    def offset(self, lid):
        '''
        Get the offset of a contained element
        lid
            a label
        '''
        return self.offsets[lid]        
        
        
        
#! There is situations when cluch data is aligned. Acccount for that
class Clutch(TypeContainerOffset):
    '''
    Collection of non-similar data.
    This can return bytesize. And cumulative offsets.
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        A list of [type1, type2 ...}
    '''
    def __init__(self, args):
        super().__init__(args)
        self.size = len(args)
        
        # a cumulative list of byte index.
        offsets = []
        i = 0
        #? what if the type bytesize is None? That would be the case
        # for dynamic arrays...
        for tpe in args:
            assert isinstance(tpe, Type), 'Clutch: arg not a Type. args:{}, arg: {}'.format(args, tpe)
            offsets.append(i)
            i += tpe.byteSize
        self.offsets = offsets
        self.byteSize = i

    def elemType(self, lid):
        return self.elementType[lid]
        
    def offset(self, lid):
        return self.offsets[lid]
        
    def subTypes(self):
        return self.elementType

    def containsTypeSingular(self):
        for tpe in self.subTypes():
            if (not isinstance(tpe, TypeSingular)):
                return False 
        return True

    def typeDepth(self):
        maxDepth = 0
        for tpe in self.subTypes():
            maxDepth = max(maxDepth, tpe.typeDepth())
        return maxDepth + 1
        
        
                
#! There is situations when cluch data is aligned. Acccount for that
class ClutchLabeled(TypeContainerOffset):
    '''
    Collection of non-similar data.
    This can return bytesize. And cumulative offsets.
    The reason for the unusual and clumsy construction interface is so
    container types can present a consistent interface.
    args
        A list of of [label1, type1, label2, type2 ...}
    '''
    isLabeled = True

    def __init__(self, args):
        #NB Yes, I can do it faster and tidier. I have reasons
        assert(len(args) % 2 == 0), 'ClutchLabeled: supplied args not even number? args:{}'.format(
                args
            )

        # Make a map of the args
        elementType = {}
        for i in range(0, len(args), 2):
            elementType[args[i]] = args[i + 1]
        super().__init__(elementType)
        self.size = len(elementType) 
        
        # a cumulative list of byte index.
        offsets = {}
        i = 0
        #? what if the type bytesize is None? That would be the case
        # for dynamic arrays...
        for label,tpe in elementType.items():
            assert isinstance(tpe, Type), 'ClutchLabeled: arg not a Type. args:{}, arg: {}'.format(args, tpe)
            offsets[label] = i
            i += tpe.byteSize
        self.offsets = offsets
        self.byteSize = i

    def elemType(self, lid):
        return self.elementType[lid]
        
    def offset(self, lid):
        return self.offsets[lid]

    def subTypes(self):
        return self.elementType.values()
        
    def labels(self):
        return self.elementType.keys()

    def containsTypeSingular(self):
        for tpe in self.subTypes():
            if (not isinstance(tpe, TypeSingular)):
                return False 
        return True

    def typeDepth(self):
        maxDepth = 0
        for tpe in self.subTypes():
            maxDepth = max(maxDepth, tpe.typeDepth())
        return maxDepth + 1

#x see also tpl_vars
def accessSnippet(b, tpe, path):
    #! protrect against path type error
    currTpe = tpe
    for lid in path:
        b += "+" 
        b += str(currTpe.offset(lid))
        currTpe = currTpe.elemType(lid)
    return b
        
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
