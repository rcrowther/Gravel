from PhasePipeline import PhasePipeline
from reporters.ConsoleStreamReporter import ConsoleStreamReporter

from phases.Basic import (
    PrintTokensPhase, 
    SyntaxPhase, 
    TreePrint, 
    TreePrintDisplay, 
    StripComments,
    #NamesValidate
    )

from phases.Checks import (
    MakeSymbolTable,
    )
    
#from phases.UnParsers import (
    #TreeChainsReverse
    #)
    





#? could do this using a setting in the pipeline,
#? but this may be useful too
def PrintTokens():
    phaseList = [
        PrintTokensPhase(),
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )
        
        
def PrintTree():
    phaseList = [
        SyntaxPhase(),
        StripComments(),
        TreePrintDisplay(),
        #TreePrint()
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )
        
def Stock():
    phaseList = [
        SyntaxPhase(),
        StripComments(),
        #TreeChainsReverse(),
        MakeSymbolTable(),
        TreePrintDisplay(),
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )

#from phases import Documentation
import phases.Documentation

def GDoc():
    phaseList = [
        SyntaxPhase(),
        phases.Documentation.GravelDoc(),
        ]
    return PhasePipeline( 
        phaseList 
        )


def GDocToTerminal():
    phaseList = [
        SyntaxPhase(),
        phases.Documentation.GDocToTerminal(),
        ]
    return PhasePipeline( 
        phaseList 
        )
