#!/usr/bin/env python3



class SubBuilder():
    '''
    Like the main builder, but only accepts code.
    Can be used when patches of code need to be picked up and inserted
    elsewhere or repeated e.g. loop unrolling and/or macros.
    Uses the same structure as the main builder, so a direct substitute.

    Elements added to the code section should be for a single line of 
    Assembly code i.e. one complete opcode. The current style 
    inflection code depends on this.
     
    Adding to the main builder is like this,
    b = Builder()
    sB = SubBuilder()
    sb._code.append('')
    b.addAll(sB)
    '''
    def __init__(self):
        self._code = []

    def addAll(self, iterable):
        self._code.extend(iterable)
                
    def result(self):
        return self._code
         
    def __repr__(self):
        return "Builder()"
        
        
        
## Builder
class Builder():
    '''
    Main builder for compilation.
    Includes add methods for the verious sections of an executable 
    object file. These sub-builders are gathered as sets, so that
    repeated addittions will not repeat in final output.
    
    Elements added to the code section should be for a single line of 
    Assembly code i.e. one complete opcode. The current style 
    inflection code depends on this.
    '''
    def __init__(self):
        self._externs = set()
        self._data = set()
        self._rodata = set()
        self._bss = set()
        self._text = []
        self._code = []

    def externsAdd(self, s):
        self._externs.add(s)
        
    def dataAdd(self, s):
        self._data.add(s)
     
    def rodataAdd(self, s):
        self._rodata.add(s)
             
    def bssAdd(self, s):
        self._bss.add(s)
  
    def textAdd(self, s):
        self._text.append(s)
            
    def addAll(self, iterable):
        self._code.extend(iterable)
        
    ## For code, defaults to class implementation
    #x in Python, not reliable
    def __iadd__(self, s):
        #print('s')
        #print(str(s))
        self._code.append(s)
         
    def __repr__(self):
        return "Builder()"


