from Phases import Phase

from trees.Visitors import Visitor
from trees.Trees import *



class DocumentationVisitor(Visitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def namelessData(self, t):
        # only on the module?
        pass

    def renderParameterDefinitions(self, t):
        for p in t.params:
            self.b.append(p.parsedData)
            self.b.append(': ')
            self.b.append('???')
            self.b.append(' ')
            
    def dataDefine(self, t):
        #prev = t.prevSibling()
        #if(isinstance(prev, Comment):
        #    b.append(prev.parsedData.strip())
        name = t.parsedData
        self.b.append('val ')
        self.b.append(name)
        self.b.append('{')
        #self.renderParameterDefinitions(t)
        self.b.append('}\n')
                    
    def contextDefine(self, t):
        #prev = t.prevSibling()
        #if(isinstance(prev, Comment):
        #    b.append(prev.parsedData.strip())
        #print(str(t))        
        name = t.parsedData
        self.b.append('fnc ')
        self.b.append(name)
        self.b.append('(')
        self.renderParameterDefinitions(t)
        self.b.append(')\n')

    
          
#? could do this using a setting in the pipeline,
#? but this may be useful too
class GravelDoc(Phase):
    #? after Syntax (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Assemble Graveldoc",
            "Take the AST, remove data other than defines and prefix multiline comments",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        tree = compilationUnit.tree
        v = DocumentationVisitor(tree)
        print(''.join(v.b))
