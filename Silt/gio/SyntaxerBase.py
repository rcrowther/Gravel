#import sys
#from Tokens import *
from gio.reporters.Position import Position
from gio.reporters.Message import Message
from gio.exceptions import GIOSyntaxError



# All rules should progross to next token if 
# successful
# All rules are optional. If not, name as  ''Fix'
class SyntaxerBase:
    tokenToString = {}

    '''
    Generates a tree holding the structure of tokens.
    The sole purpose of this class is to extract and organise data from 
    the token stream. Unlike most other parsers it is not concerned with
    names, ''symbols', or anything else. 
    '''
    def __init__(self, reporter):
        self.reporter = reporter
        self.tok = None
        self.src = None   
        self.it = None



    ## reporter helpers
    def toPosition(self):
        '''
        Retern a position object
        Note that since a syntaxer expects a lexical iterator, the 
        current position in source will bw the start of the current 
        token, not a position by codepoint.
        '''
        return Position(self.it.tokenLineCount, self.it.tokenStartOffset)

    def errorWithPos(self, pos, msg):
        '''
        Error message with explicit pos.
        This makes it possible to use delayed positions, rather than
        current position.
        Full source, position and token detail.
        Sometimes it may be preferable to hold on to a pos, to report 
        back after later parsing. This is slightly less convenient. Use
        error() to report on the current pos.
        '''
        msgKlass = Message.withSrcPos(
            msg,
            self.src,
            pos,
            self.src.lineByIndex(self.it.tokenLineCount)
        )
        tokenTxt = self.it.textOf()
        if (tokenTxt):
            msgKlass.details = ["token text : '{}'".format(tokenTxt)]
        self.reporter.error(msgKlass)
        raise GIOSyntaxError() 
                
    def error(self, msg):
        '''
        Error message.
        Full source, position and token detail
        '''
        pos = Position(self.it.tokenLineCount, self.it.tokenStartOffset)
        self.errorWithPos(pos, msg)
        # msgKlass = Message.withPos(msg, self.src, pos, self.src.lineByIndex(self.it.tokenLineCount))
        # tokenTxt = self.it.textOf()
        # if (tokenTxt):
            # msgKlass.details = ["token text : '{}'".format(tokenTxt)]
        # self.reporter.error(msgKlass)
        # raise GIOSyntaxError() 
        
    def expectedTokenError(self, ruleName, tok):
         self.error("In rule '{}' expected token '{}' but found '{}'".format(
             ruleName,
             self.tokenToString[tok],
             self.tokenToString[self.tok]
        ))

    def expectedRuleError(self, currentRule, expectedRule):
         self.error("In rule '{}' expected rule '{}'. Current token: '{}'".format(
             currentRule,
             expectedRule,
             self.tokenToString[self.tok]
        ))                       

    def warningWithPos(self, pos, msg):
        '''
        Warning message with explicit position.
        Full source, position and token detail.
        Sometimes it may be preferable to hold on to a pos, to report 
        back after later parsing. This is slightly less convenient. Use
        error() to report on the current pos.
        '''
        msgKlass = Message.withSrcPos(
            msg,
            self.src,
            pos,
            self.src.lineByIndex(self.it.tokenLineCount)
        )
        tokenTxt = self.it.textOf()
        if (tokenTxt):
            msgKlass.details = ["token text : '{}'".format(tokenTxt)]
        self.reporter.warning(msgKlass)
        
    def warning(self, msg):
        '''
        Warning message.
        Full source, position and token detail
        '''
        pos = Position(self.it.tokenLineCount, self.it.tokenStartOffset)
        self.warningWithPos(pos, msg)


    def info(self, msg):
        '''
        Mild info message.
        Only lists source, with no token detail
        '''
        pos = Position(self.it.tokenLineCount, self.it.tokenStartOffset)
        msgKlass = Message.withSrc(msg, self.src)
        self.reporter.info(msgKlass)

    ## reporter helpers, old     
    # def position(self):
        # return Position(self.source, self.it.lineCount, self.it.lineOffset)

    # def error(self, msg):
        # tokenTxt = self.it.textOf()
        # msg = Message.withPos(msg, self.source, self.position())
        # if (tokenTxt):
            # msg.details = ["token text : '{0}'".format(tokenTxt)]
        # self.reporter.error(msg)
        # sys.exit("Error message")

    # def expectedTokenError(self, ruleName, tok):
         # self.error("In rule '{0}' expected token '{1}' but found '{2}'".format(
             # ruleName,
             # tokenToString[tok],
             # tokenToString[self.tok]
             # ))

    # def expectedRuleError(self, currentRule, expectedRule):
         # self.error("In rule '{0}' expected rule '{1}'. Current token: '{2}'".format(
             # currentRule,
             # expectedRule,
             # tokenToString[self.tok]
             # ))
             
    ## iterators
    def textOf(self):
        return self.it.textOf()
        
    def _next(self):
        self.tok = self.it.__next__()


    ## Token helpers
    def isToken(self, token):
       return (token == self.tok)

    #def option(self, token, action, b):
        #if (token == self.tok):
            #action(b)
            
    def getTokenOrError(self, ruleName,  token):
        '''
        Get a token or throw an error
        When you know what it is, and must have it
        '''
        if(self.tok != token):
           self.expectedTokenError(ruleName, token)
        t = self.textOf()
        self._next()
        return t

    def skipTokenOrError(self, ruleName,  token):
        '''
        Pass over a token or throw an error
        When you know what it is, and it must be there (e.g. bracket ends)
        '''
        if(self.tok != token):
            self.expectedTokenError(ruleName, token)
        self._next()
         
    #?! These do the same
    def skipToken(self, token):
        '''
        (optionally) Pass over a token
        When you know what it is, and are not interested (e.g. brackets)
        return
            If skips, returns True.
        '''
        r = False
        if (self.tok == token):
            r = True
            self._next()
        return r

    #?! These do the same
    def optionallySkipToken(self, token):
        '''
        Optionally skip a token.
        return
            If skips, returns True.
        ''' 
        r = (token == self.tok)
        if (r):
            self._next()
        return r
            
            
    ## Rule helpers
    #? issues here: 
    # - these really need the ability to pass
    # in trees or args to the rules.
    # - and to take one or more rules
    def zeroOrMore(self, rule, ruleArgs):
        '''
        Run a rule zero or more times.
        rule
            an optional boolean-return function
        ruleArgs
            args to supply to the rule
        '''
        run = True
        while(run):
            run = rule(ruleArgs) 
                

    def one(self, rule, ruleArgs, expectedRuleName):
        '''
        Run a rule one or more times.
        Throws an expectedRuleError if no match.
        rule
            an optional boolean-return function
        ruleArgs
            args to supply to the rule
        '''
        if (not(rule(ruleArgs))):
            self.expectedRuleError(
                "oneOrMore", 
                expectedRuleName
            )    

    def oneOrMore(self, rule, ruleArgs, expectedRuleName):
        '''
        Run a rule one or more times.
        Throws an expectedRuleError if no match.
        rule
            an optional boolean-return function
        ruleArgs
            args to supply to the rule
        '''               
        self.one(rule, ruleArgs, expectedRuleName)
        self.zeroOrMore(rule, ruleArgs)
        
        
    # Could be more rigourous, what if delimiter is in rule
    # or rule goes wrong?
    #x probably
    # def zeroOrMoreDelimited(self, ruleFixed, endToken):
        # '''
        # Apply a rule optionally, repeatedly, until an end token.
        # Often easier and more human for list rules to match the 
        # delimiter than to keep checking if contained rules match.
        # Skips the delimiting token.
        # ruleFixed 
            # nust be non-optional 'fixed' (throws error)
        # '''
        # count = 0
        # while(not self.isToken(endToken)):
            # ruleFixed()
            # count += 1
        # self._next()
        # return count

    # #x probably
    # def oneOrMoreDelimited(self, ruleFixed, endToken):
        # '''
        # Apply a rule repeatedly until an end token.
        # Often easier and more human for list rules to match the 
        # delimiter than to keep checking if contained rules match.
        # Skips the delimiting token.
        # ruleFixed 
            # nust be non-optional 'fixed' (throws error)
        # '''
        # count = 0
        # while(True):
            # ruleFixed()
            # count += 1
            # if (self.isToken(endToken)):
                # break
        # #print("count {}".format(count))
        # #! no?
        # self._next()
        # return count
        
    # #x probably
    # def oneOrError(self, ruleOption, currentRuleName, expectedRuleName):
        # '''
        # Match one rule or throw an error.
        # This helper makes an optional rule into a necesssary rule.
        # ruleOption
            # an opyional rule. 
        # '''
        # if(not ruleOption()):
            # self.expectedRuleError(currentRuleName, expectedRuleName)
            
    ## Rules

    ## Root rule
    def root(self):
        raise NotImplementedError()
            
    def parse(self, tokenIterator):
        self.it = tokenIterator
        self.src = tokenIterator.src
        # charge
        self._next()
        try:
            # start me up
            self.root()
            # if we don't get an exception, we do not have grammar 
            # enough to parse the input. I figure that's an error
            self.error('Parsing did not complete: lastToken: {},'.format(
                self.tokenToString[self.tok],                
            ))
        # Any other exception can float up as an exception i.e. also a 
        # parsing error.
        # They are either GIOLexicalError, or GIOSyntxError
        except StopIteration:
            # All ok
            print('parsed')
            pass
