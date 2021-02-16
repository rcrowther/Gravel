#!/usr/bin/env python3



# class Syntaxer():
    # def __init__(self, source, reporter):
        # self.it = mkTokenIterator(source, reporter)
        # self.tok = None

# def exp(self)
    # self.getOrFail('(')

    # self.getOrFail(')')
    # if (self.getOptional(codeBlockStart)):
        # expList()
        # self.getOrFail(codeBlockEnd)

# def expList(self)
    # while (self.exp):
        # pass
    
        
# def tokens(self, code):
    # tokens = code.replace('(', ' ( ').replace(')', ' ) ').split()
    # for tok in tokens:
        # if (tok === '(')
        # if (tok === ')')
        
        # if (tok.startswith('begin')):
        # if (tok.startswith('end')):
        # else:
            # tok

import sys
from Codepoints import *
import Tokens
from TokenIterator import TokenIterator
from Syntaxer import Syntaxer
from Compiler import Compiler
from BuilderAPI import BuilderAPI64
from tpl_style import *
import nasmFrames

#! unaltered
class TrackingIterator():
    '''
    Iterate codepoints keeping track of positions.
    
    LineCount starts from 1.
    lineOffset starts from 0 (col:...).
    lineOffset and lineCount are designed to give the point
    after next().
    
    Passesa all source characters, including lineends and whitespace, 
    unmodified.
    '''

    def __init__(self, codepointIt):
        self.it = codepointIt
        self._lineOffset = 0
        self._lineCount = 1
        self.lineOffset = 0
        self.lineCount = 1
                    
    def __iter__(self):
        return self
        
    def __next__(self):
        c = self.it.__next__()
        self.lineCount  = self._lineCount
        self.lineOffset = self._lineOffset
        self._lineOffset += 1
        if (c == LINE_FEED):
            self._lineCount += 1
            self._lineOffset = 0
        return c
        
#! unaltered
class FileIterator():
    #NB Changes the syntax from read-a-char
    # to __next__-for-a-char iteration
    def __init__(self, path):
        self.path = path
        self.fd = open(path, 'r')
        line = self.fd
        
    def __next__(self):
        c = None
        c = self.fd.read(1)
        if (not c):
            self.fd.close()
            raise StopIteration
        return ord(c)
        
    def __iter__(self):
        return self
        
def main():
    args = sys.argv
    if (len(args) < 2):
        print('need filepath!')
        exit(1)
    # with open(args[1], "r") as f:
        # code = f.readlines()
        # print(code)
    filePath = args[1]
    
    # Make specific file iterator then track
    fit = FileIterator(filePath)
    trit = TrackingIterator(fit)
    #for cp in trit:
    #    print(cp)
    
    # make token iterator
    tkit = TokenIterator(filePath, trit)
    #for t in tkit:
    #    print(Tokens.tokenToString[t])
    #Syntaxer(tkit)
    builderAPI = BuilderAPI64()

    # parse input and build
    c = Compiler(tkit, builderAPI)
    finishedBuilder = c.result()

    # style
    #print(str(finishedBuilder._code))
    o = builderPrint(nasmFrames.frame64, finishedBuilder, baseStyle)
    
    # output
    #print(o)
    with open('build/out.asm', 'w') as f:
        f.write(o)
        
if __name__ == "__main__":
    main()
