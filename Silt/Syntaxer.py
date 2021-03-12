#from Lexer import Lexer
from Tokens import *
#from Position import Position
#from Message import messageWithPos
from tpl_types import typeNameSingularToType, typeNameContainerToType
from gio.SyntaxerBase import SyntaxerBase
from library.encodings import Codepoints


## Custom argument Types
class ArgFunc:
    def __init__(self, name, args):
        self.name = name
        self.args = args
        
    def __repr__(self):
        return "ArgFunc(name:'{}',  args:{})".format(
            self.name,
            self.args
        )

class Path(list):
    pass


class ProtoSymbol():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ProtoSymbol(name:'{}')".format(
            self.name,
        )
        
    def toString(self):
        return self.name[1:]
        
        
        
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
    tokenToString = tokenToString

       
    def commentCB(self, text):
        print('comment with "' + text)

    ## Rules
    def comment(self):
        commit = (self.isToken(MULTILINE_COMMENT) or self.isToken(COMMENT))
        if (commit):
            self.commentCB(self.textOf())
            self._next()
        return commit
        
    #?
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


    def findIdentifier(self, pos, sym):
        raise NotImplemented()
        
    def argExprOrSymbol(self, argsB):
        name = self.textOf()
        pos = self.toPosition()
        self._next() 
        if(self.optionallySkipToken(LBRACKET)):
            #? If there is a func in a line-level func, it is either a
            # Boolean op or a datatype 
            # Constuct an AST to hold data and represent the possible 
            # nesting
            # Or a specialism to catch boolops and datatypes?
            args = self.args()
            #print('argExp')
            # This makes typenames
            if (name in typeNameContainerToType):
                arg = typeNameContainerToType[name](args)
            # This makes conditions
            #elif (name in ConditionalTypeNames):
            #    arg = typeNameConditionToType[name](args)                
            else:
                #! this is currently an error, 
                # functions as args can only be condition or data types
                arg = ArgFunc(name, args)
            self.skipTokenOrError('argExprOrSymbol', RBRACKET)
            argsB.append(arg)
        else:
            #print('argSym:')
            #print(name)
            #print(str(ord(name[0]) == Codepoints.AT))
            # It was a standalone identifier as an arg. That's a symbol
            # is it a Protosymbol? Type it as that.
            if (ord(name[0]) == Codepoints.AT):
                if (len(name) < 2):
                    msg = '"@" codepoint stands alone in func args ("@" opens a string to form a variable).' 
                    self.errorWithPos(pos, msg)
                arg = ProtoSymbol(name)
            else:
                # We can lookup all other symbols for code value. 
                # first, check against singular typenames
                if (name in typeNameSingularToType):
                    arg = typeNameSingularToType[name]
                else:
                    # otherwise it's a dynamically created identifier
                    arg = self.findIdentifier(pos, name)
            argsB.append(arg)


    def pathFixed(self, argsB):
        path = Path()
        # over the opening bracket
        self._next() 
        while (True):
            if(self.isToken(STRING)):
                path.append(self.textOf())
                self._next() 
            elif(self.isToken(INT_NUM)):
                path.append(int(self.textOf()))
                self._next() 
            else:
                break
        self.skipTokenOrError('path', RSQUARE)
        argsB.append(path)
                        
    def arg(self, argsB):
        r = False
        #print(tokenToString[self.tok])
        # Args need to be converted to datatypes
        isConst = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM) or 
            self.isToken(STRING) or 
            self.isToken(MULTILINE_STRING)
            )
        if (isConst):
            # We can work without errors. We know they parse 
            # as strings or numbers from the tokeniser
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
        elif (self.isToken(LSQUARE)):
            self.pathFixed(argsB) 
            r = True
            
        # skip trailing commas
        self.skipToken(COMMA)
        return r


    def args(self):
        argsB = []
        while (self.arg(argsB)):
            pass
        return argsB
        
    def exprCB(self, pos, name, args):
        print('expr {}({})'.format(name, args))
        
    def expr(self):
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            
            # stash the position at the start of the expression
            pos = self.toPosition()
            #print(str(pos))
            self._next()
            self.skipTokenOrError('expr', LBRACKET)
            posArgs = self.toPosition()
            args = self.args()
            
            # Can't use skipTokenOrError(). That will advance the
            # iterator. If this is the last expression, with no 
            # following whitespace (or newline) that would throw 
            # StopIteration before callback on the parsed function. 
            # So we test the rbracket is there, then callback on the 
            # function...
            #print('{}({})'.format(name, args))
            if (self.isToken(RBRACKET)):
                self.exprCB(pos, posArgs, name, args)
                # ..if EOF, then that is thown here
                self._next()
            else:
                self.expectedTokenError('expr', RBRACKET)
                
            # Now move on and check for a linefeed.
            self.skipTokenOrError('expr',  LINEFEED)
        return commit
                     
    def punctuation_ignored(self):
        # commit = (self.isToken(LINEFEED))
        # if (commit):
            # self._next()
        #return commit
        while(self.skipToken(LINEFEED)):
            pass
        return True
                
    def seqContents(self):
        '''
        Used for body contents.
        Allows definitions.
        '''
        while(
            self.expr()
            or self.comment()
            or self.punctuation_ignored()
        ):
            pass
        return True
        
    def root(self):
        self.seqContents()
