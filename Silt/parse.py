#!/usr/bin/env python3

import math
import operator as op

Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below) 
                          # is a mapping of {variable: value}



def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv, 
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: List(x), 
        'list?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),  
		'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()

def eval(x: Exp, env=global_env) -> Exp:
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):        # variable reference
        return env[x]
    elif isinstance(x, Number):      # constant number
        return x                
    elif x[0] == 'if':               # conditional
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif x[0] == 'define':           # definition
        (_, symbol, exp) = x
        env[symbol] = eval(exp, env)
    else:                            # procedure call
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)
        
def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens."
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()
    

def parse(program: str) -> Exp:
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')
    token = tokens.pop(0)
    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off ')'
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers become numbers; every other token is a symbol."
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)


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
    fit = FileIterator(filePath)
    trit = TrackingIterator(fit)
    #for cp in trit:
    #    print(cp)
    tkit = TokenIterator(filePath, trit)
    #for t in tkit:
    #    print(Tokens.tokenToString[t])
    #Syntaxer(tkit)
    Compiler(tkit)
    
if __name__ == "__main__":
    main()
