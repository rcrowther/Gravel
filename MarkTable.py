from Mark import Mark


#? Should be fully path qualified, or seperate tables for each scope
#! also needed for Kinds


class DuplicateDefinitionException(Exception):
    pass
    

#! sure ther may come to bbe a named tuple with defaults, but not yet...
#? could stash definition position


class MarkTable():
    def __init__(self, presets={}):
        self.presets = presets
        self.underlying = {k:v for k, v in presets.items()}

    def __call__(self, k):
        return self.underlying[k]
        
    def define(self, name):
        '''
        @return True if added and defined, false otherwise (e.g. already defined)
        '''
        props = self.underlying.get(name)
        if (props):
            if (props.is_defined):
                return None
            else:
                props.is_defined = True
        else:
            props = Mark(name)
            props.is_defined = True
            self.underlying[name] = props
        return props
    
    def note(self, name):
        '''
        Silently add a value if not exists
        @return the new value
        '''
        props = self.underlying.get(name)
        if (not props):
            props = Mark(name)
            self.underlying[name] = props
        return props
        
    def toString(self):
        return "MarkTable({})".format(self.underlying)
