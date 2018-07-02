from Phases import Phase
from Syntaxer import Syntaxer
from Tokens import tokenToString


#? could do this using a setting in the pipeline,
#? but this may be useful too
class PrintTokensPhase(Phase):
    #? allow nothing after this phase
    def __init__(self):
        Phase.__init__(self,
            "tokenPrint",
            "read source, print the tokens from lexing.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        src = compilationUnit.source
        #parser = Syntaxer(src, reporter)
        #compilationUnit.tree = parser.ast
        it = src.tokenIterator(reporter)
        for tok in it:
            print("[{},{}] '{}': '{}'".format(
            it.lineCount,
            it.lineOffset,
            tokenToString[tok], it.textOf()
            ))
  


class TreePrint(Phase):
    #? after Syntax so there is a tree
    def __init__(self):
        Phase.__init__(self,
            "Print the AST Tree",
            "Prints the tree. This print is of working intermediate code, and hard to read.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #src = compilationUnit.source
        #parser = Syntaxer(src, reporter)
        print(compilationUnit.tree)


        
from trees.Visitors import RawPrint

#? could do this using a setting in the pipeline,
#? but this may be useful too
class TreePrintDisplay(Phase):
    #? after Syntax so there is a tree
    def __init__(self):
        Phase.__init__(self,
            "Print the AST Tree",
            "Prints the tree. This is depth-ordered representation for easy reading.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        RawPrint(compilationUnit.tree)
             
             
              
class SyntaxPhase(Phase):
    def __init__(self):
        Phase.__init__(self,
            "parser",
            "read source files, make tree",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        src = compilationUnit.source
        parser = Syntaxer(src, reporter)
        compilationUnit.tree = parser.ast




from trees.Visitors import VisitorForBodies
from trees.Trees import CommentBase



class CommentStripVisitor(VisitorForBodies):
    def nodeWithBody(self, t):
        t.body = [child for child in t.body if (not(isinstance(child, CommentBase)))]



class StripComments(Phase):
    #? after Syntax so there is a tree (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Strip Comments",
            "Remove comments from the AST",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        if (not compilationUnit.tree):
            reporter.warning('phases.Basic.StripComments was unable to load a tree. Does a tree exist at for this phase?')
            return
        CommentStripVisitor(compilationUnit.tree)




from trees.Visitors import VisitorNodeDispatch
from trees.Trees import NameMixin
from MarkTable import ExpressionMarkTable


class NamesVerifyVisitor(VisitorNodeDispatch):
    def __init__(self, tree):
        self.table = ExpressionMarkTable()
        super().__init__(tree)
        
    def node(self, t):
        # check something is there
        if (isinstance(t, NameMixin)):
            print('named item: ' + str(t.parsedData))
            self.table.note(t.)
            define()
            
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
        NamesVerifyVisitor(compilationUnit.tree)

#x
class InfixChainingVisitor(VisitorForBodies):
    def nodeWithBody(self, t):
        # check something is there
        if(t.body):
            node = t.body[0]
            nxt = node._next
            # until we run out of data 
            while (nxt):
                if (isinstance(node, ContextCall) and isinstance(nxt, ContextCall) and isInfix(nxt.parsedData)):
                  node.isChained = True
                node = nxt
                nxt = node._next

                  # or isinstance(node, ContextCall) and )
        #t.body = [child for child in t.body if (not(isinstance(child, CommentBase)))]

            
class ChainsInfixMark(Phase):
    #? after Syntax so there is a tree (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Mark Infix Chains",
            "The parser will not mark infixed expressions, so this phase handles that.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        InfixChainingVisitor(compilationUnit.tree)
    #def __init__(self):
        #Phase.__init__(self,
            #"Tree tidy",
            #"Where possible, blend mono operations into values, and nest infix binops.",
            #True
            #)

    #def run(self, compilationUnit, reporter, settings):
        ## How to scan and rebuild at same time?
        #for t in compilationUnit.tree:
            ## merge +VE/-VE mono operations into values
            #if (
            #isinstance(t, MonoOpExpressionCall) and
            #(t.parsedData == '-' or t.parsedData == '+')
            #):
                ## nxt = t.nextInSeq()
                #nxt = t.next
                #if(
                #isinstance(nxt, IntegerNamelessData) or 
                #isinstance(nxt, FloatNamelessData)
                #):
                    #nxt.parsedData = t.parsedData + nxt.parsedData
                    ##? remove the node Mono node
                    #mo.remove()
        
            ## assemble chains
            #if (
            #isinstance(t, ContextCall)
            #):
              
                ## nxt = t.nextInSeq()
                #while(True):
                    #nxt = t.next
                    #if (
                        #(nxt == ContextCall) and isInfix(nxt.parsedData)
                        #):
                        #t.chain.append(nxt)
                        #nxt.remove()
                      

#class TypecheckTree(Phase):
    #def __init__(self):
        #Phase.__init__(self,
            #"Typecheck Tree",
            #"Generate a tree suitable for typecheckng.",
            #True
            #)

    #def run(self, compilationUnit, reporter, settings):
          ## Need to dive into binops
          ## need to work from inside namespaces to out
          
