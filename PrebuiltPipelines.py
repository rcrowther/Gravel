from PhasePipeline import PhasePipeline
from reporters.ConsoleStreamReporter import ConsoleStreamReporter

from phases.Basic import (
    PrintTokensPhase, 
    SyntaxPhase, 
    TreePrint, 
    TreePrintDisplay, 
    StripComments,
    NamesVerify,
    #NamesValidate
    )

from phases.ToLinear import (
    TreeChainsReverse
    )
    
from phases.Documentation import GravelDoc




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
        NamesVerify(),
        TreePrintDisplay(),
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )

def Documentation():
    phaseList = [
        SyntaxPhase(),
        GravelDoc(),
        ]
    return PhasePipeline( 
        phaseList 
        )
