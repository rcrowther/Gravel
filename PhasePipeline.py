#from Phase import PhaseList
#from MarkTables import ExpressionMarkTable, KindMarkTable

# RunnerContext

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
                reporter.info("phase: '{0}'".format(p.name))
            p.run(compilationUnit, reporter, settings)
            if (reporter.hasErrors()):
                break

        if (reporter.hasErrors()):
            # detailed output of errors handled by idividual reporters
            print('errors...')
            print(reporter.summaryString())
             #sys.exit("Error message")
        else:
            print('done')


    def __repr__(self):
        return "<PhasePipeline phases={}>".format(self.phaseList)
