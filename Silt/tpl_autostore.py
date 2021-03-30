import architecture
from tpl_access_builders import AccessValue, AccessAddress
#from collections import namedtuple
from exceptions import BuilderError
import tpl_locationRoot as Loc
from tpl_vars import Var, NoVar, UpdateLocationBuilder
from collections import OrderedDict

# We need here, too
arch = architecture.architectureSolve(architecture.x64)


# registers
# Don't use directly, hence underscore
# _DataVar = namedtuple('DataVar', ['priority','var'])

# NoDataVar = _DataVar(-1, None)

# def mkDataVar(priority, var):
    # if (priority < 0):
        # raise BuilderError('priority < 0 for existing var. var:{}'.format(var))
    # return _DataVar(priority, var)



    
    
    
    
# assume we always have a Var
class AutoStoreReg():
    '''
    Store in automatically allocated locations.
    '''
    def __init__(self, generalRegisters):
        self.generalRegisters = generalRegisters
        self.regCount = len(self.generalRegisters)
        
        # Preserve some order. Generally prefer to fill less contentious
        # registers first
        self.MapRegData = OrderedDict()
        for reg in generalRegisters:
            self.MapRegData[reg ] = NoVar

    def __call__(self, regName):
        '''
        Get the var for this register.
        Throws error if register is unalllocated.
        '''
        r = self.MapRegData[regName]
        if (r == NoVar):
            raise BuilderError("Register is unallocated. regName:{}".format(regName))
        return r
    #x
    # def getVar(self, reg):
        # '''
        # Return the var on a register.
        # return
            # the var, or None.
        # '''    
        # data = self.MapRegData[reg]
        # varOrNot = None    
        # if not(isinstance(data, NoDataVar)):
            # varOrNot = data.var
        # return varOrNot

    def isAllocated(self, regName):
        var = self.MapRegData[regName]
        return (var != NoVar)

    def isNotAllocated(self, regName):
        var = self.MapRegData[regName]
        return (var == NoVar)
    
    #x
    # def getPriority(self, reg):
        # data = self.MapRegData[reg]
        # return data.priority
        
    def regBest(self):
        '''
        Returns a reg that is available.
        return
            the lowest priority register.
        '''
        prevPriority = 99999999
        registerName = None
        for reg, var in self.MapRegData.items():
            if (var.priority < prevPriority):
                registerName = reg
        return registerName

    def findRegExclusive(self, priority, excludeReg):
        '''
        Return a reg under or equal to the given priority.
        The register may have no var attached..
        This can exclude a register from the pool. This is because 
        sometimes a register is needed for an existing register value.
        It is not helpful to return the same register as a candidate :)
        excludeReg
            A register name to exclude from any positive result
        return
            the lowest priority register or, if not found, None
        '''
        #? Why not 0? Unallocated is priority -1
        if (priority < 1):
            raise BuilderError("Can't set a priority under 1! priority:{}".format(priority))
        prevPriority = priority
        registerName = None
        for reg, var in self.MapRegData.items():
            if ((var.priority <= prevPriority) and (reg != excludeReg)):
                prevPriority = var.priority
                registerName = reg
        return registerName

    def findReg(self, priority):
        '''
        Return a reg under the given priority.
        return
            the lowest priority register or, if not found, None
        '''
        return self.findRegExclusive(priority, None)
    
    # def setOverwrite(self, regVar):
        # registerName = regVar.loc.lid
        # self.MapRegData[registerName] = regVar
        
    # def set(self, priority, regVar):
        # '''
        # Set regVar data.
        # Always sets, whatever the priority
        # regVar
            # must be a regVar
        # return
            # the replaced varData, if any
        # '''
        # registerName = regVar.loc.lid
        # oldData = self.MapRegData[registerName]
        # self.MapRegData[registerName] = mkDataVar(priority, regVar)
        # return oldData     

    def _set(self, registerName, var):
        '''
        Set regVar data.
        For utility.
        Does not protect against the var having the correct register, 
        priority, etc.
        regVar
            must be a regVar
        return
            the replaced varData, if any
        '''
        self.MapRegData[registerName] = var


    def delete(self, regName):
        '''
        Set regVar to having no var attached.
        Will delete any existing var within the tracking structure (the 
        var will also need removing from other structures like an 
        environment).    
        '''
        self.MapRegData[regName] = NoVar

    def remove(self, regName):
        r = self.MapRegData[regName]
        self.MapRegData[regName] = NoVar
        return r
        
# Stack
# _DataStack = namedtuple('DataStack', ['offset','var'])

# NoDataStack = _DataStack(-1, None)

# def mkDataStack(offset, var):
    # #if (priority < 0):
    # #    raise CompilerError('priority < 0 for existing var. var:{}'.format(var))
    # return _DataStack(offset, var)    
    
    
# class AutoStoreStack():
    # '''
    # Store in automatically allocated locations.
    # '''
    # def __init__(self, byteWidth):
        # self.byteWidth = byteWidth        
        # # and the stack
        # self.stackTrack = []
        # # points at the current stack poition, like RSP
        # self.currOffset = 0
        
    # def pushStack(self, var):
        # '''
        # Push one bytewidth item to the stack
        # return
            # the generated dataStack
        # '''
        # # anyVar? even a stackLocated var?
        # #b._code.append("push " + AccessValue(var.loc).result())
        # self.currOffset -= self.byteWidth
        # dataStack = mkDataStack(self.currOffset, var)
        # self.stackTrack.append( dataStack )
        # return dataStack

    # # Or should e from type?
    # def addUntrackedSlotsToStack(self, size):
        # '''
        # Move stack tracking down to make space.
        # Moves by size number of slots i.e. bytewidth.
        # Note this will move the pointer to the end of the space (not the
        # following slot)
        # return
            # offset of last slot
        # '''
        # self.currOffset -= (size * self.byteWidth)
        # return self.currOffset
        
        
    # def popStack(self):
        # '''
        # Pop stack to last recorded item
        # '''
        # dataStack = self.stackTrack.pop()
        # if (dataStack.offset < self.currOffset):
            # raise BuilderError('Stack has been popped. currentIndex:{}'.format(self.currOffset))
        # #if (stackIndex > self.currOffset):
        # #    raise CompilerError('top of stack has unpopped items. currentIndex:{}'.format(self.currOffset))
        # offsetToPop = dataStack.offset
        # #b._code.append("lea rsp [rbp-{}]".format(offsetToPop))
        # #b._code.append("pop " + AccessValue(regVar.loc).result())
        # self.currOffset = offsetToPop + self.byteWidth
        # return dataStack
        
        
#! should be slotting. 
#! with priorities
#? Automatically?
 
# _DataStack = namedtuple('DataStack', ['priority','var'])

# NoDataStack = _DataStack(-1, None)

# def mkDataStack(priority, _DataVar):
    # #if (priority < 0):
    # #    raise CompilerError('priority < 0 for existing var. var:{}'.format(var))
    # return _DataStack(priority, var)    
    
    
    
class AutoStoreStack():
    '''
    Store in slots.
    '''
    def __init__(self, byteWidth, sizeSlots, offsetSlots):
        self.byteWidth = byteWidth
        self.offsetSlots = offsetSlots
        self.sizeSlots = sizeSlots
             
        # where vars are held
        self.MapSlotData = {}
        
        # a freelist
        self.freeSlots = [i for i in range(0, sizeSlots)]

    def __call__(self, slot):
        '''
        Get the var for this slot.
        Throws error if slot is unalllocated.
        '''
        if (slot > self.sizeSlots or slot < 0):
            raise BuilderError('Slot is out of range? slotIndex:{}'.format(slot))
        if (slot in self.freeSlots):
            raise BuilderError("Slot is unallocated. slot:{}".format(slot))
        return self.MapSlotData[slot]
                


    def removeSlotFree(self):
        '''
        return a free slot.
        '''
        return self.freeSlots.pop()
        
    # def get(self, slotIndex):
        # '''
        # Return the data on a slot.
        # return
            # the data
        # '''    
        # if (slotIndex > self.sizeSlots or slotIndex < 0):
            # raise BuilderError('Slot is out of range? slotIndex:{}'.format(slotIndex))
        # if (slotIndex in self.freeSlots):
            # raise BuilderError('Get a free slot? slotIndex:{}'.format(slotIndex))
        # return self.MapSlotData[slotIndex]


    def getOffset(self, slot):
        return  (self.byteWidth * (self,offsetSlots + slot))

    def _set(self, slot, var):
        '''
        Add a var to the stash
        '''
        self.MapSlotData[slot] = var
        
    # Or should be from type?
    def delete(self, slot):
        '''
        Delete an item from a slot
        return
            offset of last slot
        '''
        if (slot > self.sizeSlots or slot < 0):
            raise BuilderError('Slot is out of range? slotIndex:{}'.format(slot))
        if (slot in self.freeSlots):
            raise BuilderError('Delete a free slot? slotIndex:{}'.format(slot))        
        self.freeSlots.append(slot)

    def remove(self, slot):
        r = self(slot)
        self.freeSlots.append(slot)        
        return r
        

        
class AutoStoreX64():
    '''
    Operate a AutoStoreReg and a AutoStoreStack together.
    Is not a builder.
    '''
    #sometimes we sneed to 
    # - shift to another register, say from Rax
    # - We need to move to a spacific register, say RSI for a call
    # - Or we need to shift to a register, say from a label
    # - or we are happey to to shift to stack, without argument
    # - abandon var, it is used
    # There's a difference between allocation and moving,
    # "I want this new data defined on a register"
    # "I want to salvage this vaar from stack"
    # "I want this var pushed to stack" 
    #! my problem... do I want to put var creators in here?
    # They belong here, but that would make this non-optional
    # used, though need them all,
    # RODataX64
    # RODataX64
    # RegisterX64
    # RegisteredAddressX64
    # StackX64
    #
    #? This is complex, and I don't like. Rasons
    # - Location data is in two places, the location, and the lists
    # held by the store classes. I don't see how this can be clarified...
    # the store indexes are an index for operations otherwise difficult to
    # perform (lowest priority reg variable)
    # It's needing an interface for every storage tyoe
    # - it will need toi be a builder, to enact cascading operations.
    def __init__(self, arch, sizeSlots, initialOffset):
        self.autoReg = AutoStoreReg(arch['generalPurposeRegisters'])
        self.autoStack = AutoStoreStack(arch['bytesize'], sizeSlots, initialOffset)
        self.updateLocationBuilder = UpdateLocationBuilder(arch)

    def toRegOverwrite(self, var, regName):
        '''
        Move an existing var to a named register, oberwiting any contents.
        Will kill any allocated var,
        The register must be one that exists on any X... microprocessor,
        i.e. xAX xBX xCX xSI xDI
        '''
        
        
    def toReg(self, var, regName):
        '''
        Move an existing var to a named register.
        If the register has an existing var, if existing var has enough 
        priority or there is an empty register, the exisitng var is 
        moved to a register. Otherwise, it goes to stack.
        The register must be one that exists on any X... microprocessor,
        i.e. xAX xBX xCX xSI xDI
        '''
        # may require a shunt away. Is that to another register?
        # stack?
        # abandoned?
        oldVar = self.autoReg.get(reg)
        if (oldVar):
            # if abandoned, no problewm
            ...
            # Try get on another register, depending on it's priority
            self.regToStack(b, reg)
            
            # if that fails, the stack
                 
                         
    def toRegGP(self, b, var):
        '''
        Move an existing var to a register.
        Priority is ignored, the var will go to a register.
        The register is not known, it is any general purpose register.
        If the register has an existing var, if existing var has enough 
        priority or there is an empty register, the exisitng var is 
        moved to a register. Otherwise, it goes to stack.        
        '''
        excludeReg = ''
        if (isinstance(var, Loc.RegisterX64)):
            excludeReg = var.loc.lid
        dstRegOpt = self.autoReg.findRegExclusive(priority, excludeReg)
        if(dstRegOpt):
            # We got a reg
            oldVar = self.autoReg.getVar(reg)
            if (oldVar):
                # existing var must be going on the stack. Otherwise, 
                # we'd've got an empty register
                self.regToStack(b, reg)
            # var on reg
            var.toReg(b, reg)
            self.autoReg.set(priority, var)
        else:
            # ok, (not enough priority) that goes to stack.
            var.toStack(b)
            #self.autoReg.set(priority, var)
        

        
    def _varRegToRegNamed(self, b, regName, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #! check its a regVar
        data = self.autoReg.remove(regName)

        # modify location in var
        data.var.loc.lid = dstRegName

        # update indexes  
        self.autoStack._set(dstRegName, data)
        
    def _toStack(self, regName):
        '''
        Move an existing regVar to stack.
        No checks, may throw error on overallocate
        '''
        #! check its a regVar
        data = self.autoReg.remove(regName)
        slot = self,autoStack.removeSlotFree()
        
        # modify location in var
        data.var.loc =  Loc.StackX64(slot)
        
        # update indexes  
        self.autoStack._set(slot, data)
                    
    def _varRegExistingMove(self, regName):
        '''
        Move an existing var off a register.
        The variable will be forced off the register. Priority is 
        (initially) ignored.
        If a var exists and has enough priority (or there is an 
        empty register) the exisitng var is 
        moved to another register. Otherwise, it is moved to stack. 
        '''                         
        alloced = self.autoReg.isAllocated(regName)
        if (alloced):
            # There is a var. It must be moved somewhere.
            # Let's see if it has enough priority to stay on registers
            dstRegNameOpt = self.autoReg.findRegExclusive(
                self.autoReg.getPriority(regName), 
                regName
            )
            if(dstRegNameOpt):
                # We got a regName to move to
                # Now we need, if necessary, to clear out that reg too
                alloced2 = self.autoReg.isAllocated(dstRegNameOpt)

                if(alloced2):
                    # We tried to find a place for the displaced var
                    # using findRegExclusive. If an unallocated 
                    # register was available, it would have been 
                    # returned.
                    # But we got an allocated register, which means
                    # all registers are allocated. And the displaced var
                    # has a high enough priority to displace some other 
                    # var.
                    # So second displaced var must be going to the stack. 
                    self._toStack(b, dstRegNameOpt)

                # displaced var to new reg
                self._varRegToRegNamed(b, regName, dstRegNameOpt)
            else:
                # Not enough priority, 
                # var go to stack.
                self._toStack(b, regName)
        


    def varROCreate(self, label, tpe):
        '''
        Create a var on read-only segment memory,
        ''' 
        return Var.Var(
            Loc.RODataX64(label), 
            tpe
        )
                        
    def varRegCreateOverwrite(self, regName, tpe, priority):
        '''
        Create a var on a named register.
        Deletes existing contents
        '''   
        var = Var.Var(
            Loc.RegisterX64(regName), 
             tpe
        )
        dataVar = mkDataVar(priority, var)
        self.autoReg._set(regName, dataVar)

    def varRegCreate(self, regName, tpe, priority):
        '''
        Create a var on a named register.
        Relocates existing contents.
        '''   
        self._varRegExistingMove(regName)
        self.varRegCreateOverwrite(regName, tpe, priority)

        
    def varRegAnyCreateOverwrite(self, tpe, priority):
        '''
        Create a var on a register.
        Deletes existing contents
        '''           
        regName = self.autoReg.regBest()
        self.varRegCreateOverwrite(regName, tpe, priority)


    def varRegAnyCreate(self, tpe, priority):
        '''
        Create a var on a register.
        Relocates existing contents.
        '''           
        regName = self.autoReg.regBest()
        self._varRegExistingMove(regName)
        self.varRegCreateOverwrite(regName, tpe, priority)


            
        # var = Var.Var(
            # Loc.RegisterX64(register), 
            # tpe
        # )
        # var = Var.Var(
            # Loc.RegisteredAddressX64(register), 
            # tpe
        # )
        
    # ok
    def varStackCreate(self, tpe):
        '''
        Create a var on the stack.
        The new var always has the lowest priority.
        return
            the allocated slot
        ''' 
        slot = self,autoStack.removeSlotFree()
        var = Var(
            Loc.StackX64(slot),
            tpe
        )   
        self.autoStack._set(slot, var)
   
    def varCreate(self, tpe, priority):
        '''
        Ceate a var on a register, but on fail creates on stack.
        For the location decision, priority is assessed.
        '''
        regNameMaybe = self.autoReg.findReg(priority)
        if (regNameMaybe):
            self.varRegCreate(regNameMaybe, tpe, priority)
        else:
            self.varStackCreate(tpe)
            
                            

def mkAutoStoreX64():
    return AutoStoreX64()
