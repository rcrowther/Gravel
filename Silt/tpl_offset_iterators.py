


# Right, in the first place, we are not interested in
# the label or index return
# That's a specialism
class OffsetIterator():
    pass

class OffsetIteratorIndexedGenerator(OffsetIterator):
    # For large Arrays    
    def __init__(self, size, tpe):
        self.x = size
        self.tpe = tpe
        self.byteSize = tpe.byteSize
        self.offsetSum = -(self.byteSize)
        
    def __iter__(self):
        return self

    def __next__(self):
        if (self.x == 0):
            raise StopIteration
        self.x -= 1
        self.offsetSum += self.byteSize
        return (self.offsetSum, self.tpe)
               
               
               
                
class OffsetIteratorMapCached(OffsetIterator):
    # For labeled Clutchs
    # cache should be OrderedDict(label, type)
    
    def __init__(self, cache):
        self.it = iter(cache.items())
        self.offsetSum = 0
        
    def __iter__(self):
        return self

    def __next__(self):
        thisOffset = self.offsetSum
        label, tpe = next(self.it)
        self.offsetSum += tpe.byteSize
        return (thisOffset, tpe)



class OffsetIteratorListCached(OffsetIterator):
    # For indexed Clutchs 
    # cache should be List(type)
    def __init__(self, cache):
        self.it = iter(cache)
        self.offsetSum = 0
                
    def __iter__(self):
        return self

    def __next__(self):
        thisOffset = self.offsetSum
        tpe = next(self.it)
        self.offsetSum += tpe.byteSize
        return (thisOffset, tpe)
            
