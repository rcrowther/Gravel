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

class LocalAlloc():
    def __init__(self, idx, isReg, isNonParamReg, location, isOffload):
        self.idx = idx
        self.isReg = isReg
        self.isNonParamReg = isNonParamReg
        self.location = location
        self.isOffload = isOffload
        
    def __repr__(self):
        return "LocalAlloc(idx:{}, isReg:{}, isNonParamReg{}, location:{}, isOffload:{})".format(
            self.idx, self.isReg, self.isNonParamReg, self.location, self.isOffload
            ) 


###
# StartStops
#            
class StartStop():
    def __init__(self, idx, isStart, prevCallIdx):
        self.idx = idx
        self.isStart = isStart
        self.prevCallIdx = prevCallIdx
        self.scopedCalls = None

    def __repr__(self):
        return "StartStop(idx:{}, isStart:{}, prevCallIdx:{}, scopedCalls:{})".format(
            self.idx, self.isStart, self.prevCallIdx, self.scopedCalls
            ) 
                        
def startStopStart(idx, prevCallIdx):
    return StartStop(idx, True, prevCallIdx)

def startStopUse(idx, prevCallIdx):
    return StartStop(idx, False, prevCallIdx)


class StartStopBuilder():
    # Filter data usage to first start and stop
    # The indexes given for labels are unique and serial ids.
    # Parameters are treated as a local variable. They should not be 
    # noted at source (i.e. at top of call code) but when they are first
    # used (even if not an allocation).
    # However, if a label is the same as a param, call paramAsoc() also, 
    # as the data is needed.
    # Call() should be used whenever there is a call. It is treated as 
    # an index.
    def __init__(self):
        self.startStops = []
        self.maxIdx = 0
        self.callCount = -1
        self.paramAssocs = {}
        
    def call(self):
        self.callCount += 1
        
    def paramAssoc(self, paramId, labelId):
        self.paramAssocs[paramId] = labelId
        
    def firstUse(self, idx):
        self.startStops.append(startStopStart(idx, self.callCount))
        if (idx > self.maxIdx):
            self.maxIdx = idx
                
    def use(self, idx):
        self.startStops.append(startStopUse(idx, self.callCount))

    def result(self):
        b = []
        # Also stashes callcount to transfer to the start marker.
        usageEcountered = [False for a in range(0, (self.maxIdx + 1))]
        tailPrevCallIdx = [-1 for a in range(0, (self.maxIdx + 1))]
        for ss in reversed(self.startStops):
            if (ss.isStart):
                # copy callCount to start mark
                ss.scopedCalls = range(ss.prevCallIdx + 1, tailPrevCallIdx[ss.idx] + 1)
                b.append(ss)
            if ((not ss.isStart) and (usageEcountered[ss.idx] == False)):
                b.append(ss)
                usageEcountered[ss.idx] = True
                tailPrevCallIdx[ss.idx] = ss.prevCallIdx
        b.reverse()
        return b

    def __repr__(self):
        return "StartStopBuilder(startStops:{}, maxIdx:{})".format(
            self.startStops, self.maxIdx
            )       
            
#NB: a sketch, keep!
# def stopStartScan(paramLabels, lines):
    # # rScan lines and return a start stop list
    # # The list is the first and last occurence of a label. It has
    # # no location, but is in order of appearence.
    # # Note that parameters are treated no differently, they too are 
    # # measured from first use to last use (not from the start of all 
    # # lines).
    # # The resulting information also carriees a count of calls made 
    # # within the scope of the labels.
    # b = StartStopBuilder()
    # #? just a big number?
    # # also carries callCount
    # labelActive = [-1 for a in range(0, 32)]
    # currentHighIdx = 0
    
    # while line in lines:
        # if line contains label:
            # if (labelActive[labelIdx] == -1):
                # r = paramLabels.find(label)
                # if (r != -1):
                    # b.paramAssocs(r, labelIdx)
                # b.firstUse(labelIdx)
                # labelActive[labelIdx] = 0
                # currentHighIdx = labelIdx
            # else:
                # b.use(labelIdx, labelActive[labelIdx])
        # if line contains call:
           # for i in range(0, currentHighIdx):
               # labelActive[i] += 1 
    # return b.result()
 
    
###
# Allocing
#

def parameterAlloc(paramData, localAllocs, startStopB):
            
    if (action.isLeaf or action.callCount < 3):
        # leave on the parameter
        # do not scan for parameter vars
        # load localAlloc data
        #? stopStart not required? Yes, we need to know whee to stop to stop protecting.
        for i, p in enumerate(paramData):
            localAllocs.append(LocalAlloc(i, True, True, paramRegisters[i], False))
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
# def parametersAllocate(paramCount, paramRegisters, startStopB, offload):
    # localAllocs = []

    # if (offload):
        # # params become locals to allocate.
        # i = 0
        # while(i < paramCount):
            # startStopB.firstUse(i)        
            # i += 1
        
    # if (not offload):
        # # straight on localAllocs
        # i = 0
        # while(i < paramCount):
            # reg = paramRegisters[i]
            # localAllocs.append(LocalAlloc(i, True, False, reg, False))
            # i += 1
            
# current logic
# - Parameter ids are given the parameter register if not offloaded, or
# a non parameter register if offloaded
# Thus offload tells if offload code required.
# Other local ids are given non-parameter registers or an offset.
# Non-parameter free lists are recycled if the id is out of scope.
#! Use parameter free list if no actions intrude.
#! - these would have high priority
#! lower param reg usage protection by only using in-scope protection

MemLoc = collections.namedtuple("MemLoc", "isReg loc")
def regMemLoc(loc):
    return MemLoc(True, loc)

def stackMemLoc(loc):
    return MemLoc(False, loc)
    
class LiveAllocate():
    # registers are from 0. Registers include param and nonparam
    # in the same sequence.
    # label ids are from 0. Labels do not include the initial statement
    # of a parameter, but do include the subsequent use of parameters.
    def __init__(self, 
        paramCount,
        paramAssocs, 
        paramRegCount, 
        nonParamRegCount, 
        startStops,
        labelCount,
        ):
        self.paramCount = paramCount
        self.paramAssocs = paramAssocs
        self.paramRegCount = paramRegCount
        self.startStops = startStops
        self.labelCount = labelCount
        # Parameter registers are of limited use.
        # At first they are locked and unavailable, so this is empty.
        # On release, (by value allocation or out of scope) they
        # are still of limited use, as they cannot cross a call
        # (even a push/pop may not protect against subcalls).
        # but they are a valuable resource for quick calculation
        # witness the use of rax etc.
        self.paramRegisters = [] #[r for r in range(0, paramRegCount)]
        # All used non-param registers should be restored by 
        # initial/funal push/pops (often convention) 
        self.nonParamRegistersToProtect = set()
        self.nonParamRegisters = [r for r in range(paramRegCount, paramRegCount + nonParamRegCount)]
        # Array(Tuple(MemLoc(from), to))
        self.initialParamTransfer = []
        # if a paramreg wishes to sustain over a call, it must be 
        # push/popped.
        # Hash(callId:Array(paramReg))
        self.callParamRegProtection = {}
        # leap to start info easily
        self.startAccess = [-1 for id in range(0, labelCount)]
        for ss in self.startStops:
            if ss.isStart:
                self.startAccess[ss.idx] = ss
        self.stackOffset = 8
        self.stackFreeList = []
        
        # Sometimes a loc must be initialized from an internal shuffle.
        # Two situations are a shunt from paramReg, and
        # a shunt into a scope from stack.
        # ArrayById(Tuple(from: MemLoc, to: MemLoc))
        self.locInitialize = []

        # finally, this is where a local is to be found
        # Array(MemLoc) where array idx = localIdx
        self.localAllocs = [-1 for id in range(0, labelCount)]
        
    def paramRegisterCanAlloc(self):
        return (len(self.paramRegisters) > 0)

    def paramRegisterAlloc(self):
        rid = self.paramRegisters.pop()
        return rid
        
    def paramRegisterDealloc(self, rid):
        self.paramRegisters.append(rid)
                
    def nonParamRegisterCanAlloc(self):
        return (len(self.nonParamRegisters) > 0)

    def nonParamRegisterAlloc(self):
        rid = self.nonParamRegisters.pop()
        self.nonParamRegistersToProtect.add(rid)
        return rid

    def nonParamRegisterDealloc(self, rid):
        self.nonParamRegisters.append(rid)
        
    def stackAlloc(self):
        if (len(self.stackFreeList) > 0):
            sid = self.stackFreeList.pop()
        else:
            sid = self.stackOffset
            self.stackOffset += 8
        return sid
        
    def memLocDeAlloc(self, memLoc):
        loc = memLoc.loc
        if (memLoc.isReg):
            if (loc < self.paramRegCount):
                self.paramRegisters.append(loc)
            else:
                self.nonParamRegisters.append(loc)
        else:
            stackFreeList.append(memLoc.loc)
                            
    def paramAlloc(self):
        # Q & A :)
        #! don't defend. Stuff to do.
        if(self.paramCount > 0):
            if(self.paramRegCount > 0):
                #paramLabelsOnRegisters = math.min(self.paramCount, self.paramRegCount)
                #paramLabelsOnStack = 0
                #diff = self.paramCount - paramLabelsOnRegisters
                #if (diff > 0):
                #    paramLabelsOnStack = diff
                paramLabelsOnRegisters = self.paramCount
                paramLabelsOnStack = 0
            else:
                paramLabelsOnStack = self.paramCount
                
            # (for what it is worth) Any paramregs over the paramcount are
            # available                
            self.paramRegisters = [reg for reg in range(paramLabelsOnRegisters, self.paramRegCount)]

            for rid in range(0, paramLabelsOnRegisters):
                print(str(rid))
                # Q leave parameter on register? 
                # A if scope within 1 call of param (the start)?
                prevCallIdx = self.startAccess[self.paramAssocs[rid]].prevCallIdx
                if (prevCallIdx < 2):
                    print("reg param value close enough to code to leave param on register; rid {}".format(rid))
                    # mark any first funcCall for paramReg protection
                    if (prevCallIdx == 1):
                        self.callParamRegProtection[0] = [idx] 
                else:
                    # Move param value somewhere
                    # subject of an initial param transfer, the register
                    # is deallocated.
                    self.paramRegisterDealloc(rid)
                    #Q can it be stashed on a nonParam register?
                    #? and if it is distant/somewhat usused, should it be?
                    if (self.nonParamRegisterCanAlloc()):
                        print("reg param value moved to nonParamRegister; rid {}".format(rid))
                        rid = self.nonParamRegisterAlloc()
                        # mark paramRegister for transfer to nonParamRegister
                        trans = (regMemLoc(idx), regMemLoc(rid))
                        self.initialParamTransfer.append(trans) 
                    else:
                        # onto stack
                        print("reg param value moved to nonParamRegister; rid {}".format(rid))
                        sid = self.stackAlloc()
                        # mark paramRegister for transfer to stack
                        locs = (regMemLoc(idx), stackMemLoc(sid))
                        self.initialParamTransfer.append(locs) 
                        
                        # Q on use, do we need to transfer from stack?
                        #? do this here, or later?
                        #if (not param.stayonStack)
                        # mark stackVal for transfer to register
                        #rid = ???
                        #locs = (stackMemLoc(sid), regMemLoc(rid))
                        #locInitialize[idx] = locs
            #for idx in range(0, paramLabelsOnStack):
                # Nothing to do?
                
    def localAlloc(self):
        for ss in self.startStops:
            # Q Where do non-param locals go?
            # A if register available and scope less then 1 call, on register
            #! not dealing with offsets/stack storage
            if (not ss.isStart):
                # mem location is now free
                memLoc = self.localAllocs[ss.idx]
                self.memLocDeAlloc(memLoc)
            if (ss.isStart):
                #! paramscheck
                paramAssocs
                if (ss.idx in self.scopeToParam):
                    # ok, we found a scope which labels a parameter
                
                
                if (self.nonParamRegisterCanAlloc()):
                    rid = self.nonParamRegisterAlloc()
                    print("local on nonParamRegister; lid:{} rid {}".format(ss.idx, rid))
                    self.localAllocs[ss.idx] = regMemLoc(rid)
                else:
                    callsInScope = ss.callCount
                    if (self.paramRegisterCanAlloc() and (callsInScope < 1)):
                        rid = self.nonParamRegisterAlloc()
                        print("local on nonParamRegister; lid:{} rid {}".format(ss.idx, rid))
                        self.localAllocs[ss.idx] = regMemLoc(rid)
                    else:
                        raise Error( "No registrs, no solution: data{}".format(ss))

                        # onto stack
                        #print("reg param value moved to nonParamRegister; rid {}".format(rid))
                        #sid = self.stackAlloc()
            
    def resultStr(self):
        return "LiveAllocateData(nonParamRegistersToProtect:{}, initialParamTransfer:{}, locInitialize:{}, callParamRegProtection:{})".format(
            self.nonParamRegistersToProtect,
            self.initialParamTransfer,
            self.locInitialize, 
            self.callParamRegProtection,
        )

    def stateStr(self):
        return "LiveAllocateState(paramRegisters:{}, nonParamRegisters:{}, stackOffset:{}, stackFreeList:{})".format(
            self.paramRegisters,
            self.nonParamRegisters,
            self.stackOffset, 
            self.stackFreeList,
        )        
        
    def __repr__(self):
        return "LiveAllocate(paramCount:{}, paramAssocs:{}, paramRegCount:{}, labelCount:{})".format(
            self.paramCount,
            self.paramAssocs,
            self.paramRegCount, 
            self.labelCount,
            #self.startStops,
            )       
    
def localsAllocate(
    paramRegCount, 
    nonParamRegCount, 
    startStops, 
    offloadParams
    ):
    # Make allocation decisions from a startStopList
    # 
    # UsedParamReg and UsedNonParamReg hold used registers
    # @startStops 
    paramRegisters = ParamRegisters.copy()
    paramRegisters.reverse()
    offsetPtr = 0
    # the following hold currently free storage places
    freeNonParamregisters = nonParamRegisters.copy()
    freeNonParamregisters.reverse()
    freeParamReg = []
    freeOffsets = []
    # following holds usage data
    #! currently a full solution, narrow this for scope
    UsedParamReg = set()
    #NB all need protection on action entry and exit
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
                localAllocs.append(LocalAlloc(ss.idx, True, False, reg, False))
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
                    localAllocs.append(LocalAlloc(ss.idx, True, False, reg, False))
                elif (len(freeOffsets) > 0):
                    loc = freeOffsets.pop()            
                    localAllocs.append(LocalAlloc(ss.idx, False, False, loc, False))
                else:
                    loc = offsetPtr
                    offsetPtr += 8
                    localAllocs.append(LocalAlloc(ss.idx, False, False, loc, False))
    print(str(UsedParamReg))    
    print(str(UsedNonParamReg))    
    return localAllocs
                
def actionIntCode(b, aName, paramsOffloaded, localAllocs):
    # @paramsOffloaded List((id:int, dst:int)) of params to offload
    b.append("actionOpen({})".format(aName))
    # protect on entry nonparam registers for convention
    # series of pushes
    b.append("protectLocals({})".format(nonparamCount))
    if (paramsOffloaded):
        b.append("offloadParams({})".format(nonparamCount))
        

    # protect on exit nonparam registers for convention
    b.append("unProtectLocals({})".format(nonparamCount))
    b.append("actionClose({})".format(aName))
        
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


class Action():
    def __init__(self, label, localAlloc):
        # @paramOffloads List(id:int, loc) of params to offload
        self.label = label
        #self.localCount = localCount
        self.localAlloc = localAlloc
        print(str(localAlloc))
        self.regOffloads = [a for a in localAlloc if ((a.isOffload == True) and (a.isReg == True))]
        
    def open(self, b):
        b.extend([
            "",
            "{}:".format(self.label),
            "push rbp ;Push the base pointer",
            "mov rbp, rsp ;Level the base pointer"
            ])

        # protect used nonparam registers
        npRegAllocs = [a for a in self.localAlloc if (a.isNonParamReg == True)]
        for a in npRegAllocs:
            b.append("push {}".format(a.location))
        # set any offloads
        allOffloads = [a for a in self.localAlloc if (a.isOffload == True)]
        for a in allOffloads:
            if (a.isReg):
                b.append("mov {}, {}".format(
                    a.location,
                    ParamRegisters[a.idx]
                    ))
            if (not a.isReg):
                b.append("mov [bpr+{}], {}".format(
                    a.location,
                    ParamRegisters[a.idx]
                    ))
                    
    def close(self, b):
        # restore used nonparam registers
        for a in reversed(self.regOffloads):
            b.append("pop {}".format(a.location))
        b.extend([
            "pop rbp ;reset the bpr",
            "ret"
            ])

###
# Tests
#
def testMangle():
    scopeB = mangleScope(["StringBuilder", "Heap"])
    mangledName = mangleFunc(scopeB, "clutch", ["StringBuilder", "int64"])
    print(mangledName)

def testStartStopBuilder():
    # inline scopes
    b = StartStopBuilder()
    b.firstUse(0)
    b.use(0)
    b.firstUse(1)
    b.use(1)
    #print(str(b))
    print(b.result())

    # callCount handling
    b = StartStopBuilder()
    b.firstUse(0)
    b.call()
    b.use(0)
    b.firstUse(1)
    b.call()
    b.call()
    b.use(1)
    #print(str(b))
    print(b.result())

    # callCount dead calls
    b = StartStopBuilder()
    b.call()
    b.firstUse(0)
    b.use(0)
    b.call()
    b.call()
    #print(str(b))
    print(b.result())
    
    # multiple use scope
    b = StartStopBuilder()
    b.firstUse(0)
    b.call()
    b.use(0)
    b.call()
    b.use(0)
    b.call()
    b.use(0)
    #print(str(b))
    print(b.result())
        
    # overlaid scopes
    b = StartStopBuilder()
    b.firstUse(0)
    b.use(0)
    b.firstUse(1)
    b.use(1)
    b.use(0)
    #print(str(b))
    print(b.result())
               

def testliveAllocate():
    testStartStops = [
        # newsize
        startStopStart(0, 0),
        # sb
        startStopStart(1, 0),
        # extralen
        startStopStart(2, 0),
        startStopUse(2, 0),
        startStopUse(0, 0),
        startStopUse(1, 1)
        ]
        
    ll = LiveAllocate(
        paramCount = 2,
        paramAssocs = {0:1, 1:2}, 
        paramRegCount = 6, 
        nonParamRegCount = 5, 
        startStops = testStartStops,
        labelCount = 3,
        )
    ll.paramAlloc()
    ll.localAlloc()
    print(ll)
    print(ll.stateStr())
    print(ll.resultStr())
    
    # # 2 flat allocs
    # testStartStops0 = [
        # startStopStart(0),
        # startStopUse(0),
        # startStopStart(1),
        # startStopUse(1),
        # ]
    # # 3 overlap allocs
    # testStartStops1 = [
        # startStopStart(0),
        # startStopStart(1),
        # startStopStart(2),
        # startStopUse(1),
        # startStopUse(0),
        # startStopUse(2),
        # ]
    # # param and alloc
    # testStartStops2 = [
        # startStopParamDeclare(0),
        # startStopParamUse(0),
        # startStopStart(1),
        # startStopUse(1),
        # ]
    # # param and alloc overlap
    # testStartStops3 = [
        # startStopParamDeclare(0),
        # startStopStart(1),
        # startStopUse(1),
        # startStopParamUse(0),
        # ]
        
def testActionCode():
    b = []
    localAlloc = [
        LocalAlloc(0, True, True, 'rbx', True),
        LocalAlloc(1, True, True, 'r12', False),
        ]
    a = Action("testAction", localAlloc)
    a.open(b)
    a.close(b)
    return b
    
def main():
    #testMangle()
    #testStartStopBuilder()
    testliveAllocate()
    #r = testActionCode()
    #print("\n".join(r))
    
if __name__== "__main__":
    main()
