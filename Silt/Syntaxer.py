#from Lexer import Lexer
from Tokens import *
#from Position import Position
#from Message import messageWithPos
from tpl_types import typeNameSingularToType, typeNameContainerToType
from gio.SyntaxerBase import SyntaxerBase

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

        
class Syntaxer(SyntaxerBase):
    '''
    Generates a tree holding the structure of tokens.
    The sole purpose of this class is to extract and organise data from 
    the token stream. Unlike most other parsers it is not concerned with
    much with lexicon e.g. does the name exist? However, it converts
    tokens to an appropriate type i.e. numbers become numeric 
    constructs.  
    '''

       
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

    def findIdentifier(self, pos, sym):
        raise NotImplemented()
        
    def argExprOrSymbol(self, argsB):
        name = self.textOf()
        self._next() 
        if(self.optionallySkipToken(LBRACKET)):
            # if there is a func in a main func, constuct an AST
            # to hold data and represent the possible nesting
            args = self.args()
            #print('argExp')
            if (not(name in typeNameContainerToType)):
                arg = ArgFunc(name, args)
            else:
                arg = typeNameContainerToType[name](args)
            self.skipTokenOrError('argExprOrSymbol', RBRACKET)
            argsB.append(arg)
        else:
            #print('argSym')
            #print(name)
            # It was a symbol
            # We can lookup all symbols for code value. Protosymbols are
            # tokened as STRING in the tokenIterator.
            if (name in typeNameSingularToType):
                arg = typeNameSingularToType[name]
            else:
                arg = self.findIdentifier(self.position(), name)
            argsB.append(arg)
                
    def arg(self, argsB):
        r = False
        #print(tokenToString[self.tok])
        # We can work without errors. We know they parse 
        # as strings or numbers from the tokeniser
        isConst = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM) or 
            self.isToken(STRING) or 
            self.isToken(MULTILINE_STRING)
            )
        if (isConst):
            v = self.textOf()
            if (self.isToken(INT_NUM)):
                v = int(v)
            if (self.isToken(FLOAT_NUM)):
                v = float(v)
            argsB.append(v)
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
                     
    def punctuation(self):
        commit = (self.isToken(LINEFEED) or self.isToken(COMMA))
        if (commit):
            #name = self.textOf()
            self._next()
            #self.exprCB(name, args)
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
            or self.punctuation()
        ):
                pass
            #? what are we doing here at the end?
            #if (len(lst) > 1):
            #    lst[-1].prev = lst[-2]
        return True
        
    def root(self):
        self.seqContents()
