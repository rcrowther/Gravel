from library.encodings.Codepoints import *
import Tokens
from .reporters.Reporter import Reporter
from .reporters.Message import Message
from .reporters.Position import Position
from .exceptions import GIOLexicalError



## TODO:
# Test for end
# Need to test for '$' initially, as used to mark 
# internal-generated names and marked-up operator to alphanumeric transforms.
#! do stubs '???'
#! problems:
#! eagar grabbing of the cp means if we hit EOF,  we can do not know if 
# brackets are closed.
#? scan errors probably throw as SyntaxError or ValueError, not StopIteration
class LexerBase():
    '''
    Iterate comments, identifiers, numerics, etc.
    Very simple, compared to other efforts, but it works.
    zeroOrMore(zeroOrMore(Space) ~ (
    Comment
    | Number
    | String
    | Punctuation
    | Identifier
    | OperatorIdentifier
    ))
    A few notes:
    - Comment can be single or muti-line
    - Numbers can include the dot
    - Punctuation is always single chars
    - Identifier starts with an alphabetic, can be followed by not 
    (whitespace or number).
    - OperatorIdentifier starts with any non-whitespace, 
    non-alphanumeric. The other major dfference is they will not match
    a numeric.
    
    
    Identifiers stall on punctuation to allow identifiers to push against punctuation. 
    Operator identifiers stall on punctuation and also on numbers, to allow '-20' etc.
    
    Any associated data-as-text-of-token (not for punctuation, but every other token)
    can be accessed through textOf().
    
    Brackets are stripped from MULTILINE_COMMENT and STRING. Warnings 
    are loaded to the Reporter if these brackets are not balanced.
    
    Token iterators are not reusable. See also the factory method
    mkTokenIterator()
    '''
    def __init__(self, src, trackingIterator, reporter):
        self.src = src
        #self.exhausted = False
        self.it = trackingIterator
        self.reporter = reporter
        # To hold data for each token e.g. a string, a number etc.
        self.b = []
        # current token in iterator
        #something dead to start
        self.tok = None
        # by setting the first cp to space, the whitepace skip
        # is triggered, loading the first significant codepoint.
        self.cp = SPACE

        # keep track of token start positions for errors. Token start 
        # position is more useful than current position.
        #NB cant self.stashOffsets() as no next() has been called    
        self.tokenStartOffset = 0
        self.tokenLineCount = 0
        
    def source(self):
        return self.src

    def stashOffsets(self):
        self.tokenStartOffset = self.it.lineOffset
        self.tokenLineCount = self.it.lineCount
                
    #def tokenStartOffset(self):
    #    return self.lineOffset

    #def lineCount(self):
    #    return self.lineCount

    def error(self, msg):
        '''
        Send a message with both source and position.
        Raises GIOLexicalError
        '''
        pos = Position(self.tokenLineCount, self.tokenStartOffset)
        msgKlass = Message.withSrcPos(
            msg, 
            self.src, 
            pos, 
            self.src.lineByIndex(self.tokenLineCount)
        )
        self.reporter.error(msgKlass)
        raise GIOLexicalError()
        
    def _next(self):
        #print('_nxt')
        self.cp = self.it.__next__()
       
    def textOf(self):
        '''
        Return the text of each token
        return 
            the token as text
        '''
        return ''.join(map(chr, self.b))

    def _clear(self):
        '''
        Clear the buffer used to gather token text
        '''
        self.b = []

    def _loadUntil(self, cp):
        '''
        Load the builder from current char until matching the given 
        codepoint.
        
        Used for gathering strings etc. Note that his will gather 
        linefeeds also
        '''
        while(self.cp != cp):
            self.b.append(self.cp)
            self._next()

    def _loadUntilOrLineFeed(self, cp):
        '''
        Load the builder from current char until matching the given 
        codepoint or a linefeed.
        
        Used for gathering strings etc. Note that his will gather 
        linefeeds also
        '''
        while(self.cp != cp and self.cp != LINE_FEED):
            self.b.append(self.cp)
            self._next()
            
    def isWhitespace(self):
        '''
        Not including linefeed.
        '''
        return (self.cp <= 32 and (not self.cp == LINE_FEED))

    def isWhitespaceOrLinefeed(self):
        return (self.cp <= 32)
    
    def skipWhitespace(self):
        '''
        Not including linefeed.
        '''        
        while (self.isWhitespace()):
            self._next()

    def _loadUntilWhitespaceOrLinefeed(self):
        while (not(self.isWhitespaceOrLinefeed())):
            self.b.append(self.cp)
            self._next()

    ## a few general matches
    def isAlphabetic(self):
        '''
        Includes underline
        '''
        return ((self.cp >= 65 and self.cp <= 90) or (self.cp >= 97 and self.cp <= 122) or self.cp == UNDERSCORE)

    def isNumeric(self):
        '''
        Match all latin numbers
        '''
        return (self.cp >= 48 and self.cp <= 57)

    def isPlusMinus(self):
        '''
        Match plus/hyphen-minus latin
        '''
        return (self.cp == 43 or self.cp == 45)

    def isMathematicalSign(self):
        '''
        Match plus/hyphen-minus/asterisk/solidus latin.
        Bear in mind all these codepoints except PLUS have legitimate 
        use elsewhere.Asterix is not even the proper Unicode codepoint 
        for multiplication, though now universally accepted as a 
        substitute. Code may need to differentiate more, for example
        by context, than using a simple match. 
        '''
        return (
            self.cp == PLUS
            or self.cp == HYPHEN_MINUS
            or self.cp == ASTERISK
            or self.cp == SOLIDUS
        )

                       
    def getNext(self):
        '''
        To be overridden
        Search for tokens
        Always starts on a non-whiltespace, non-line-end with 
        text cleared and offsets loaded.
        return 
            true to continue, false to report generic error (token not 
            recognised) and raise StopIteration
        '''
        # All nexessary clearing, skipping, and poitioning, is done
        # in the method that calls this stub.
        # Code here should go hunting for tokens.
        # To fail call self.error(msg)
        # Don't forget a return!
        raise NotImplementedError()

                
    def __iter__(self):
        return self

    def __next__(self):
        self._clear() 
        self.skipWhitespace()
        self.stashOffsets()
        if(not(self.getNext())):
            msg = 'Not recognised as token. last codepoint:{}'.format(self.cp)
            self.error(msg)
        return self.tok




# from gio.Sources import FileSource, StringSource, StringsSource
# from gio.CodepointIterators import (
    # FileIterator,
    # StringIterator,
    # StringsIterator
    # )
# from gio.TrackingIterator import TrackingIterator


    
