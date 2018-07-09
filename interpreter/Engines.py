from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Source import StringLineSource

from Tokens import tokenToString
from trees.Visitors import Visitor
import Keywords



#class Engine(Visitor):

    #def __init__(self):
        #self.reporter = ConsoleStreamReporter()
        #self.src = StringLineSource()
        #self.symbolTable = {}
        #self.curr = 0
        
        
    #def seq(self, t):
        #e = None
        #for e in t.children:
            #self.dispatch(e)
        #return e
            
    #def operaterCall(self, t):
        #if (t.name == '+'):
            #return self.curr + self.dispatch(t.params[0])
        #elif (t.name == '-'):
            #return self.curr - self.dispatch(t.params[0])
        #elif (t.name == '*'):
            #return self.curr * self.dispatch(t.params[0])
        #elif (t.name == '/'):
            #return self.curr / self.dispatch(t.params[0])

    #def unaryOp(self, t):
        #op = t.name
        #if (op == '+'):
            #return + self.dispatch(t.params[0])
        #elif op == '-'):
            #return - self.dispatch(t.params[0])
            
            
    ##! how/where to convert to value
    #def namelessData(self, t):
        #t.parsedData
        #return 
        
        
    #def evaluate(self, line):
        #print('evaluating...')
        #it = self.src.tokenIterator(self.reporter, line)
        #for tok in it:
            #print("[{},{}] '{}' '{}'".format(
            #it.lineCount,
            #it.lineOffset,
            #tokenToString[tok], it.textOf()
            #))
        #tree = ???
        #tree.dispatch()


from PrebuiltPipelines import Stock
from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Source import FileSource
from CompilationUnit import CompilationUnit
from trees.Visitors import NonTraversingVisitor
from trees.Trees import *


#! incomplete, will we use the typechecked tree?
#! needs data storage
class FileEngine(NonTraversingVisitor):
    def __init__(self):
        #! needs to be scoped
        self.dataStash = {}
        self.returnStash = 22
        
    def _evaluateBody(self, body):
        for e in body:
            # the last return is interesting,
            #! as are any 'returns'
            self.visit(e)
        
    #for AST?
    def multiLineComment(self, t):
        pass

    def singleLineComment(self, t):
        pass
                      
    def parameterDefinition(self, t):
        pass

    def namelessDataBase(self, t):
        print('...namelessDataBase: ' + str(t))
        if isinstance(t, IntegerNamelessData):
            self.returnStash = int(t.parsedData)
        if isinstance(t, FloatNamelessData):
            self.returnStash = float(t.parsedData)
        if isinstance(t, StringNamelessData):
            self.returnStash = t.parsedData

    def monoOpExpressionCall(self, t):
        pass
        
    def dataDefine(self, t):
        self._evaluateBody(t.body)
        self.dataStash[t.parsedData] = self.returnStash 
        #pass
         
    def namelessBody(self, t):
        pass
        
    def contextDefine(self, t):
        pass
        
    def contextCall(self, t):
        if(t.parsedData in Keywords.INFIX):
            print('context call isChained: ' + str(t.isChained))
            #self.returnStash
            print('context call: ' + t.parsedData)
            if(t.isChained):
                print('ret val: ' + str(self.returnStash))
                print('parameters: ' + str(t.params))
                chainValue = self.returnStash
                self.visit(t.params[0])
                self.returnStash = chainValue + self.returnStash
                print('chainval: ' + str(self.returnStash))
        #elif(t.parsedData in Keywords.MONOP):
        else:
            #custom call

                
            
        
        #print('def count: ' + str(len(t.body)))
        
        #pass 
                
    def conditionalCall(self, t):
        pass
        
    def conditionalContextCall(self, t):
        pass
        
    def namelessFunc(self, t):
        print('twaddle')
        for e in t.body:
            self.visit(e) 


    def evaluate(self, filePath='test/syntax.gv'):
      
        # build an AST from the sources
        r = ConsoleStreamReporter()
        p = Stock()
        cu = CompilationUnit(FileSource(filePath))
        p.run(cu, r)
        
        if (r.hasErrors()):
            print('Parse Errors: interpretation not attempted')
        else:
            # ok, now interpret the tree
            self.visit(cu.tree)
  
        print('interpreter datashtash:\n' + str(self.dataStash))
