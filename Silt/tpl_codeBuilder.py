#!/usr/bin/env python3


class FuncBuilder():
    def __init__(self, name):
        self.name = name
        self._code = []
        self.stackAllocSize = 0
        self.heapAllocSize = 0
        
    def __iadd__(self, s):
        self._code.append(s)
        return self
         
    def __repr__(self):
        return "FuncBuilder(name:{})".format(self.name)

              
## Builder
class Builder():
    def __init__(self):
        self._externs = set()
        self._data = set()
        self._rodata = set()
        self._bss = set()
        self._text = []
        self._code = []
        self.currentFunc = None
        self.funcs = []


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

    def funcBegin(self, name):
        if (self.currentFunc):
            raise  ValueError('Function not closed: func: {}'.format(self.currentFunc))
        self.currentFunc = FuncBuilder(name)

    #! dont like this arch code in the builder
    #? Why not list funcdata and resolve later?
    def funcEnd(self):
        # build the func data into the main builder
        ## jump label
        # self._code.append('{}:'.format(self.currentFunc.name))

        # ## allocations
        # stackAllocSize = self.currentFunc.stackAllocSize 
        # if(stackAllocSize > 0):
            # self._code[0] = "rsp - {}".format(stackAllocSize)
        # heapAllocSize = self.currentFunc.heapAllocSize 
        # if(heapAllocSize > 0):
            # self._code[1] =  "mov {}, {}".format(cParameterRegister[0], heapAllocSize)
            # self._code[2] =  "call malloc"

        # ## code body
        # self._code.extend(self.currentFunc._code)

        # # return
        # self._code.append('ret')
        
        # zero
        self.funcs.append( self.currentFunc )
        self.currentFunc = None

    def stackAllocAdd(self, s, byteSize):
        self.currentFunc += s
        self.currentFunc.stackAllocSize += byteSize

    def heapAllocAdd(self, s, byteSize):
        self.currentFunc += s
        self.currentFunc.heapAllocSize += byteSize
                
    ## For code, defaults to class implementation
    def __iadd__(self, s):
       #self._code.append(s)
       self.currentFunc += s
       return self
         
    def __repr__(self):
        return "Builder()"


