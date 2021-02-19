import Tokens
from Codepoints import *
from Position import Position, toPositionString
from Message import messageWithPos


punctuationCodepoints = [COLON, LEFT_BRACKET, RIGHT_BRACKET]

# dict of codepoint to token
# i.e. Codepoints.PERIOD (46) : Tokens.PERIOD (40)
#! do something about ICOMMA (this uses ICOMMAS)
punctuationCodepointToToken = {
    COLON : Tokens.COLON,
    LEFT_BRACKET : Tokens.LBRACKET,
    RIGHT_BRACKET : Tokens.RBRACKET,
    }
    
#? want line indications on these errors?
#! comma skipping
class TokenIterator():
    def __init__(self, src, trackingIterator):
        self.src = src
        self.it = trackingIterator
        # To hold data for each token e.g. a string, a number etc.
        self.b = []
        # current token in iterator
        #something dead to start
        self.tok = None
        # by setting the first cp to space, the whitepace skip
        # is triggered, loading the first significant codepoint.
        self.c = SPACE
        # keep track for errors. Start being more useful than end.
        self.start_pos = None
        # offset of a token is the first cp in every token
        # so we need to stash this position as the source is iterated
        self.stashOffsets()  
        
    def stashOffsets(self):
        self.lineOffset = self.it.lineOffset
        self.lineCount = self.it.lineCount
        
    def _next(self):
        #print('_nxt')
        self.c = self.it.__next__()

    def textOf(self):
        return ''.join(map(chr, self.b))

    def _clear(self):
        self.b = []
        
    def _loadUntil(self, cp):
        '''
        Load the builder from current char until matching the given 
        codepoint.
        
        Used for gathering strings and ids.
        '''
        while(self.c != cp):
            #print('cmmnt ' + str(self.c) + str(chr(self.c)))
            self.b.append(self.c)
            self._next()

    def isWhitespace(self):
        return (self.c <= 32 and (not self.c == LINE_FEED))

    def isWhitespaceOrLinefeed(self):
        return (self.c <= 32)

    def isAlphabetic(self):
        return ((self.c >= 65 and self.c <= 90) or (self.c >= 97 and self.c <= 122) or self.c == UNDERSCORE)

    def isNumeric(self):
        '''
        All latin numbers
        '''
        return (self.c >= 48 and self.c <= 57)

    def isPlusMinus(self):
        '''
        All latin numbers
        '''
        return (self.c == 43 or self.c == 45)

    def isPunctuation(self):
        return (self.c in punctuationCodepoints)
        
    def scanIdentifier(self):
        '''
        [a-z, A-Z] ~ zeroOrMore(not(Whitespace) | not(Punctuation))
        '''
        if(self.isAlphabetic() or self.c == AT):
            self.tok = Tokens.IDENTIFIER 
            while (True):
                self.b.append(self.c)
                self._next()
                # allow most codepoints after the alphabetic,
                # short of whitespace or punctuation
                if (
                    (self.isWhitespaceOrLinefeed()) or
                    (self.isPunctuation())
                 ):
                    break
            return True
        else:
            return False

    def skipWhitespace(self):
        #print("whitespace {}".format(self.isWhitespace()))  
        while (self.isWhitespaceOrLinefeed()):
            self._next()

    def scanNumber(self):
        if (self.isNumeric() or self.isPlusMinus()):
            self.start_pos = Position(
                self.src,
                self.lineCount, 
                self.lineOffset
                )
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
            if (not(
                (self.isWhitespaceOrLinefeed()) or
                (self.isPunctuation())
             )): 
                msg = messageWithPos(
                    self.start_pos,
                    'Token scanned as a number not ends with whitespace or punctuation'
                ) 
                #self.reporter.error(Message.withPos(msg, self.src, self.start_pos))
                #raise StopIteration
                raise SyntaxError(msg)
                
            return True
        else:
            return False
            
          
    def scanPunctuation(self):
        '''
        Matches [punctuation] codepoints.
        ''' 
        if (self.c in punctuationCodepointToToken):
            self.tok = punctuationCodepointToToken[self.c] 
            self._next()
            return True
        return False
        
    def scanString(self):
        if (self.c == ICOMMAS or self.c == ICOMMA):
            isSingle = (self.c == ICOMMA)  
            self.tok = Tokens.STRING
            self.start_pos = Position(
                self.src,
                self.lineCount, 
                self.lineOffset
                )
            self._next()
            if(isSingle):
                #! this should be  self._loadUntil(ICOMMA or NEWLINE)
                self._loadUntil(ICOMMA)
            else:
                if(not self.c == ICOMMAS):
                    msg = messageWithPos(
                        self.start_pos,
                        'Double inverted comma scanned as string start but not followed with double inverted commas'
                    ) 
                    #self.reporter.error(Message.withPos(msg, self.src, self.start_pos))
                    raise SyntaxError(msg)
                self._next()
                if (self.c == ICOMMAS):
                    self.tok = Tokens.MULTILINE_STRING
                    self._next()
                self._loadUntil(ICOMMAS)
            # step over the end delimiter
            self._next()
            return True
        else:
            return False

    def scanComment(self):
        if (self.c == HASH):
            self.tok = Tokens.COMMENT              
            self.start_pos = Position(
                self.src,
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
            self._next()
            return True
        else:
            return False
            
    def scanIdentifier(self):
        '''
        [a-z, A-Z] ~ zeroOrMore(not(Whitespace) | not(Punctuation))
        '''
        if(self.isAlphabetic() or self.c == AT):
            self.tok = Tokens.IDENTIFIER 
            while (True):
                self.b.append(self.c)
                self._next()
                # allow most codepoints after the alphabetic,
                # short of whitespace or punctuation
                if (
                    (self.isWhitespaceOrLinefeed()) or
                    (self.isPunctuation())
                 ):
                    break
            return True
        else:
            return False
            
    def getNext(self):
        self._clear()
        #print("getNext")
        # skip to non-whitespace
        self.skipWhitespace()
        #print("skipped")
        self.stashOffsets()
        if (self.scanNumber()):
            pass
        elif (self.scanString()):
            pass
        elif (self.scanPunctuation()):
            pass
        elif (self.scanComment()):
            pass
        elif (self.scanIdentifier()):
            pass
        else:
            # Unscanable. Should never be reached
            self.start_pos = Position(
                self.src,
                self.lineCount, 
                self.lineOffset
                )
           #msg = 'Codepoint can not be recognised as token; codepoint:{}'.format(self.c)
            msg = messageWithPos(
                self.start_pos,
                'Codepoint can not be recognised as token; codepoint:{}'.format(self.c)
            ) 
            raise ValueError(msg)

    def __iter__(self):
        return self
        
    def __next__(self):
        self.getNext()
        return self.tok
        
