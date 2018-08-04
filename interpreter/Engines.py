from gio.Sources import StringSource
from Tokens import tokenToString
from trees.Visitors import Visitor
import Keywords

from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from reporters.Message import MessageNoPos



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
from gio.Sources import FileSource
from CompilationUnit import CompilationUnit
from trees.Visitors import NonTraversingVisitor
from trees.Trees import *


#! incomplete, will we use the typechecked tree?
#! needs data storage
class FileEngine(NonTraversingVisitor):
  
    def __init__(self):
        #! needs to be scoped
        self.dataStash = {}
        #! why use the stash, and not return? Clean code?
        self.returnStash = None
        
    def _evaluateBody(self, body):
        for e in body:
            # the last return is interesting,
            #! as are any 'returns'
            self.visit(e)

    def _evaluateParams(self, params):
        b = []
        for e in params:
            self.visit(e)
            b.append(self.returnStash)
        self.returnStash = b


                  
    #for AST?
    def multiLineComment(self, t):
        pass

    def singleLineComment(self, t):
        pass
                      
    def parameterDefinition(self, t):
        pass

    def namelessDataBase(self, t):
        #print('...namelessDataBase: ' + str(t))
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
         
    def namelessBody(self, t):
        self._evaluateBody(t.body)
        
    def contextDefine(self, t):
        pass
        
    def contextCall(self, t):
        #! evaluate params
        #! pump into function
        # Note that signatures should have been checked
        if(t.parsedData in Keywords.INFIX):
            #print('paramList: ' + str(t.parsedData))
            #print('paramList: ' + str(t.params))
            self._evaluateParams(t.params)
            #print('eval paramList: ' + str(self.returnStash))
            if (t.parsedData == '+'):
                self.returnStash = self.returnStash[0] + self.returnStash[1]
            if (t.parsedData == '-'):
                self.returnStash = self.returnStash[0] - self.returnStash[1]
            if (t.parsedData == '*'):
                self.returnStash = self.returnStash[0] * self.returnStash[1]
            if (t.parsedData == '%'):
                self.returnStash = self.returnStash[0] / self.returnStash[1]
            print(t.position.toPositionString() + ' binop count: ' + str(self.returnStash))
        #pass 
                
    def conditionalCall(self, t):
        pass
        
    def conditionalContextCall(self, t):
        pass
        
    def namelessFunc(self, t):
        self._evaluateBody(t.body)



    def evaluate(self, filePath='test/syntax.gv'):      
        r = ConsoleStreamReporter()

        # build an AST from the sources
        cu = CompilationUnit(FileSource(filePath))
        p = Stock()
        p.run(cu, r)
        
        if (r.hasErrors()):
            r.info(MessageNoPos('Parse Errors: interpretation not attempted', cu.source))
        else:
            # ok, now interpret the tree
            #? does the interpreter require the reporter, also?
            self.visit(cu.tree)
        msg = MessageNoPos('interpreter dataStash:', cu.source)
        msg.details.append( str(self.dataStash)  )
        r.info(msg)
