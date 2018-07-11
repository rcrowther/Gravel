from Codepoints import *
import Tokens
from reporters.Reporter import Reporter
from reporters.Message import Message
from Position import Position


## TODO:
# Test for end
# Need to test for '$' initially, as used to mark 
# internal-generated names and marked-up operator to alphanumeric transforms. 
#! take a reporter for 'token error'
#! this is for string sources?
#! do stubs '???'
#! two problems:
#! reporter needs a source
#! eagar grabbing of the cp means if we hit EOF,  we can do not know if 
# brackets are closed.
class TokenIterator():
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
    def __init__(self, trackingIterator, reporter, src):
        self.src = src
        self.exhausted = False
        self.reporter = reporter
        self.it = trackingIterator
        self.b = []
        #something dead to start
        self.tok = None
        # by setting the first cp to space, the whitepace skip
        # is triggered, loading the first significant codepoint.
        self.c = SPACE
        self.brackets_closed = True
        # keep track for errors. Start being more useful than end.
        self.start_pos = None
        # offset of a token is the first cp in every token
        # so we need to stash this position as the source is iterated
        self.lineOffset = self.it.lineOffset
        self.lineCount = self.it.lineCount        
        
    #def source(self):
    #    return self.it.source

    def stashOffsets(self):
        self.lineOffset = self.it.lineOffset
        self.lineCount = self.it.lineCount
                
    #def lineOffset(self):
        #return self.lineOffset

    #def lineCount(self):
        #return self.lineCount

    def _next(self):
        #print('_nxt')
        self.c = self.it.__next__()
       
    def textOf(self):
        return ''.join(map(chr, self.b))

    def _clear(self):
        self.b = []

    def _loadUntil(self, cp):
        '''
        Load the builder from current until matching the given codepoint.
        '''
        while(self.c != cp):
            #print('cmmnt ' + str(self.c) + str(chr(self.c)))
            self.b.append(self.c)
            self._next()

    def isWhitespace(self):
        return (self.c <= 32)

    def isAlphabetic(self):
        return ((self.c >= 65 and self.c <= 90) or (self.c >= 97 and self.c <= 122) or self.c == UNDERSCORE)

    def isPunctuation(self):
        return (self.c in Tokens.punctuationCodepoints)

    def isNumeric(self):
        '''
        All latin numbers
        '''
        return (self.c >= 48 and self.c <= 57)

    def scanIdentifier(self):
        '''
        [a-z, A-Z] ~ zeroOrMore(not(Whitespace) | not(Punctuation))
        '''
        if(self.isAlphabetic()):
            self.tok = Tokens.IDENTIFIER 
            while (True):
                self.b.append(self.c)
                self._next()
                # allow most codepoints after the alphabetic,
                # short of whitespace or punctuation
                if (
                    (self.isWhitespace()) or
                    (self.isPunctuation())
                 ):
                    break
            return True
        else:
            return False
          
    def scanPunctuation(self):
        '''
        Matches [punctuation] codepoints.
        ''' 
        if (self.c in Tokens.punctuationCodepointToToken):
            self.tok = Tokens.punctuationCodepointToToken[self.c] 
            self._next()
            return True
        return False

    def scanNumber(self):
        if (self.isNumeric()):
            self.tok = Tokens.INT_NUM
            while(True):
                self.b.append(self.c)
                self._next()
                if(not self.isNumeric()):
                    break

            if (self.c == PERIOD):
                self.tok = Tokens.FLOAT_NUM 
                while(True):
                    self.b.append(self.c)
                    self._next()
                    if(not self.isNumeric()):
                        break
            return True
        else:
            return False

    def scanComment(self):
        if (self.c == HASH):
            self.tok = Tokens.COMMENT              
            self.brackets_closed = False
            self.start_pos = Position(
                self.lineCount, 
                self.lineOffset
                )
            self._next()
            if (self.c == HASH):
               self.tok = Tokens.MULTILINE_COMMENT
               self._next()
               self._loadUntil(HASH)
            else:
               self._loadUntil(LINE_FEED)
            # step over the end delimiters
            self.brackets_closed = True
            self._next()
            return True
        else:
            return False

    def scanString(self):
        if (self.c == ICOMMAS):
            self.tok = Tokens.STRING
            self.brackets_closed = False
            self.start_pos = Position(
                self.lineCount, 
                self.lineOffset
                )
            self._next()
            if (self.c == ICOMMAS):
                self.tok = Tokens.MULTILINE_STRING
                self._next()
                self._loadUntil(ICOMMAS)
            else:
                self._loadUntil(LINE_FEED)
            # step over the end delimiters
            self.brackets_closed = True
            self._next()
            return True
        else:
            return False
    
    def scanOperatorIdentifier(self):
        '''
        [^a-z, A-Z] ~  zeroOrMore(not(Whitespace) | not(Numeric) | not(Alphabetic) | not(Punctuation))
        '''
        while (True):
            self.b.append(self.c)
            self._next()
            if (
                (self.isWhitespace()) 
                or (self.isNumeric())
                or (self.isAlphabetic())
                or (self.isPunctuation())
                ):
                break
        if (self.isNumeric() or self.isAlphabetic()):
            self.tok = Tokens.MONO_OPERATER
        else:
            self.tok = Tokens.OPERATER
        return True

    def skipWhitespace(self):
          while (self.isWhitespace()):
             self._next()
          
    def getNext(self):
        self._clear()
        # skip to non-whitespace
        self.skipWhitespace()
        self.stashOffsets()
        if (self.scanIdentifier()):
            pass
        elif (self.scanPunctuation()):
            pass
        elif (self.scanNumber()):
            pass
        elif (self.scanComment()):
            pass
        elif (self.scanString()):
            pass
        # Note, this is anything that is left?
        else:
            self.scanOperatorIdentifier()
            #pass
        #else:
            # Unscanable. Should never be reached.
            #self.tok = tokens['empty']

    def __iter__(self):
        return self

    def __next__(self):
        #print ('nxt')
        #print(str(self.c))
        try:
            self.getNext()
        except StopIteration as e:
            # catch last token
            if (self.exhausted):
                raise e
            else:
                self.exhausted = True
                #! resolve unclosed brackets for things detected here
                # note that punctuated bracketing is resolved in the
                # parser
                if (not self.brackets_closed):
                    # MULTILINE_COMMENT && STRING 
                    msg = 'Open {} brackets not closed by end of file.'.format(
                    Tokens.tokenToString[self.tok]
                    )
                    self.reporter.error(Message(msg, self.src, self.start_pos))
                raise e
        return self.tok




from gio.Sources import FileSource, StringSource, StringsSource
from gio.CodepointIterators import (
    FileIterator,
    StringIterator,
    StringsIterator
    )
from gio.TrackingIterator import TrackingIterator

def mkTokenIterator(src, reporter):
    it = None
    if (isinstance(src, FileSource)):
        it = FileIterator(src.srcPath)
    elif (isinstance(src, StringSource)):
        it = StringIterator(src.line)
    elif (isinstance(src, StringsSource)):
        it = StringsIterator(src.strings)
    else:
        raise Exception('recieved unknown Source: source type: {}'.format(type(src)))
    return TokenIterator(TrackingIterator(it), reporter, src)
    
