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
  


from trees.Visitors import RawPrint

#? could do this using a setting in the pipeline,
#? but this may be useful too
class PrintTreePhase(Phase):
    #? allow nothing after this phase
    def __init__(self):
        Phase.__init__(self,
            "parser tree print",
            "read source, make tree, print tree after parsing",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        src = compilationUnit.source
        parser = Syntaxer(src, reporter)
        RawPrint(parser.ast)
             
             
              
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

#class TreeTidy(Phase):
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
          
