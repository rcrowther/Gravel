import math

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
    def children(self, offsetIndexAndLabels):
        '''
        List the children/contained types.
        offsetIndextAndLabels
            [] of indexes and labels for arrays and clutches. Only 
            labeles are used, to trace types contained in a clutch.
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
                    typeMem.append(tpe)
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
    def __init__(self, elementType):
        self.elementType = elementType

    def equals(self, other):
        #return self.canEqual(other) and self.elementType.equals(other)
        return (type(self) == type(other)) and self.elementType.equals(other.elementType)

    def containsTypeSingular(self):
        '''
        Are all child types TypeSingular?
        '''
        raise NotImplementedError('This type has no __repr__ representation');
        
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
    '''
    #byteSize = arch['bytesize']
    def __init__(self, elementType):
        if not(isinstance(elementType, Type)):
            raise ValueError('Pointer elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
            
    def containsTypeSingular(self):
        return isinstance(self.elementType, TypeSingular)            
                            
    def typeDepth(self):
        return self.elementType.typeDepth() + 1
        
        
        
class TypeContainerOffset(TypeContainer):
    pass
    
class Array(TypeContainerOffset):
    '''
    An array of data
    This type cannot return it's bytesize
    '''
    def __init__(self, elementType):
        if not(isinstance(elementType, Type)):
            raise ValueError('Array elementType not a Type. elementType: {}'.format(type(elementType)))
        super().__init__(elementType)
        
    def containsTypeSingular(self):
        return isinstance(self.elementType, TypeSingular)

    def typeDepth(self):
        return self.elementType.typeDepth() + 1        
        
        
#! There is situations when cluch data is aligned. Acccount for that
class Clutch(TypeContainerOffset):
    '''
    Collection of non-similar data.
    This can return bytesize. And cumulative offsets.
    elementType
        A dict of {key: type, ...}
    '''
    def __init__(self, elementType):
        super().__init__(elementType)
        '''
        a cumulative list of byte index.
        '''
        self.offsets = {}
        byteSize = 0
        #! what if the type bytesize is None
        #? that should never be. Only applies to arrays, and no array should be raw in a clutch?
        for k,tpe in elementType.items():
            if not(isinstance(tpe, Type)):
                raise ValueError('Clutch: an element of elementType not instance of Type. elementType:{}, element: {}'.format(elementType, tpe))
            self.offsets[k] = byteSize
            # Humm, This can be none, if it's an array
            if (tpe.byteSize):
                byteSize += tpe.byteSize
            else:
                byteSize = None
                break
        self.byteSize = byteSize

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
