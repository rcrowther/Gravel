from Phases import Phase


'''
Checks.
Test consistency of structures.
e.g. stated kinds are consistent.
'''


from trees.Visitors import VisitorNodeDispatch
from trees.Trees import (NameMixin, ParameterDefinition, DataDefine, ContextDefine)
#from MarkTable import ExpressionMarkTable
from NameTable import ExpressionNameTable


#! I am not happy. Python checks types, after a fashion, probably by 
#! dragging them round with an object. Scala checks types.
#? how do we know if we have found the right name if one name has 
#? different types? +=(:String) +=(:Int)
#? Also: Is it not faster to look for type in a scope type key, rather 
#? than scope first (a potentially massive search?) i.e. can we keep 
#? lists of methoids registered to a type?
class NamesVerifyVisitor(VisitorNodeDispatch):
    def __init__(self, tree, reporter):
        self.table = ExpressionNameTable()
        self.reporter = reporter
        super().__init__(tree)
        
    def node(self, t):
        # check something is there
        if (isinstance(t, NameMixin)):
            if (
                #! establishes a new scope
                #isinstance(t, ParameterDefinition)
                isinstance(t, DataDefine)
                or isinstance(t, ContextDefine)
            ):
                r = self.table.define(t.parsedData, t)
                if (r):
                   # oh dear, double definition
                   name = t.parsedData
                   nameNode = self.table(name)
                   msg = 'Name definition repeated. name:"{}" first declaration position:{}'.format(
                      name,
                      nameNode.definitionTree.position.toDisplayString()
                      )
                   self.reporter.error(msg, r.position)
                return
            print('named item: ' + str(t.parsedData))
            self.table.note(t.parsedData, t)

            
class NamesVerify(Phase):
    #? after Syntax so there is a tree (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Check names have a definition.",
            "This will also build, on the compilation unit, a name tree.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        NamesVerifyVisitor(compilationUnit.tree, reporter)
