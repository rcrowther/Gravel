from gio.SyntaxerBase import SyntaxerBase
WORD = 3
PUNCTUATION = 4


class WordSyntaxer(SyntaxerBase):

    def word(self):
        commit = (self.isToken(WORD))
        if (commit):
            name = self.textOf()
            print(name)
            self._next()
        return commit

    def punctuation(self):
        commit = (self.isToken(PUNCTUATION))
        if (commit):
            name = self.textOf()
            print(name)
            self._next()
        return commit
        
    def seqContents(self):
        '''
        Used for body contents.
        Allows definitions.
        '''
        while(
            self.word() or
            self.punctuation()
        ):
            pass
            #? what are we doing here at the end?
            #if (len(lst) > 1):
            #    lst[-1].prev = lst[-2]
        return True

    def root(self):
        self.seqContents()
    
