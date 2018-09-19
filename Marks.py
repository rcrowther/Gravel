from Kinds import Kind, Any


#? Is this another attempt to do what I don't want to do?
#? What will we be asking:
#? Is a name/type in a scope
#? Is a name in a type?
#? etc.
#! when we say owner here, what do we mean? check with Scala REPL.
# --- bad coding to keep scope owner in scope and symbol.
# Owners appear to not be handled through Scope (though how are they
# then found?) Owners appear to be registered through symbols, see 
# Symbols.scala:1144. Yet what owners are these? Lets assume they are 
# type owners, 
class Mark:
    '''
    Data for an identifier in a program.
    The identifier could be a variable, function, namespace etc.
    Due to allowing one_name/many_types and many_names/one_type entities
    The code must provide unique keys (this is sometimes called a Symbol, 
    but usage of the word is often wandering, or includes opportunistic 
    information such as documentation).
    Owner is also called ''Scope', but I prefer this Scala usage.
    The unique key must include:
    ~ name
    : an important id for a user
    ~ type?
    : because same names may be isolated by type?
    - owner
    : because all name/types can be duplicated across owners
    
    Currently, this would not be used for typechecking, only name 
    resolution?
    @owner a pointer to another Mark.
    '''
    
    _id = 0
    #??? How does Scala do the key/hash?
    def newId(self):
        Mark._id += 1
        return Mark._id
        
    def __init__(self, name):
        #assert isinstance(scope, Scope), "Is not Scope: scope:{}".format(scope)
        #assert isinstance(kind, Kind), "Is not Kind: kind:{}".format(kind)
        id = self.newId() 
        self.name = name
        #self.kind = kind
        self.kind = Any
        # Scope is added automatically
        #x Should it be here at all?
        self.scope = None
        self.definitionTrees = []
        self.instanceTrees = []
        
    #! how do we effectively key?
    def key(self):
        #return ???
        return ''
        
    def toString(self):
        return 'Mark(name:"{}" kind:{})'.format(
            self.name,
            self.kind,
            #self.owner
            )
            
    def __repr__(self):
        return self.toString()

def mkBuiltin(name, kind):
    assert isinstanceof(Kind, kind), "Supplied parameter is not kind param:{}".format(kind) 
    m = Mark(name)
    m.kind = kind 
    return m
   
   
#?
globalPackage = Mark('GlobalPackage')
    
testMark = Mark('TestMark')
testMark2 = Mark('TestMark2')


# code, recievesReturn, type of params, returnType, interpreter func, description
#! These are solid marks, for stuff like Integer, and could do with caching
# Whereas other marks such as local variables may be very temporary?
#! how to integrate with other marks, especially as these can be directly 
# evaluated from parameters. Whereas the custom tree marks require tree 
# negotiation for evalauation?
#! for sure have a difference between a builtin, guarenteed to be there,
# and the hunt for definitions in the other mark?
class BuiltinMark:
    '''
    Data for an identifier in a program.
    The identifier could be a variable, function, namespace etc.
    Due to allowing one_name/many_types and many_names/one_type entities
    The code must provide unique keys (this is sometimes called a Symbol, 
    but usage of the word is often wandering, or includes opportunistic 
    information such as documentation).
    Owner is also called ''Scope', but I prefer this Scala usage.
    The unique key must include:
    ~ name
    : an important id for a user
    ~ type?
    : because same names may be isolated by type?
    - owner
    : because all name/types can be duplicated across owners
    
    Currently, this would not be used for typechecking, only name 
    resolution?
    @owner a pointer to another Mark.
    '''
    
    _id = 0
    #??? How does Scala do the key/hash?
    def newId(self):
        BuiltinMark._id += 1
        return BuiltinMark._id
        
    def __init__(self, 
        name,
        receivesReturn, 
        paramKinds, 
        returnKind, 
        evaluate, 
        description
        ):
        #assert isinstance(scope, Scope), "Is not Scope: scope:{}".format(scope)
        #assert isinstance(kind, Kind), "Is not Kind: kind:{}".format(kind)
        self.id = self.newId() 
        self.name = name
        self.receivesReturn = receivesReturn
        self.paramKinds = paramKinds
        self.returnKind = returnKind
        # Scope is added automatically
        #x Should it be here at all?
        self.evaluate = evaluate
        self.description = description

    def paramCount(self):
        l = len(self.paramKinds)
        if (receivesReturn):
           l += 1
        return l
        
    def toString(self):
        return 'BuiltinMark(name:"{}" receivesReturn: {} paramKinds:{}, returnKind:{})'.format(
            self.name,
            self.receivesReturn,
            self.paramKinds,
            self.returnKind,
            #self.evaluate,
            #self.description
            )
            
    def __repr__(self):
        return self.toString()
