#from Codepoints import LINE_FEED
LINE_FEED = 10

#! with or without lineends
class CodePointIterator:
    '''
    Iterate codepoints from some Source.  
    
    Should:
    ++
    - return unicode codepoints
    - Right strip and replaces linends with (Linuxy) cp = 10
    - throw StopIteration
    - do any tidy, such as file descriptor closing
    +
    Returned streams will include line ends.
    Line ends will be unified to a single codepoint, 
    Codepoints.LINE_FEED.
    '''
    def __iter__(self):
        return self
        
        
# The problem is, doesn't close files on exception       
class FileIteratorUnstripped(CodePointIterator):
    '''
    Much simpler than the usual FileIterator, but bulk loads whole file 
    and will not rstrip()
    '''
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

# The problem is, doesn't close files on exception       
class FileIteratorByLine(CodePointIterator):
    #NB Changes the syntax from read-a-char
    # to __next__-for-a-char iteration
    def __init__(self, path):
        self.path = path
        self.fd = open(path, 'r')
        self.loadNewLine()
        
    def loadNewLine(self):
        self.line = self.fd.readline()
        if (self.line == ''):
            self.fd.close()
            raise StopIteration   
        # ensuring newline
        self.line = self.line.rstrip()
        self.line += chr(LINE_FEED)
        self.charNum = 0
        self.lineCharLen = len(self.line)
        
    def __next__(self):
        if(self.charNum >= self.lineCharLen):
            self.loadNewLine()
        c = self.line[self.charNum]
        self.charNum += 1
        return ord(c)
        
        

class FileIterator(CodePointIterator):
    #NB Changes the syntax from read-a-char
    # to __next__-for-a-char iteration
    def __init__(self, path):
        self.path = path
        self.lineNum = -1
        self.cpNum = 0
        with open(path, 'r') as f:
            self.lineList = f.readlines()
        self.linesLen = len(self.lineList)
        self.lineCPLen = 0
        self.loadNewLine()
        
    def loadNewLine(self):
        self.lineNum += 1
        if (self.lineNum >= self.linesLen):
            raise StopIteration   
        self.line = self.lineList[self.lineNum]
        # ensuring newline
        self.line = self.line.rstrip()
        self.line += chr(LINE_FEED)
        self.cpNum = 0
        self.lineCPLen = len(self.line)
        
    def __next__(self):
        if(self.cpNum >= self.lineCPLen):
            self.loadNewLine()
        c = self.line[self.cpNum]
        self.cpNum += 1
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
