from gio.LexerBase import LexerBase
from library.encodings.Codepoints import *
import gio.test.word_tokens as Tokens



class WordLexer(LexerBase):

    def scanWord(self):
        commit = self.isAlphabetic()
        if(commit):
            self.tok = Tokens.WORD
            self._loadUntilWhitespaceOrLinefeed()
        return commit
        
    def scanPunctuation(self):
        commit = (self.cp == LINE_FEED or self.cp == COMMA or self.cp == PERIOD)
        if(commit):
            self.tok = Tokens.PUNCTUATION
            #self.skipToken()
            self._next()
        return commit
        
    def getNext(self):
        r = True
        if (self.scanWord()):
            pass
        elif(self.scanPunctuation()):
            pass
        else:
            r = False
        return r
