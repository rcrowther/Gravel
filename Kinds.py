
#from Trees import Tree

# names are checked before they arrive
class BaseKind():
    '''
    Like Tree, Kind toString() prints as code that represents a working 
    AST.
    '''
    is_defined = False
    is_const = False
    is_ref = False
    parents = []
    
    def __init__(self, name):
        self.parsedKind = name
        
    def toString(self):
        return "Kind('{}')".format(
        self.parsedKind
        )
        
    def __repr__(self):
        return self.toString()
        
        
        
'''
Base of all real kinds (non-func?).
has no parents.
'''
class _Any(BaseKind):
    def __init__(self):
        super().__init__('')
        
    def toString(self):
        return "Any"
        
Any = _Any()

'''
Unknown kind.
Used for basic initialising. Only before a typechecker.
'''
class _UnknownKind(BaseKind):
    def __init__(self):
        super().__init__('')
        
    def toString(self):
        return "UnknownKind"
        
UnknownKind = _UnknownKind()


#! like scala.Unit
'''
Absense of kind.
e.g. expression with no return.
''' 
class _NoKind(BaseKind):
    def __init__(self):
        super().__init__('')
        
    def toString(self):
        return "NoKind"
        
NoKind = _NoKind()
    
    
    
    
class Kind(BaseKind):
    pass    

## Basics
# These are the kinds for Atoms when they are first read....
# if they have no type annotation.
StringKind = Kind('String') 
IntegerKind = Kind('Int')
FloatKind = Kind('Float')
#_utf8 = Kind('UTF')
#_utf8.contentKinds.append(Kind('8'))

class CollectionKind(BaseKind):
    def __init__(self, name, contentKinds=[]):
        self.contentKinds = contentKinds
        super().__init__(self, name)

    def toString(self):
        return "CollectionKind({}, {})".format(
        self.name,
        self.contentKinds
        )
        
        

