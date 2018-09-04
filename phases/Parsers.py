from Phases import Phase

'''
Parsers.
Build data structures from source material.
'''

from trees.Visitors import VisitorNodeDispatch
from trees.Trees import (NameMixin, ParameterDefinition, DataDefine, ContextDefine,
ContextCall
)
from MarkTable import ExpressionScopeTable


#! I am not happy. Python checks types, after a fashion, probably by 
#! dragging them round with an object. Scala checks types.
#? how do we know if we have found the right name if one name has 
#? different types? +=(:String) +=(:Int)
#? Also: Is it not faster to look for type in a scope type key, rather 
#? than scope first (a potentially massive search?) i.e. can we keep 
#? lists of methods registered to a type?
#! not a check anymore?
class MakeMarkTableVisitor(VisitorNodeDispatch):
    def __init__(self, tree, reporter):
        self.table = ExpressionScopeTable
        self.currentScope = self.table 
        self.reporter = reporter
        super().__init__(tree)
        
    def node(self, t):
        # check something is there
        #if (isinstance(t, NameMixin)):
        if (t.isMark):
            #if (t.isDefinition):
            #    self.table.add(t)
                
            if (
                #! establishes a new scope
                #isinstance(t, ParameterDefinition)
                isinstance(t, DataDefine)
                or isinstance(t, ContextDefine)
                # tests for undeclared calls
                #or isinstance(t, ContextCall)
                ):
                self.table.add(t)
                #self.currentScope = self.currentScope.newChildScope()
            print('named item: ' + str(t.parsedData))


            
class MakeMarkTable(Phase):
    #? after Syntax so there is a tree (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Build a mark table.",
            "Builds on the compilation unit. Only builds the base structure.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        v = MakeMarkTableVisitor(compilationUnit.tree, reporter)
        print(str(v.table))
        compilationUnit.markTable = v.table


# Maybe build some classes into the marks, now?
