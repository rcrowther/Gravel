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
        self.ast = mkLambda(NoPosition)
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

    #def option(self, token, action, b):
        #if (token == self.tok):
            #action(b)
            
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

    def optionallySkipToken(self, token):
        '''
        Optionally skip a token.
        If skips, returns True.
        ''' 
        r = (token == self.tok)
        if (r):
            self._next()
        return r
            
    ## Rules

    def optionalKindAnnotation(self, tree):
        '''
        Optionally match a Kind annotation.
        '''
        coloned = self.optionallySkipToken(COLON)
        if (coloned):
            tree.kindStr = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            # add contents
            #self.optionalGenericParams(k)
        return coloned
        
        
    def atomExpression(self, lst):
        '''
        (IntNum | FloatNum | String) ~ option(KindAnnotation)
        '''
        commit = self.isToken(INT_NUM) or self.isToken(FLOAT_NUM)  or self.isToken(STRING) or self.isToken(MULTILINE_STRING)
        if (commit):
            t = None
            if (self.isToken(INT_NUM)):
                t = mkIntegerAtom(self.position(), self.textOf())       
            if (self.isToken(FLOAT_NUM)):
                t = mkFloatAtom(self.position(), self.textOf())       
            if (self.isToken(STRING)):
                t = mkStringAtom(self.position(), self.textOf())       
            if (self.isToken(MULTILINE_STRING)):
                t = mkStringAtom(self.position(), self.textOf())       
            lst.append(t)
            self._next()
            self.optionalKindAnnotation(t)
        return commit
        
            
            
    def identifierOptionalKind(self, lst):
        '''
        Optional type declaration.
        Succeed or error
        '''
        # id
        markStr = self.getTokenOrError('Optional Kinded Identifier', IDENTIFIER) 
        t = mkParameterDefinition(self.position(), markStr)
        # delimit
        self.optionalKindAnnotation(t)
        return True
              
    def defineParameter(self, lst):
        '''
        Enforced type declaration.
        Succeed or error
        '''
        # id
        markStr = self.getTokenOrError('Define Parameter', IDENTIFIER) 
        # delimit
        self.skipTokenOrError('Define Parameter', COLON)
        # type
        t = mkParameterDefinition(self.position(), markStr)
        t.returnKind = self.getTokenOrError('Define Parameter', IDENTIFIER)
        lst.append(t)
        return True

    def defineParameters(self, lst):
        '''
        Enforced bracketing.
        Suceed or error
        '''
        self.skipTokenOrError('Define Parameters', LBRACKET)          
        while(not self.isToken(RBRACKET)):
            self.defineParameter(lst)
        self.skipTokenOrError('Define Parameters', RBRACKET)          
        return True


        

    def defineFunction(self, lst):
        '''
        'fnc' ~ Identifier /OperatorIdentifier~ DefineParameters  ~ Option(Kind) ~ ExplicitSeq
        Definitions attached to code blocks
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) and self.it.textOf() == 'fnc')
        if(commit):
             self._next()
             pos = self.position()
             
             # get mark
             #markStr = self.getTokenOrError('Define Function', IDENTIFIER)     
             ##
             # currently. can't be dried out
             if(self.tok != IDENTIFIER and self.tok != OPERATER):
                 #self.expectedTokenError(ruleName, token)
                 self.error("In rule '{}' expected '{}' or '{}' but found '{}'".format(
                     'Define Function',
                     tokenToString[IDENTIFIER],
                     tokenToString[OPERATER],
                     tokenToString[self.tok]
                     ))
             markStr = self.textOf()
             self._next()
             #
             t = mkContextNode(pos, markStr)
             lst.append(t)
             #t.isDef = True
             # generic params?
             self.defineParameters(t.params)
             self.optionalKindAnnotation(t)
             #! body
             #self.explicitSeq(t.body)
        return commit 

    def parametersForOperaterCall(self, lst):
        '''
        One parameter, optional bracketing.
        Succeed or error
        '''
        bracketted = self.optionallySkipToken(LBRACKET)
        if (not self.isToken(RBRACKET)):          
            self.identifierOptionalKind(lst)
        if (bracketted):
            self.skipTokenOrError('Operater Call Parameters', RBRACKET)          
        return True

    def parametersForCall(self, lst):
        '''
        Assured brackets
        Multiple parameters, optional kind.
        Succeed or error
        '''
        self.skipTokenOrError('Function Call Parameters', LBRACKET)          
        while(not self.isToken(RBRACKET)):
            self.identifierOptionalKind(lst)
        self.skipTokenOrError('Function Call Parameters', RBRACKET)          
        return True
                
    def callFunction(self, lst):
        '''
        Identifier ~ DefineParameters ~ Option(Kind) ~ ExplicitSeq
        Definitions attached to code blocks
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER))
        if(commit):       
             # get mark    
             t = mkContextNode(self.position(), self.textOf())
             lst.append(t)
             self._next()
             # generic params?
             self.parametersForCall(t.params)
             self.optionalKindAnnotation(t)            
        return commit 

    def operatorCall(self, lst):
        '''
        OperaterIdentifier ~ DefineParameter ~ Option(Kind) ~ ExplicitSeq
        Slightly, but strongly, different to functionCall.
        '''
        commit = (self.isToken(OPERATER))
        if(commit):       
             # get mark    
             t = mkContextNode(self.position(), self.textOf())
             lst.append(t)
             self._next()
             # generic params?
             self.parametersForOperaterCall(t.params)
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
            # must go after defines, which are more specialised in the
            # first token
            or self.callFunction(lst)
            or self.operatorCall(lst)
            or self.atomExpression(lst)
            ):
            pass
        
        
    def root(self):
        try:
            # charge
            self._next()
            self.seqContents(self.ast.body)
            # if we don't except on StopIteration...
            self.error('Parsing did not complete: lastToken: {},'.format(
                tokenToString[self.tok]
                ))
        except StopIteration:
            # All ok
            pass
