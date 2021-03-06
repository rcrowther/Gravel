
class AddressBuilder():
    '''
    Expects and must have a lid (label or register name)
    Does no checking, just a builder
    '''
    def __init__(self, lid):
        self.offset = 0
        self.lid = lid
        
    def addOffset(self, offset):
        self.offset += offset
        
    def result(self, asAddress):
        b = self.lid
        if (self.offset):
            # print numerics with a sign... in Python...
            b += '{:+}'.format(self.offset)
        if (asAddress):
            b = '[' + b + ']' 
        return b

    def asValue(self):
        b = self.lid
        if (self.offset):
            raise ValueError('AddressBuilder: Address added to value build. lid:{}'.format(self.lid))
        return b
        
    def asAddress(self):
        b = self.lid
        if (self.offset):
            # print numerics with a sign... in Python...
            b += '{:+}'.format(self.offset)
            b = '[' + b + ']' 
        return b
