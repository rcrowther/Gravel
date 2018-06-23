
#from Trees import Tree

# names are checked before they arrive
#! generic kinds?
#! How to make new kinds, based on this?
#! how to test for type? subtypes? etc.
#1 widen/narrow types?
#! what is:
# existential type " and wildcard types."
# polytype "type of a polymorphic value"
# skolem
# compound type
# Wile I am not planning to allow to add new types anythime soon,
# I'd prefer not to be hardwired with an inheritance sytem. But do I
# implement, effectively, an inheritance system (of owners)? Ideas,
# anyone?
# For sure, would like to print the tree of inheritance
class Kind():
    '''
    Kind of an value or expression.
    This class is used for custom kinds.
    Like Tree, Kind toString() prints as code that represents a working 
    AST.
    '''
    _in = None
    _out = None
    is_defined = False
    is_const = False
    is_ref = False

    def __init__(self, name):
        self.name = name
            
    def toString(self):
        return "{}".format(
        self.name
        )    

    def __repr__(self):
        return self.toString()
        
'''
Base of all real kinds (non-func?).
has no parents.
'''
class _Any(Kind):
    def __init__(self):
        self._in = 0
        self._out = 1
        super().__init__("Any")

Any = _Any()



class _Nothing(Kind):
    '''
    Absense of anything.
    A Kind for the kindless. Or an unreal Kind.
    e.g. expressions with no return. Or compiler visions, such as '???'.
    '''
    def __init__(self):
       super().__init__("Nothing")
        
Nothing = _Nothing()


class _AnyVal(Kind):
    def __init__(self):
        super().__init__("AnyVal")
        
AnyVal = _AnyVal()



#! like scala.Unit
#? like void
class _NoVal(Kind):
    '''
    Absense of value.
    e.g. expression with no return.
    ''' 
    def __init__(self):
       super().__init__("NoVal")
        
NoVal = _NoVal()




class _AnyRef(Kind):
    def __init__(self):
       super().__init__("AnyRef")
        
AnyRef = _AnyRef()



#! like scala.Null
class _NoRef(Kind):
    '''
    Absense of reference.
    e.g. expression with no return.
    ''' 
    def __init__(self):
       super().__init__("NoRef")
        
NoRef = _NoRef()    
    
    
#x What for?
#class Kind(Kind):
#    pass    

## Basics
# Values
# UnnamedData Kinds initial .
'''
An Integer which will be the largest a machine can naturally handle.
'''
class _Integer(Kind):
    def __init__(self):
       super().__init__("Integer")

Integer = _Integer()



'''
A Float which will be the largest a machine can naturally handle.
'''
class _Float(Kind):
    def __init__(self):
       super().__init__("Float")
        
Float = _Float()

# and these
#Float32 = _AnyVal('Float32')
#Float64 = _AnyVal('Float64')
#Bits8 =  _AnyVal('Bits8')
#Bits16 =  _AnyVal('Bits16')
#Bits32 =  _AnyVal('Bits32')
#Bits64 =  _AnyVal('Bits64')
#Bits128 =  _AnyVal('Bits128')

# Refs


#! yet to sort outexistential kinds etc.
class _String(Kind):
    def __init__(self):
       super().__init__("String")

String = _String()


#_utf8 = Kind('UTF')
#_utf8.contentKinds.append(Kind('8'))

class CollectionKind(Kind):
    def __init__(self, name, contentKinds=[]):
        self.contentKinds = contentKinds
        super().__init__(name)

    def toString(self):
        return "{}[{}]".format(
        self.name,
        self.contentKinds
        )

class List(CollectionKind):
    def __init__(self, contentKinds=[]):
        super().__init__('List', contentKinds)

# Array?
class Seq(CollectionKind):
    def __init__(self, contentKinds=[]):
        super().__init__('Seq', contentKinds)

class Iterable(CollectionKind):
    def __init__(self, contentKinds=[]):
        super().__init__('Iterable', contentKinds)
 
