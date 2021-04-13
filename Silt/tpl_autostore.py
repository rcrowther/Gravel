import architecture
from tpl_access_builders import AccessValue, AccessAddress
#from collections import namedtuple
from exceptions import BuilderError
import tpl_locationRoot as Loc
from tpl_vars import Var, NoVar, UpdateLocationBuilder
from collections import OrderedDict

# We need here, too
arch = architecture.architectureSolve(architecture.x64)



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

    def isAllocated(self, regName):
        var = self.MapRegData[regName]
        return (var != NoVar)

    def isNotAllocated(self, regName):
        var = self.MapRegData[regName]
        return (var == NoVar)
    
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

    def deleteAll(self, regNames):
        '''
        Delete a var from a register
        Will delete any existing var (the var will also need removing 
        from other structures like an environment).
        Throws no error.    
        '''
        for regName in regNames:
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

    def isAllocated(self, slot):
        return (not(slot in self.freeSlots))
        
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


    def deleteAll(self, slots):
        '''
        Delete a var from a register
        Will delete any existing var (the var will also need removing 
        from other structures like an environment).
        Throws no error.    
        '''
        for slot in slots:
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
    Is a builder. However, it only builds code when it needs to move 
    variable data to other store types. It does not allocate, 
    deallocate, regisster on deregister with environments.
    '''
    # This works in itself. But is fouling up because stack is
    # held by environment, but registers and labels are universal
    # Do we need a function to 'delete all tese (from an environment) 
    # variables'?
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
    # held by the store classes. I don't see how this can be clarified.
    # - the store indexes are an index for operations otherwise difficult to
    # perform (e.g. lowest priority reg variable)
    # - It needs an interface for every storage tyoe
    # - it needs to be a builder, because the moves can cascade.
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

    def _toRegNamed_common(self, b, var, dstRegName):
        # modify location in var and build
        self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        self.autoReg._set(dstRegName, var)
        
    def _varLabelToRegNamed(self, b, var, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_regToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))

        self._toRegNamed_common(b, var, dstRegName)

        # modify location in var and build
        # self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        # self.autoReg._set(dstRegName, var)
        
    # needed
    def _regToRegNamed(self, b, regName, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_regToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))
        #? check its a regVar
        var = self.autoReg.remove(regName)
        self._toRegNamed_common(b, var, dstRegName)

        # modify location in var and build
        # self.updateLocationBuilder.toRegister(b, var, dstRegName)
        #print(str(var))

        # update tracking  
        # self.autoReg._set(dstRegName, var)

    def _stackToRegNamed(self, b, slot, dstRegName):
        '''
        Move an existing reg var to another register.
        No checks, may be destructive at destination
        '''
        #print('_regToRegNamed:')
        #print(str(regName))
        #print(str(dstRegName))
        #? check its a regVar
        var = self.autoStack.remove(slot)
        self._toRegNamed_common(b, var, dstRegName)

        
    def toReg(self, b, var, regName):
        '''
        Move an existing var to a named register.
        If the register has an existing var, if existing var has enough 
        priority or there is an empty register, the exisitng var is 
        moved to a register. Otherwise, it goes to stack.
        The register must be one that exists on any X... microprocessor,
        i.e. xAX xBX xCX xSI xDI
        '''
        # defend dstReg
        self._varRegExistingMove(b, regName)
        loc = var.loc
        if isinstance(loc, Loc.LocationLabel):
            self._varLabelToRegNamed(b, var, regName)
        elif isinstance(loc, Loc.LocationRegister):
            self._regToRegNamed(b, var.loc.lid, regName)
        elif isinstance(loc, Loc.LocationStack):
            self._stackToRegNamed(b, var.loc.lid, regName)

    def toRegAny(self, b, var):
        '''
        Move an existing var to a register.
        Silently protects against moving an existing varReg. 
        Other variables go to the lowest priority register.
        Guarentees register placement. that may cause variable 
        displacemet.
        '''
        if (not(isinstance(var.loc, Loc.LocationRegister))):
            regName = self.autoReg.regBest()
        # if (not(
            # isinstance(var.loc, Loc.LocationRegister) 
            # and (var.loc.lid == regName)
        # )):
            self.toReg(b, var, regName)

    # Should be from Reg
    def _toStack_common(self, b, var):
        slot = self.autoStack.findSlot()

        # modify location in var and build
        self.updateLocationBuilder.toStack(b, var, slot)

        # update tracking  
        self.autoStack._set(slot, var)
        
    # needed
    def _varRegToStack(self, b, regName):
        '''
        Move an existing regVar to stack.
        No checks, may throw error on overallocate
        '''
        var = self.autoReg.remove(regName)
        self._toStack_common(b, var)

    #! yes, but labels should go back to being labels!!!
    def toStack(self, b, var):
        '''
        Move an existing var to stack.
        '''
        # may require a shunt away. Is that to another register?
        # defend dstReg
        loc = var.loc
        if isinstance(loc, Loc.LocationRegister):
            self._varRegToStack(b, var.loc.lid)
        else:
            #NB if on stack already, this errors
            self._toStack_common(b, var)

    def offReg(self, b, regName):
        '''
        Move data off a register.
        The destination is chosen automatically.
        '''
        var = self.autoReg.remove(regName)
        
        # if a label revert to label
        if (var.loc.labelLoc):
            var.loc = var.loc.labelLoc
        else:
            # var to stack.
            self._toStack_common(b, var)
                                
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
            # Let's see if it is a label. If it is, we can revert to the 
            # label
            var = self.autoReg(regName)
            if (isinstance(var, Loc.LocationLabel)):
                self.autoReg.remove(regName)
                self.updateLocationBuilder.toLabel(var)
            else:
                # Let's see if it has enough priority to stay on registers
                dstRegNameOpt = self.autoReg.findRegExclusive(
                    var.priority, 
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
                        self.offReg(b, dstRegNameOpt)

                    # displaced var to new reg
                    self._regToRegNamed(b, regName, dstRegNameOpt)
                else:
                    # Not enough priority, 
                    self.offReg(b, regName)

    #NB vars must be returned so they can be set on an environment
    def varROCreate(self, name, tpe, priority):
        '''
        Create a var on read-only segment memory,
        Untracked, present for a consistent interface.
        ''' 
        var = Var(
            name,
            Loc.RODataX64(name), 
            tpe
        )
        var.priority = priority
        return var
                        
    def varRegCreate(self, b, name, regName, tpe, priority):
        '''
        Create a var on a named register.
        If the register has an existing var it is moved to another 
        register or stack. The destination depends on the
        priority of the displaced var, and may cascade.
        Tracked
        '''   
        self._varRegExistingMove(b, regName)
        var = Var(
            name,
            Loc.RegisterX64(regName), 
            tpe
        )
        var.priority = priority
        self.autoReg._set(regName, var)
        return var

    def varRegAddrCreate(self, b, name, regName, tpe, priority):
        '''
        Create a var on a named register.
        If the register has an existing var it is moved to another 
        register or stack. The destination depends on the
        priority of the displaced var, and may cascade.
        Tracked
        '''   
        self._varRegExistingMove(b, regName)
        var = Var(
            name,
            Loc.RegisteredAddressX64(regName), 
            tpe
        )
        var.priority = priority
        self.autoReg._set(regName, var)
        return var
        
    def varRegAnyCreate(self, b, name, tpe, priority):
        '''
        Attempt to create a var on a register.
        If the var has sufficient priority or registers are free, it
        will be placed on a register. The register is chosen by the 
        autostore. Autostore may displace existing vars to stack. 
        Otherwise, the var will be placed on the stack.
        '''   
        regName = self.autoReg.findReg(priority)
        var = None
        if (regName):
            var = self.varRegCreate(b, name, regName, tpe, priority)
        else:
            var = self.varStackCreate(b, name, tpe, priority)
        return var
      
    # ok
    def varStackCreate(self, name, tpe, priority):
        '''
        Create a var on the stack.
        return
            the allocated var
        ''' 
        slot = self.autoStack.findSlot()
        var = Var(
            name,
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
            
    def deleteAll(self, symList):
        '''
        Delete all variables in the given list.
        Throws no error
        '''
        self.autoReg.deleteAll(symList)
        self.autoStack.deleteAll(symList)

            
                            

#def mkAutoStoreX64():
#    return AutoStoreX64()
