import architecture
import tpl_LocationRoot


class Base():

    def value(self):
        return self.loc.value()

    def toStackIndex(self, b, index):
        self.loc = self.loc.toStackIndex(b, index)

    def toRegister(self, b, targetRegisterName):
        self.loc = self.loc.toRegister(b, targetRegisterName)

    def accessPartial(self):
        '''
        Build a snippet of code to access the var.
        This acesses to top-level tpye of any goven tpye tree. In the 
        case of singular types, it will access the value directly. In
        the case of a container, it returns the container. To access  
        values in a container, a path is needed. 
        This method should always succeed???
        For access to containers see accessBPathuilder()
        '''
        return NotImplementedError()

    def accessPartialDeep(self):
        '''
        Build a snippet of code to access a value in a var.
        This accesses a position in a type tree. To do this, it needs a 
        path. The method may error, refusing direct access if the path
        os too deep for the architecture to handle.
        For simple acess to singular types, see accessBuilder()
        '''
        return NotImplementedError()
                
                
                
class ROC64(Base):
    def __init__(self, label, tpe):
        self.loc = tpl_LocationRoot.LocationRootRODataX64(label)
        self.tpe = tpe

    def accessPartial(self):
        # labels represent assembler -driven addresses.
        # They do not need address syntax  
        return self.loc.lid


    
    def accessPartialDeep(self, path):
        # labels represent assembler -driven addresses.
        # They do not need address syntax  
        return self.loc.lid + str(self.type.offsetDeep(path))        
        
class RegX64(Base):
    def __init__(self, register, tpe):
        self.loc = tpl_LocationRoot.LocationRootRegisterX64(register)
        self.tpe = tpe

class StackX64(Base):
    def __init__(self, index, tpe):
        self.loc = tpl_LocationRoot.LocationRootStackX64(index)
        self.tpe = tpe



