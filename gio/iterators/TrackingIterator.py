#from Codepoints import LINE_FEED
LINE_FEED = 10

from .CodepointIterators import (
    FileIterator,
    FileIteratorUnstripped,
    StringIterator,
    StringsIterator
)



class TrackingIterator():
    '''
    Iterate codepoints keeping track of positions.
    
    Both LineCount and lineOffset start from  0 (can be adjusted in 
    reporters, but not here).
    lineOffset and lineCount are designed to give the point
    after next().
    
    Passes all source characters, including lineends and whitespace, 
    unmodified.
    
    Should be passed a codepoint iterator
    '''

    def __init__(self, codepointIt):
        self.it = codepointIt
        self.lineCount = 0
        self.lineOffset = -1 
        self.prev = None
        
    def __iter__(self):
        return self
        
    def __next__(self):
        cp = self.it.__next__()
        self.lineOffset += 1
        if (self.prev == LINE_FEED):
            self.lineCount += 1
            self.lineOffset = 0
        #self.prev = self.it.__next__()
        #return self.prev
        self.prev = cp
        return cp


# Forr sanities sake, constuctors
class FileIteratorUnstrippedTracking(TrackingIterator):
    def __init__(self, path):
        super().__init__(FileIteratorUnstripped(path))

class FileIteratorTracking(TrackingIterator):
    def __init__(self, path):
        super().__init__(FileIterator(path))

class StringIteratorTracking(TrackingIterator):
    def __init__(self, line):
        super().__init__(StringIterator(line))

class StringsIteratorTracking(TrackingIterator):
    def __init__(self, strings):
        super().__init__(StringsIterator(strings))
