import architecture
from tpl_address_builder import AddressBuilder
#from tpl_either import Either
from exceptions import BuilderError


#! problems here
# - Arch is all through them
# - yet should be at least an input parameter
# - Tests are arch dependant, though x64/x32 will share most the same code





#! This Statice return needs looking at becausse it includes the 
# parameter protection.
#! such errors need to be asserts to fit in with the other template
# helpers. See the AccessBuilders. 
#!? (can be added later if we throw a message up) get position for errors
class LocationRoot():
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
    isAddressLoc = None
    
    def __init__(self, lid):
        self._validInitialLID(lid)
        self.lid = lid
        
    def _validInitialLID(self, lid):
        return NotImplementedError()

    # def toStackIndex(self, b, slot):
        # '''
        # Copy the data to a stack allocation
        # '''
        # raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            # self
        # ))
                        
    # def toRegister(self, b, targetRegisterName):
        # '''
        # Copy the data to a register
        # '''
        # raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            # self
        # ))
                
    def __repr__(self):
        return "{}(lid: '{}')".format(self.__class__.__name__, self.lid)
        
    def __str__(self):
        return str(self.lid)



class LocationLabel(LocationRoot):
    isAddressLoc = True

    def _validInitialLID(self, lid):
        if (not (type(lid) == str)):
            msg = 'LocationLabel: Parameter must be class "str". arg: "{}"'.format(
                lid
            )
            raise BuilderError(msg)
        registers = self.arch['registers']
        if (lid in registers):
            msg = 'LocationLabel: Label name must not be in registers. label: "{}" registers:"{}"'.format(
                label,
                ", ".join(registers)
            )
            raise BuilderError(msg)
            
#! bodge. Cant be arsed to build proper            
NoLoc = LocationLabel('')
            
            
class RODataX64(LocationLabel):
    '''
    Presents data accessed through a label.
    The lid is a label, an assembler contruct holding a data address.
    Typically, this class would be used for global data labels.
    This kind of storage can represent many datatypes, but definition 
    can be awkward for types deeper than one level.
    '''
    def __init__(self, label):
        super().__init__(label)

    # def toStackIndex(self, b, slot):
        # '''
        # Copy the data to a stack allocation
        # '''
        # b += "mov {}[rbp - {}], {}".format(
            # self.arch['ASMName'],
            # slot * self.arch['bytesize'], 
            # self.value()
        # )
        # return StackX64(index)

    # #! ok
    # def toRegister(self, b, targetRegisterName):
        # if (not(targetRegisterName in self.arch['registers'])):
            # raise NotImplementedError('toRegister: targetRegisterName not a register')
        # #? or mov {}, {}
        # b += 'lea {}, [{}]'.format(targetRegisterName, self.value())              
        # return RegisterX64(targetRegisterName) 



class LocationRegister(LocationRoot):
    def _validInitialLID(self, lid):
        if (not (type(lid) == str)):
            msg = 'LocationRegister: Parameter must be class "str". arg: "{}"'.format(
                lid
            )
            raise BuilderError(msg)
        if (not (lid in self.arch['registers'])):
            msg ='LocationRegister: Parameter must be in registers. arg: "{}", registers:"{}"'.format(
                lid,
                ", ".join(self.arch['registers'])
            )
            raise BuilderError(msg)    
    
    
    
class RegisterX64(LocationRegister):
    '''
    Presents data in a register.
    The lid is a register, the value used directly.
    Typically, data in 'eax', 'rax' etc.
    This kind of storage can only represent numbers up to the bitWidth.
    '''
    isAddressLoc = False

    #! repeated
    # def value(self):
        # return self.lid
        
    # def address(self):
        # #? Can get LEA of a register? Dunno.
        # raise NotImplementedError('A LocationRootRegister can not be treated as an address. Transfer to a register first rootStorage:{}'.format(
            # self
        # ))
        
    # def toStackIndex(self, b, slot):
        # '''
        # Copy the data to a stack allocation
        # '''
        # b += "mov [rbp - {}], {}".format(slot * self.arch['bytesize'], self.value())
        # return StackX64(index)
        
    # def toRegister(self, b, targetRegisterName):
        # if (not(targetRegisterName in self.arch['registers'])):
            # raise NotImplementedError('toRegister: targetRegisterName not a register')
        # if (self.lid == targetRegisterName):
            # raise ValueError('toRegister', 'data already in given register. locationRoot:{}'.format(self))
        # else:
            # b += 'mov {}, {}'.format(targetRegisterName, self.value())              
        # return RegisterX64(targetRegisterName)        
    
    
        
class RegisteredAddressX64(LocationRegister):
    '''
    Presents data where the address is in a register.
    The lid is a register, the value is used as an address.
    Typically, this class would be used for heap data.
    This kind of storage can represent many datatypes.
    '''
    isAddressLoc = True

    # def value(self):
        # return AddressBuilder(self.lid).result(True) 
        
    # def address(self):
        # return self.lid     
                    
    #! repeated


    # def toStackIndex(self, b, slot):
        # '''
        # Copy the data to a stack allocation
        # '''
        # b += "mov [rbp - {}], {}".format(slot * self.arch['bytesize'], self.value())
        # return StackX64(index)
        
    # def toRegister(self, b, targetRegisterName):
        # if (not(targetRegisterName in self.arch['registers'])):
            # raise NotImplementedError('toRegister: targetRegisterName not a register')
        # if (self.lid == targetRegisterName):
            # raise ValueError('toRegister', 'data already in given register. locationRoot:{}'.format(self))
        # else:
            # b += 'mov {}, {}'.format(targetRegisterName, self.value())              
        # return RegisterX64(targetRegisterName)        



class LocationStack(LocationRoot):
        
    def _validInitialLID(self, lid):
        if (not (type(lid) == int)):
            msg = 'LocationStack: Parameter must be class "int". slot: "{}"'.format(
                lid
            )
            raise BuilderError(msg)
        if (lid == 0):
            msg = "LocationStack: Slot can not be 0 (stack pointers point to last itemm, slot zero holds a pointer to base). slot: '{}'".format(
                lid
            )
            raise BuilderError(msg)
        if (lid < 0):
            msg = "LocationStack: Slot can not be negative. slot: '{}'".format(
                lid
            )
            raise BuilderError(msg)
        #! not here, in alloc
        # if (lid & 1):
            # # i.e. not a lid divisable by 2
            # # In this architecture, lid ''slots' are eight bytes. But 
            # # stack must be aligned to 16 bytes. So issue a warning. 
            # msg = "LocationStack: Slot number not divisible by 2. Calls in this frame will fail. slot: '{}'".format(
                # lid
            # )
            # raise BuilderError(msg)


        
class StackX64(LocationStack):
    '''
    Presents data held on the stack.
    The lid is a stack offset.
    Typically, this class would be used for small local variables.
    This kind of storage can represent many datatypes, but size 
    should be kept down, and access is limited (adressed data needs 
    multiple loads).
    '''
    isAddressLoc = False

    def __init__(self, index):
        super().__init__(index)    
        self.stackByteSize = self.arch['bytesize']
        
    # def value(self):
        # b = AddressBuilder('rbp')
        # b.addOffset(-(self.lid * self.stackByteSize))
        # return b.result(True)

    # def address(self):
        # # needs LEA
        # raise NotImplementedError('A RootStorageStack can not be treated as an address. Transfer to a register first rootStorage:{}'.format(
            # self
        # ))
        
    # def toStackIndex(self, b, slot):
        # '''
        # Copy the data to a stack allocation
        # '''
        # raise ValueError('toStack: value already in stack. locationRoot:{}'.format(self))
        
    # def toRegister(self, b, targetRegisterName):
        # if (not(targetRegisterName in self.arch['registers'])):
            # raise NotImplementedError('toRegister: targetRegisterName not a register')
        # b += 'lea {}, {}'.format(targetRegisterName, self.address())              
        # return LocationRootRegisterX64(targetRegisterName)



class StackedAddressX64(LocationStack):

    isAddressLoc = True

    def __init__(self, slot):
        super().__init__(slot)    
        self.stackByteSize = self.arch['bytesize']
                
    # def value(self):
        # # needs LEA
        # raise NotImplementedError('A StackedAddressX64 can not be treated as an value. Transfer to a register first rootStorage:{}'.format(
            # self
        # ))
        
    # def address(self):
        # b = AddressBuilder('rbp')
        # b.addOffset(-(self.lid * self.stackByteSize))
        # return b.result(True)

    # def toStackIndex(self, b, slot):

    
    
