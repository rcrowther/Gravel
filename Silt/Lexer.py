import Tokens
from library.encodings.Codepoints import *
from gio.LexerBase import LexerBase

#punctuationCodepoints = [COLON, LEFT_BRACKET, RIGHT_BRACKET]

# dict of codepoint to token
# i.e. Codepoints.PERIOD (46) : Tokens.PERIOD (40)
#! do something about ICOMMA (this uses ICOMMAS)
punctuationCodepointToToken = {
    COMMA : Tokens.COMMA,
    LINE_FEED : Tokens.LINEFEED,
    COLON : Tokens.COLON,
    LEFT_BRACKET : Tokens.LBRACKET,
    RIGHT_BRACKET : Tokens.RBRACKET,
    }

punctuationCodepoints = punctuationCodepointToToken.keys()
    

class Lexer(LexerBase):

    #def __init__(self,  src, trackingIterator, reporter):
    #    super().__init__(src, trackingIterator, reporter)

    def isPunctuation(self):
        return (self.cp in punctuationCodepoints)
        
    def scanNumber(self):
        if (self.isNumeric() or self.isPlusMinus()):
            self.tok = Tokens.INT_NUM
            while(True):
                self.b.append(self.cp)
                self._next()
                if(not self.isNumeric()):
                    break

            if (self.cp == PERIOD):
                self.tok = Tokens.FLOAT_NUM 
                while(True):
                    self.b.append(self.cp)
                    self._next()
                    if(not self.isNumeric()):
                        break
            if (not(
                (self.isWhitespaceOrLinefeed()) or
                (self.isPunctuation())
             )): 
                msg = 'Token scanned as a number not ends with whitespace or punctuation'
                self.error(Message.withPos(msg, self.src, self.start_pos))
                
            return True
        else:
            return False
            

    def scanString(self):
        if (self.cp == ICOMMAS or self.cp == ICOMMA):
            self.tok = Tokens.STRING
            isSingle = (self.cp == ICOMMA)  
            self._next()
            if(isSingle):
                self._loadUntilOrLineFeed(ICOMMA)
            else:
                if(not self.cp == ICOMMAS):
                    msg = 'Inverted commas scanned as string start but not followed with inverted commas'
                    self.error(msg)
                self._next()
                self._loadUntil(ICOMMAS)
            # step over the end delimiter
            self._next()
            return True
        else:
            return False

          
    def scanPunctuation(self):
        '''
        Matches [punctuation] codepoints.
        ''' 
        if (self.cp in punctuationCodepointToToken):
            self.tok = punctuationCodepointToToken[self.cp] 
            self._next()
            return True
        return False

    def scanComment(self):
        if (self.cp == HASH):
            self.tok = Tokens.COMMENT              
            self._next()
            if (self.cp == HASH):
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
        [a-z, A-Z] ~ zeroOrMore(not(WhitespaceOrLinefeed) | not(Punctuation))
        '''
        if(self.isAlphabetic() or self.cp == AT):
            #? isProtoSymbol is a deep speciality of this tokeniser.
            # If an identifier starts with AT, it is scanned with 
            # identifier logic, but tokened as a string.
            # This will feed the syntaxer with a string, to form 
            # symbols, thus addressing the issue that when a symbol is
            # formed, the id is really a string, not an initialized
            # symbol
            #isProtoSymbol = (self.cp == AT)
            while (True):
                self.b.append(self.cp)
                self._next()
                # allow most codepoints after the alphabetic,
                # short of whitespace or punctuation
                if (
                    (self.isWhitespaceOrLinefeed()) or
                    (self.isPunctuation())
                 ):
                    break
            # if (isProtoSymbol):
                # self.tok = Tokens.STRING
                # if (len(self.b) < 2):
                    # msg = '"@" char stands alone.\n    This codepoint indicates a string intended to create a symbol. Add a name or remove?'
                    # self.error(msg)
                # self.b = self.b[1:]
            # else:
            self.tok = Tokens.IDENTIFIER 
            return True
        else:
            return False
            
    def getNext(self):
        r = True
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
            r = False
        return r
