#from gio.CodepointIterators import File, StringLine
#from gio.TokenIterator import TokenIterator
#from gio.TrackingIterator import TrackingIterator


#! A source should understand if it has a filepath or not
#! A source may not have a position
#! There is always a source, even if it is the compiler
class Source:
    '''
    Main interface to parsable naterial.
    Includes a token iterator, and way to retrieve source by line
    (mainly for error reporting)
    '''
    # Path if a file location (or some virtual file etc.)
    srcPath = None
       
    # Yes, I know it's not Pythonic.
    # But it works allwhere. R.C.
    def cmp(self, other):
        return (self.srcPath == other.srcPath)
        
    def lineByIndex(self, lineNum):
        pass

    def locationStr(self):
        '''
        location of this source for display purposes.
        Never empty, even in the case of commandline entry.
        '''
        # e.g. File "<stdin>" (Python), <console> (Scala)
        pass
    
    #def tokenIterator(self, reporter):
        #pass         
    def toString(self):
        return '<Source srcPath:"{}" locationStr:{}>'.format(
            self.srcPath,
            self.locationStr(),
            )
            
    def __repr__(self):
        return self.toString()

         
class FileSource(Source):
    def __init__(self, srcPath):
        self.srcPath = srcPath
        self.lineList = []
                
    def lineByIndex(self, lineNum):
        '''
        Get a line from the file by index.
        Indexes work from 1. 0 is an error.
        Caches the source, for faster calls on the same file.
        Intended for error reporting, not processing.
        @throw error if index is out of range
        @return line is rstrip(), including line ends.
        '''
        assert lineNum > 0, "linenum (from a Position?) < 1"
        if (not self.lineList):
            with open(self.srcPath, 'r') as f:
                self.lineList = f.readlines()
        return self.lineList[lineNum - 1].rstrip()
            
    def locationStr(self):
        return self.srcPath
                    
    #def tokenIterator(self, reporter):
        #it = File(self.srcPath)
        #it = TrackingIterator(it)
        #return TokenIterator(it, reporter, self.srcPath)



class StringSource(Source):
    def __init__(self, line):
        self.line = line

    def lineByIndex(self, lineNum):
        '''
        Get the line.
        The index is disregarded.
        Intended for error reporting, not processing.
        @return line is rstrip(), including line ends.
        '''
        return self.line.rstrip()

    def locationStr(self):
        return '<terminal>'
        
    #def tokenIterator(self, reporter):
        #it = StringLine(self.line)
        #it = TrackingIterator(it)
        #return TokenIterator(it, reporter, self.srcPath)



class StringsSource(Source):
    def __init__(self, strings):
        assert (isinstance(strings, list)), 'Not a list: {}'.format(type(strings))
        self.strings = strings

    def lineByIndex(self, lineNum):
        '''
        Get the line by index.
        Indexes work from 1. 0 is an error.
        Intended for error reporting, not processing.
        @return line is rstrip(), including line ends.
        '''
        assert lineNum > 0, "linenum (from a Position?) < 1"
        return self.strings[lineNum - 1].rstrip()

    def locationStr(self):
        return '<terminal>'
