
from Mark import NoMark, UndefinedMark

# names are checked before they arrive
class BaseKind():
    is_defined = False
    is_const = False
    is_ref = False
    parents = []
    
    def __init__(self, mark):
        self.mark = mark
        
    def toString(self):
        return "Kind('{}')".format(
        self.mark.toString(),
        )
        
    def __repr__(self):
        return self.toString()
        
        
        
'''
Base of all real kinds (non-func?).
has no parents.
'''
class _Any(BaseKind):
    def __init__(self):
        super().__init__(NoMark)
        
    def toString(self):
        return "Any"
        
Any = _Any()

'''
Unknown kind.
Used for basic initialising. 
'''
class _UnknownKind(BaseKind):
    def __init__(self):
        super().__init__(NoMark)
        
    def toString(self):
        return "UnknownKind"
        
UnknownKind = _UnknownKind()



'''
Absense of kind.
e.g. expression with no return.
''' 
class _NoKind(BaseKind):
    def __init__(self):
        super().__init__(NoMark)
        
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
    def __init__(self, mark, contentKinds=[]):
        self.contentKinds = contentKinds
        super().__init__(self, mark)

    def toString(self):
        return "CollectionKind({}, {})".format(
        self.mark.toString(),
        self.contentKinds
        )
        
        

