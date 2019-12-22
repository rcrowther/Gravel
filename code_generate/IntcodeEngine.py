#!/usr/bin/env python3

import collections

#? Last malloc can stay on its reg, but only if no func calls? (is that woth it?)


# C++ name mangling
# http://itanium-cxx-abi.github.io/cxx-abi/abi.html#demangler
# Will we be calling in on C++ mangled names? I don't think so.
# Beyond that, what name mangling do we need?
#? Always do returns
#?
typeEncoding = {
    "void": "v" ,
    #"wchar_t": "w" ,
    "bool": "b" ,
    #"char": "c" ,
    #"signed char": "a" ,
    "int8": "a" ,
    #"unsigned char": "h" ,
    "uint8": "h" ,
    #"short": "s" ,
    "int16": "s" ,
    #"unsigned short": "t" ,
    "uint16": "t" ,
    #"int": "i" ,
    #"unsigned int": "j" ,
    #"long": "l" ,
    "int32": "l" ,
    #"unsigned long": "m" ,
    "uint32": "m" ,
    #"long long: "x" , __int64",
    "int64": "x" ,
    #"unsigned long long: "y" , __int64",
    "uint64": "y" ,
    #"__int128": "n" ,
    "int128": "n" ,
    #"unsigned __int128": "o" ,
    "uint128": "o" ,
    #"float": "f" ,
    "float32": "f" ,
    #"double": "d" ,
    "float64": "d" ,
    #"long double: "e" , __float80",
    #"__float128": "g" ,
    "addr": "R"
    }    
       
def mangleScope(nameList):
    scopeB = []
    if (len(nameList) > 0):
        scopeB = ["N"]
        for n in nameList:
            scopeB.append(str(len(n)))          
            scopeB.append(n) 
    return scopeB
    
def mangleFunc(scopeB, name, typeList):
    scopeB.append(str(len(name)))          
    scopeB.append(name) 
    scopeB.append("E")
    typeB = []
    first = True
    for t in typeList:
        tEncode =  ''
        if (not first):
            tEncode =  '|'
        first = False
        if not t in typeEncoding:
            tEncode += t
        if t in typeEncoding:
            tEncode += typeEncoding[t]
        typeB.append(tEncode)
    return "-Z{}{}".format("".join(scopeB), "".join(typeB))


# func entry
# If there are any following calls, then parameters into a function 
# must be localised, or parameter data will be lost.
# True even if a one off into one action
# But not true if paerams used for acess or arithmetic, etc.
#? This would be more efficient to be only to the parameter depth of the
# called functions?
# both below

#allLocals = List()
# class Local():
    # def __init__(self):
        # self.isParam = False 
        # self.param = None
        # self.inCorrectPosition = False 
        # self.liveActCount = 0
        # self.isParamLocal = False
        # self.localIdx = 0
        # self.liveDepth = 0
        # self.location = 0
        
# allLocals = []
# if (not func.isLeafCode):    
    # #func.localiseParameters
    # i = 0
    # for local in allLocals:
        # # if true local can stay on param. May need defending.
        # local.isParamLocal = (isParam and local.inCorrectPosition and local.liveActCount > 2)

class RegAlloc:
    def __init__(self, idx, isReg, location):
        self.idx = idx
        self.isReg = isReg
        self.location = location
        
    def __repr__(self):
        return "RegAlloc(idx:{}, isReg:{}, location:{})".format(
            self.idx, self.isReg, self.location
            ) 
            
StartStop = collections.namedtuple("StartStop", "isStart idx isParam")
def startStopStart(idx):
    return StartStop(True, idx, False)

def startStopUse(idx):
    return StartStop(False, idx, False)

def startStopParamDeclare(idx):
    return StartStop(True, idx, True)

def startStopParamUse(idx):
    return StartStop(False, idx, True)
        
# List(startStop)
#startStops = []
ParamRegisters = [  
    "rdi",
    "rsi",
    "rdx",
    "rcx",
    "r8",
    "r9", 
    ]
    
NonParamRegisters = [   
    "rbx",
    # stack ptr
    #"r10",
    #"r11",
    "r12",
    "r13",
    "r14",
    "r15",
    ]
        



class StartStopBuilder():
    # Filter data usage to first start and stop
    #
    def __init__(self):
        self.startStops = []
        self.maxIdx = 0
        
    def paramDeclare(self, idx):
        self.startStops.append(startStopParamDeclare(idx))

    def paramUse(self, idx):
        self.startStops.append(startStopParamUse(idx))        
        
    def firstUse(self, idx):
        self.startStops.append(startStopStart(idx))
    
    def use(self, idx):
        self.startStops.append(startStopUse(idx))
        if (idx > self.maxIdx):
            self.maxIdx = idx
        
    def result(self):
        b = []
        usageEcountered = [False for a in range(0, (self.maxIdx + 1))]
        for ss in reversed(self.startStops):
            if (ss.isStart): 
                b.append(ss)
            if ((not ss.isStart) and (not usageEcountered[ss.idx])):
                b.append(ss)
                usageEcountered[ss.idx] = True
        b.reverse()
        return b

    def __repr__(self):
        return "StartStopBuilder(startStops:{}, maxIdx:{})".format(
            self.startStops, self.maxIdx
            )         
        
def parameterAlloc(paramData, localAllocs, startStopB):
            
    if (action.isLeaf or action.callCount < 3):
        # leave on the parameter
        # do not scan for parameter vars
        # load localAlloc data
        #? stopStart not required? Yes, we need to know whee to stop to stop protecting.
        for i, p in enumerate(paramData):
            localAllocs.append(RegAlloc(i, True, paramRegisters[i]))
    else:
        # alloc stash locals
        for i, p in enumerate(paramData):
            startStopB.firstUse(i)
        #! how to generate load code?
    
# Right. Need to know what to do with this gear.
# locals will be replaced with local alloc.
#? params different? but not used differently? so include?
# params need to know if using direct call (so needs protection)
# or offload
# offloaded params act like a local
#isParam isOffloaded
# So whenever meet the name, 
# if offloaded is the idx location
# if not offloaded is the cParam reg
# caveat, needs to generate code for offloading
# so it only needs to know the register
def parametersAllocate(paramCount, paramRegisters, startStopB, offload):
    localAllocs = []

    if (offload):
        # params become locals to allocate.
        i = 0
        while(i < paramCount):
            startStopB.firstUse(i)        
            i += 1
        
    if (not offload):
        # straight on localAllocs
        i = 0
        while(i < paramCount):
            reg = paramRegisters[i]
            localAllocs.append(RegAlloc(i, True, reg))
            i += 1
            
def localsAllocate(
    nonParamRegisters, 
    paramRegisters, 
    startStops, 
    offloadParams
    ):
    # Make allocation decisions from a startStopList
    #
    paramRegisters = ParamRegisters.copy()
    paramRegisters.reverse()
    offsetPtr = 0
    # the following hold currently free storage places
    freeNonParamregisters = nonParamRegisters.copy()
    freeNonParamregisters.reverse()
    freeParamReg = []
    freeOffsets = []
    # following holds usage data
    UsedParamReg = set()
    UsedNonParamReg = set()
    # container for final decisions
    localAllocs = []
    
    for ss in startStops:
        # NB if this first test fails, params are treated
        # as a local variable, and alllocated accordingly
        if (ss.isParam and (not offloadParams)):
            #! not dealing with offsets/stack storage
            if (not ss.isStart):
                # register is now free
                alloc = localAllocs[ss.idx]
                if (alloc.isReg):
                    freeParamReg.append(alloc.location)                
            if (ss.isStart):
                reg = paramRegisters.pop()            
                UsedParamReg.add(reg)           
                localAllocs.append(RegAlloc(ss.idx, True, reg))
        else:
            if (not ss.isStart):
                # register is now free
                alloc = localAllocs[ss.idx]
                if (alloc.isReg):
                    freeNonParamregisters.append(alloc.location)
                if (not alloc.isReg):
                    freeOffsets.append(alloc.location)            
            if (ss.isStart):
                if (len(freeNonParamregisters) > 0):
                    # Non Params are unordered, so sourced and pushed
                    # to the freelist
                    reg = freeNonParamregisters.pop()
                    UsedNonParamReg.add(reg)           
                    localAllocs.append(RegAlloc(ss.idx, True, reg))
                elif (len(freeOffsets) > 0):
                    loc = freeOffsets.pop()            
                    localAllocs.append(RegAlloc(ss.idx, False, loc))
                else:
                    loc = offsetPtr
                    offsetPtr += 8
                    localAllocs.append(RegAlloc(ss.idx, False, loc))
    print(str(UsedParamReg))    
    print(str(UsedNonParamReg))    
    return localAllocs
                
# # its depth problem. Wait to do this code, I don't recall offhand
    # if (freeReg > 0):
         # local.location(pop(freeReg))
        # else if (cRegisters > 0):
            # local.location(pop(cRegister))
        # else:
            # local.isStack = True
            # local.location(offset)
            # offset += size
        # b.append("l.alloc(byteSpace.bit64)")
        # b.append("localSet(b, l({}), cParamSrc({}))".format(i) )

# # Now sources are
# def paramSrc(idx):
    # param = allParams[idx]
    # if (param.isCorrect):
        # return "cParamSrc({})".format(idx)
    # return "l({})".format(idx)

# # func call
    # funcName = ???
    # # Not including correct positioned params
    # # src may be a localIdx if unmodified?
    # # List((pos, src))
    # paramSrcList = []
    # for paramSrc in paramSrcList:
        # b.append("cParamSet(b, {}, {})".format(paramSrc.pos, paramSrc.src) )
    # b.append("funcCall(b, \"{}\")".format(funcName))
    

# func exit
# func exit must include local close, and func close
# could jump to the repeated code?

def testMangle():
    scopeB = mangleScope(["StringBuilder", "Heap"])
    mangledName = mangleFunc(scopeB, "clutch", ["StringBuilder", "int64"])
    print(mangledName)
        

def testlocalsAllocate():
    # 2 flat allocs
    testStartStops0 = [
        startStopStart(0),
        startStopUse(0),
        startStopStart(1),
        startStopUse(1),
        ]
    # 3 overlap allocs
    testStartStops1 = [
        startStopStart(0),
        startStopStart(1),
        startStopStart(2),
        startStopUse(1),
        startStopUse(0),
        startStopUse(2),
        ]
    # param and alloc
    testStartStops2 = [
        startStopParamDeclare(0),
        startStopParamUse(0),
        startStopStart(1),
        startStopUse(1),
        ]
    # param and alloc overlap
    testStartStops3 = [
        startStopParamDeclare(0),
        startStopStart(1),
        startStopUse(1),
        startStopParamUse(0),
        ]
    la = localsAllocate(
        NonParamRegisters,
        ParamRegisters, 
        testStartStops3, 
        # offloadParams
        False
        #True
        )
    print(la)
    
def testStartStopBuilder():
    b = StartStopBuilder()
    b.firstUse(0)
    b.use(0)
    b.firstUse(1)
    b.use(1)
    print(str(b))
    print(b.result())

    b = StartStopBuilder()
    b.firstUse(0)
    b.use(0)
    b.firstUse(1)
    b.use(1)
    b.use(0)
    print(str(b))
    print(b.result())
        
def main():
    #testMangle()
    testlocalsAllocate()
    #testStartStopBuilder()
    
if __name__== "__main__":
    main()
