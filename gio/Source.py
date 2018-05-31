from gio.TokenIterator import TokenIterator
from gio.CodepointIterators import File
from gio.TrackingIterator import TrackingIterator
#from TokenIterator import TokenIterator



class Source:
    '''
    Includes a token iterator, as main interface to
    parsable naterial
    '''
    def __init__(self, srcPath):
        '''
        Require a path, of some kind
        For user display, amongst other uses. 
        '''
        pass
        

    def tokenIterator(self):
         '''
         Returns a token iterator for the source
         '''
         pass
         
         
         
class FileSource:
    def __init__(self, srcPath):
        self.srcPath = srcPath
        
    def tokenIterator(self, reporter):
         it = File(self.srcPath)
         it = TrackingIterator(it)
         return TokenIterator(it, reporter, self.srcPath)
