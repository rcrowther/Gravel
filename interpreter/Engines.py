from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Source import StringLineSource

from Tokens import tokenToString
from Visitors import Visitor




class Engine(Visitor):

    def __init__(self):
        self.reporter = ConsoleStreamReporter()
        self.src = StringLineSource()
        self.symbolTable = {}
        self.curr = 0
        
        
    def seq(self, t):
        e = None
        for e in t.children:
            self.dispatch(e)
        return e
            
    def operaterCall(self, t):
        if (t.name == '+'):
            return self.curr + self.dispatch(t.params[0])
        elif (t.name == '-'):
            return self.curr - self.dispatch(t.params[0])
        elif (t.name == '*'):
            return self.curr * self.dispatch(t.params[0])
        elif (t.name == '/'):
            return self.curr / self.dispatch(t.params[0])

    def unaryOp(self, t):
        op = t.name
        if (op == '+'):
            return + self.dispatch(t.params[0])
        elif op == '-'):
            return - self.dispatch(t.params[0])
            
            
    #! how/where to convert to value
    def namelessData(self, t):
        t.parsedData
        return 
        
        
    def evaluate(self, line):
        print('evaluating...')
        it = self.src.tokenIterator(self.reporter, line)
        for tok in it:
            print("[{},{}] '{}' '{}'".format(
            it.lineCount,
            it.lineOffset,
            tokenToString[tok], it.textOf()
            ))
        tree = ???
        tree.dispatch()
