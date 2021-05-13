import architecture
from tpl_address_builder import AddressBuilder
#from tpl_either import Either
from exceptions import BuilderError


#! problems here
# - Arch is all through them
# - yet should be at least an input parameter
# - Tests are arch dependant, though x64/x32 will share most the same code

#! These constructions can raise BuilderErrors on parameter params.
#!? (can be added later if we throw a message up) get position for errors
#? Should have RO attribute?
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
    isReadOnly = False
    
    # If the src was a label, then an assembler will track the loc,
    # and these classes fo not need to.
    # However, a label var value may be transferred to some other 
    # location. If so, we need to know the what the original
    # location was. Then if the var is displaced it can be returned to
    # the label value, rather than occupying stack space.
    # We do this by stashing the label (as the original location)
    labelLoc = None
    
    def __init__(self, lid):
        self._validInitialLID(lid)
        self.lid = lid
        
    def _validInitialLID(self, lid):
        return NotImplementedError()
                
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

            
# was RODataX64
class GlobalROAddressX64(LocationLabel):
    '''
    Presents data accessed through a label.
    The lid is a label, an assembler contruct holding a data address.
    Typically, this class would be used for global data labels.
    This kind of storage can represent many datatypes, but definition 
    can be awkward for types deeper than one level.
    '''
    isReadOnly = True
    
    def __init__(self, label):
        super().__init__(label)
        self.labelLoc = self



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
     
    
            
class RegisteredAddressX64(LocationRegister):
    '''
    Presents data where the address is in a register.
    The lid is a register, the value is used as an address.
    Typically, this class would be used for heap data.
    This kind of storage can represent many datatypes.
    '''
    isAddressLoc = True



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



class StackedAddressX64(LocationStack):

    isAddressLoc = True

    def __init__(self, slot):
        super().__init__(slot)    
        self.stackByteSize = self.arch['bytesize']
