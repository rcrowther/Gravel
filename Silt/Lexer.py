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
    LEFT_SQR : Tokens.LSQUARE,
    RIGHT_SQR : Tokens.RSQUARE,
    }

punctuationCodepoints = punctuationCodepointToToken.keys()
    

class Lexer(LexerBase):

    #def __init__(self,  src, trackingIterator, reporter):
    #    super().__init__(src, trackingIterator, reporter)

    def isPunctuation(self):
        return (self.cp in punctuationCodepoints)

    #! think this is how we make '--' '+' etc into identifiers
    def dispatchMathSigns(self):
        '''
        ['+', '-', '*', '/']
        followed by IDENTIFIER,
         ~ zeroOrMore(not(WhitespaceOrLinefeed) | not(Punctuation))
         or by INT/FLOATNUM,
         ~ oneOrMore([0-9]) ~ optional('.' ~ oneOrMore([0-9])
        '''
        # Load the initial symbol so available in textOf()
        if (self.isMathematicalSign()):
            # load this up
            self.b.append(self.cp)

            # try the next codepoint
            self._next()
            if(not self.isNumeric()):
                # assume this is an identifier
                # ids starting witth math signs are a speciality,
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
                self.tok = Tokens.IDENTIFIER 
                return True
            else:
                #assume a number
                self.numberBody()

    #! need to remove plus/minus if go with dispatchMathSigns()
    def scanNumber(self):
        '''
        optional[+=] ~ oneOrMore([0-9]) ~ optional('.' ~ oneOrMore([0-9])
        '''
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
                #self.error(Message.withPos(msg, self.src, self.start_pos))
                self.error(msg)
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
        Match [punctuation] codepoints.
        ''' 
        if (self.cp in punctuationCodepointToToken):
            self.tok = punctuationCodepointToToken[self.cp] 
            self._next()
            return True
        return False

    def scanKV(self):
        '''
        '~' ~ '>'
        '''
        if (self.cp == TILDE):
            self.tok = Tokens.KEY_VALUE              
            self._next()
            if (self.cp == RIGHT_ANGLE):
                self._next()
            else:
                msg = "Stanalone tithe must be followed ny a' >'"
                self.error(msg)
            return True
        return False
        
    def scanRepeat(self):
        '''
        '*'
        '''
        if (self.cp == ASTERISK):
            self.tok = Tokens.REPEAT              
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
        elif (self.scanKV()):
            pass
        elif (self.scanRepeat()):
            pass
        else:
            r = False
        return r
