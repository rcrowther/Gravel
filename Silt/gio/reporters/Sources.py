
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
        # Compare one source with another for equality.
        raise NotImplementedError()
        
    def isLinebasedSource(self):
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
            
    def __repr__(self):
        return 'Source(locationStr:{})'.format(
            self.locationStr(),
        )


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
        # @srcPath a string (not a File)
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
                                        
    def lineByIndex(self, lineIdx):
        '''
        Get a line from the file by index.
        Indexes work from 1. 0 is an error.
        Caches the source, for faster calls on the same file.
        Intended for error reporting, not processing.
        @throw error if index is out of range
        @return line is rstrip(), including line ends.
        '''
        # Caches the source, for faster calls on the same file.
        if (not self.lineList):
            with open(self.srcPath, 'r') as f:
                self.lineList = f.readlines()
        assert (lineIdx >= 0 and lineIdx < len(self.lineList)), "lineIdx out of range. lineIdx:{}".format(lineIdx)
        return self.lineList[lineIdx].rstrip()
            
    def locationStr(self):
        return self.srcPath



class StringSource(Source):
    def __init__(self, line):
        self.line = line

    def isLinebasedSource(Self):
        return True
        
    def lineByIndex(self, lineNum):
        # Linenum is ignored, in action
        assert (lineNum == 0), "String source recieved non-zero linenum. lineNum:{}".format(lineNum)
        return self.line.rstrip()

    def locationStr(self):
        return '<console>'



class StringsSource(Source):
    '''
    Each string is a line
    '''
    def __init__(self, strings):
        assert (isinstance(strings, list)), 'Not a list: {}'.format(type(strings))
        self.strings = strings

    def isLinebasedSource(Self):
        return True
        
    def lineByIndex(self, lineIdx):
        assert (lineIdx >= 0 and lineIdx < len(self.strings)), "lineIdx out of range. lineIdx:{}".format(lineIdx)
        return self.strings[lineIdx].rstrip()

    def locationStr(self):
        return '<console>'
