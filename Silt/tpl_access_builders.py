import tpl_locationRoot as Loc
from tpl_address_builder import AddressBuilder


# What I could use then, is this...
# difference between this and theother address builder is it takes 
# account of the Loc.
# It does not take account of type, like saying ''dont build an 
# address from a register variable, but do we want that? 
class AccessBuilder():
    '''
    Expands the simple address builder with locations.
    '''
    def __init__(self, loc):
        self.register = ''
        self.offset = 0
        self.loc = loc
        self.b = AddressBuilder(loc.lid)
          
        #NB The base for stack based items is the 'xbp' register
        # The lid which is a slot, is used later
        if (
            isinstance(loc, Loc.StackX64)
            or isinstance(self.loc, Loc.StackedAddressX64)
        ):
            self.b = AddressBuilder('rbp')


    def addOffset(self, offset):
        '''
        Add an pffset to the address.
        The addition is not tested in many ways. If a relative address 
        can be built, it will be.
        '''
        raise NotImplementedError('A AccessBuilder should never be instanced. accessBuilder:{}\nShould this be a subclass?'.format(
            self
        ))
            
    def addRegister(self, register):
        '''
        Add a register to the address.
        The addition is not tested in many ways. If a relative address 
        can be built, it will be.
        '''
        raise NotImplementedError('A AccessBuilder should never be instanced. accessBuilder:{}\nShould this be a subclass?'.format(
            self
        ))

    def result(self):
        raise NotImplementedError('A AccessBuilder should never be instanced. accessBuilder:{}\nShould this be a subclass?'.format(
            self
        ))
    def __repr__(self):
        return "AccessBuilder(location:{})".format(self.loc)



class AccessValue(AccessBuilder):
    '''
    Get the value from a location
    Allows adding register values and offsets, for suitable 
    locations
    '''
    # This is horrible contorted code. However, to push it back into
    # the locations is to confuse and bury the builder API. And it
    # is contorted for a reason, it models Assembly language 
    # commonplaces. 
    def __init__(self, loc):
        super().__init__(loc)

    def addOffset(self, offset):
        # Most just add the offset, even RegisterX64 and 
        # StackedAddressX64 (which will later throw an error)
        # however direct absolute stack access requires negative
        # values
        if (isinstance(self.loc, Loc.StackX64)):
            self.b.addOffset(-(offset))
        else:
            self.b.addOffset(offset)
            
    def addRegister(self, register):
        # Most just add the offset, even RegisterX64 and 
        # StackedAddressX64 (which will later throw an error)
        # however direct absolute stack access requires negative
        # offsetting
        if isinstance(self.loc, Loc.StackX64):
            self.b.addRegister('-' + register)
        else:
            self.b.addRegister('+' + register)
        
    # only thing that should throw an error
    def result(self):
        # needs LEA
        assert(not(isinstance(self.loc, Loc.StackedAddressX64))), 'StackedAddressX64 values not directly accessible. Transfer to a register. rootStorage:{}'.format(self.loc)

        if isinstance(self.loc, Loc.StackX64):
            # Need to add the slot offset
            self.b.addOffset(-(self.loc.lid * self.loc.stackByteSize))

        # They all return address access except...
        r = None
        if (isinstance(self.loc, Loc.RegisterX64)):
            assert(not(self.b.offset)), 'An offset from a RegisterX64 is a curious thing? rootStorage:{}'.format(self.loc)
            assert(not(self.b.register)),'A register offset from a RegisterX64 is a curious thing? rootStorage:{}'.format(self.loc) 
            # can raise errors
            r = self.b.asValue()
        else:
            # can raise errors
            r = self.b.asAddress()
        return r
            

            
class AccessAddress(AccessBuilder):
    '''
    Get the addrress of a location
    Allows adding register values and offsets, for suitable 
    locations
    '''
    #? Probably has limited use, aside from diagnosis...
    def __init__(self, loc):
        super().__init__(loc)

    def addOffset(self, offset):
        # however direct absolute stack access requires negative
        # values
        if (isinstance(self.loc, Loc.StackedAddressX64)):
            self.b.addOffset(-(offset))
        else:
            self.b.addOffset(offset)
            
    def addRegister(self, register):
        # however direct absolute stack access requires negative
        # offsetting
        if isinstance(self.loc, Loc.StackedAddressX64):
            self.b.addRegister('-' + register)
        else:
            self.b.addRegister('+' + register)

    # only thing that should throw an error
    def result(self):
        assert(not(isinstance(self.loc, Loc.RegisterX64))), 'A Register can not be treated as an address? Maybe change location type? location:{}'.format(self.loc)
        assert(not(isinstance(self.loc, Loc.StackX64))),  'A Stack var can not be treated as an address. Needs LEA to gather whole address location:{}'.format(self.loc)

        if isinstance(self.loc, Loc.StackedAddressX64):
            # Need to add the slot offset
            self.b.addOffset(-(self.loc.lid * self.loc.stackByteSize))

        # They mostly return value access except...
        r = None
        if isinstance(self.loc, Loc.StackedAddressX64):
            # can raise errors
            r = self.b.asAddress()        
        else:
            # can raise errors
            r = self.b.asValue()        
        return r

