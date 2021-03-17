import architecture
from tpl_address_builder import AddressBuilder
from tpl_either import Either


#! problems here
#- Arch is all through them
# - Everything is arch ependant, though x64/x32 will share most the same code

# We need here, too
arch = architecture.architectureSolve(architecture.x64)





#! This Statice return needs looking at becausse it includes the 
# parameter protection.
#! such errors need to be asserts to fit in with the other template
# helpers. See the AccessBuilders. 
#!? (can be added later if we throw a message up) get position for errors
class LocationRootX64():
    '''
    Present data as a location within various CPU constructs.
    Has methods to return snippets that access the data. 
    The class only presents the root of the datatype i.e. the top level.
    It unifies access methods across the CPU constructs. 
    It also allows transfer of values round the CPU constructs with
    clear syntax. 
    Both the access and the transfer methods can avoid or block
    nonsense that can occur accidentally such as mistaking an address 
    for a value.
     
    lid 
        a register name, a stack offset, or label to segment data.
    '''
    arch = architecture.architectureSolve(architecture.x64)

    def __init__(self, lid):
        self.lid = lid

    def _validInitialLID(self, lid):
        return NotImplementedError()
        
    #x needed now? See the offset stuff in types and vars
    def value(self):
        '''
        Code to access the value.
        If a pointer, this is the pointer address
        May not work on some storage types
        return
            a snippet that acesses the value
        '''
        raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            self
        ))

    #x needed now? See the offset stuff in types and vars        
    def address(self):
        '''
        Code to use the value as an address of a value.
        To use this method, the value needs to be a pointer.
        May not work on some storage types
        return
            a snippet that treats the value as an address
        '''
        raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            self
        ))
        
    # def toStackPush(self):
        # '''
        # Push the address to the stack. 
        # records the offset
        # '''
        # if (type(self) == LocationRootStackX64):
            # raise ValueError('toStack: value already in stack. locationRoot:{}'.format(self))
        # #! this push not working
        # self.b += "push {}".format(self.lid)
        # #return LocationRootStackX64(index)


    def toStackIndex(self, b, index):
        '''
        Copy the data to a stack allocation
        '''
        raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            self
        ))
                        
    def toRegister(self, b, targetRegisterName):
        '''
        Copy the data to a register
        '''
        raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            self
        ))
                
    def __repr__(self):
        return "{}(lid: '{}')".format(self.__class__.__name__, self.lid)
        
    def _b_str__(self):
        return str(self.lid)



class RODataX64(LocationRootX64):
    '''
    Presents data accessed through a label.
    The lid is a label, an assembler contruct holding a data address.
    Typically, this class would be used for global data labels.
    This kind of storage can represent many datatypes, but definition 
    can be awkward for types deeper than one level.
    '''
    def __init__(self, label):
        #assert self._validInitialLID(label)
        super().__init__(label)

    # def _validInitialLID(self, lid):
        # if (not (type(lid) == str)):
            # raise TypeError('LocationRootRODataX64: Parameter must be class "str". lid: "{}"'.format(
                # lid
            # ))
        # if (lid in self.arch['registers']):
            # raise ValueError('LocationRootRODataX64: Label id must not be in registers. lid: "{}" registers:"{}"'.format(
                # type(label),
                # ", ".join(registers)
            # ))
        # return True

    #? toCodeValue(self)
    def value(self):
        return AddressBuilder(self.lid).result(True)  

    #? toCodeAddress(self)
    def address(self):
        return self.lid        
        #raise NotImplementedError('value: a value can not be acessed from a stack offset.If required, location{}\nTransfer to a register first'.format(
        #    self
        #))

    
    #! ok
    def toStackIndex(self, b, index):
        '''
        Copy the data to a stack allocation
        '''
        b += "mov {}[rbp - {}], {}".format(
            self.arch['ASMName'],
            index * self.arch['bytesize'], 
            self.value()
        )
        return StackX64(index)
        
    #! ok
    def toRegister(self, b, targetRegisterName):
        if (not(targetRegisterName in self.arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        #? or mov {}, {}
        b += 'lea {}, [{}]'.format(targetRegisterName, self.value())              
        return RegisterX64(targetRegisterName) 

def _validInitialLabel(lid):
    msg = ''
    status = Either.NO_MESSAGE
    if (not (type(lid) == str)):
        msg = 'LocationRootRODataX64: Parameter must be class "str". arg: "{}"'.format(
            lid
        )
        status = Either.ERROR
    if (lid in arch['registers']):
        msg = 'LocationRootRODataX64: Label id must not be in registers. label: "{}" registers:"{}"'.format(
            type(label),
            ", ".join(registers)
        )
        status = Either.ERROR
    return (status, msg)

def RODataX64Either(label):
    data = _validInitialLabel(label)
    loc = RODataX64(label)
    return Either(data[0], data[1], loc)  
    
    
    
class RegisterX64(LocationRootX64):
    '''
    Presents data in a register.
    The lid is a register, the value used directly.
    Typically, data in 'eax', 'rax' etc.
    This kind of storage can only represent numbers up to the bitWidth.
    '''
    def __init__(self, register):
        #assert self._validInitialLID(register)
        super().__init__(register)    
     
    def value(self):
        return self.lid
        
    def address(self):
        #? Can get LEA of a register? Dunno.
        raise NotImplementedError('A LocationRootRegister can not be treated as an address. Transfer to a register first rootStorage:{}'.format(
            self
        ))
        
    def toStackIndex(self, b, index):
        '''
        Copy the data to a stack allocation
        '''
        b += "mov [rbp - {}], {}".format(index * self.arch['bytesize'], self.value())
        return StackX64(index)
        
    def toRegister(self, b, targetRegisterName):
        if (not(targetRegisterName in self.arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        if (self.lid == targetRegisterName):
            raise ValueError('toRegister', 'data already in given register. locationRoot:{}'.format(self))
        else:
            b += 'mov {}, {}'.format(targetRegisterName, self.value())              
        return RegisterX64(targetRegisterName)        

def _validInitialRegister(lid):
    msg = ''
    status = Either.NO_MESSAGE
    if (not (type(lid) == str)):
        msg = 'LocationRootRegisterX64: Parameter must be class "str". arg: "{}"'.format(
            lid
        )
        status = Either.ERROR
    if (not (lid in arch['registers'])):
        msg ='LocationRootRegisterX64: Parameter must be in registers. arg: "{}", registers:"{}"'.format(
            lid,
            ", ".join(self.arch['registers'])
        )
        status = Either.ERROR
    return (status, msg)
    
def RegisterX64Either(register):
    data = _validInitialRegister(register)
    loc = RegisterX64(register)
    return Either(data[0], data[1], loc)          
    
    
    
        
class RegisteredAddressX64(LocationRootX64):
    '''
    Presents data where the address is in a register.
    The lid is a register, the value is used as an address.
    Typically, this class would be used for heap data.
    This kind of storage can represent many datatypes.
    '''
    def value(self):
        return AddressBuilder(self.lid).result(True) 
        
    def address(self):
        return self.lid         
         
def RegisteredAddressX64Either(register):
    data = _validInitialRegister(register)
    loc = RegisteredAddressX64(register)
    return Either(data[0], data[1], loc)       
        
        
        
class StackX64(LocationRootX64):
    '''
    Presents data held on the stack.
    The lid is a stack offset.
    Typically, this class would be used for small local variables.
    This kind of storage can represent many datatypes, but size 
    should be kept down, and access is limited (adressed data needs 
    multiple loads).
    '''
    def __init__(self, index):
        #assert self._validInitialLID(index)
        super().__init__(index)    
        self.stackByteSize = self.arch['bytesize']

    def value(self):
        b = AddressBuilder('rbp')
        b.addOffset(-(self.lid * self.stackByteSize))
        return b.result(True)

    def address(self):
        # needs LEA
        raise NotImplementedError('A RootStorageStack can not be treated as an address. Transfer to a register first rootStorage:{}'.format(
            self
        ))
        
    def toStackIndex(self, b, index):
        '''
        Copy the data to a stack allocation
        '''
        raise ValueError('toStack: value already in stack. locationRoot:{}'.format(self))
        
    def toRegister(self, b, targetRegisterName):
        if (not(targetRegisterName in self.arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        b += 'lea {}, {}'.format(targetRegisterName, self.address())              
        return LocationRootRegisterX64(targetRegisterName)

def _validInitialStackSlot(lid):
    msg = ''
    status = Either.NO_MESSAGE
    if (not (type(lid) == int)):
        msg = 'LocationRootStackX64: Parameter must be class "int". slot: "{}"'.format(
            lid
        )
        status = Either.ERROR
    if (lid == 0):
        msg = "LocationRootStackX64: Slot can not be 0 (stack pointers point to last itemm, slot zero holds a pointer to base ). slot: '{}'".format(
            lid
        )
        status = Either.ERROR
    if (lid < 0):
        msg = "LocationRootStackX64: Slot can not be negative. slot: '{}'".format(
            lid
        )
        status = Either.ERROR
    if (lid & 1):
        # i.e. not a lid divisable by 2
        # In this architecture, lid ''slots' are eight bytes. But 
        # stack must be aligned to 16 bytes. So issue a warning. 
        msg = "LocationRootStackX64: Slot number not divisible by 2. Calls in this frame will fail. slot: '{}'".format(
            lid
        )
        status = Either.WARNING
    return (status, msg)

def StackX64Either(index):
    data = _validInitialStackSlot(index)
    loc = StackX64(index)
    return Either(data[0], data[1], loc)



class StackedAddressX64(LocationRootX64):

    def __init__(self, index):
        #assert self._validInitialLID(index)
        super().__init__(index)    
        self.stackByteSize = self.arch['bytesize']
        
    def value(self):
        # needs LEA
        raise NotImplementedError('A StackedAddressX64 can not be treated as an value. Transfer to a register first rootStorage:{}'.format(
            self
        ))
        
    def address(self):
        b = AddressBuilder('rbp')
        b.addOffset(-(self.lid * self.stackByteSize))
        return b.result(True)

def StackedAddressX64Either(index):
    data = _validInitialStackSlot(index)
    loc = StackedAddressX64(index)
    return Either(data[0], data[1], loc)
            
    
    
