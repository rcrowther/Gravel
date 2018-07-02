import sys
from trees.Trees import *
from Position import Position
from Tokens import *


INFIX = [
'|',
'||',
'^',
'&',
'&&',
'<',
'<<',
 '>',
'>>',
#'=', 
'!',
#??? ':'
'+', 
'++',
'-',
'--',
'*',
'/',
'%',
]

def isInfix(name):
  return ((name[-1] == '=') or (name in INFIX))
  
class Syntaxer:
    '''
    Tree holding the structure of tokens.
    The sole purpose of this class is to extract and organise data from 
    the token stream. Unlike most other parsers it is not concerned with
    names, ''symbols', or anything else. 
    '''
    def __init__(self, source, reporter):
        self.source = source
        self.reporter = reporter
        self.it = source.tokenIterator(reporter)
        self.tok = None
        self.ast = mkNamelessFunc(NoPosition)
        # start me up
        self.root()
        #print(self.ast.toString())
   
   
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

    def oneOrMoreDelimited(self, lst, rule, endToken):
        '''
        Often easier and more human for list rules to match the 
        delimiter than to keep checking if contained rules match.
        Skips the delimiting token.
        '''
        while(True):
            rule(lst)
            if (self.isToken(endToken)):
                break
        self._next()
        
    def oneOrError(self, lst, rule, currentRule, expectedRule):
        '''
        Match one rule or mark an error.
        '''
        if(not rule(lst)):
            self.expectedRuleError(currentRule, expectedRule)
            
    ## Rules
    def optionalKindAnnotation(self, tree):
        '''
        option(':' ~ Kind)
        Optionally match a Kind annotation.
        '''
        coloned = self.optionallySkipToken(COLON)
        if (coloned):
            tree.kindStr = self.getTokenOrError('Kind Annotation', IDENTIFIER) 
            # add contents
            #self.optionalGenericParams(k)
        return coloned
        
    def namelessDataExpression(self, lst):
        '''
        (IntNum | FloatNum | String) ~ option(KindAnnotation)
        '''
        commit = self.isToken(INT_NUM) or self.isToken(FLOAT_NUM)  or self.isToken(STRING) or self.isToken(MULTILINE_STRING)
        if (commit):
            t = None
            if (self.isToken(INT_NUM)):
                t = mkIntegerNamelessData(self.position(), self.textOf())       
            if (self.isToken(FLOAT_NUM)):
                t = mkFloatNamelessData(self.position(), self.textOf())       
            if (self.isToken(STRING)):
                t = mkStringNamelessData(self.position(), self.textOf())       
            if (self.isToken(MULTILINE_STRING)):
                t = mkStringNamelessData(self.position(), self.textOf())       
            lst.append(t)
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
              
    def defineParameter(self, lst):
        '''
        identifier ~ ':' ~ Kind
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
        '(' ~ zeroOrMore(defineParameter) ~')'
        Enforced bracketing.
        Suceed or error
        '''
        self.skipTokenOrError('Define Parameters', LBRACKET)
        self.zeroOrMoreDelimited(lst, self.defineParameter, RBRACKET)        
        return True

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
            lst.append(t)
            
            # Kind
            self.optionalKindAnnotation(t)
            
            # body (namelessData)
            #! Perhaps could take an expression
            #? close to namelessFuncCall but inly alowing one expression
            self.skipTokenOrError('Define Data', LCURLY)
            self.namelessDataExpression(t.body)
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
            lst.append(t)
            
            # params
            #! generic params
            self.defineParameters(t.params)

            # Kind
            self.optionalKindAnnotation(t)            
            
            # body (exp seq)
            self.skipTokenOrError('Define Function', LCURLY)
            self.seqContents(t.body)
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
        #lst.append(t)
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
        
    def functionCall(self, lst):
        '''
        (Identifier | OPERATER) ~ Arguments ~ Option(Kind)
        
        '''
        #! this textOf is direct, but could be done by token lookup
        commit = (self.isToken(IDENTIFIER) or self.isToken(OPERATER))
        if(commit):       
            # node    
            t = mkContextCall(self.position(), self.textOf())
            lst.append(t)
            self._next()
            
            # params
            # Allow for the special case of infix (binop) operator 
            # params, with no brackets and one parameter
            if (not isInfix(t.parsedData)):
                self.parametersForFunctionCall(t.params)
            else:
                self.oneOrError(t.params, 
                    self.expressionCall, 
                    'functionCall infix operator params',
                    'expressionCall'
                    )
                    
            # Kind
            self.optionalKindAnnotation(t)
        return commit 


    #! maybe should be in function itself?
    def operaterMonoFunctionCall(self, lst):
        '''
        MonoOperaterIdentifier ~ MonoOpCallParameter ~ Option(Kind)
        Slightly, but strongly, different to namedFunctionCall.
        '''
        commit = (self.isToken(MONO_OPERATER))
        if(commit):       
            # get mark    
            #print ('MONO operator:' + self.textOf())
            t = mkMonoOpExpressionCall(self.position(), self.textOf())
            lst.append(t)
            self._next()
            #! not expression, as another mono is not available, but otherwise ok
            self.oneOrError(lst, 
                self.expressionCall, 
                'parameterForMonoOperaterCall', 
                'expressionCall'
                )
            #self.optionalKindAnnotation(t)            
        return commit
                
    def comment(self, lst):
        commit = self.isToken(COMMENT)
        if (commit):
            t = mkSingleLineComment(self.position(), self.textOf())
            lst.append(t)
            self._next()
        return commit

    def multilineComment(self, lst):
        commit = self.isToken(MULTILINE_COMMENT)
        if (commit):
            t = mkMultiLineComment(self.position(), self.textOf())
            lst.append(t)
            self._next()
        return commit
            
            
            
    def namelessBodyCall(self, lst):
        '''
        '{'~ oneOrMore(ExpressionCall) ~'}'
        '''
        commit = (self.isToken(LCURLY))
        if(commit): 
            self._next()
            
            # node    
            t = mkNamelessBody(self.position())
            lst.append(t)

            # body
            self.oneOrMoreDelimited(t.body, self.expressionCall, RCURLY)
        return commit



    def expressionCall(self, lst):
        '''
        namelessDataExpression | namedFunctionCall | operaterFunctionCall
        Calls where they can be used nested (not as the target
        of allocation etc.?)
        '''
        #print('expression')
        commit = (
            self.namelessDataExpression(lst) 
            or self.functionCall(lst)
            or self.operaterMonoFunctionCall(lst)
            or self.namelessBodyCall(lst)
            )
            
        # chaining
        #! Not DRY (because not convinced of final form yet).
        if (commit):
            t = lst[-1]
            if (self.optionallySkipToken(PERIOD)):
                t.isChained = True
            # The iterator is resting on the next op. What if it's an 
            # infix? Prefer this sneaky look-forward to a 
            # high-engineered look-back
            elif ((self.isToken(IDENTIFIER) or self.isToken(OPERATER)) and isInfix(self.it.textOf())):
                t.isChained = True
            #elif (isinstance(t, NameMixin) and isInfix(t.parsedData) and len(lst) > 1):
                #lst[-2].isChained = True
        return commit
        
    def seqContents(self, lst):
        '''
        Used for body contents.
        Allows definitions.
        '''
        while(
            self.comment(lst)
            or self.multilineComment(lst)
            or self.dataDefine(lst)
            or self.functionDefine(lst)
            # calls must go after defines, which are more 
            # specialised in the first token
            or self.expressionCall(lst)
            ):
            if (len(lst) > 1):
                lst[-1].prev = lst[-2]        
        
    def root(self):
        try:
            # charge
            self._next()
            self.seqContents(self.ast.body)
            # if we don't except on StopIteration...
            self.error('Parsing did not complete: lastToken: {},'.format(
                tokenToString[self.tok],                
                ))
        except StopIteration:
            # All ok
            print('parsed')
            pass
