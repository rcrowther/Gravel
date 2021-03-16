#from Lexer import Lexer
from Tokens import *
#from Position import Position
#from Message import messageWithPos
from tpl_types import (
    typeNameSingularToType, 
    typeNameContainerToType,
    typeNames,
)

from gio.SyntaxerBase import SyntaxerBase
from library.encodings import Codepoints


NamesBooleanComparisons  = [
    'gt', 'gte', 'lt', 'lte', 'eq', 'neq',
]
NamesBooleanCollators = [
    'and', 'or', 'xor', 
]
NamesBooleanFuncs = [
 'not',
]
NamesBooleanFuncs.extend(NamesBooleanComparisons)
NamesBooleanFuncs.extend(NamesBooleanCollators)


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

        
class FuncBoolean(ArgFunc):
    def __repr__(self):
        return "FuncBoolean(name:'{}',  args:{})".format(
            self.name,
            self.args
        )    

    def __str__(self):
        return "{}({})".format(
            self.name,
            self.args
        )        
        
class ArgList(list):
    pass
    
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

       


    ## Rules
    
    # Comments
    def commentCB(self, text):
        print('comment with "' + text)
        
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


    ## Some basics
    def symbol(self, argsB):
        '''
        Where it must be a symbol 
        ... and not the possibility of a function. It must also be 
        defended against builtin symbol names that need different casts, 
        such as boolean and type functions.
        '''
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            pos = self.toPosition()
            # cast as a symbol or a Protosymbol.
            if (ord(name[0]) == Codepoints.AT):
                if (len(name) < 2):
                    msg = '"@" codepoint stands alone in args ("@" opens a string to form a variable).' 
                    self.errorWithPos(pos, msg)
                arg = ProtoSymbol(name)
            else:
                # We can lookup all other symbols for code value. 
                # This is where we would check for builtin symbol names
                # such as boolean and type names, but this rule should 
                # be defended
                # So it's a dynamically created identifier
                arg = self.findIdentifier(pos, name)
            argsB.append(arg)
            self._next() 
        return commit
        
    def constant(self, argsB):
        commit = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM) or 
            self.isToken(STRING) or 
            self.isToken(MULTILINE_STRING)
            )
        if (commit):
            # We can work without errors. We know they parse 
            # as strings or numbers from the tokeniser
            v = self.textOf()
            
            # if not string, cast
            if (self.isToken(INT_NUM)):
                v = int(v)
            if (self.isToken(FLOAT_NUM)):
                v = float(v)
            argsB.append(v)
            self._next()
        return commit
            
    

    ## boolean func parsing
    #! no commas
    def funcBooleanNot(self, argsB):
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name == 'not')
        )    
        if (commit):
            self._next() 
            self.skipTokenOrError('funcBooleanNot', LBRACKET)
            # must contain two args
            # args can be Symbols or constants
            notArgB = []
            if (not(
                self.funcBooleanComparison(notArgB) 
                or self.funcBooleanCollation(notArgB) 
            )):
                self.expectedRuleError(
                    "funcBooleanNot", 
                    "funcBooleanComparison or funcBooleanCollation"
                )
            self.skipTokenOrError('funcBooleanNot', RBRACKET)
            # make type, add to args
            argsB.append(
                FuncBoolean(name, notArgB)
            )
        return commit
                
    def funcBooleanComparison(self, argsB):
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name in NamesBooleanComparisons)
        )
        if (commit):
            self._next() 
            self.skipTokenOrError('funcBooleanComparison', LBRACKET)
            # must contain two args
            # args can be Symbols or constants
            cmpArgB = []
            if(not(
                self.symbol(cmpArgB) or 
                self.constant(cmpArgB)
            )):
                self.expectedRuleError(
                    "funcBooleanComparison-arg1", 
                    "symbol or constant"
                )
            if(not(
                self.symbol(cmpArgB) or 
                self.constant(cmpArgB)
            )):
                self.expectedRuleError(
                    "funcBooleanComparison-arg2", 
                    "symbol or constant"
                )
            self.skipTokenOrError('funcBooleanComparison', RBRACKET)
            # make type, add to args
            argsB.append(
                FuncBoolean(name, cmpArgB)
            )
        return commit

    def funcBooleanCollation(self, argsB):
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name in NamesBooleanCollators)
        )       
        if (commit):
            self._next() 
            self.skipTokenOrError('funcBooleanCollation', LBRACKET)

            # oneOrMore args
            # args can be anythin in funcBoolean i.e. boolean funcs,
            # constants, symbols
            colArgB = []
            
            #? No commas
            self.oneOrMore(self.funcBoolean, colArgB, "funcBoolean")
            self.skipTokenOrError('funcBooleanCollation', RBRACKET)
            
            # make type, add to args
            argsB.append(
                FuncBoolean(name, colArgB)
            )
        return commit
            
                
    ## boolean func root
    ## We do not type the result exactly. 
    # The inner Types are all ArgFunc FuncBoolean.
    # This lack of sophistication (the API can unwrap again) disguises
    # a detailed parse that checks funcNames, and argument types and 
    # counts
    def funcBoolean(self, argsB):
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name in NamesBooleanFuncs)
        )
        if (commit):
            #self._next() 
            #self.skipTokenOrError('funcBoolean', LBRACKET)
            funcArgsB = []
            # should be one of these...
            if (not(
                self.funcBooleanComparison(argsB)
                or self.funcBooleanCollation(argsB)
                or self.funcBooleanNot(argsB)
            )):
                self.expectedRuleError(
                    "funcBoolean", 
                    "funcBooleanComparison, funcBooleanCollation or funcBooleanNot"
                )
            #self.skipTokenOrError('funcBoolean', RBRACKET)                 
            # make type, add to args
            #argsB.append(
            #    FuncBoolean(name, funcArgsB)
            #)
        return commit
        
    ## Types
    def typeArgContainer(self, argsB):
        # args are a fair old mess for container types
        #
        # ClutchLabeled: [label1, type1, label2, type2 ...]
        # Clutch [type1, type2 ...} 
        # ArrayLabeled [containedType, label1, label2...]
        # Array [containedType, size]
        # So we're nob being clever or OCD. If its a arg type thats
        # acceptable, it's in. But order or signature ignored.
        # For now.
        commit = (
                self.constant(argsB)
                or self.typeDeclaration(argsB)
        )
        return commit
            
            
    def typeDeclaration(self, argsB):
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name in typeNames)
        )
        if (commit):
            #self._next() 
            #self.skipTokenOrError('funcBoolean', LBRACKET)
            tpe = None
            if (name in typeNameSingularToType):
                #easy
                self._next() 
                tpe = typeNameSingularToType[name]
            elif (name in typeNameContainerToType):
                # they all are functions with args
                self._next() 
                self.skipTokenOrError('typeDeclaration', LBRACKET)
                tpeArgsB = []
                #? With this, can't skp commas
                self.oneOrMore(self.typeArgContainer, tpeArgsB, "typeArgContainer")
                self.skipTokenOrError('typeDeclaration', RBRACKET)                 
                tpe = typeNameContainerToType[name](tpeArgsB)
            argsB.append(
                tpe
            )
        return commit

                    
    ## General args
    def findIdentifier(self, pos, sym):
        raise NotImplemented()
        
        

    ## general args
    # def argExprOrSymbol(self, argsB):
        # name = self.textOf()        
        # pos = self.toPosition()
        # self._next()             
        # if(self.optionallySkipToken(LBRACKET)):
            # #? If there is a func in a line-level func, it is either a
            # # Boolean op or a datatype 
            # # Constuct an AST to hold data and represent the possible 
            # # nesting
            # # Or a specialism to catch boolops and datatypes?
            # args = self.args()
            # #print('argExp')
            # # This makes typenames
            # #if (name in typeNameContainerToType):
            # #    arg = typeNameContainerToType[name](args)
            # # This makes booleans
            # #elif (name in NamesBooleanFunc):
            # #    arg = funcBooleanRoot[name](args) 
                # #arg = FuncBoolean(name, args)
            # #else:
                # #! this is currently an error,.
                # # functions as args can only be condition or data types
                # #temp: make ArgFunc
                # #arg = ArgFunc(name, args)
            # self.error('Only datatypes and booleans allowed as funcs ')
            # self.skipTokenOrError('argExprOrSymbol', RBRACKET)
            # argsB.append(arg)
        # else:
            # #print('argSym:')
            # #print(name)
            # #print(str(ord(name[0]) == Codepoints.AT))
            # # The arg is a standalone identifier. That's a symbol
            # # or a Protosymbol. Type it as that.
            # if (ord(name[0]) == Codepoints.AT):
                # if (len(name) < 2):
                    # msg = '"@" codepoint stands alone in func args ("@" opens a string to form a variable).' 
                    # self.errorWithPos(pos, msg)
                # arg = ProtoSymbol(name)
            # else:
                # # We can lookup all other symbols for code value. 
                # # first, check against singular typenames
                # if (name in typeNameSingularToType):
                    # arg = typeNameSingularToType[name]
                # else:
                    # # otherwise it's a dynamically created identifier
                    # arg = self.findIdentifier(pos, name)
            # argsB.append(arg)

    def argList(self, argsB):
        # only accepts strings, for now
        commit = self.isToken(LBRACKET)
        if (commit):
            self._next() 
            argList = ArgList()
            while (True):
                if(self.isToken(STRING)):
                    argList.append(self.textOf())
                    self._next()
                else:
                    break
            self.skipTokenOrError('argList', RBRACKET)
            argsB.append(argList)
        return commit                    
                            
    #! I'd need to tokenise for double brackets.
    # because we cant peek. Gnnnaaarr!
    def path(self, argsB):
        commit = self.isToken(LSQUARE)
        if (commit):
            # over the opening bracket
            self._next() 
            path = Path()
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
        return commit
        
        
    def arg(self, argsB):
        r = False
        
        #NB all args converted to datatypess
        if (
            self.constant(argsB)
            
            # Both test identifier names also
            or self.funcBoolean(argsB)
            or self.typeDeclaration(argsB)
            
            # No expressions allowed nested,
            # ater booleans and funcs, so identifiers must be a symbol
            or self.symbol(argsB)
            or self.argList(argsB)
            or self.path(argsB)
        ):
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
        #? But not types or booleanFuncs
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
