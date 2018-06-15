from Phases import Phase
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
