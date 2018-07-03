from TreeInfo import UndefinedTreeInfo

from Keywords import KEY_EXPRESSIONS, KEY_KINDS


#? Should be fully path qualified, or seperate tables for each scope
#! also needed for Kinds

#! what does a mark table need?
#! to collect marks and verify one declaration
#! the tree position, for errors
#? Perhaps: type: verifying assignments and expressions in the source 
#? code are semantically correct. But not part of this at all?
#! Register cope 
class DuplicateDefinitionException(Exception):
    pass
    

#! sure ther may come to be a named tuple with defaults, but not yet...
#? could stash definition position, value, state, scope, and type
#! name = TreeInfo
#! all data here
#! generate ids for trees without them
#mark -> [treeInfo]
class MarkTable():
    '''
    List of Marks
    presets dict of (name -> storageTyoe)
    '''
    def __init__(self, presets={}):
        self.presets = presets
        self.underlying = {}
        self.clear()

    def clear(self):
      '''
      Replace all entries with presets.
      '''
      self.underlying = {k:v for k, v in self.presets}
      
    def __call__(self, k):
        return self.underlying[k]
        
    def define(self, tree):
        '''
        @return True if added and defined, False otherwise (e.g. already defined)
        '''
        v = self.underlying.get(tree.parsedData)
        if (v):
            if (v.is_defined):
                return False
            else:
                v.is_defined = True
        else:
            e = TreeInfo(name)
            e.is_defined = True
            self.underlying[name] = e
        return True
    
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

#? By including these we avoid redefinitions.
#? but do we want to do that?
#? there may be up to 50 keywords? For expression and Kind? 

def ExpressionMarkTable():
    return MarkTable(KEY_EXPRESSIONS)

def KindMarkTable():
    return MarkTable(KEY_KINDS)
