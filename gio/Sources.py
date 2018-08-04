#from gio.CodepointIterators import File, StringLine
#from gio.TokenIterator import TokenIterator
#from gio.TrackingIterator import TrackingIterator


#! There is always a source, even if it is the compiler
class Source:
    '''
    Main interface to parsable naterial.
    If possible, includes a way to retrieve source by line
    (mainly for error reporting)
    '''
    # Yes, I know it's not Pythonic.
    # But it works allwhere. R.C.
    def cmp(self, other):
        raise NotImplementedError()
        
    def isLinebasedSource(Self):
        '''
        If it is a linebased source, it's worth printing a line
        position.
        '''
        raise NotImplementedError()

    def isFileSource(self):
        '''
        If it is a file source, the source may receive special
        formatting.
        '''
        return False
                
    def lineByIndex(self, lineNum):
        '''
        Get a line from a source by index.
        Indexes work from 1. 0 is an error.
        Intended for error reporting, not processing.
        @throw error if index is out of range
        @return line is rstrip(), including line ends.
        '''
        raise NotImplementedError()

    def locationStr(self):
        '''
        location of this source for display purposes.
        Should never empty, even in the case of commandline entry.
        '''
        # e.g. File "<stdin>" (Python), <console> (Scala)
        raise NotImplementedError()
            
    def toString(self):
        return '<Source locationStr:{}>'.format(
            self.locationStr(),
            )
            
    def __repr__(self):
        return self.toString()



class _BuiltInSource:
    def cmp(self, other):
        return bool(other == self)

    def isLinebasedSource(Self):
        return False
        
    def locationStr(self):
        return '<builtin>'
        
BuiltInSource = _BuiltInSource()
        
        
        
                 
class FileSource(Source):
    def __init__(self, srcPath):
        self.srcPath = srcPath
        self.lineList = []

    # Yes, I know it's not Pythonic.
    # But it works allwhere. R.C.
    def cmp(self, other):
        return (self.srcPath == other.srcPath)

    def isLinebasedSource(Self):
        return True

    def isFileSource(self):
        return True
                                        
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
        # Caches the source, for faster calls on the same file.
        if (not self.lineList):
            with open(self.srcPath, 'r') as f:
                self.lineList = f.readlines()
        return self.lineList[lineNum - 1].rstrip()
            
    def locationStr(self):
        return self.srcPath



class StringSource(Source):
    def __init__(self, line):
        self.line = line

    def isLinebasedSource(Self):
        return True
        
    def lineByIndex(self, lineNum):
        # Linenum is ignored, in action
        return self.line.rstrip()

    def locationStr(self):
        return '<terminal>'



class StringsSource(Source):
    def __init__(self, strings):
        assert (isinstance(strings, list)), 'Not a list: {}'.format(type(strings))
        self.strings = strings

    def isLinebasedSource(Self):
        return True
        
    def lineByIndex(self, lineNum):
        assert lineNum > 0, "linenum (from a Position?) < 1"
        return self.strings[lineNum - 1].rstrip()

    def locationStr(self):
        return '<terminal>'
