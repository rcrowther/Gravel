from trees.Trees import BuiltinCall

from Keywords import KEY_EXPRESSIONS, KEY_KINDNAMES

#import collections

#? Should be fully path qualified, or seperate tables for each scope
#! also needed for Kinds

#! what does a mark table need?
#! to collect marks and verify one declaration
#! the tree position, for errors
#? Perhaps: type: verifying assignments and expressions in the source 
#? code are semantically correct. But not part of this at all?
#! Register cope 
#class DuplicateDefinitionException(Exception):
#    pass
    
class NameInfo():
    def __init__(self, name):
        self.name = name
        self.isDefined = False
        self.definitionTree = None
        self.trees = []
       
    def addDefinition(self, definitionTree):
        assert (self.isDefined == False), "Attrempted to define node, but already defined. definitionTree:{}".format(
            self.definitionTree
            )
        self.isDefined = True
        self.definitionTree = definitionTree

    def addReference(self, tree):
        self.trees.append(tree) 

    def __repr__(self):
        return '<NameInfo name:"{}", isDefined:{}, noteCount:{}>'.format(
            self.name,
            self.isDefined,
            len(self.trees)
            )

def mkNameInfoBuiltinDefinition(name):
    n = NameInfo(name)
    n.addDefinition(BuiltinCall()) 
    return n
    
def mkNameInfoDefinition(name, definitionTree):
    n = NameInfo(name)
    n.addDefinition(definitionTree) 
    return n

def mkNameInfo(name, tree):
    n = NameInfo(name)
    n.addReference(tree) 
    return n    
    
    
#! sure there may come to be a named tuple with defaults, but not yet...
#? could stash definition position, value, state, scope, and type
#! name = TreeInfo
#! all data here
#! generate ids for trees without them
#mark -> [treeInfo]
class NameTable():
    '''
    List of Names.
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
        self.underlying = {k: mkNameInfoBuiltinDefinition(k) for k in self.presets}
        
    def __call__(self, name):
        return self.underlying[name]
        
    def define(self, name, tree):
        '''
        Add a name to the tree, marking as a definition.
        The curious return logic is so support code can handle errors. 
        @return None or, if the node is already defined, the tree.
        '''
        n = self.underlying.get(name)
        if (n):
            if (n.isDefined):
                return tree
            n.addDefinition(tree)
        else:
            n = mkNameInfoDefinition(name, tree)
            self.underlying[name] = n
        return None
    
    def note(self, name, tree):
        '''
        Add a name to the tree.
        If the name exists, the tree is added to existing information.
        @return the node
        '''
        n = self.underlying.get(name)
        if (not n):
            n = mkNameInfo(name, tree)
            self.underlying[name] = n
        else:
            n.addReference(tree)
        return n
        
    def toString(self):
        return "NameTable({})".format(self.underlying)

    def __repr__(self):
        return self.toString()
        
        
#? By including these we avoid redefinitions.
#? but do we want to do that?
#? there may be up to 50 keywords? For expression and Kind? 

def ExpressionNameTable():
    return NameTable(KEY_EXPRESSIONS)

#? some code someplace builds the KindTTree
def KindNameTable():
    return NameTable(KEY_KINDNAMES)
