from TokenIterator import TokenIterator
from Tokens import *
from Position import Position
from Message import messageWithPos

class ArgFunc:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return "ArgFunc(name:'{}',  args:{})".format(
            self.name,
            self.args
        )

class BooleanOp(ArgFunc):
    def __repr__(self):
        return "BooleanOp(name:'{}',  args:{})".format(
            self.name,
            self.args
        )    
        
class Syntaxer:
    '''
    Generates a tree holding the structure of tokens.
    The sole purpose of this class is to extract and organise data from 
    the token stream. Unlike most other parsers it is not concerned with
    names, ''symbols', or anything else. 
    '''
    def __init__(self, tokenIt):
        #self.code = code
        self.it = tokenIt
        self.tok = None

        # start me up
        self.root()

    ## report helpers     
    def position(self):
        return Position(self.it.src, self.it.lineCount, self.it.lineOffset)
        
    def error(self, msg):
        tokenTxt = self.it.textOf()
        msg = messageWithPos( self.position(), msg)
        if (tokenTxt):
            msg += " token text : '{0}'".format(tokenTxt)
        raise SyntaxError(msg)

    def expectedTokenError(self, ruleName, tok):
         self.error("In rule '{0}' expected token '{1}' but found '{2}'".format(
             ruleName,
             tokenToString[tok],
             tokenToString[self.tok]
             ))

    def expectedRuleError(self, currentRule, expectedRule):
         self.error("In rule '{0}' expected rule '{1}'. Current token: '{2}'".format(
             currentRule,
             expectedRule,
             tokenToString[self.tok]
             ))
                     
    def textOf(self):
        return self.it.textOf()
        
    def _next(self):
        #self.prevLine = self.it.lineCount()
        #self.prevOffset = self.it.lineOffset()
        self.tok = self.it.__next__()

    ## Token helpers
    def isToken(self, token):
       return (token == self.tok)

    def optionallySkipToken(self, token):
        '''
        Optionally skip a token.
        If skips, returns True.
        ''' 
        r = (token == self.tok)
        if (r):
            self._next()
        return r

    def skipTokenOrError(self, ruleName,  token):
       if(self.tok != token):
           self.expectedTokenError(ruleName, token)
       self._next()
       
    def commentCB(self, text):
        print('comment with "' + text)

    ## Rules
    def comment(self):
        commit = (self.isToken(MULTILINE_COMMENT) or self.isToken(COMMENT))
        if (commit):
            self.commentCB(self.textOf())
            self._next()
        return commit
        
    def optionalKindAnnotation(self):
        '''
        option(':' ~ Kind)
        Optionally match a Kind annotation.
        '''
        coloned = self.optionallySkipToken(COLON)
        if (coloned):
            print('kind with "' + self.textOf())
            #tree.kindStr = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            #tree.parsedKind = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            # add contents
            #self.optionalGenericParams(k)
        return coloned

    # def constantCB(self, text):
        # print('constant with "' + text)
                
    # def constant(self):
        # commit = (
            # self.isToken(INT_NUM) or 
            # self.isToken(FLOAT_NUM) or 
            # self.isToken(STRING) or 
            # self.isToken(MULTILINE_STRING)
            # )
        # if (commit):
            # self._next()
            # self.optionalKindAnnotation()
            # self.constantCB(self.textOf())
        # return commit
        
    # def exprCB(self, name, args):
        # print('expr with "' + name)
        
    # def symbolCB(self, name):
        # print('constant with "' + name)
        
    # No parens unless side-effects?
    # Side effects is everything to us
    # https://docs.scala-lang.org/style/naming-conventions.html
    # def exprOrSym(self):
        # commit = (self.isToken(IDENTIFIER))
        # if (commit):
            # name = self.textOf()
            # self._next()
            # #self.skipTokenOrError('expr', LBRACKET)
            # if(self.optionallySkipToken(LBRACKET)):
                # print('expr with "' + name)
                # L = self.seqContents()
                # self.skipTokenOrError('expr', RBRACKET)
                # self.exprCB(name, *L)
            # else:
                # print('symbol with "' + name)
                # self.symbolCB(name)
                # self.symbolCB(name)
        # return commit

    def argExprOrSymbol(self, argsB):
        name = self.textOf()
        self._next() 
        if(self.optionallySkipToken(LBRACKET)):
            # if there is a func in a main func, constuct an AST
            # to hold data and represent the possible nesting
            args = self.args()
            #print('argExp')
            arg = ArgFunc(name, args)
            self.skipTokenOrError('argExprOrSymbol', RBRACKET)
            argsB.append(arg)
        else:
            #print('argSym')
            # It was a symbol
            argsB.append(name)
                 
    def arg(self, argsB):
        r = False
        #print(tokenToString[self.tok])
        # We can get away with these. as strings. We know they parse 
        # as sytings or numbers from the tokeniser
        isConst = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM) or 
            self.isToken(STRING) or 
            self.isToken(MULTILINE_STRING)
            )
        if (isConst):
            argsB.append(self.textOf())
            self._next()
            r = True
        elif (self.isToken(IDENTIFIER)):
            #argsB.append(self.textOf())
            #self._next()           
            self.argExprOrSymbol(argsB) 
            #BooleanOp
            r = True
        return r

    def args(self):
        argsB = []
        while (self.arg(argsB)):
            pass
        return argsB
        
    def exprCB(self, name, args):
        print('expr {}({})'.format(name, args))
        
    def expr(self):
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            self._next()
            self.skipTokenOrError('expr', LBRACKET)
            args = self.args()
            self.skipTokenOrError('expr', RBRACKET)
            self.exprCB(name, args)
        return commit
                     
    def seqContents(self):
        '''
        Used for body contents.
        Allows definitions.
        '''
        while(
            #self.constant()
            #or self.comment()
            #or self.exprOrSym()
            self.expr()
            or self.comment()
        ):
                pass
            #? what are we doing here at the end?
            #if (len(lst) > 1):
            #    lst[-1].prev = lst[-2]
        return True
        
    def root(self):
        try:
            # charge
            self._next()
            self.seqContents()
            # if we don't get StopIteration...
            self.error('Parsing did not complete: lastToken: {},'.format(
                tokenToString[self.tok],                
                ))
        except StopIteration:
            # All ok
            print('parsed')
            pass
