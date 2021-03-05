import tpl_locationRoot


class VarBase():

    def value(self):
        return self.loc.value()

    def toStackIndex(self, b, index):
        self.loc = self.loc.toStackIndex(b, index)

    def toRegister(self, b, targetRegisterName):
        self.loc = self.loc.toRegister(b, targetRegisterName)



class VarRO(VarBase):
    def __init__(self, label. tpe):
        self.loc = tpl_locationRoot.LocationRootRODataX64(label)
        self.tpe = tpe


class VarReg(VarBase):
    def __init__(self, register. tpe):
        self.loc = tpl_locationRoot.LocationRootRegisterX64(register)
        self.tpe = tpe

class VarStack(VarBase):
    def __init__(self, index. tpe):
        self.loc = tpl_locationRoot.LocationRootStackX64(index)
        self.tpe = tpe



