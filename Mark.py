



class Mark:
    '''
    Identifier for a program construct.
    This could be a variable, function, namespace etc.
    Due to allowing one_name/many_types and many_anmes/one_type entities
    The code must provide unique keys (this isometimes called a Symbol, 
    but usage of the word is often wandering, or includes opportunistic 
    information such as documentation).
    Currently, this would not be used for typechecking, only name 
    resolution?
     
    '''
    ??? How does Scala do the key/hash?
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        
    def key(self):
        return ???
        
    def toString(self):
        return "<Mark name:{} kind:{}>".format(
            self.name,
            self.kind
            )
            
    def __repl__(self):
        return self.toString()
