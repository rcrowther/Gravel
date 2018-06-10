from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Source import StringLineSource

from Tokens import tokenToString


class Engine():

    def __init__(self):
        self.reporter = ConsoleStreamReporter()
        self.src = StringLineSource()
        self.symbolTable = {}
        
    def evaluate(self, line):
        print('evaluating...')
        it = self.src.tokenIterator(self.reporter, line)
        for tok in it:
            print("[{},{}] '{}' '{}'".format(
            it.lineCount,
            it.lineOffset,
            tokenToString[tok], it.textOf()
            ))
