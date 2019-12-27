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


#? how span actions
# if it goes into an action, it doen't span it.
#? what if only one use?
# No such thing. If stated, will be repeated?
#! add read/write comment on usage, and compact, write most significant
#! therefore, consider edhge swapping, which implies what?
#! leaf acttions now considered?
#! stack backup for registry overflow?
#? what about types


###
# StartStops
#            
class StartStop():
    def __init__(self, idx, isStart, prevCallIdx, scopedCalls):
        self.idx = idx
        self.isStart = isStart
        self.prevCallIdx = prevCallIdx
        self.scopedCalls = scopedCalls

    def __repr__(self):
        return "StartStop(idx:{}, isStart:{}, prevCallIdx:{}, scopedCalls:{})".format(
            self.idx, self.isStart, self.prevCallIdx, self.scopedCalls
            ) 
                        
def startStopStart(idx, prevCallIdx):
    return StartStop(idx, True, prevCallIdx, None)

def startStopUse(idx, prevCallIdx):
    return StartStop(idx, False, prevCallIdx, None)



class StartStopBuilder():
    # Filter data usage to first start and stop
    # The indexes given for labels are unique and serial ids.
    # Parameters are treated as a local variable. They should not be 
    # noted at source (i.e. at top of call code) but when they are first
    # used (even if not an allocation).
    # However, if a label is the same as a param, call paramAssocLabel() also, 
    # as the data is needed.
    # Call() should be used whenever there is a call. It is treated as 
    # an index.
    def __init__(self):
        self.startStops = []
        self.maxIdx = 0
        self.callCount = -1
        self.paramIdTolabelIds = {}
        
    def call(self):
        self.callCount += 1
        
    def paramAssocLabel(self, paramId, labelId):
        self.paramIdTolabelIds[paramId] = labelId
        
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
                    # b.paramIdTolabelIds(r, labelIdx)
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

#! enable
class LiveAllocStats():
    def __init__(self):
        self.paramsLeftOnRegisters = []
        self.paramsMovedToNonParamRegisters = []
        self.paramsMovedToStack = []
        
    def __repr__(self):
        return "StartStopBuilder(paramsLeftOnRegisters:{}, paramsMovedToNonParamRegisters:{}, paramsMovedToStack:{})".format(
            self.paramsLeftOnRegisters,
            self.paramsMovedToNonParamRegisters,
            self.paramsMovedToStack,
            ) 
            
MemLoc = collections.namedtuple("MemLoc", "isReg loc")
def regMemLoc(loc):
    return MemLoc(True, loc)

def stackMemLoc(loc):
    return MemLoc(False, loc)
    
# current logic
# - Parameter ids are given the parameter register if not offloaded, or
# a non parameter register if offloaded
# Thus offload tells if offload code required.
# Other local ids are given non-parameter registers or an offset.
# Non-parameter free lists are recycled if the id is out of scope.
#! Use parameter free list if no actions intrude.
#! - these would have high priority
#! lower param reg usage protection by only using in-scope protection
#?  carries a lot of init data?
class LiveAllocate():
    # registers are from 0. Registers include param and nonparam
    # in the same sequence.
    # label ids are from 0. Labels do not include the initial statement
    # of a parameter, but do include the subsequent use of parameters.
    def __init__(self, 
        paramCount,
        paramIdTolabelIds, 
        paramRegCount, 
        nonParamRegCount, 
        startStops,
        labelCount,
        ):
        self.paramCount = paramCount
        self.paramIdTolabelIds = paramIdTolabelIds
        # reversse lookup too
        self.labelToParamIds = {kv[1]:kv[0] for kv in self.paramIdTolabelIds.items()}
        self.paramRegCount = paramRegCount
        self.nonParamRegCount = nonParamRegCount
        self.startStops = startStops
        self.labelCount = labelCount
        # Parameter registers are of limited use.
        # At first they are locked and unavailable, so this is empty.
        # On release, (by value allocation or out of scope) they
        # are still of limited use, as they cannot cross a call
        # (even a push/pop may not protect against subcalls).
        # but they are a valuable resource for quick calculation
        # witness the use of rax etc.
        self.paramRegistersFree = [] #[r for r in range(0, paramRegCount)]
        # All used non-param registers should be restored by 
        # initial/funal push/pops (often convention) 
        self.nonParamRegistersToProtect = set()
        # all are free, initially
        self.nonParamRegistersFree = [r for r in range(paramRegCount, paramRegCount + nonParamRegCount)]
        # Array(Tuple(from: MemLoc, to: MemLoc))
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
        self.stats = LiveAllocStats()
        
    def paramRegisterCanAlloc(self):
        return (len(self.paramRegistersFree) > 0)

    def paramRegisterAlloc(self, stopStartStart):
        rid = self.paramRegistersFree.pop()
        dstMemLoc = regMemLoc(rid)
        lid = stopStartStart.idx
        self.localAllocs[lid] = dstMemLoc
        self.paramInitAssert(lid, dstMemLoc)
        # Needs protection over inner calls
        for cid in stopStartStart.scopedCalls:
            self.callParamRegProtection[cid].append(rid)
        return rid
        
    #? unused, preferring pre-edge scan
    def paramRegisterTargetedAlloc(self, stopStartStart, rid):
        # Target a particular paramregisteer for allocation.
        # This can be useful especially at the start of the allocaations,
        # to keep a parameter on it's allocated register.
        if (not(rid in self.paramRegistersFree)):
            raise IndexError("reg param id not in free list; rid {}, list:{} ".format(rid, self.nonParamRegistersFree))
        self.paramRegistersFree.remove(rid)
        dstMemLoc = regMemLoc(rid)
        lid = stopStartStart.idx
        self.localAllocs[lid] = dstMemLoc
        self.paramInitAssert(lid, dstMemLoc)
        # Needs protection over inner calls
        for cid in stopStartStart.scopedCalls:
            self.callParamRegProtection[cid].append(rid)
        return rid
                
    def paramRegisterDealloc(self, rid):
        self.paramRegistersFree.append(rid)
                
    def nonParamRegisterCanAlloc(self):
        return (len(self.nonParamRegistersFree) > 0)

    def nonParamRegisterAlloc(self, lid):
        rid = self.nonParamRegistersFree.pop()
        dstMemLoc = regMemLoc(rid)
        self.localAllocs[lid] = dstMemLoc
        self.paramInitAssert(lid, dstMemLoc)
        # needs protection over call entry/exit
        self.nonParamRegistersToProtect.add(rid)
        return rid
        
    def nonParamRegisterDealloc(self, rid):
        self.nonParamRegistersFree.append(rid)
        
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
                self.paramRegistersFree.append(loc)
            else:
                self.nonParamRegistersFree.append(loc)
        else:
            stackFreeList.append(memLoc.loc)

    def paramInitAssert(self, lid, dstMemLoc):
        if (lid in self.labelToParamIds):
            srcIdx = self.labelToParamIds[lid]
            #? mor than this for srces, need a list of src memlocs
            trans = (regMemLoc(srcIdx), dstMemLoc)
            self.initialParamTransfer.append(trans) 

    def paramAlloc(self):
        # Q & A :)
        paramLabelOnRegisterCount = min(self.paramCount, self.paramRegCount)
        paramLabelOnStackCount = self.paramCount - paramLabelOnRegisterCount
            
        # Assuming all paramreg values will be offloaded, any paramregs 
        # are initially available.
        # This may be modified by code below.               
        self.paramRegistersFree = [i for i in range(0, self.paramRegCount)]

        for pid in range(0, paramLabelOnRegisterCount):
            print(str(pid))
            # Q leave parameter on register? 
            # A if scope within 1 call of param (the start)?
            prevCallIdx = self.startAccess[self.paramIdTolabelIds[pid]].prevCallIdx
            if (prevCallIdx < 2):
                print("reg param value close enough to code to leave param on register; pid {}".format(pid))
                # mark any first funcCall for paramReg protection
                self.callParamRegProtection[0] = [pid]
                # alloc and reserve the register
                self.paramRegistersFree.remove(pid)
                lid = self.paramIdTolabelIds[pid]
                self.localAllocs[lid] = regMemLoc(pid)
                #self.paramRegisterTargetedAlloc(stopStartStart, rid)

            #NB dont allocate, we'll figure out later
            # else:
                # # Move param value somewhere
                # # subject of an initial param transfer, the register
                # # is deallocated.
                # self.paramRegisterDealloc(rid)
                # #Q can it be stashed on a nonParam register?
                # #? and if it is distant/somewhat usused, should it be?
                # if (self.nonParamRegisterCanAlloc()):
                    # print("reg param value moved to nonParamRegister; pid {}".format(pid))
                    # rid = self.nonParamRegisterAlloc()
                    # # mark paramRegister for transfer to nonParamRegister
                    # trans = (regMemLoc(idx), regMemLoc(rid))
                    # self.initialParamTransfer.append(trans) 
                    # self.localAllocs[self.paramIdTolabelIds[pid]] = regMemLoc(pid)                    
                # else:
                    # # onto stack
                    # print("reg param value moved to stack; pid {}".format(pid))
                    # sid = self.stackAlloc()
                    # # mark paramRegister for transfer to stack
                    # locs = (regMemLoc(pid), stackMemLoc(sid))
                    # self.initialParamTransfer.append(locs) 
                    # self.localAllocs[self.paramIdTolabelIds[pid]] = stackMemLoc(pid)                    
                   
                    # Q on use, do we need to transfer from stack?
                    #? do this here, or later?
                    #if (not param.stayonStack)
                    # mark stackVal for transfer to register
                    #rid = ???
                    #locs = (stackMemLoc(sid), regMemLoc(rid))
                    #locInitialize[idx] = locs
        #for idx in range(0, paramLabelOnStackCount):
            # Nothing to do?
                
    def localAlloc(self):
        for ss in self.startStops:
            # Q Where do non-param locals go?
            # A if register available and scope less then 1 call, on register
            #! not dealing with offsets/stack storage
            if (not ss.isStart):
                # mem location is now free
                memLoc = self.localAllocs[ss.idx]
                if (memLoc == -1):
                    print("deallocating unallocated memLoc!: lid:{}".format(ss.idx))
                else:
                    self.memLocDeAlloc(memLoc)
                
            # if a label labels a parameter this is already allocated.   
            # Only start if not alloced already?
            #(not(ss.idx in self.paramLabels))             
            if (ss.isStart and (self.localAllocs[ss.idx] == -1)):
                if (self.nonParamRegisterCanAlloc()):
                    rid = self.nonParamRegisterAlloc(ss.idx)
                    print("local on nonParamRegister; lid:{} rid {}".format(ss.idx, rid))
                else:
                    callsInScope = ss.callCount
                    if (self.paramRegisterCanAlloc() and (callsInScope < 1)):
                        rid = self.paramRegisterAlloc(ss)
                        print("local on nonParamRegister; lid:{} rid {}".format(ss.idx, rid))
                    else:
                        raise Error( "No registrs, no solution: data{}".format(ss))

                        # onto stack
                        #print("reg param value moved to nonParamRegister; rid {}".format(rid))
                        #sid = self.stackAlloc()
            
    def resultStr(self):
        return "LiveAllocateData(nonParamRegistersToProtect:{}, initialParamTransfer:{}, locInitialize:{}, callParamRegProtection:{}, localAllocs:{})".format(
            self.nonParamRegistersToProtect,
            self.initialParamTransfer,
            self.locInitialize, 
            self.callParamRegProtection,
            self.localAllocs,
        )

    def stateStr(self):
        return "LiveAllocateState(paramRegistersFree:{}, nonParamRegistersFree:{}, stackOffset:{}, stackFreeList:{})".format(
            self.paramRegistersFree,
            self.nonParamRegistersFree,
            self.stackOffset, 
            self.stackFreeList,
        )        
        
    def __repr__(self):
        return "LiveAllocate(paramCount:{}, paramIdTolabelIds:{}, paramRegCount:{}, nonParamRegCount:{}, labelCount:{})".format(
            self.paramCount,
            self.paramIdTolabelIds,
            self.paramRegCount, 
            self.nonParamRegCount,
            self.labelCount,
            #self.startStops,
            )       
    
#! needs rewriting
#! add action stubs
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


class StubIntCode():
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
    #StringBuilder__ensureSpace
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
        paramIdTolabelIds = {0:1, 1:2}, 
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

def testliveAllocate2():
    #StringBuilder_create
    testStartStops = [
        # sb
        startStopStart(0, 2),
        # ptr
        startStopStart(1, 2),
        startStopUse(1, 2),
        startStopUse(0, 2),
        ]
        
    ll = LiveAllocate(
        paramCount = 0,
        paramIdTolabelIds = {}, 
        paramRegCount = 6, 
        nonParamRegCount = 5, 
        startStops = testStartStops,
        labelCount = 2,
        )
    ll.paramAlloc()
    ll.localAlloc()
    print(ll)
    print(ll.stateStr())
    print(ll.resultStr())


def testliveAllocate3():
    #StringBuilder_append
    b = StartStopBuilder()
    # len
    b.firstUse(0)
    # str
    b.firstUse(1)
    ## strlen
    b.call()
    # sb
    b.firstUse(2)
    b.use(0)
    ## ensure
    b.call()
    # sb.str    
    b.firstUse(3)
    b.use(3)
    b.use(0)
    ## memmove
    b.call()
    # sb.size += len
    b.firstUse(4)
    b.use(2)
    b.use(4)
    b.use(0)
    # sb.str(sb.size)
    b.firstUse(5)
    b.use(5)
    b.use(2)
    #print(b.result())
            
    ll = LiveAllocate(
        paramCount = 2,
        paramIdTolabelIds = {0:2, 1:1}, 
        paramRegCount = 6, 
        nonParamRegCount = 5, 
        startStops = b.result(),
        labelCount = 6,
        )
    ll.paramAlloc()
    ll.localAlloc()
    print(ll)
    print(ll.stateStr())
    print(ll.resultStr())

    
def testStubIntCode():
    b = []
    localAlloc = [
        LocalAlloc(0, True, True, 'rbx', True),
        LocalAlloc(1, True, True, 'r12', False),
        ]
    a = StubIntCode("testAction", localAlloc)
    a.open(b)
    a.close(b)
    return b
    
def main():
    #testMangle()
    #testStartStopBuilder()
    #testliveAllocate()
    #testliveAllocate2()
    testliveAllocate3()
    #r = testStubIntCode()
    #print("\n".join(r))
    
if __name__== "__main__":
    main()
