

        
# This stack is a little oddly constructed.
# Partially, this is Python. So we have lists, where a raw list 
# implementation would be more likely.
# But mostly,
# What we would like is an in-memory DB of Marks.
# But his is odd, as one of the indexes, Scope, provides key data.
# The current solution is to compose the table into scope.
# The table is not used for much. if anything, at present. But it is
# The base of the structure.
class MarkTable():
    def __init__(self):
        self.underlying = []
        #scopeTree = None
        
    #def find(self, mark):
        #r = None
        #for v in self.underlying:
            #if (mark == v):
                #r = v
                #break
        #return r
                        
    #def _findByName(self, name):
        #r = None
        #for v in self.underlying:
            #if (v.name == name):
                #r = v
                #break
        #return r

    #def _findIndexByName(self, name):
        #r = None
        #for i, v in enumerate(self.underlying):
            #if (v.name == name):
                #r = i
                #break
        #return r
                
    def create(self, mark):
        self.underlying.append(mark)
        
    #def readByName(self, name):
        #return self._findByName(name)       

    def delete(self, mark):
        #! untested
        i = self.underlying.index(mark)
        del( self.underlying[i] )
   
    def size(self):
        return len(self.underlying)



class Scope():
    '''
    A list of Marks.
    
    The record will reject multiple insertions of the same mark.
    '''
    def __init__(self, markTable):
        self.markTable = markTable
        self.depth = 0
        self.parent = None
        self.marks = []
        
    def containsName(self, name):
        return bool(self.findByName(name))

    def findIndexByName(self, name):
        r = None
        for i, v in enumerate(self.marks):
            if (v.name == name):
                r = i
                r1 = v
                break
        return (r, r1)
        
    def findByName(self, name):
        r = None
        for v in self.marks:
            if (v.name == name):
                r = v
                break
        return r
        
    def isEmpty(self):
        return (len(self.marks) < 1)
        
    def createUnique(self, mark):
        '''
        Add a mark to this scope.
        Will reject if a similar name exists.
        
        @return True if added, else False
        '''
        # test unique
        found = self.findByName(mark.name)
        if(not found):
          self.create(mark)
        return bool(not found)

    def create(self, mark):
        '''
        Add a mark to this scope.
        Will reject if a similar name exists.
        
        @return True if added, else False
        '''
        mark.scope = self
        self.markTable.create(mark)
        self.marks.append(mark)
                
    def readByName(self, name):
        return self.findByName(name)

    def deleteByName(self, name):
        pos, mark = self.findIndexByName(name)
        del(self.marks[pos])
        self.markTable.delete(mark)

    def newChildScope(self):
        '''
        Return a new scope, a child of this.
        For the new scope, sets the parent (this), the depth, and 
        copies this scope's marks.
        Mark data must be entered by flat downward traversal. If depths
        are recursed first, lower levels will not recieve later (higher)
        scope addittions.
        '''
        s = Scope(self.markTable)
        s.marks = [e for e in self.marks]    
        s.parent = self
        s.depth = self.depth + 1
        return s

    def size(self):
        return len(self.marks)

    def toList(self):
        return [m for m in self.marks]
                
    def toString(self):
        return 'Scope("{}")'.format('", "'.join([m.name for m in self.marks]))

    def __repr__(self):
        return self.toString()
        
        
ExpressionScope = Scope(MarkTable())
KindScope = Scope(MarkTable())
