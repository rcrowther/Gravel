from Marks import Mark, globalPackage

#! replace current Mark table with this.
#? Where are these held? Once again Scala compiler is impenetrable.
# The Namer says a context, presumably part of the Compilation Unit.
#? Investigate how a LISP holds it's context---with values also?
#? LISP uses Lazy discovery?
#? Why is anything deleted from the symboltable?
#? Seems several reasons, like erasure, but none appear to be central,
#? maybe type specialize
#? From Scala. The only thing I learn here are,
# - symbols can be repeated in scopes. They are resolved lazy, not eagar.
# - lookup is important
# "After flatten, all classes are owned by a PackageClass"
#? enclClass - set in the compiler? see note ref above
#? outerClass
#? Do we find a symbols owner, then look for the matching Scope? Or
#? is that through 'package class'. Where do wee find the new scope?

#? GUESSES:
#? no need to match types. This is always known because of namespacing.
#? Scala does not eagarly test for name clashes because of the 
#? possibility of switching owner. Gravel will (and it will likly kill
#? us sometime, but I can't help but think that eagar testing is cleaner
#? and faster).

#? why is the parent scope in every entry?
#! List structure with None is a pain. (if (None) starts to eveything) 
class ScopeEntry():
    '''
    Link data into a list with an owner.
    '''
    # Also, the wrapping can handlle other possibilities e.g.
    # - if we boost the simple 'name' to become a record of data
    def __init__(self, mark, parent):
        assert isinstance(mark, Mark), "Parameter is not a Mark: kind:{}".format(type(mark))
        assert isinstance(parent, Scope), "Parameter is not a Scope: kind:{}".format(type(owner))
        self.mark = mark
        self.parent = parent
        # ScopeEntry
        self.next = None
        self
        
    def clone(self):
        return ScopeEntry(self.mark, self.parent)
        
    def toString(self):
        #return "ScopeEntry(mark:{} parent:{})".format(
            #self.mark,
            #self.parent
            #)
        return self.mark.toString()
                        
    def __repr__(self):
        return self.toString()


#? Scala has unlink
#? Scala has a cache of entries
#? Scala has a hash for names
#? Scala has a cache of size
#? Scala:
#? Con
#? Very slow for lookups, esp. in Python
#? Symbol data must be entered by flat downward traversal. If depths
#? are recursed first, lower levels will not recieve tail upper
#? level symbols 
#? Pro
#? links different scopes together by linking lists. Very natural.
#? Can unlink easily
#? Lazy Scala lookups can handle parent modification.
class Scope():
    '''
    A list of Marks.
    
    The record can handle multiple insertions of the same mark.
    '''
    def __init__(self, entries = None):
        
        self.entries = None
        if (entries):
            e = entries
            while(e):
                self.add( e.clone() )  
                e = e.next          
        self.depth = 0

    def isEmpty(self):
      return (self.size() < 1)

    def add(self, entry):
        assert isinstance(entry, ScopeEntry), "Parameter is not a ScopeEntry: kind:{}".format(type(entry))
        e = self.entries
        if (not e):
            self.entries = entry
            return
        while(e.next):
            e = e.next
        e.next = entry

    def addMark(self, mark):
        self.add(ScopeEntry(mark, self))
        return mark

    def addUniqueMark(self, mark):
        #? slow, do in one pass
        assert (not self.findMark(mark.name)), "name exists: mark:{}".format(mark)
        return self.addMark(mark)
        
    def addMarkIfNew(self, mark):
        m = self.findMark(mark.name)
        if (not m):
            m = self.addMark(mark)
        return m
        
    def containsName(self, name):
        return bool(self.findEntry(name))

    def find(self, entry):
        assert isinstance(entry, ScopeEntry), "Parameter is not a ScopeEntry: kind:{}".format(type(entry))

    def findEntry(self, name):
        '''
        Find the first occurence of a name.
        Note that names can appear multiple times
        '''
        e = self.entries
        while (e and (e.mark.name != name)):
            e = e.next
        return e

    #? for lazy detection
    def findNextEntry(self, entry):
        '''
        Find the next occurence of a name.
        '''
        assert isinstance(entry, ScopeEntry), "Parameter is not a ScopeEntry: kind:{}".format(type(entry))
        e = entry.next
        name = entry.mark.name
        while (e and (e.mark.name != name)):
            e = e.next
        return e
        
    def findMark(self, name):
        '''
        @return NoSymbol
        '''
        e = self.findEntry(name)
        if (e):
            return e.mark
        return None
        
    def newChildScope(self):
        s = Scope(self.entries)
        #s.entries = [s for s in self.entries]
        s.depth = self.depth + 1
        return s
                

        


    #def deleteEntry(self, entry):
        #for e in self.entries:
            #if (e.next == entry):
                #break
        #e.next = entry.next

    #def deleteName(self, name):
        #entry = self.findName(name)
        #while (entry):
            #self.deleteEntry(entry)
            #e = self.findEntry(entry)
              

        
    #def isSameScope(other):
      #? All this does is check symbols are same as other

    #def isChild(self, other):
      #? All this does is check symbols are within other

    def _calcSize(self):
        s = 0
        e = self.entries
        while (e):
            s += 1
            e = e.next
        return s

    
    def size(self):
        return self._calcSize()

    def toList(self):
        '''
        All entries in this scope, in order of insertion.
        '''
        b = []
        e = self.entries
        while (e):
            b.append(e)
            e = e.next
        return b
                    
    def toString(self):
        #? Scala filters for definition Marks only
        return "Scope({} depth:{})".format(
            self.toList(),
            self.depth   
            )
            
    def __repr__(self):
        return self.toString()
        
            
                
class _GlobalScope(Scope):
    def toString(self):
        return "GlobalScope"
            
globalScope = _GlobalScope()
