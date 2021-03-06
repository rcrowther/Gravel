import architecture


#! problems here
#- Arch is all through them
# - Everything is arch ependant, though x64/x32 will share most the same code


#! These could include relaitve address tragets to, but look at other 
# architectures first
#!? get position for errors
class LocationRootX64():
    '''
    Location of data that can be moved directly to a register.
    Location is a register name, a stack offset, or label to segment data.
    It can not be a deep data type, such as an Array.
    '''
    arch = architecture.architectureSolve(architecture.x64)

    def __init__(self, lid):
        self.lid = lid

    def _validInitialLID(self, lid):
        return NotImplementedError()
        
    #x needed now? See the offset stuff in types and vars
    def value(self):
        '''
        Code to represent the value at the location.
        If a pointer, this is the pointer address
        May not work on some storage types
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
        '''
        raise NotImplementedError('A location should never be instanced. location:{}\nShould this be a subclass?'.format(
            self
        ))

    #x needed now? See the offset stuff in types and vars        
    def valueAsPointer(self):
        '''
        Code to represent the value at the location as a pointer.
        If a pointer, this is the pointer address
        May not work on some storage types
        return
            register name or stack offset in bytes e.g. 'rax' or 'rbp - 16'
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
        return self.lid  

    #? can do this
    def valueAsPointer(self):
        return '[{}]'.format(self.lid)        
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
        
    def valueAsPointer(self):
        return '[{}]'.format(self.lid)        

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
            warning('toRegister', 'data already in given register. locationRoot:{}'.format(self))
        else:
            b += 'mov {}, {}'.format(targetRegisterName, self.value())              
        return RegisterX64(targetRegisterName)        
        
        
        
class StackX64(LocationRootX64):
    def __init__(self, index):
        assert self._validInitialLID(index)
        super().__init__(index)    
        self.stackByteSize = self.arch['bytesize']


    def _validInitialLID(self, lid):
        if (not (type(lid) == int)):
            raise TypeError('LocationRootStackX64: Parameter must be class "int". lid: "{}"'.format(
                lid
            ))
        return True
            
    def value(self):
        return '[rbp - {}]'.format(self.lid * self.stackByteSize)

    def valueAsPointer(self):
        raise NotImplementedError('A stackAlloc can not be treated as an address (it uses an indirection to access). location: {}\nIf required, transfer to a register first'.format(
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
        b += 'lea {}, {}'.format(targetRegisterName, self.valueAsPointer())              
        return LocationRootRegisterX64(targetRegisterName)


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
    
    
