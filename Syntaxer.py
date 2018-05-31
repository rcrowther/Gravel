import sys
from trees.Trees import *
from Position import Position
from Tokens import *

class Syntaxer:
    '''
    '''
    def __init__(self, source, reporter):
        self.source = source
        self.reporter = reporter
        self.it = source.tokenIterator(reporter)
        self.tok = None
        self.ast = Lambda()
        # start me up
        self.root()
        print(self.ast.toString())
   
   
    ## reporter helpers     
    def position(self):
        return Position(self.source.srcPath, self.it.lineCount, self.it.lineOffset)
        
    def error(self, msg):
        txt = self.it.textOf()
        if (txt):
            txtO = "\n                token text : '{0}'".format(txt)
        else:
            txtO = ''

        #pos = Position(self.it.source(), self.prevLine, self.prevOffset)
        self.reporter.error(msg + txtO, self.position())

        sys.exit("Error message")

    def expectedTokenError(self, ruleName, tok):
         self.error("In rule '{0}' expected '{1}' but found '{2}'".format(
             ruleName,
             tokenToString[tok],
             tokenToString[self.tok]
             ))

    ## iterators
    def textOf(self):
        return self.it.textOf()
        
    def _next(self):
        #self.prevLine = self.it.lineCount()
        #self.prevOffset = self.it.lineOffset()
        self.tok = self.it.__next__()


    ## rule helpers
    def isToken(self, token):
       return (token == self.tok)

    def getTokenOrError(self, ruleName,  token):
       if(self.tok != token):
           self.expectedTokenError(ruleName, token)
       t = self.textOf()
       self._next()
       return t

    def skipTokenOrError(self, ruleName,  token):
       if(self.tok != token):
           self.expectedTokenError(ruleName, token)
       self._next()
              
    def skipToken(self, token):
        r = False
        if (token != self.tok):
            r = True
            self._next()
        return r
            
    ## Rules

    def optionalKindAnnotation(self, tree):
        '''
        Succeed or error
        '''
        if (self.isToken(COLON)):
            self._next()
            kindStr = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            t.kindStr = kindStr
            # add contents
            #self.optionalGenericParams(k)
           
    def parameter(self, lst):
        '''
        Succeed or error
        '''
        # id
        markStr = self.getTokenOrError('Parameter', IDENTIFIER) 
        # delimit
        self.skipTokenOrError('Parameter', COLON)
        # type
        kindStr = self.getTokenOrError('Parameter', IDENTIFIER)            
        t = mkParameterDefinition(self.position(), markStr, kindStr)
        lst.append(t)
        return True

    def defineParameters(self, lst):
        '''
        Suceed or error
        '''
        self.skipTokenOrError('Define Parameters', LBRACKET)          
        while(not self.isToken(RBRACKET)):
            self.parameter(lst)
        self.skipTokenOrError('Define Parameters', RBRACKET)          
        return True

    def defineFunction(self, lst):
        '''
        'fnc' ~ Identifier ~ DefineParameters ~ ExplicitSeq
        Definitions attached to code blocks
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) and self.it.textOf() == 'fnc')
        if(commit):
             self._next()
             pos = self.position()
             
             # get mark
             markStr = self.getTokenOrError('Define Function', IDENTIFIER)     
             t = mkContextNode(pos, markStr)
             lst.append(t)
             #t.isDef = True
             # generic params?
             self.defineParameters(t.params)
             self
             #self.explicitSeq(t.body)
             lst.append(t)
             self.optionalKindAnnotation(t)
        return commit 
        
    def comment(self, lst):
        commit = self.isToken(COMMENT)
        if (commit):
            t = mkComment(self.position(), self.textOf())
            lst.append(t)
            self._next()
        return commit

    def multilineComment(self, lst):
        commit = self.isToken(MULTILINE_COMMENT)
        if (commit):
            t = mkComment(self.position(), self.textOf())
            lst.append(t)
            self._next()
        return commit
        
    def seqContents(self, lst):
        '''
        Used for body contents
        '''
        while(
            self.comment(lst)
            or self.multilineComment(lst)
            or self.defineFunction(lst)

            ):
            pass
        
        
    def root(self):
        try:
            # charge
            self._next()
            self.seqContents(self.ast.body)
            # if we don't except on StopIteration...
            self.error('Parsing did not complete')
        except StopIteration:
            # All ok
            pass
