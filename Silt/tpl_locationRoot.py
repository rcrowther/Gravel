import architecture
from tpl_address_builder import AddressBuilder


#! problems here
#- Arch is all through them
# - Everything is arch ependant, though x64/x32 will share most the same code


#! These could include relaitve address tragets to, but look at other 
# architectures first
#!? get position for errors
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
        
    def __str__(self):
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
        assert self._validInitialLID(label)
        super().__init__(label)

    def _validInitialLID(self, lid):
        if (not (type(lid) == str)):
            raise TypeError('LocationRootRODataX64: Parameter must be class "str". lid: "{}"'.format(
                lid
            ))
        if (lid in self.arch['registers']):
            raise ValueError('LocationRootRODataX64: Label id must not be in registers. lid: "{}" registers:"{}"'.format(
                type(label),
                ", ".join(registers)
            ))
        return True
        
    def value(self):
        return AddressBuilder(self.lid).result(True)  

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



class RegisterX64(LocationRootX64):
    '''
    Presents data in a register.
    The lid is a register, the value used directly.
    Typically, data in 'eax', 'rax' etc.
    This kind of storage can only represent numbers up to the bitWidth.
    '''
    def __init__(self, register):
        assert self._validInitialLID(register)
        super().__init__(register)    

    def _validInitialLID(self, lid):
        if (not (type(lid) == str)):
            raise TypeError('LocationRootRegisterX64: Parameter must be class "str". lid: "{}"'.format(
                lid
            ))
        if (not (lid in self.arch['registers'])):
            raise ValueError('LocationRootRegisterX64: Parameter must be in registers. lid: "{}", registers:"{}"'.format(
                lid,
                ", ".join(self.arch['registers'])
            ))
        return True
                
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
        
        
        
class RegisteredAddressX64(RegisterX64):
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
        assert self._validInitialLID(index)
        super().__init__(index)    
        self.stackByteSize = self.arch['bytesize']


    def _validInitialLID(self, lid):
        if (not (type(lid) == int)):
            raise TypeError('LocationRootStackX64: Parameter must be class "int". lid: "{}"'.format(
                lid
            ))
        if (lid == 0):
            raise TypeError("LocationRootStackX64: Slot can not be 0 (stack pointers point to last itemm, slot zero holds a pointer to base ). lid: '{}'".format(
                lid
            ))
        if (lid < 0):
            raise TypeError("LocationRootStackX64: Slot can not be negative. lid: '{}'".format(
                lid
            ))
        if (lid & 1):
            # i.e. not a lid divisable by 2
            # In this architecture, lid ''slots' are eight bytes. But 
            # stack must be aligned to 16 bytes. So issue a warning. 
            raise TypeError("LocationRootStackX64: Slot has been set to a number not divisible by 2. Later calls will fail. lid: '{}'".format(
                lid
            ))
        return True
            
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

class StackedAddressX64(LocationRootX64):

    def value(self):
        # needs LEA
        raise NotImplementedError('A StackedAddressX64 can not be treated as an value. Transfer to a register first rootStorage:{}'.format(
            self
        ))
        
    def address(self):
        b = AddressBuilder('rbp')
        b.addOffset(-(self.lid * self.stackByteSize))
        return b.result(True)
        
# def mkLocationRoot(rawLocation, arch):
    # l = None
    # if (rawLocation in arch['registers']):
        # l = LocationRootRegisterX64(rawLocation)
    # elif(type(rawLocation) == str):
        # l = LocationRootRODataX64(rawLocation)
    # elif(type(rawLocation) == int):
        # l = LocationRootStackX64(rawLocation)
    # else:
        # raise NotImplementedError('mkLocationRoot: Parameter must be an int or str. type(rawLocation): {}'.format(type(rawLocation)))
    # return l
    
    
