from tpl_types import Type, TypeNumeric, TypeString
from Syntaxer import ProtoSymbol, Path, FuncBoolean
from tpl_vars import Base


#? Need a specific type test?
class ValOrVarTypeTest():
    def __init__(self, typeString, valType, varTpe):
        self.typeString = typeString
        self.valType = valType
        self.varTpe = varTpe
        
    def __call__(self, val):
        return (
            isinstance(val, self.valType) 
            or (hasattr(val, 'tpe') and val.tpe.equals(self.varTpe))
        )
        
    def __str__(self):
        return "ValOrVarTypeTest({})".format(self.typeString)




class ValOrVarTypeTypeTest():
    '''
    Test for value or general var type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, typeString, valType, varTpe):
        self.typeString = typeString
        self.valType = valType
        self.varTpe = varTpe
        
    def __call__(self, val):
        return (
            isinstance(val, self.valType) 
            or (hasattr(val, 'tpe') and isinstance(val.tpe, self.varTpe))
        )
        
    def __str__(self):
        return "ValOrVarTypeTest({})".format(self.typeString)
                
def intOrVarNumeric():
    return ValOrVarTypeTypeTest("Int value or variable", int, TypeNumeric)

def strOrVarStr():
    return ValOrVarTypeTypeTest("String value or variable", str, TypeString)    
    
    
                
class InstanceTest():
    def __init__(self, typeString, valType):
        self.typeString = typeString
        self.valType = valType
        
    def __call__(self, val):
        return isinstance(val, self.valType)

    def __str__(self):
        return "InstanceTest({})".format(self.typeString)
        
def intVal():
    return InstanceTest("Integer", int)
    
def strVal():
    return InstanceTest("String", str)

def protoSymbolVal():
    return InstanceTest("ProtoSymbol", ProtoSymbol)

def pathVal():
    return InstanceTest("Path (array of ineces and labels)", Path)
    
def booleanFuncVal():
    return InstanceTest("(tree of) Boolean logic", FuncBoolean) 

def listVal():
    #! With this mechanism, we can test internal types
    return InstanceTest("list (of something)", list) 
    
def anyVar():
    return InstanceTest("a Variable", Base) 

def anyType():
    return InstanceTest("Compiler Type", Type)



class VarTypeTest():
    def __init__(self, typeString, varTpe):
        self.typeString = typeString
        self.varTpe = varTpe
        
    def __call__(self, val):
        return (hasattr(val, 'tpe') and val.tpe.equals(self.varTpe))

    def __str__(self):
        return "VarTypeTest({})".format(self.typeString)
                

def numericVar():
    return VarTypeTest("Numeric variable", TypeNumeric)

def strVar():
    return VarTypeTest("String variable", TypeString)

#def regVar():
# need a special test here for Location
#    return VarTypeTest("Register variable", )
