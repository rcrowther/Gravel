    

#! problems here
#- Arch is all through them
# - Everything is arch ependant, though x64/x32 will share most the same code


#! These could include relaitve address tragets to, but look at other 
# architectures first
#! what about heap locations?
class LocationRoot():
    '''
    Location of data that can be moved directly to a register.
    Location is a register name, a stack offset, or label to segment data.
    It can not be a deep data type, such as an Array.
    '''
    def __init__(self, lid):
        self.lid = lid

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
        # if (type(self) == LocationRootStack):
            # raise ValueError('toStack: value already in stack. locationRoot:{}'.format(self))
        # #! this push not working
        # self.b += "push {}".format(self.lid)
        # #return LocationRootStack(index)


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



class LocationRootROData(LocationRoot):
    def __init__(self, label):
        if (label in arch['registers']):
            raise ValueError('Label id must not be in registers. lid: {} registers:"{}"'.format(
                type(label),
                ", ".join(registers)
            ))
        super().__init__(label)

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
            arch['ASMName'],
            index * arch['bytesize'], 
            self.value()
        )
        return LocationRootStack(index)
        
    #! ok
    def toRegister(self, b, targetRegisterName):
        if (not(targetRegisterName in arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        #? or mov {}, {}
        b += 'lea {}, [{}]'.format(targetRegisterName, self.value())              
        return LocationRootRegister(targetRegisterName) 

class LocationRootRegister(LocationRoot):
    def __init__(self, register):
        if (not (register in arch['registers'])):
            raise ValueError('Parameter must be in registers. lid: {} registers:"{}"'.format(
                register,
                ", ".join(arch['registers'])
            ))
        super().__init__(register)    
        
    def value(self):
        return self.lid
        
    def valueAsPointer(self):
        return '[{}]'.format(self.lid)        

    def toStackIndex(self, b, index):
        '''
        Copy the data to a stack allocation
        '''
        b += "mov [rbp - {}], {}".format(index * arch['bytesize'], self.value())
        return LocationRootStack(index)
        
    def toRegister(self, b, targetRegisterName):
        if (not(targetRegisterName in arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        if (self.lid == targetRegisterName):
            warning('toRegister', 'data already in given register. locationRoot:{}'.format(self))
        else:
            b += 'mov {}, {}'.format(targetRegisterName, self.value())              
        return LocationRootRegister(targetRegisterName)        
        
        
        
class LocationRootStack(LocationRoot):
    def __init__(self, index):
        if (not (type(index) == int)):
            raise TypeError('Parameter must be class int. lid: {}'.format(type(index)))
        super().__init__(index)    
        self.stackByteSize = arch['bytesize']

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
        if (not(targetRegisterName in arch['registers'])):
            raise NotImplementedError('toRegister: targetRegisterName not a register')
        b += 'lea {}, {}'.format(targetRegisterName, self.valueAsPointer())              
        return LocationRootRegister(targetRegisterName)


def mkLocationRoot(rawLocation):
    l = None
    if (rawLocation in arch['registers']):
        l = LocationRootRegister(rawLocation)
    elif(type(rawLocation) == str):
        l = LocationRootROData(rawLocation)
    elif(type(rawLocation) == int):
        l = LocationRootStack(rawLocation)
    else:
        raise NotImplementedError('mkLocationRoot: Parameter must be an int or str. type(rawLocation): {}'.format(type(rawLocation)))
    return l
    
    
