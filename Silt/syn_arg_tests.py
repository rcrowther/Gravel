from tpl_types import (
    Type, 
    TypeNumeric, 
    TypeString, 
    TypeContainerOffset
)
from Syntaxer import (
    ProtoSymbol,
    ArgList,
    Path, 
    FuncBoolean
)
from tpl_vars import Var
from tpl_locationRoot import RegisterX64



#! Umm, the unused base
class ArgTest():
    def __call__(self, val):
        raise NotImplementedError()
        
        
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
    return ValOrVarTypeTypeTest("Int value or int variable", int, TypeNumeric)

def strOrVarStr():
    return ValOrVarTypeTypeTest("String value or string variable", str, TypeString)    
    
def strOrVarAny():
    # specifically for string functions, allows a constant str through too
    return ValOrVarTypeTypeTest("String value or string variable", str, Type)    
    
                
                
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

def argListVal():
    return InstanceTest("ArgList (of strings)", ArgList)
    
def pathVal():
    return InstanceTest("Path (array of ineces and labels)", Path)
    
def booleanFuncVal():
    return InstanceTest("(tree of) Boolean logic", FuncBoolean) 

#def listVal():
    #! With this mechanism, we can test internal types
    # Wgat does the ABOVE MEAN> tthere are no inner lists?
#    return InstanceTest("list (of something)", list) 
    
def anyVar():
    return InstanceTest("a Variable", Var) 

def anyType():
    return InstanceTest("Compiler Type", Type)



class VarTypeTypeTest():
    '''
    Test for general var type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, typeString, varTypeType):
        self.typeString = typeString
        self.varTypeType = varTypeType
        
    def __call__(self, val):
        return (
            isinstance(val, Var)
            and isinstance(val.tpe, self.varTypeType)
        )

    def __str__(self):
        return "VarTypeTypeTest({})".format(self.typeString)
                

def numericVar():
    return VarTypeTypeTest("Numeric variable", TypeNumeric)

def stringVar():
    return VarTypeTypeTest("String variable", TypeString)

def containerOffsetVar():
    return VarTypeTypeTest("ContainerOffset variable", TypeContainerOffset)



class VarLocTest():
    def __init__(self, typeString, locType):
        self.typeString = typeString
        self.locType = locType
        
    def __call__(self, val):
        return (
            (isinstance(val, Var))
            and (isinstance(val.loc, self.locType))
        )

    def __str__(self):
        return "VarLocTest({})".format(self.typeString)    

def regVar():
    return VarLocTest("Register variable", RegisterX64)
