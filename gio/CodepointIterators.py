from Codepoints import LINE_FEED


class CodePointIterator:
    '''
    Iterate codepoints from some Source.  
    
    Should:
    ++
    - return unicode codepoints
    - throw StopIteration
    - do any tidy, such as file descriptor closing
    +
    Returned streams will include line ends.
    Line ends will be unified to a single codepoint, 
    Codepoints.LINE_FEED.
    '''
    def __iter__(self):
        return self
        
        
#! assumes Linuxy Python by assuming line-end is codepoint LINE_FEED         
class FileIterator(CodePointIterator):
    #NB Changes the syntax from read-a-char
    # to __next__-for-a-char iteration
    def __init__(self, path):
        self.path = path
        self.fd = open(path, 'r')
        line = self.fd
        
    def __next__(self):
        c = None
        c = self.fd.read(1)
        if (not c):
            self.fd.close()
            raise StopIteration
        return ord(c)



#$ Clumsy for Python, but keeping it generic. 
class StringIterator(CodePointIterator):

    def __init__(self, line):
        # ensuring newline
        self.line = line.rstrip()
        self.line += chr(LINE_FEED)
        self.i = 0
        self.lineLen = len(self.line)
  
    def __next__(self):
        if (self.i >= self.lineLen):
            raise StopIteration
        else:  
            r = ord(self.line[self.i])
            self.i += 1
            return r


       
class StringsIterator(CodePointIterator):

    def __init__(self, strings):
        assert (len(strings) > 0), "supplied 'strings' data has no content"
        self.strings = strings
        # ensure line ends
        self.strings = [line.rstrip() + chr(LINE_FEED) for line in self.strings]
        self.lineI = 0
        self.line = self.strings[0]
        self.linesLen = len(self.strings)
        self.cpI = 0
        self.lineLen = len(self.line)
  
    def _nextLine(self):
        self.lineI += 1
        if (self.lineI >= self.linesLen):
            raise StopIteration
        self.line = self.strings[self.lineI]
        self.lineLen = len(self.line)
        self.cpI = 0
 
    def __next__(self):
        if (self.cpI >= self.lineLen):
            self._nextLine()
        r = ord(self.line[self.cpI])
        self.cpI += 1   
        return r
