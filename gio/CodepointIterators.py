
class CodePointIterator:
    '''
    Iterate codepoints from some source.  
    Should:
    ++
    - return unicode codepoints
    - throw StopIteration
    - do any tidy, such as file descriptor closing
    +
    Returned streams will include line ends.
    '''
    def __iter__(self):
        return self
        
        
        
class FileIterator(CodePointIterator):
    # Changes the syntax from read-a-char
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
class StringLineIterator(CodePointIterator):

    def __init__(self, line):
        self.line = line
        self.i = -1
        self.len = len(line)
  
    def __next__(self):
        self.i += 1   
        if (self.i == self.len):
            raise StopIteration
        else:  
            return ord(self.line[self.i])

       
