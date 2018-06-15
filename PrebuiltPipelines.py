from PhasePipeline import PhasePipeline
from reporters.ConsoleStreamReporter import ConsoleStreamReporter

from phases.Basic import PrintTokensPhase, SyntaxPhase, PrintTreePhase




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
        PrintTreePhase(),
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )
        
def Stock():
    phaseList = [
        SyntaxPhase(),
        #phases.TreePhases.RemoveCommentsPhase(self.reporter),
        ]
    reporter = ConsoleStreamReporter()
    return PhasePipeline( 
        phaseList,
        #codeGenContext, 
        )
