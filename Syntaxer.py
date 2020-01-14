import sys
from gio.TokenIterator import mkTokenIterator
from trees.Trees import *
from Tokens import *
import Keywords
from Position import Position
from reporters.Message import Message


# We've got problems:
# - Identifying by name alone does not split between '+' (monop) and
# '+' (binop). Is this kind of issue what full names are for? It's
# making the monop scene a mess. This, essentially, is the problem of 
# polymorphism, arrising early.
# - chaining for the interpreter means signalling the last item, not 
# the first (chain the trailing return into this). But I recall that
# we chained the first op for a reason? Reversal?
# - chaining feels compromised? Why have parameters if reaching for
# the next item in line?
def isInfix(name):
  return ((name[-1] == '=') or (name in Keywords.INFIX))
  
  
  
class Syntaxer:
    '''
    Generates a tree holding the structure of tokens.
    The sole purpose of this class is to extract and organise data from 
    the token stream. Unlike most other parsers it is not concerned with
    names, ''symbols', or anything else. 
    '''
    def __init__(self, source, reporter):
        self.source = source
        self.reporter = reporter
        #self.it = source.tokenIterator(reporter)
        self.it = mkTokenIterator(source, reporter)
        self.tok = None
        self.ast = []
        self.chainedItem = None
        # start me up
        self.root()
        #print(self.ast.toString())
   
   
    ## reporter helpers     
    def position(self):
        return Position(self.source, self.it.lineCount, self.it.lineOffset)
        
    def error(self, msg):
        tokenTxt = self.it.textOf()
        msg = Message.withPos(msg, self.source, self.position())
        if (tokenTxt):
            msg.details = ["token text : '{0}'".format(tokenTxt)]
        self.reporter.error(msg)
        sys.exit("Error message")

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
             
    ## iterators
    def textOf(self):
        return self.it.textOf()
        
    def _next(self):
        #self.prevLine = self.it.lineCount()
        #self.prevOffset = self.it.lineOffset()
        self.tok = self.it.__next__()


    ## Token helpers
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
            
            
    ## Rule helpers
    #! enable
    def zeroOrMoreDelimited(self, lst, rule, endToken):
        '''
        Often easier and more human for list rules to match the 
        delimiter than to keep checking if contained rules match.
        Skips the delimiting token.
        '''
        while(not self.isToken(endToken)):
            rule(lst)
        self._next()

    def oneOrMoreDelimited(self, rule, endToken):
        '''
        Often easier and more human for list rules to match the 
        delimiter than to keep checking if contained rules match.
        Skips the delimiting token.
        @rule nust be non-optional (throws error)
        '''
        count = 0
        while(True):
            rule()
            count += 1
            if (self.isToken(endToken)):
                break
        #print("count {}".format(count))
        #! no?
        self._next()
        return count
        
    def oneOrError(self, ruleOption, currentRuleName, expectedRuleName):
        '''
        Match one rule or mark an error.
        '''
        if(not ruleOption()):
            self.expectedRuleError(currentRuleName, expectedRuleName)
            
    ## Rules
    def optionalKindAnnotation(self, tree):
        '''
        option(':' ~ Kind)
        Optionally match a Kind annotation.
        '''
        coloned = self.optionallySkipToken(COLON)
        if (coloned):
            #tree.kindStr = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            tree.parsedKind = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            # add contents
            #self.optionalGenericParams(k)
        return coloned
        
    #? nmelessData?
    def dataNameless(self):
        '''
        (IntNum | FloatNum | String) ~ option(KindAnnotation)
        '''
        commit = (
            self.isToken(INT_NUM) or 
            self.isToken(FLOAT_NUM) or 
            self.isToken(STRING) or 
            self.isToken(MULTILINE_STRING)
            )
        if (commit):
            t = None
            if (self.isToken(INT_NUM)):
                t = mkIntegerData(self.position(), self.textOf())       
            if (self.isToken(FLOAT_NUM)):
                t = mkFloatData(self.position(), self.textOf())       
            if (self.isToken(STRING)):
                t = mkStringData(self.position(), self.textOf())       
            if (self.isToken(MULTILINE_STRING)):
                t = mkStringData(self.position(), self.textOf())       
            self.ast.append(t)
            self._next()
            self.optionalKindAnnotation(t)
        return commit
        
            
    # lot like a simple call
    # and a parameter
    def identifierOptionalKind(self, lst):
        '''
        identifier ~ Option(Kind)
        Optional type declaration.
        Succeed or error
        '''
        # id
        markStr = self.getTokenOrError('Optional Kinded Identifier', IDENTIFIER) 
        t = mkParameterDefinition(self.position(), markStr)
        # delimit
        self.optionalKindAnnotation(t)
        return True
              
    # def defineParameter(self, lst):
        # '''
        # identifier ~ ':' ~ Kind
        # Enforced type declaration.
        # Succeed or error
        # '''
        # # id
        # markStr = self.getTokenOrError('Define Parameter', IDENTIFIER) 
        # # delimit
        # self.skipTokenOrError('Define Parameter', COLON)
        # # type
        # t = mkParameterDefinition(self.position(), markStr)
        # t.returnKind = self.getTokenOrError('Define Parameter', IDENTIFIER)
        # self.ast.append(t)
        # return True

    # def defineParameters(self, lst):
        # '''
        # '(' ~ zeroOrMore(defineParameter) ~')'
        # Enforced bracketing.
        # Suceed or error
        # '''
        # self.skipTokenOrError('Define Parameters', LBRACKET)
        # self.zeroOrMoreDelimited(lst, self.defineParameter, RBRACKET)        
        # return True
    #x
    def dataDefine(self, lst):
        '''
        'fnc' ~ (Identifier | OperatorIdentifier) ~ DefineParameters  ~ Option(Kind) ~ ExplicitSeq
        Definitions attached to code blocks
        Used for both named and operater functions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (
            self.isToken(IDENTIFIER) and 
            self.it.textOf() == 'val' or
            self.it.textOf() == 'var'
            )
        if(commit):
            self._next()
            pos = self.position()
            
            # mark 
            if(self.tok != IDENTIFIER and self.tok != OPERATER):
                self.tokenError("In rule '{}' expected '{}' or '{}' but found '{}'".format(
                    'Define Data',
                    tokenToString[IDENTIFIER],
                    tokenToString[OPERATER],
                    tokenToString[self.tok]
                    ))
            markStr = self.textOf()
            self._next()
            
            # make node
            t = mkDataDefine(pos, markStr)
            self.ast.append(t)
            
            # Kind
            self.optionalKindAnnotation(t)
            
            # body (namelessData)
            #! Perhaps could take an expression
            #? close to namelessFuncCall but inly alowing one expression
            self.skipTokenOrError('Define Data', LCURLY)
            self.dataNameless(t.body)
            self.skipTokenOrError('Define Data', RCURLY)
        return commit
        
    def functionDefine(self, lst):
        '''
        'fnc' ~ (Identifier | OperatorIdentifier) ~ DefineParameters  ~ Option(Kind) ~ ExplicitSeq
        Definitions attached to code blocks
        Used for both named and operater functions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) and self.it.textOf() == 'fnc')
        if(commit):
            self._next()
            pos = self.position()
             
            # mark
            # currently. can't be dried out
            if(self.tok != IDENTIFIER and self.tok != OPERATER):
                self.tokenError("In rule '{}' expected '{}' or '{}' but found '{}'".format(
                    'Define Function',
                    tokenToString[IDENTIFIER],
                    tokenToString[OPERATER],
                    tokenToString[self.tok]
                    ))
            markStr = self.textOf()
            self._next()

            # make node
            t = mkContextDefine(pos, markStr)
            self.ast.append(t)
            
            # params
            #! generic params
            self.defineParameters(t.params)

            # Kind
            self.optionalKindAnnotation(t)            
            
            # body (exp seq)
            self.skipTokenOrError('Define Function', LCURLY)
            self.seqContents()
            self.skipTokenOrError('Define Function', RCURLY)
        return commit
        

                      
    #??? test expression embedding
    def parametersForFunctionCall(self, lst):
        '''
        '(' ~ zeroOrMore(expression) ~')' | Empty
        Multiple parameters, optional kind.
        Succeed or error
        '''
        bracketted = self.optionallySkipToken(LBRACKET)
        if (bracketted):
            #if(self.chainedItem):
                #self.ast.append(self.chainedItem)
                #self.chainedItem = None
            self.zeroOrMoreDelimited(lst, self.expressionCall, RBRACKET)          
        return True
        
    #def parametersForChainedOperaterFunctionCall(self, lst):
        #'''
        #expression |
        #'(' ~ zeroOrMore(expression) ~ ')'
        #One parameter, optional bracketing.
        #Succeed or error
        #'''
        #bracketted = self.optionallySkipToken(LBRACKET)
        #if (not bracketted):
            ## assume binOp
            #self.oneOrError(lst, 
                #self.expressionCall, 
                #'parametersForOperaterCall', 
                #'expressionCall'
                #)
        #else:
           ## allow any parameters
            #self.zeroOrMoreDelimited(lst, self.expressionCall, RBRACKET)
        #return True
      
      
    #def chainedOperaterBinOpCall(self, lst):
        #'''
        #OperatorIdentifier ~ ExpressionCall
        #'''
        ## get mark    
        #print ('binop operator:' +  self.textOf())
        #t = mkContextCall(self.position(), self.textOf())
        #self.ast.append(t)
        #self._next()
        ## generic params?
        #self.oneOrError(lst, 
            #self.expressionCall, 
            #'expressionCall', 
            #'chainedOperaterBinOpCall'
            #)
        ##self.optionalKindAnnotation(t)            
        #return True
      
      
    #def optionalChainedExpressionCall(self, lst):
        #'''
        #zeroOrMore(period ~ namedFunctionCall) | (operaterFunctionCall))
        #Used after function and operator calls.
        #'''
        #while(True):
            #if (self.tok == PERIOD): 
                #self._next()
                #self.functionCall(lst)
                #continue
            #if (self.tok == OPERATER and isInfix(self.it.textOf())):
                #self.chainedOperaterBinOpCall(lst)
                #continue
            #break
        
    def functionCall(self, lst, isDotChained):
        '''
        (Identifier | OPERATER) ~ Arguments ~ Option(Kind)
        
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) or self.isToken(OPERATER))
        if(commit):       
            # node    
            t = mkContextCall(self.position(), self.textOf())
            
            # if chained (in either way), grab last expression and use 
            # as first parameter to this expression
            if (isDotChained or isInfix(self.textOf())):
                t.params.append(lst.pop()) 
                             
            self.ast.append(t)
            self._next()
            
            # params
            if (not isInfix(t.parsedData)):
                self.parametersForFunctionCall(t.params)
            else:
                # Allow for the special case of infix (binop) operator 
                # params, with no brackets and one parameter.
                #print('    infixing : ' + str(t.parsedData))
                self.oneOrError(t.params, 
                    self.expressionCall, 
                    'functionCall infix operator params',
                    'expressionCall'
                    )
                #print('    infixed : ' + str(t.params))

            # Kind
            self.optionalKindAnnotation(t)
        return commit 


    #! maybe should be in function itself?
    # def operaterMonoFunctionCall(self, lst):
        # '''
        # MonoOperaterIdentifier ~ MonoOpCallParameter ~ Option(Kind)
        # Slightly, but strongly, different to namedFunctionCall.
        # '''
        # commit = (self.isToken(MONO_OPERATER))
        # if(commit):       
            # # get mark    
            # #print ('MONO operator:' + self.textOf())
            # t = mkMonoOpExpressionCall(self.position(), self.textOf())
            # self.ast.append(t)
            # self._next()
            # #! not expression, as another mono is not available, but otherwise ok
            # self.oneOrError(lst, 
                # self.expressionCall, 
                # 'parameterForMonoOperaterCall', 
                # 'expressionCall'
                # )
            # #self.optionalKindAnnotation(t)            
        # return commit
                
    def comment(self):
        commit = self.isToken(COMMENT)
        if (commit):
            t = mkSingleLineComment(self.position(), self.textOf().lstrip())
            self.ast.append(t)
            self._next()
        return commit

    def multilineComment(self):
        commit = self.isToken(MULTILINE_COMMENT)
        if (commit):
            t = mkMultiLineComment(self.position(), self.textOf().lstrip())
            self.ast.append(t)
            self._next()
        return commit


    #x
    def expressionCall(self, lst):
        '''
        dataNameless | namedFunctionCall | operaterFunctionCall
        Calls where they can be used nested (not as the target
        of allocation etc.?)
        '''
        #print('expression')
        #! need a way to spot dot-chaining misapplied 
        isDotChained = self.optionallySkipToken(PERIOD)

        commit = (
            self.dataNameless(lst) 
            or self.functionCall(lst, isDotChained)
            or self.operaterMonoFunctionCall(lst)
            or self.seqNameless()
            )
            
        # chaining
        #! Not DRY (because not convinced of final form yet).
        # for the interpreter, we catch the last return
        # For the compiler, we do inner first.
        #if (commit):
          
            ##t = lst[-1]
            ##if (self.optionallySkipToken(PERIOD)):
            ##    t.isChained = True
            ## The iterator is resting on the next op. What if it's an 
            ## infix? Prefer this sneaky look-forward to a 
            ## high-engineered look-back
            ##elif ((self.isToken(IDENTIFIER) or self.isToken(OPERATER)) and isInfix(self.it.textOf())):
            ##    t.isChained = True
            ##elif (isinstance(t, NameMixin) and isInfix(t.parsedData) and len(lst) > 1):
                ##lst[-2].isChained = True
            ## if this was chained, add in tree for parameter
            #if(self.chainedItem):
                #print('    chaining tree: ' + str(self.chainedItem))
                #print('    ...to: ' + str(lst[-1]))
                #lst[-1].params.insert(0, self.chainedItem)
                #self.chainedItem = None
                
            #isBinopId = ((self.isToken(IDENTIFIER) or self.isToken(OPERATER)) and isInfix(self.it.textOf()))
            #if (
                #isBinopId
                #or self.optionallySkipToken(PERIOD)
                #):
                #print('    popping: ' + str(lst[-1]))
                #self.chainedItem = lst.pop()
                
        return commit
######### NEW


## Seq
#! Option
    def seqNameless(self):
        '''
        '{'~ oneOrMore(ExpressionCall) ~'}'
        '''
        commit = (self.isToken(LCURLY))
        if(commit): 
            self._next()

            startLen = len(self.ast)
            
            # body
            #self.oneOrMoreDelimited(t.body, self.expressionCall, RCURLY)
            self.seqContents()
            self.skipTokenOrError('CodeSeqNameless', RCURLY)

            paramCount = len(self.ast) - startLen 
            
            # node    
            t = mkCodeSeqNameless(self.position(), paramCount)
            self.ast.append(t)
            
        return commit


    #? No Kind option
    def seqNamedDefine(self):
        '''
        'nb' ~ (Identifier | OperatorIdentifier) ~ Option(Kind) ~ ExplicitSeq
        Definitions attached to code blocks
        Used for both named and operater functions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) and self.it.textOf() == 'nb')
        if(commit):
            self._next()
            pos = self.position()
             
            # mark
            if(self.tok != IDENTIFIER and self.tok != OPERATER):
                self.tokenError("In rule '{}' expected '{}' or '{}' but found '{}'".format(
                    'CodeSeq Named',
                    tokenToString[IDENTIFIER],
                    tokenToString[OPERATER],
                    tokenToString[self.tok]
                    ))
            markStr = self.textOf()
            self._next()

            # make node
            # node    
            t = mkCodeSeqNamedDefine(self.position(), markStr)
            self.ast.append(t)

            # body
            self.skipTokenOrError('CodeSeq Named', LCURLY)            
            self.seqContents()
            self.skipTokenOrError('CodeSeq Named', RCURLY)            
        return commit
        
## Namespace

    #! don't call it this, its a nameSet, or something
    #! Code lot like a function call but different (DRY). No return
    #! cause it's assumed to be anamespace or Unit.... if anything.
    def slotDefine(self, lst):
        '''
        'ns' ~ Identifier ~ ExplicitSeq
        Definition of a namespace. Conceptually, a labeled set of 
        expressions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) and self.it.textOf() == 'ns')
        if(commit):        
            self._next()
            pos = self.position()
             
            # mark
            if(self.tok != IDENTIFIER):
                self.expectedTokenError(
                    'CodeSlot Define',
                    IDENTIFIER
                    )
            markStr = self.textOf()
            self._next()

            # make node
            # node    
            t = mkCodeSlotNamedDefine(self.position(), markStr)
            
            # params
            #self.parametersOption(t.params)
                
            # body
            self.skipTokenOrError('CodeSlot Define', LCURLY)            
            self.seqContents(t.body)
            self.skipTokenOrError('Named Block', RCURLY)            

            self.ast.append(t)
        return commit

    #def gteOperatorPrecidence(op1, op2):
        #op1
        #return

    def operatorCall(self, opStack):
        commit = self.isToken(OPERATER)
        if (commit):
            t = mkOperatorCall(self.position(), self.textOf())
            # #! for now, assume equal precidence
            while (
                (len(opStack) > 0) and
                # #t.precidence >= opStack.top.precidence and
                opStack[-1] != LBRACKET
                ):
                self.ast.append(opStack.pop())
            opStack.append(t)
            self._next()
        return commit
                    
    def multiActionCall(self):
        # has no idea if calling within a nameSet, or container, but 
        # does it matter?
        #out = []
        opStack = []
        commit = (           
            # these are the possibilities to open a call
            self.isToken(INT_NUM) or
            self.isToken(FLOAT_NUM)  or
            self.isToken(STRING) or
            #self.isToken(MULTILINE_STRING) or
            self.isToken(IDENTIFIER) or
            self.isToken(MONO_OPERATER)
            )
        # print('multiActionCall1 {} {} {}'.format(
            # tokenToString[self.tok], 
            # self.textOf(),
            # commit
            # ))
        if (commit):
            prevWasData = False

                #? or make list? multiActionCall()
                # prev was op
            while(
                self.isToken(INT_NUM) or
                self.isToken(FLOAT_NUM)  or
                self.isToken(STRING) or
                #self.isToken(MULTILINE_STRING) or
                self.isToken(IDENTIFIER) or
                self.isToken(MONO_OPERATER) or
                # in chained actions, also deal witth these,
                # interspacing the chains
                self.isToken(OPERATER) or
                self.isToken(LBRACKET) or
                self.isToken(RBRACKET)
                ):

                if (prevWasData):
                    commit = self.operatorCall(opStack)
                    if (not commit):
                        # something to do with EOL
                        self.expectedTokenError(
                            'Operator Call',
                            OPERATER
                            )                    
                    if (self.isToken(LBRACKET)):
                        opStack.append(LBRACKET)
                        self._next()
                    prevWasData = False
                else:
                    if (self.isToken(MONO_OPERATER)):
                        #! should be ultimate precidence
                        #? so no probs with a push?
                        t = mkMonoOperatorCall(self.position(), self.textOf())
                        opStack.append(t)
                        self._next()

                    # #StringNamelessData
                    # #ContextCall
                    if (self.isToken(IDENTIFIER)):
                        t = mkContextCall(self.position(), self.textOf())
                        self.ast.append(t)
                        #? params
                        # parametersCallOption
                        self._next()
                        #self.parametersOption(t.params)
                    
                    elif(
                        self.isToken(INT_NUM) or
                        self.isToken(FLOAT_NUM)  or
                        self.isToken(STRING) or
                        self.isToken(MULTILINE_STRING)
                        ):
                        self.dataNameless()

                    if (self.isToken(RBRACKET)):
                        while(opStack[-1] != LBRACKET):
                            self.ast.append(opStack.pop())
                        opStack.pop()
                        self._next()

                    prevWasData = True
                
            #print('multiActionCall2')
            # empty out
            if (len(opStack) > 0):
                self.ast.append(opStack.pop())
            #print("str out: {}".format(out))
            self._next()
        return commit
            
                      
    def lineFeed(self):
        '''
        'Nothing'
        '''
        commit = (self.isToken(LINEFEED))
        if(commit): 
            self._next()
        return commit
                                    
    def seqContents(self):
        '''
        Used for body contents.
        Allows definitions.
        '''
        entryCount = len(self.ast)
        while(
            self.comment()
            or self.multilineComment()
            # multiactioncall
            #or self.dataNameless()
            or self.seqNameless()
            or self.seqNamedDefine()
            or self.actionDefine()
            #or self.slotDefine()
            or self.multiActionCall() 
            #or self.actionCall()
            #or self.dataDefine()
            #or self.functionDefine()
            # calls must go after defines, which are more 
            # specialised in the first token
            #or self.expressionCall()
            or self.lineFeed()
            ):
                pass
            #? what are we doing here at the end?
            #if (len(lst) > 1):
            #    lst[-1].prev = lst[-2]
        eCount = len(self.ast) - entryCount
        mkCodeSeqNameless(self.position(), eCount)


## Construction parts


    def parameterDefine(self):
        '''
        identifier ~ Option(':' ~ Kind)
        Succeed or error
        '''
        # id
        markStr = self.getTokenOrError('Parameter Define', IDENTIFIER) 
        t = mkParameterDefinition(self.position(), markStr)
        # type
        #! tmp. use type() ???
        #! is this optional?
        self.skipTokenOrError('Parameter Define', COLON)
        #if (self.isToken(COLON)):
        #    self._next()
        t.kind = self.getTokenOrError('Parameter Define', IDENTIFIER)
        self.ast.append(t)
        return True
        
    def parametersDefineOption(self):
        '''
        option('(' ~ oneOrMore(parameter) ~')') 
        Enforced bracketing.
        '''
        commit = self.isToken(LBRACKET)
        #print(str(commit))
        count = 0
        if (commit):
            # One or more params
            self._next()
            #! tor now. Will be MultiActionCall
            count = self.oneOrMoreDelimited(
                self.parameterDefine,
                RBRACKET
                )   
        return count
        
    def parametersCallOption(self):
        '''
        option('(' ~ oneOrMore(parameter) ~')') 
        Enforced bracketing.
        '''
        commit = self.isToken(LBRACKET)
        #print(str(commit))
        count = 0
        if (commit):
            # One or more params
            #! multiActionCalls, but not yet
            self._next()
            count = self.oneOrMoreDelimited(
                self.parameter,
                RBRACKET
                )   
        return count
        
## Actions
    #! unify paramCount handling
    def actionDefine(self):
        '''
        ('am' | 'ac') ~ 
        (
        (Identifier ~ Parameters)   |
        (OperatorIdentifier ~ Parameter)
        )
         ~ Option(Kind) ~ '=' ~ Option(ExplicitSeq)
        Definitions attached to code blocks
        Used for both named and operater functions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (
            self.isToken(IDENTIFIER) and
            (self.it.textOf() == 'am' or self.it.textOf() == 'ac')
            )
        if(commit): 
            self._next()
            pos = self.position()
             
            # mark
            # currently. can't be dried out
            if(
                self.tok != IDENTIFIER and 
                self.tok != OPERATER and 
                self.tok != MONO_OPERATER
                ):
                self.expectedTokenError(
                    'Define Action',
                    IDENTIFIER
                    )

                # self.tokenError("In rule '{}' expected '{}' or '{}' but found '{}'".format(
                    # 'Define Action',
                    # tokenToString[IDENTIFIER],
                    # tokenToString[OPERATER],
                    # tokenToString[self.tok]
                    # ))
            markStr = self.textOf()
            
            if(self.tok == IDENTIFIER):
                # make node
                t = mkCodeSeqContextDefine(pos, markStr)
                
                # params
                self._next()
                # Need to use seperate code to the shunt algorithm to
                # handle actioncalls. 
                # label1 + label2
                # is ok,
                # label1 9 + label2
                # will read as a missing operator (not a parameter)
                # label1(8 + 4) + label2
                # will read as missing an operator and as a bracketed
                # sub-action 
                paramCount = self.parametersDefineOption()
                t.paramCount = paramCount
                # because body to come
                t.paramCount += 1    
                #print("count {}".format(t.paramCount))

            elif(self.tok == OPERATER):
                # make node
                t = mkOperatorContextDefine(pos, markStr)
                
                # params, preset.count
                # one only (other is 'self')
                self._next()
                self.parameterDefine()
                self.parameterDefine()
                                        
            elif(self.tok == MONO_OPERATER):
                # make node
                t = mkMonoOperatorContextDefine(pos, markStr)
            
                # params, Preset count, one only.
                self._next()
                self.parameterDefine()

            # Kind (return)
            #self.optionalKindAnnotation(t)
            
            # Allocate
            #! skipOp
            if (not (self.isToken(OPERATER) and self.it.textOf() == '=')):
                self.expectedTokenError('Action Define',  EQUALS)
            self._next()

            # body (exp seq)
            self.oneOrError(
                self.seqNameless, 
                'Action Define', 
                'CodeSeq Nameless'
                )
            self.ast.append(t)
        return commit
        
    #? converrted, but not of use?
    # def actionCall(self):
        # '''
        # (Identifier ~ oneOrMore(parameters) | ((Identifier | Operator) ~ parameter)
        # Definitions attached to code blocks
        # Used for both named and operater functions.
        # '''
        # #! this textOf is direct, but could be done by token lookup
        # commit = (
                # self.isToken(IDENTIFIER) or 
                # self.isToken(OPERATER) or 
                # self.isToken(MONO_OPERATER)
                # )
        # if (commit):
            # # node    
            # t = mkContextCall(self.position(), self.textOf())
            
            # #! these need to be expressions, but not now...
            # if(self.tok == IDENTIFIER):
                # # params
                # self._next()
                # self.parametersOption(t.params)

            # elif(self.tok == OPERATER):
                # # params, preset.count
                # # one only (other is 'self')
                # self._next()
                # self.parameter(t.params)
            
            # elif(self.tok == MONO_OPERATER):
                # # params, Preset count, one only.
                # self._next()
                # self.parameter(t.params)
                        
            # t.paramCount = paramCount        
            # self.ast.append(t)
        # return commit
        
    def actionCall(self):
        '''
        (Identifier ~ oneOrMore(parameters) | ((Identifier | Operator) ~ parameter)
        Definitions attached to code blocks
        Used for both named and operater functions.
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = self.isToken(IDENTIFIER)
        if (commit):
            # node    
            t = mkContextCall(self.position(), self.textOf())
            
            #! these need to be expressions, but not now...
            # params
            self._next()
            paramCount = self.parametersOption(t.params)

            t.paramCount = paramCount        
            self.ast.append(t)
        return commit
        
## Root rule
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
