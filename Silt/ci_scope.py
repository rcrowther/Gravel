#!/usr/bin/env python3


import time
from collections import namedtuple

ScopeEntry = namedtuple('ScopeEntry', ['data', 'owner', 'next'])



class SymNameIt():
    def __init__(self, elems, name):
        self.e = elems
        self.name = name
        
    def __iter__(self):
        return self
        
    def __next__(self):
        while(self.e and (self.e.data.name != self.name)):
            self.e = self.e.next
        if (self.e):
            r = self.e.data
            self.e = self.e.next
            return r
        else:
            raise StopIteration()
  
  
class SymOwnerIt():
    def __init__(self, elems, owner):
        self.e = elems
        self.owner = owner
        
    def __iter__(self):
        return self
        
    def __next__(self):
        while(self.e and (self.e.owner != self.owner)):
            self.e = self.e.next
        if (self.e):
            r = self.e.data
            self.e = self.e.next
            return r
        else:
            raise StopIteration()  
  
#! rebane
# Not a scope at all. It's a symbol map (attached to a scope).
class Scope():
    '''
    Handles data scoping.
    Each scope is a way of keying names to data. New values can be added
    to the scope then looked up.
    Key values scan be multiple for the same name. Lookups are in first 
    in, first out order. 
    Nested scopes can be created, which inherit the maps of another
    Scope.
    Lookups can be for either the scope or scope and all super values.
    '''
    #? Lookups need to be in FIFO order.
    # Could use a reverse iterator, but lookup is important.
    # The current solution is to use a linked list. This gives an 
    # efficient prepend, but I find this a poor excuse for a linked list.
    # A split-storage deque may be better, but this will do for now.
    #NB Tests say this is an order slower than a dict
    # But thats Python.
    def __init__(self, datas):
        '''
        A new scope, charged with elems.
        Mainly internal use. See empty() and nestedScope().
        datas
            List of datums to put in a scope. Must have name and data 
            attributres (which would safely be a Symbol)
        '''
        self.elems = None
        for e in datas:
            self.add(e)
        self.depth = 0
        
    @classmethod
    def empty(cls):
        '''
        Create an empty scope.
        '''
        return Scope([])
        
    def addScope(self, scope):
        '''
        Add a scopes definitions to a new scope.
        Only add to a new scope. It overwrites existing definitions.
        '''
        self.elems = scope.elems
        self.depth += 1
    
    #?x using addScope()
    def nestedScope(self):
        scope = Scope(self.elems)
        scope.depth += 1
        return scope
        
    def add(self, data):
        assert hasattr(data, 'name'), f"Data has no attribute 'name', data:{data}'"
        e = ScopeEntry(data, self, self.elems)
        self.elems = e

    def __call__(self, name):
        '''
        Find first data with a matching name attribute.
        Last in wins.
        Also looks in any super-scopes.
        '''
        # lookup was originally keyed to name, but I don't like the
        # duplication, and doubt it affects performance.
        #? Could return NoVar
        e = self.elems 
        while (e and (e.data.name != name)):
            e = e.next
        if (e):
            e = e.data
        return e

    def findAllByName(self, name):
        '''
        Find all data with a matching name attribute.
        Last in first.
        Also looks in any super-scopes.
        '''
        return SymNameIt(self.elems, name)

    def findAllNested(self):
        '''
        Find all data in the near scope.
        Last in first.
        '''
        return SymOwnerIt(self.elems, self)

    def forEachLocal(self, func):
        for data in self.findAllNested():
            func(data)
    
    def forEach(self, func):
        for data in self.elems:
            func(data)
            
    def toList(self):
        '''
        local elements as a list.
        '''
        r = []
        e = self.elems
        while (e and (e.owner == self)):
            r.append( e.data )
            e = e.next
        return r

    def toListAll(self):
        '''
        local elements as a list.
        '''
        r = []
        e = self.elems
        while (e):
            r.append( e.data )
            e = e.next
        return r
                
    def size(self):
        e = self.elems
        i = 0
        while (e):
            i += 1
            e = e.next
        return i
        
    def __repr__(self):
        strList = [e.name for e in self.toList()]
        return f'Scope({ ", ".join(strList)})'
        
        
        
# def main():
    # m = {'a': 5, 'b': 3}
    # sp = Scope([])
    # sp.add(5)
    # sp.add({name:'b'})

    # s = time.perf_counter()
    # m['b']
    # e = time.perf_counter()
    # print(f"Time: {s - e}")
    # s = time.perf_counter()
    # sp.find('b')
    # e = time.perf_counter()
    # print(f"Time: {s - e}")

# if __name__ == "__main__":
    # main()

