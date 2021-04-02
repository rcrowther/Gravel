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
        #print(str(var))
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
        Set a var to a register.
        For utility.
        Forces into tracking, overwriting.
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
        Delete a var from a register
        Will delete any existing var (the var will also need removing 
        from other structures like an environment).
        Throws no error.    
        '''
        self.MapRegData[regName] = NoVar

    def remove(self, regName):
        '''
        Take the var from a register and set the register as empty.
        Throws an error if there is no var there.
        '''
        r = self(regName)
        self.delete(regName)
        return r
        
    def __str__(self):
        return str(self.MapRegData)
        
        
        
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
            raise BuilderError('Slot value is out of range? slotIndex:{}'.format(slot))
        if (slot in self.freeSlots):
            raise BuilderError("Slot is unallocated. slot:{}".format(slot))
        return self.MapSlotData[slot]
                
    def findSlot(self):
        '''
        return a free slot.
        '''
        # It would make more concurrent sense to pop(), but to keep the 
        # interface similar to AutoReg, we look
        if (not(self.freeSlots)):
            raise BuilderError("No slots left in sn stack area.")
        return self.freeSlots[-1]
        
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
        return  (self.byteWidth * (self.offsetSlots + slot))

    def _set(self, slot, var):
        '''
        Set a var to a stack slot.
        For utility.
        Forces into tracking, overwriting.
        Does not protect against the var having the correct register, 
        priority, etc.
        '''
        # 'orrible. But I don't care. R.C.
        if (slot in self.freeSlots):
            self.freeSlots.remove(slot)
        self.MapSlotData[slot] = var
        
    # Or should be from type?
    def delete(self, slot):
        '''
        Delete a var from a slot
        Will delete any existing var (the var will also need removing 
        from other structures like an environment).
        Throws no error.
        '''        
        if (not(slot in self.freeSlots)):
            self.freeSlots.append(slot)

    def remove(self, slot):
        '''
        Take the var from a slot and set the slot as empty.
        Throws an error if there is no var there.
        '''
        r = self(slot)
        self.delete(slot)        
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

    # def toRegOverwrite(self, var, regName):
        # '''
        # Move an existing var to a named register, oberwiting any contents.
        # Will kill any allocated var,
        # The register must be one that exists on any X... microprocessor,
        # i.e. xAX xBX xCX xSI xDI
        # '''
        # pass
        

                 
                         
    # def toRegGP(self, b, var):
        # '''
        # Move an existing var to a GP register.
        # Priority is ignored, the var will go to a register.
        # The register is not known, it is any general purpose register.
        # If the register has an existing var, if existing var has enough 
        # priority or there is an empty register, the exisitng var is 
        # moved to a register. Otherwise, it goes to stack.        
        # '''
        # excludeReg = ''
        # if (isinstance(var, Loc.RegisterX64)):
            # excludeReg = var.loc.lid
        # dstRegOpt = self.autoReg.findRegExclusive(priority, excludeReg)
        # if(dstRegOpt):
            # # We got a reg
            # oldVar = self.autoReg.getVar(reg)
            # if (oldVar):
                # # existing var must be going on the stack. Otherwise, 
                # # we'd've got an empty register
                # self.regToStack(b, reg)
            # # var on reg
            # var.toReg(b, reg)
            # self.autoReg.set(priority, var)
        # else:
            # # ok, (not enough priority) that goes to stack.
            # var.toStack(b)
            # #self.autoReg.set(priority, var)
        
    def _varLabelToRegNamed(self, b, var, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_varRegToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))

        # modify location in var and build
        self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        self.autoReg._set(dstRegName, var)
        
    # needed
    def _varRegToRegNamed(self, b, regName, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_varRegToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))
        #? check its a regVar
        var = self.autoReg.remove(regName)

        # modify location in var and build
        self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        self.autoReg._set(dstRegName, var)

    def _stackToRegNamed(self, b, slot, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_varRegToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))
        #? check its a regVar
        var = self.autoStack.remove(slot)

        # modify location in var and build
        self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        self.autoReg._set(dstRegName, var)
        
        
    def toReg(self, b, var, regName):
        '''
        Move an existing var to a named register.
        If the register has an existing var, if existing var has enough 
        priority or there is an empty register, the exisitng var is 
        moved to a register. Otherwise, it goes to stack.
        The register must be one that exists on any X... microprocessor,
        i.e. xAX xBX xCX xSI xDI
        '''
        # may require a shunt away. Is that to another register?
        # defend dstReg
        self._varRegExistingMove(b, regName)
        loc = var.loc
        if isinstance(loc, Loc.LocationLabel):
            self._varLabelToRegNamed(b, var, regName)
        elif isinstance(loc, Loc.LocationRegister):
            self._varRegToRegNamed(b, var.loc.lid, regName)
        elif isinstance(loc, Loc.LocationStack):
            self._stackToRegNamed(b, var.loc.lid, regName)

                    
    # needed
    def _varRegToStack(self, b, regName):
        '''
        Move an existing regVar to stack.
        No checks, may throw error on overallocate
        '''
        var = self.autoReg.remove(regName)
        slot = self,autoStack.findSlot()
        
        # modify location in var and build
        self.updateLocationBuilder.toStack(b, var, slot)
        
        # update indexes  
        self.autoStack._set(slot, var)

        
    def _varRegExistingMove(self, b, regName):
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
                self.autoReg(regName).priority, 
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
                    self._varRegToStack(b, dstRegNameOpt)

                # displaced var to new reg
                self._varRegToRegNamed(b, regName, dstRegNameOpt)
            else:
                # Not enough priority, 
                # var go to stack.
                self._varRegToStack(b, regName)

    #NB vars must be returned so they can be set on an environment
    def varROCreate(self, label, tpe, priority):
        '''
        Create a var on read-only segment memory,
        Untracked, present for a consistent interface.
        ''' 
        var = Var(
            Loc.RODataX64(label), 
            tpe
        )
        var.priority = priority
        return var
                        
    def varRegCreate(self, b, regName, tpe, priority):
        '''
        Create a var on a named register.
        If the register has an existing var it is moved to another 
        register or stack. The destination depends on the
        priority of the displaced var, and may cascade.
        Tracked
        '''   
        self._varRegExistingMove(b, regName)
        var = Var(
            Loc.RegisterX64(regName), 
            tpe
        )
        var.priority = priority
        self.autoReg._set(regName, var)
        return var

    def varRegAnyCreate(self, b, tpe, priority):
        '''
        Attempt to create a var on a register.
        If the var has sufficient priority or registers are free, it
        will be placed on a register. The register is chosen by the 
        autostore. Autostore may displace existing vars to stack. 
        Otherwise, the var will be placed on the stack.
        '''   
        # regName = self.autoReg.regBest()
        regName = self.autoReg.findReg(priority)
        var = None
        if (regName):
            var = self.varRegCreate(b, regName, tpe, priority)
        else:
            var = self.varStackCreate(b, tpe, priority)
        return var
      
    # ok
    def varStackCreate(self, tpe, priority):
        '''
        Create a var on the stack.
        return
            the allocated var
        ''' 
        slot = self.autoStack.findSlot()
        var = Var(
            Loc.StackX64(slot),
            tpe
        )   
        var.priority = priority
        self.autoStack._set(slot, var)
        return var
   
    def delete(self, var):
        loc = var.loc
        if isinstance(loc, Loc.LocationLabel):
            raise BuilderError('AutoStore: Readonly data deletion? :{}'.format(var))
        elif isinstance(loc, Loc.LocationRegister):
            self.autoReg.delete(var.loc.lid)
        elif isinstance(loc, Loc.LocationStack):
            self.autoStack.delete(var.loc.lid)
            
    # def varCreate(self, tpe, priority):
        # '''
        # Ceate a var on a register, but on fail creates on stack.
        # For the location decision, priority is assessed.
        # '''
        # regNameMaybe = self.autoReg.findReg(priority)
        # if (regNameMaybe):
            # self.varRegCreate(regNameMaybe, tpe, priority)
        # else:
            # self.varStackCreate(tpe)
            
                            

#def mkAutoStoreX64():
#    return AutoStoreX64()
