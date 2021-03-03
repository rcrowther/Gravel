#!/usr/bin/env python3



## Builder
class Builder():
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
                
    ## For code, defaults to class implementation
    def __iadd__(self, s):
        #print('s')
        #print(str(s))
        self._code.append(s)
         
    def __repr__(self):
        return "Builder()"


