from Phase import PhaseList
#from MarkTables import ExpressionMarkTable, KindMarkTable

# RunnerContext

class PhasePipeline():        
    def __init__(self, 
        reporter, 
        #codeGenContext, 
        #settings = None
        ):
        #self.expSymbolTable = expressionActionSymbolTable
        #self.kindSymbolTable = kindSymbolTable
        self.reporter = reporter
        self.phases = PhaseList(self._requiredPhases())
        self.settings.reportPhaseNames = True


    def _requiredPhases(self):
        return [
        ]


    def run(self, phaseList, compilationUnit):
       for p in phaseList:
         if (self.settings.reportPhaseNames):
            self.reporter.info("phase: '{0}'".format(p.name))
         p.run(compilationUnit)
         if (self.reporter.hasErrors()):
             break

       if (self.reporter.hasErrors()):
             print('errors...')
             print(self.reporter.summaryString())
             # print errors/extent of errors?
             #sys.exit("Error message")
       else:
             print('done')
