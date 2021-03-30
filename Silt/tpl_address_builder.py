


class AddressBuilder():
    '''
    Builder to construct addresses to places.
    Expects and must have a lid (label/register name/slot number)
    Catches some unlikely events, but mostly a builder
    '''
    def __init__(self, lid):
        self.register = ''
        self.offset = 0
        self.lid = lid
        
    def addRegister(self, register):
        '''
        Add the sign before the reg e.g '-rax'.
        Not to do is an error.
        '''
        self.register += register
                
    def addOffset(self, offset):
        self.offset += offset

    def asValue(self):
        '''
        Return the address, treated as pointing to a value. 
        This will return the configured address undecorated, as the 
        location of a value.
        This may well itself be an address e.g. whatever is in 'rax'.
        '''
        # lid can sometimes be numeric, for stack indexes, but now
        # is a string for a builder.
        b = str(self.lid)
        assert(not(self.register)), 'AddressBuilder: Register added to value build. lid:{}'.format(self.lid)
        assert (not(self.offset)), 'AddressBuilder: Offset added to value build. lid:{}'.format(self.lid)
        return b
        
    def asAddress(self):
        '''
        Return the address, treated as an address. 
        This will wrap the configured address, as the location of an 
        address.
        '''
        # lid can sometimes be numeric, for stack indexes, but now
        # is a string for a builder.
        b = str(self.lid)
        if (self.register):
            firstChar = ord(self.register[0])
            if (firstChar != 45 and firstChar != 43):
                raise AssertionError("AddressBuilder: Register value with no sign.  register:'{}', lid:{}".format(
                self.register,
                self.lid
                ))
            b += self.register         
        if (self.offset):
            # print numerics with a sign... in Python...
            b += '{:+}'.format(self.offset)
        b = '[' + b + ']' 
        return b

    def __repr__(self):
        return "AddressBuilder({})".format(self.lid)


