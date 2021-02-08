#!/usr/bin/env python3


# class FuncBuilder():
    # def __init__(self, name, returnAuto):
        # self.name = name
        # self._code = []
        # self.stackAllocSize = 0
        # self.heapAllocSize = 0
        # self.returnAuto = returnAuto
        
    # def __iadd__(self, s):
        # self._code.append(s)
        # return self
         
    # def __repr__(self):
        # return "FuncBuilder(name:{}, returnAuto:{})".format(self.name, self.returnAuto)

              
# ## Builder
# class Builder():
    # def __init__(self):
        # self._externs = set()
        # self._data = set()
        # self._rodata = set()
        # self._bss = set()
        # self._text = []
        # self._code = []
        # self.currentFunc = None
        # self.funcs = []
        # self.funcNames = []

    # def externsAdd(self, s):
        # self._externs.add(s)
        
    # def dataAdd(self, s):
        # self._data.add(s)
     
    # def rodataAdd(self, s):
        # self._rodata.add(s)
             
    # def bssAdd(self, s):
        # self._bss.add(s)
  
    # def textAdd(self, s):
        # self._text.append(s)

    # def funcBegin(self, name, returnAuto):
        # #print('funcBegin')
        # if (self.currentFunc):
            # raise ValueError('Function not closed: func: {}'.format(self.currentFunc))
        # self.currentFunc = FuncBuilder(name, returnAuto)

    # def funcEnd(self):
        # #print('funcEnd')
        # funcName = self.currentFunc.name 
        # if (not(funcName in self.funcNames)):       
            # self.funcs.append( self.currentFunc )
            # self.funcNames.append( funcName )
        # else:
            # raise ValueError('Two funcs, same name: name: {}'.format(self.currentFunc.name))
            
        # # zero
        # self.currentFunc = None

    # def stackAlloc(self, byteSize):
        # self.currentFunc.stackAllocSize += byteSize

    # def heapAlloc(self, byteSize):
        # self.currentFunc.heapAllocSize += byteSize
                
    # ## For code, defaults to class implementation
    # def __iadd__(self, s):
        # #print('s')
        # #print(str(s))
        # self.currentFunc += s

        # return self
         
    # def __repr__(self):
        # return "Builder()"


   
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


