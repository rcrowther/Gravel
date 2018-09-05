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
#! Needs to be far more complete
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
                #! both establish a new scope before more visiting
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


# Maybe build some types into the marks, now?
from KindTrees import KindNameTree
import itertools
from reporters.Message import Message


class MarkTableKindDetermine(Phase):
    #? after MarkTable creation
    def __init__(self):
        Phase.__init__(self,
            "Add kinds to a mark table.",
            "Use trees attached to Marks to determine and insert initial Kinds.",
            True
            )

    def parseKind(self, b, compilationUnit, reporter, tree):
        '''
        Parse a kind, then append to the builder.
        Skips if the tree has no kind annotation.
        Error if the kind will not parse. 
        '''
        parsedKind = tree.parsedKind
        # Don't bother if no annotation
        if (parsedKind):
            # test aginst the list of available kinds
            isKind = compilationUnit.kindTree.contains(parsedKind)
            
            # if unparsable, warning
            if (not isKind):        
                msg = 'Kind has no definition in current scope. Ignored. kindname:"{}"'.format(
                              parsedKind
                              )
                reporter.warning(
                    Message.withPos(msg, compilationUnit.source, tree.position)
                    )
            else:
                b.append(parsedKind)
        
    def resolveKindList(self, compilationUnit, reporter, mark, l):
        '''
        Resolve a list of annotaions by narrowing.
        Takes a generous approach,
        - starts with 'Any' and narrows.
        - ignores un-narrowable annotations
        '''
        kindAcc = 'Any'
        for kind in l:
            newKindAcc = compilationUnit.kindTree.narrow(kindAcc, kind)  
            if (newKindAcc):
                kindAcc = newKindAcc
            else:
                msg = 'Can not resolve kind annotation on a mark. mark:"{}" failed annotation:"{}"'.format(
                              mark.name,
                              kind
                              )
                reporter.warning(
                    #! hard to get pos?
                    #Message.withPos(msg, compilationUnit.source, tree.position)
                    Message.withSrc(msg, compilationUnit.source)
                    )
        print('kind allocated:{}'.format(kindAcc))
        return kindAcc
        
    def setKind(self, compilationUnit, reporter, mark):
        # concatenate trees which reference this mark
        trees = itertools.chain(mark.definitionTrees, mark.instanceTrees)
        # builder gathers all valid annotations
        b = []
        for tree in trees:
            self.parseKind(b, compilationUnit, reporter, tree)
        print('potential kinds for "{}"'.format(mark.name))
        print(', '.join(b))
        
        # right, can annotations be resolved?
        #! narrow, widen, etc.
        #? may need to split indo definition/instances/assignments etc. 
        # For variables and function returns, always narrow.
        mark.kind = self.resolveKindList(compilationUnit, reporter, mark, b)

        
        
    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        
        # init a kindtree
        compilationUnit.kindTree = KindNameTree()
        
        #iterate all marks
        marks = compilationUnit.markTable.toList()
        for m in marks:
            self.setKind(compilationUnit, reporter, m)
