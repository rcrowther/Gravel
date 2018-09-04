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


#?
globalPackage = Mark('GlobalPackage')
    
testMark = Mark('TestMark')
testMark2 = Mark('TestMark2')
