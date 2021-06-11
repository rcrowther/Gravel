#from Lexer import Lexer
from Tokens import *
#from Position import Position
#from Message import messageWithPos
from ci_the import *

from tpl_types import (
    typeNameSingularToType, 
    typeNameContainerToType,
    typeNames,
)

from gio.SyntaxerBase import SyntaxerBase
from library.encodings import Codepoints

from collections import namedtuple
Arg = namedtuple('Arg',['position','value'])

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
    
class AggregateVals(list):
    pass   

#import collections
#AggregateKV = collections.namedtuple('AggregateKV', ['label', 'value'])

class KeyValue():
    def __repr__(self):
        return f"KeyValue(key:{self.key}. value:{self.value})"
        
    def __str__(self):
        return f"[{self.key} ~> {self.value}]"
        

class ProtoSymbol():
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "ProtoSymbol(name:'{}')".format(
            self.name,
        )
        
    def toString(self):
        return self.name[1:]
        
    def __str__(self):
        return self.name
        

        
        
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

    def intNum(self, argsB):
        '''
        An integer numeric. 
        It is cast as an integer.
        It is not wrapped as an Arg.
        '''
        commit = self.isToken(INT_NUM)
        if (commit):
            # We can work without errors. We know they parse 
            # as numbers from the tokeniser
            pos = self.toPosition()
            v = self.textOf()
            t = TheInt(pos, int(v))
            argsB.append(t)
            #argsB.append(int(v))
            self._next()
        return commit  
        
    def number(self, argsB):
        '''
        A numeric, float or int. 
        '''
        commit = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM)
            )
        if (commit):
            # We can work without errors. We know they parse 
            # as strings or numbers from the tokeniser
            pos = self.toPosition()
            v = self.textOf()
            
            # if not string, cast
            if (self.isToken(INT_NUM)):
                #v = int(v)
                v = TheInt(pos, int(v))
            if (self.isToken(FLOAT_NUM)):
                #v = float(v)
                v = TheFloat(pos, float(v))
            argsB.append(v)
            #argsB.append(Arg(self.toPosition(), v))
            self._next()
        return commit

    def string(self, argsB):
        '''
        A string (not multiline)
        '''
        commit = (
            self.isToken(STRING)
            )
        if (commit):
            # We can work without errors. We know they parse 
            # as strings or numbers from the tokeniser
            v = self.textOf()
            pos = self.toPosition()
            t = TheString(pos, v)
            argsB.append(t)
            self._next()
        return commit
                
    def constant(self, argsB):
        '''
        A numeric or string
        '''
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
            
            pos = self.toPosition()
            # if not string, cast
            if (self.isToken(INT_NUM)):
                #v = int(v)
                t = TheInt(pos, int(v))
            elif (self.isToken(FLOAT_NUM)):
                #v = float(v)
                t = TheFloat(pos, float(v))
            elif (
                self.isToken(STRING) or 
                self.isToken(MULTILINE_STRING)
                ):
                t = TheString(pos, v)
            #argsB.append(Arg(self.toPosition(), v))
            argsB.append(t)
            self._next()
        return commit

  
                    
    # def intNumArg(self, argsB):
        # '''
        # An intNum. 
        # It is cast as an integer.
        # It is wrapped as an Arg.
        # '''
        # commit = self.isToken(INT_NUM)
        # if (commit):
            # # We can work without errors. We know they parse 
            # # as numbers from the tokeniser
            # v = self.textOf()
            # argsB.append(Arg(self.toPosition(), int(v)))
            # self._next()
        # return commit    

    #i though both identifer lexemes,
    # type labels can only appear in type constructors
    # or path acesses, so the Syntaxer can split then from 
    # symbol labels.
    def offsetSymbol(self, argsB):
        '''
        An identifier. 
        It is cast as a string.
        It is not wrapped as an Arg.
        '''
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            pos = self.toPosition()
            # cast as a symbol or a Protosymbol.
            # if (ord(name[0]) == Codepoints.AT):
                # msg = '"@" codepoint used  when label expected.' 
                # self.errorWithPos(pos, msg)
            # else:
                # We don't cast a label as anything more special than a 
                # string
            
            t = TheOffsetSymbol(pos, v)
            #argsB.append(name)
            argsB.append(t)
            self._next() 
        return commit
        
    # def labelArg(self, argsB):
        # '''
        # An identifier that is not a protosymbol.
        # The value is cast as a string.
        # It is wrapped as an Arg.
        # '''
        # commit = (self.isToken(IDENTIFIER))
        # if (commit):
            # name = self.textOf()
            # pos = self.toPosition()
            # # cast as a symbol or a Protosymbol.
            # # if (ord(name[0]) == Codepoints.AT):
                # # msg = '"@" codepoint used  when label expected.' 
                # # self.errorWithPos(pos, msg)
            # # else:
                # # We don't cast a label as anything more special than a 
                # # string
            # argsB.append(Arg(pos, name))
            # self._next() 
        # return commit
                
    #! symbolArgument
    def symbol(self, argsB):
        '''
        An identifier. 
        Contains extra protection
        It is cast as a ProtoSymbol or symbol,  depending on presence of
        ''@'.
        It is wrapped as an Arg.
        '''
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            pos = self.toPosition()
            # cast as a symbol or a Protosymbol.
            if (ord(name[0]) == Codepoints.AT):
                if (len(name) < 2):
                    msg = '"@" codepoint stands alone ("@" opens a string to form an symbol).' 
                    self.errorWithPos(pos, msg)
                #arg = ProtoSymbol(name)
                
                #i strip the ''@' here. The data is identified by the
                # The class 
                arg = TheProtoSymbol(pos, name[1:])
            else:
                # We can lookup all other symbols for code value. 
                # This is where we would check for builtin symbol names
                # such as boolean and type names, but this rule should 
                # be defended
                # So it's a dynamically created identifier
                #! but it doesn't need to look so wide? It can only be a const
                # or perhaps a custom definition?
                smb = self.symbolUsrFind(pos, name)
                # later
                arg = TheSymbol(pos, smb)
            argsB.append(arg)
            #argsB.append(arg)
            self._next() 
        return commit


                
    # def symbolArg(self, argsB):
        # '''
        # An identifier. 
        # Contains extra protection
        # It is cast as a ProtoSymbol or symbol,  depending on presence of
        # ''@'.
        # It is wrapped as an Arg.
        # '''
        # commit = (self.isToken(IDENTIFIER))
        # if (commit):
            # name = self.textOf()
            # pos = self.toPosition()
            # # cast as a symbol or a Protosymbol.
            # if (ord(name[0]) == Codepoints.AT):
                # if (len(name) < 2):
                    # msg = '"@" codepoint stands alone ("@" opens a string to form a variable).' 
                    # self.errorWithPos(pos, msg)
                # arg = ProtoSymbol(name)
            # else:
                # # We can lookup all other symbols for code value. 
                # # This is where we would check for builtin symbol names
                # # such as boolean and type names, but this rule should 
                # # be defended
                # # So it's a dynamically created identifier
                # #! but it doesn't need to look so wide? It can only be a const
                # # or perhaps a custom definition?
                # arg = self.symbolUsrFind(pos, name)
            # argsB.append(Arg(self.toPosition(), arg))
            # #argsB.append(arg)
            # self._next() 
        # return commit
        
                                
    ## boolean func parsing
    def _booleanNot(self):
        self._next() 
        self.skipTokenOrError('booleanComparison', LBRACKET)
        
        # gather args
        tpe = None
        argsNotB = []
        pos = self.toPosition()      

        # one arg
        # arg can be booleanfunc or boolean var
        if (not(
            #self._funcBoolean(argsNotB) or
            self.funcBoolean(argsNotB) or
            self.symbol(argsNotB)
        )):
            self.expectedRuleError(
                "fBoolean function or boolean var"
            )
            
        # finish
        self.skipTokenOrError('booleanComparison', RBRACKET)
        v = FuncBoolean('not', argsNotB)
        return TheFuncBoolean(pos, v) 

    # #! no commas
    # def funcBooleanNot(self, argsB):
        # name = self.textOf()
        # commit = (
            # self.isToken(IDENTIFIER) and
            # (name == 'not')
        # )    
        # if (commit):
            # self._next() 
            # self.skipTokenOrError('funcBooleanNot', LBRACKET)
            # # must contain one arg
            # # args can be Symbols or constants
            # notArgB = []
            # if (not(
                # self.funcBooleanComparison(notArgB) 
                # or self.funcBooleanCollation(notArgB) 
            # )):
                # self.expectedRuleError(
                    # "funcBooleanNot", 
                    # "funcBooleanComparison or funcBooleanCollation"
                # )
            # self.skipTokenOrError('funcBooleanNot', RBRACKET)
            # # make type, add to args
            # #argsB.append(
            # #    FuncBoolean(name, notArgB)
            # #)
            # argsB.append(Arg(self.toPosition(),  FuncBoolean(name, notArgB)))
        # return commit

    def _booleanComparison(self, name):
        self._next() 
        self.skipTokenOrError('booleanComparison', LBRACKET)
        
        # oneOrMore args
        # args can be boolean funcs and boolean vars
        tpe = None
        argsCollB = []
        pos = self.toPosition()      

        # gather args
        while(
            #self._funcBoolean(argsCollB) or
            self.funcBoolean(argsCollB) or
            self.symbol(argsCollB) or
            self.number(argsCollB)
            ):
            self.skipToken(COMMA)        

        # test enough args
        if (len(argsCollB) != 2):
            msg  = f"Must have two arguments args:{argsCollB}"
            self.errorWithPos(pos, msg)            
                
        # finish
        self.skipTokenOrError('booleanComparison', RBRACKET)
        #return FuncBoolean(name, argsCollB)
        v = FuncBoolean(name, argsCollB)
        return TheFuncBoolean(pos, v)
                         
    # def funcBooleanComparison(self, argsB):
        # name = self.textOf()
        # commit = (
            # self.isToken(IDENTIFIER) and
            # (name in NamesBooleanComparisons)
        # )
        # if (commit):
            # self._next() 
            # self.skipTokenOrError('funcBooleanComparison', LBRACKET)
            # # must contain two args
            # # args can be Symbols or constants
            # cmpArgB = []
            # if(not(
                # self.symbol(cmpArgB) or 
                # self.constant(cmpArgB)
            # )):
                # self.expectedRuleError(
                    # "funcBooleanComparison-arg1", 
                    # "symbol or constant"
                # )
            # if(not(
                # self.symbol(cmpArgB) or 
                # self.constant(cmpArgB)
            # )):
                # self.expectedRuleError(
                    # "funcBooleanComparison-arg2", 
                    # "symbol or constant"
                # )
            # self.skipTokenOrError('funcBooleanComparison', RBRACKET)
            # # make type, add to args
            # #argsB.append(
            # #    FuncBoolean(name, cmpArgB)
            # #)
            # argsB.append(Arg(self.toPosition(),  FuncBoolean(name, cmpArgB)))
        # return commit

    def _booleanCollation(self, name):
        pos = self.toPosition()      
        self._next() 
        self.skipTokenOrError('booleanCollation', LBRACKET)
        
        # oneOrMore args
        # args can be boolean funcs and boolean vars
        tpe = None
        argsCollB = []

        # gather args
        while(
            #self._funcBoolean(argsCollB) or
            self.funcBoolean(argsCollB) or
            self.symbol(argsCollB)
            ):
            self.skipToken(COMMA)        

        # test enough args
        if (len(argsCollB) < 2):
            msg  = "Must have two arguments"
            self.errorWithPos(pos, msg)            
                
        # finish
        self.skipTokenOrError('funcBooleanCollation', RBRACKET)
        #return FuncBoolean(name, argsCollB)
        v = FuncBoolean(name, argsCollB)
        return TheFuncBoolean(pos, v)
            
    # def funcBooleanCollation(self, argsB):
        # name = self.textOf()
        # commit = (
            # self.isToken(IDENTIFIER) and
            # (name in NamesBooleanCollators)
        # )       
        # if (commit):
            # self._next() 
            # self.skipTokenOrError('funcBooleanCollation', LBRACKET)

            # # oneOrMore args
            # # args can be anything in funcBoolean i.e. boolean funcs,
            # # constants, symbols
            # colArgB = []
            
            # #? No commas
            # self.oneOrMore(self.funcBoolean, colArgB, "funcBoolean")
            # self.skipTokenOrError('funcBooleanCollation', RBRACKET)
            
            # # make type, add to args
            # #argsB.append(
            # #    FuncBoolean(name, colArgB)
            # #)
            # argsB.append(Arg(self.toPosition(),  FuncBoolean(name, colArgB)))
        # return commit
            
    # def _funcBoolean(self, argsB):
        # name = self.textOf()
        # commit = (
            # self.isToken(IDENTIFIER) and
            # (name in NamesBooleanFuncs)
        # )
        # if (commit):
            # pos = self.toPosition()      

            # #i Guaranteed success, the typename was in NamesBooleanFuncs
            # if (name in NamesBooleanCollators):
                # the = self._booleanCollation(name)
            # elif (name in NamesBooleanComparisons):
                # the = self._booleanComparison(name)
            # elif (name == 'not'):
                # the = self._booleanNot()            
            # argsB.append(the)
        # return commit
        
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
            pos = self.toPosition()      
            
            #i Guaranteed success, the typename was in NamesBooleanFuncs
            if (name in NamesBooleanCollators):
                the = self._booleanCollation(name)
            elif (name in NamesBooleanComparisons):
                the = self._booleanComparison(name)
            elif (name == 'not'):
                the = self._booleanNot()            
            #argsB.append(Arg(pos, the))
            argsB.append(the)
        return commit
      
        
    ## Types
    # Type marks ate interesting. They do not, so far, fail internally
    # for consistency. Neither do they fail aginst other types, 
    # especially as we do no type-checking, Other things fail against 
    # them.
    # As a result, a type can only fail as it is constructed. If there 
    # is some unacceptable syntax, or an integer parameter in the wrong 
    # place that kind of fail, After that. the parse, a type is
    # existential.
    # This has potential effects. 
    # - There is no need for a type to contain internal parsing detail.
    #  This is unlike similar parsed constructs such as Paths and 
    # Arglists, where That ability will be used
    # - The Gravel type can be typed into the compiler implementation 
    # languge as a unit.. Since there is no surrounding detail
    # These effects are good because it is then esier to run checks 
    # against types. Though, for consistency the type should be 
    # wrapped in a surrounding The
    def _typeContainer(self, containerName):
        self._next() 
        self.skipTokenOrError('typeContainer', LBRACKET)
        
        #i args are a fair old mess for container types
        #
        # ClutchLabeled(label1, type1, label2, type2 ...)
        # Clutch(type1, type2 ...)
        # ArrayLabeled(containedType, label1, label2...)
        # Array(containedType, size)
        # containedType means we can be recursive.
        # So we're not being clever or OCD. If its a arg type thats
        # acceptable, it's in. But order or signature ignored.
        tpe = None
        argsB = []
        if (containerName == 'Clutch'):
            while(
                #self._typeDeclaration(argsB)
                self._typeDeclaration(argsB)
                ):
                self.skipToken(COMMA)
        elif (containerName == 'Array'):
            # element Type declaration
            if(not(self._typeDeclaration(argsB))):
                pos = self.toPosition()      
                msg  = "Array argument 0 must be a type"
                self.errorWithPos(pos, msg)
            self.skipToken(COMMA)  
            
            # size      
            if (not( self.isToken(INT_NUM))):
                pos = self.toPosition()
                msg  = "Array argument 1 must be an integer"
                self.errorWithPos(pos, msg)
            v = self.textOf()
            size = int(v)
            
            # check size is a positive integer
            if (0 > size):
                msg  = "Array argument 1 must be greater than 0"
                self.errorWithPos(pos, msg)                
            self._next() 
            argsB.append(size)
        else:
            #i should never be reached
            pos = self.toPosition()      
            msg  = f"Unrecognised container {containeName}"
            self.errorWithPos(pos, msg)         
        self.skipTokenOrError('typeContainer', RBRACKET)
        tpe = typeNameContainerToType[containerName](argsB)
        return tpe

    def _typeDeclaration(self, argsB):
        '''
        Representation of a type.
        If a container, may be nested.
        Types are not wrapped in Arg,
        (typeSingular | typeContainer)
        '''
        name = self.textOf()
        commit = (
            self.isToken(IDENTIFIER) and
            (name in typeNames)
        )
        if (commit):
            name = self.textOf()
            
            #i Guaranteed success, the typename was in typeNames
            tpe = None
            if (name in typeNameSingularToType):
                tpe = typeNameSingularToType[name]
                self._next() 
            elif (name in typeNameContainerToType):
                tpe = self._typeContainer(name)
            argsB.append(tpe)
        return commit
                
    def typeDeclaration(self, argsB):
        '''
        Representation of a type.
        If a container, may be nested.
        Type declarations are wrapped in Arg for positioning, but 
        type elements in an underlying tree is not.
        (typeSingular | typeContainer)
        '''
        #? This is rubbish, but anyhow....
        pos = self.toPosition()
        returnB = []
        commit = self._typeDeclaration(returnB)
        if (commit):
            the = TheType(pos, returnB[0])
            argsB.append(the)
        return commit
                            
                            
    ## General args
    #x
    #def findIdentifier(self, pos, sym):
    #    raise NotImplemented()


    ## ArgList
    def argList(self, argsB):
        '''
        A list of strings.
        Arglists have all element argumented
        ''(' ~ string + optionaltypeContainerArg ~ '')'
        '''
        # only accepts strings, for now
        #? So that would be stringList
        # Current only use is for register popping
        commit = self.isToken(LBRACKET)
        if (commit):
            self._next() 
            argList = ArgList()
            pos = self.toPosition()
            while (
                self.string(argList)
                ):
                #elif(self.isToken(typeContainerArg)):
                #    self._next()
                self.skipToken(COMMA)
            self.skipTokenOrError('argList', RBRACKET)
            t = TheArgList(pos, argList)
            argsB.append(t)
        return commit                  
        
          
    ## Path
    #! I'd need to tokenise for double brackets.
    # because we cant peek. Gnnnaaarr!
    #! whats the difference between a path and an value list?
    # Scala
    #
    # Ada 
    # (10, December, 1815)
    # (Day => 29, Month => February, Year => 2020)
    def path(self, argsB):
        '''
        Path wraps self annd all elements in an Arg
        ''[' ~ (labelArg | intNum) + optionaltypeContainerArg ~ '']'
        '''
        commit = self.isToken(LPATH)
        if (commit):            
            self._next() 
            path = Path()
            pos = self.toPosition()
            while (
                #self.labelArg(argsB) or
                self.offsetSymbol(path) or
                self.intNum(path)
                ):
                self.skipToken(COMMA)
            self.skipTokenOrError('path', RPATH)
            #argsB.append(Arg(self.toPosition(), path))
            t = ThePath(pos, path)
            argsB.append(t)
        return commit


    ## Aggregates
    def keyValue(self, b):
        '''
        identifier ~ ''~>' ~ aggregate
        '''
        # Similar to, but not a symbol, because it isn't a symbol, 
        # its a label. And so far, can only occur here, inside 
        # square brackets
        #? ...or check it's a label
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            pos = self.toPosition()
            
            # Get the symbol
            label = self.textOf()
            theLabel = TheOffsetSymbol(pos, label)
            self._next() 

            # skip the separator
            self.skipTokenOrError('aggregateKeyValue', KEY_VALUE)

            # get the value, which can itself be any aggregate            
            #i What this means is a label must always have a aggregate
            # as value, cannot have another label. 
            # [[fortune -> [[nonsense -> 33]] ]]
            # not
            # [[fortune -> nonsense -> 33]]
            #? Is that right?
            valueB = AggregateVals()
            if(not(
                self.constant(valueB) or
                self.aggregate(valueB)
            )):
                self.expectedRuleError(
                    "keyValue", 
                    "A literal or aggregated literal"
                )
            kv = KeyValue()
            
            #! label defence against protosymbols etc.
            kv.key = label
            kv.value = valueB[0]
            #b.append(Arg(pos, kv))            
            t = TheKeyValue(pos, kv)
            b.append(t)
        return commit

    def repeatMark(self, argsB):
        '''
        ''*'
        '''
        # Similar to, but not a symbol, because it isn't a symbol, 
        # its an  operator. And so far, can only occur here, inside 
        # square brackets
        commit = (self.isToken(REPEAT))
        if (commit):
            pos = self.toPosition()
            t = TheRepeatMark(pos, '*')
            argsB.append(t)
            self._next() 
        return commit
            
    def aggregate(self, argsB):
        '''
        Aggregates wrap self and all elements in Arg
        '''
        #i aggreagtes are parsed with their position, because they will 
        # be tested against types. This can only happen at compile time,
        # when symbol maps are built. So they carry their position.
        commit = self.isToken(LCOLL)
        if (commit):
            pos = self.toPosition()
            self._next() 
            av = AggregateVals()

            #i can only be at start
            if(self.repeatMark(av)):
                self.skipToken(COMMA)
                
                #i if repeat, only one following literal allowed. Which
                # can not (unnested) be a keyValue (a keyValue location 
                # has no changing position to repeaat)
                (
                self.constant(av)         
                or self.aggregate(av)
                )
            else:
                while (
                    self.constant(av)         
                    or self.aggregate(av)
                    or self.keyValue(av)
                    ):
                    self.skipToken(COMMA)
            self.skipTokenOrError('aggregate', RCOLL)
            #argsB.append(Arg(pos, av))
            t = TheAggregateVals(pos, av)
            argsB.append(t)
        return commit


    ## Args for functions
    def arg(self, argsB):
        r = False
        
        #i all args converted to data types
        #i all args wrapped in a TheXXX
        if (
            self.constant(argsB)
            
            # Both test identifier names also
            or self.funcBoolean(argsB)
            or self.typeDeclaration(argsB)
            
            # No expressions allowed nested,
            # ater booleans and funcs, so identifiers must be a symbol
            #or self.symbolArg(argsB)
            or self.symbol(argsB)
            
            #? For register popping
            # A list of strings? Rename?
            or self.argList(argsB)
            or self.path(argsB)
            or self.aggregate(argsB)
        ):
            r = True
            
        # skip trailing commas
        self.skipToken(COMMA)
        return r


    def args(self):
        argsB = []
        pos = self.toPosition()
        while (self.arg(argsB)):
            pass
        return TheArgs(pos, argsB)
        
    def exprCB(self, pos, name, args):
        '''
        Called on sucessful parsing of an expression
        '''
        # placeholder code, usually overridden
        print('expr {}({})'.format(name, args))
        
    def expr(self):
        #? But not types or booleanFuncs
        commit = (self.isToken(IDENTIFIER))
        if (commit):
            name = self.textOf()
            
            # stash the position at the start of the expression
            expNamePos = self.toPosition()
            #print(str(pos))
            self._next()
            self.skipTokenOrError('expr', LBRACKET)
            #posArgs = self.toPosition()
            args = self.args()
            
            # Can't use skipTokenOrError(). That will advance the
            # iterator. If this is the last expression, with no 
            # following whitespace (or newline) that would throw 
            # StopIteration before callback on the parsed function. 
            # So we test the rbracket is there, then callback on the 
            # function.
            #print('{}({})'.format(name, args))
            if (self.isToken(RBRACKET)):
                #self.exprCB(expNamePos, posArgs, name, args)
                self.exprCB(expNamePos, name, args)
                
                #i ..if EOF, then that is thown here
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
