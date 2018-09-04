#from Phase import PhaseList
#from MarkTables import ExpressionMarkTable, KindMarkTable

# RunnerContext
#from reporters.Message import MessageNoPos
from reporters.Message import Message



class PhasePipeline():        
    def __init__(self, 
        phaseList
        ):
        #self.expSymbolTable = expressionActionSymbolTable
        #self.kindSymbolTable = kindSymbolTable
        self.phaseList = phaseList


    #def _requiredPhases(self):
    #    return [
    #        SyntaxPhase(self.reporter, self.settings),
       #phases.TreePhases.RemoveCommentsPhase(self.reporter),
    #    ]


    def run(self, 
        compilationUnit,
        reporter, 
        #codeGenContext, 
        settings = lambda: None
        ):
        settings.reportPhaseNames = True

        for p in self.phaseList:
            if (settings.reportPhaseNames):
                #reporter.info(MessageNoPos("phase: '{0}'".format(p.name), compilationUnit.source))
                reporter.info(Message.withSrc("phase: '{0}'".format(p.name), compilationUnit.source))
            p.run(compilationUnit, reporter, settings)
            if (reporter.hasErrors()):
                break

        if (reporter.hasErrors()):
            # detailed output of errors is handled by individual
            # reporters
            print('errors...')
            print(reporter.summaryString())
             #sys.exit("Error message")
        else:
            print('done')


    def __repr__(self):
        return "<PhasePipeline phases={}>".format(self.phaseList)
