
class TypePathError(ValueError):
    '''
    An error in a typepath
    '''
    pass

class FuncMessage(Exception):
    '''
    A base for messages thrown from from executing a func
    '''
    pass
    
# class FuncError(FuncMessage):
    # '''
    # An error from executing a func
    # '''
    # pass
    
# class FuncWarning(FuncMessage):
    # '''
    # A warning from executing a func
    # '''
    # pass
    
# class FuncInfo(FuncMessage):
    # '''
    # An info from executing a func
    # '''
    # pass

class BuilderError(FuncMessage):
    '''
    An error from a builder.
    Vuilder errors do get thrown, but should never make their way to 
    the user. They should be caught and formed into an appropriate
    error message.
    '''
    pass
