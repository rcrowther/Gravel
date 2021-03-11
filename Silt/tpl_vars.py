import architecture
import tpl_locationRoot as LocRoot
from tpl_either import Either


class Base():

    def value(self):
        return self.loc.value()

    def toStackIndex(self, b, index):
        self.loc = self.loc.toStackIndex(b, index)

    def toRegister(self, b, targetRegisterName):
        self.loc = self.loc.toRegister(b, targetRegisterName)

    def toCodeValue(self):
        '''
        Build a snippet of code to access the var.
        This acesses to top-level tpye of any goven tpye tree. In the 
        case of singular types, it will access the value directly. In
        the case of a container, it returns the container. To access  
        values in a container, a path is needed. 
        This method should always succeed???
        For access to containers see accessBPathuilder()
        '''
        return self.loc.value()

    def toCodeAddress(self):
        '''
        Build a snippet of code to access the var.
        This acesses to top-level tpye of any goven tpye tree. In the 
        case of singular types, it will access the value directly. In
        the case of a container, it returns the container. To access  
        values in a container, a path is needed. 
        This method should always succeed???
        For access to containers see accessBPathuilder()
        '''
        return self.loc.address()
        
    def accessPartialDeep(self):
        '''
        Build a snippet of code to access a value in a var.
        This accesses a position in a type tree. To do this, it needs a 
        path. The method may error, refusing direct access if the path
        os too deep for the architecture to handle.
        For simple acess to singular types, see accessBuilder()
        '''
        return NotImplementedError()
                
    def __repr__(self):
        return "Var(loc:'{}', tpe:{})".format(
            self.loc,
            self.tpe
        )


class Var(Base):
    def __init__(self, loc, tpe):
        self.loc = loc
        self.tpe = tpe
                        
            
#x
class ROX64(Base):
    def __init__(self, label, tpe):
        self.loc = LocRoot.RODataX64(label)
        self.tpe = tpe

    # def toCodeAddress(self):
        # # labels represent assembler-driven addresses.
        # return self.loc.lid
        
    # def toCodeValue(self):
        # # labels represent assembler-driven addresses.
        # return '[' + self.loc.lid + ']'
    
    def accessDeepMk(self, path):
        return '[' + self.loc.lid + str(self.type.offsetDeep(path)) + ']'        
                
def ROX64Either(label, tpe):
    locEither = LocRoot.RODataX64Either(label)
    varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    return varEither

            
#x        
class RegX64(Base):
    def __init__(self, register, tpe):
        self.loc = LocRoot.RegisterX64(register)
        self.tpe = tpe

    # def accessMk(self):
        # # registers represent assembler-driven addresses.
        # # They do not need address syntax  
        # return self.loc.lid
    
    def accessDeepMk(self, path):
        return '[' + self.loc.lid + '+' + str(self.tpe.offsetDeep(path)) + ']'   

def RegX64Either(register, tpe):
    locEither = LocRoot.RegisterX64Either(register)
    varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    return varEither
        
        
#x        
class RegAddrX64(Base):
    def __init__(self, register, tpe):
        self.loc = LocRoot.RegisteredAddressX64(register)
        self.tpe = tpe        
        
def RegAddrX64Either(register, tpe):
    locEither = LocRoot.RegisteredAddressX64Either(register)
    varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    return varEither
    
    
#x            
class StackX64(Base):
    def __init__(self, index, tpe):
        self.loc = LocRoot.StackX64(index)
        self.tpe = tpe

    # def accessMk(self): 
        # return '[rbp -' + str(self.loc.lid)  + ']' 
    
    def accessDeepMk(self, path): 
        return '[rbp -' + str(self.loc.lid + self.tpe.offsetDeep(path)) + ']' 

def StackX64Either(index, tpe):
    locEither = LocRoot.StackX64Either(index)
    varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    return varEither


        
def StackAddrX64Either(index, tpe):
    locEither = LocRoot.StackedAddressX64Either(index)
    varEither = Either.fromEither(locEither, Var(locEither.obj, tpe))
    return varEither
