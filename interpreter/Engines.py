from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Source import StringLineSource

from Tokens import tokenToString
from trees.Visitors import Visitor



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
class FileEngine(NonTraversingVisitor):
    #for AST?
    def multiLineComment(self, t):
        pass

    def singleLineComment(self, t):
        pass
                      
    def parameterDefinition(self, t):
        pass

    def namelessDataBase(self, t):
        if isinstance(t, IntegerNamelessData):
            return int(t.parsedData)
        if isinstance(t, FloatNamelessData):
            return float(t.parsedData)
        if isinstance(t, StringNamelessData):
            return t.parsedData
                        
    def monoOpExpressionCall(self, t):
        pass
        
    def dataDefine(self, t):
        pass
         
    def namelessBody(self, t):
        pass
        
    def contextDefine(self, t):
        pass
        
    def contextCall(self, t):
        pass 
                
    def conditionalCall(self, t):
        pass
        
    def conditionalContextCall(self, t):
        pass
        
    def namelessFunc(self, t):
        #print('twaddle')
        for e in t.body:
            self.visit(e) 


    def evaluate(self, filePath='test/syntax.gv'):
      
        # build an AST from the sources
        r = ConsoleStreamReporter()
        p = Stock()
        cu = CompilationUnit(FileSource(filePath))
        p.run(cu, r)
        
        # ok, now interpret the tree
        self.visit(cu.tree)
  
