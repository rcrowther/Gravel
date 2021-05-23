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
    AggregateVals,
    KeyValue,
    FuncBoolean
)
from tpl_vars import Var
from tpl_locationRoot import RegisterX64



#! Umm, the unused base
class ArgTest():
    def __call__(self, val):
        raise NotImplementedError()
        
#! typeString is displayString, or somesuch
#? Need a specific type test?
class ValOrVarTypeTest():
    def __init__(self, typeString, valType, varTpe):
        self.description = description
        self.valType = valType
        self.varTpe = varTpe
        
    def __call__(self, val):
        return (
            isinstance(val, self.valType) 
            or (hasattr(val, 'tpe') and val.tpe.equals(self.varTpe))
        )
        
    def __str__(self):
        return f"ValOrVarTypeTest({self.description})"



class ValOrVarTypeTypeTest():
    '''
    Test for value or general var type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, description, valType, varTpe):
        self.description = description
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
    def __init__(self, description, valType):
        self.description = description
        self.valType = valType
        
    def __call__(self, val):
        return isinstance(val, self.valType)

    def __str__(self):
        return "InstanceTest({})".format(self.description)
        
def intVal():
    return InstanceTest("Integer", int)
    
def strVal():
    return InstanceTest("String", str)

def protoSymbolVal():
    return InstanceTest("ProtoSymbol", ProtoSymbol)

def argListVal():
    return InstanceTest("List (of strings)", ArgList)
    
def pathVal():
    return InstanceTest("Path (array of indeces and labels)", Path)
    
def booleanFuncVal():
    return InstanceTest("(tree of) Boolean logic", FuncBoolean) 

class AggregateTest():
    def __init__(self, description):
        self.description = description
        
    def isLiteralVal(self, val):
        #print('isLiteralVal')
        #print(str(val))
        v = val
        if (isinstance(v, AggregateVals)):
            r = True
            for e in v:
                r = (r and self.isLiteralVal(e))
            return r
        elif (isinstance(v, KeyValue)):
            return self.isLiteralVal(v)
        else:
            return (isinstance(v, int) or
                    isinstance(v, float) or
                    isinstance(v, str)
                    )
                
    def __call__(self, val):
        # Problem is, outer has been stripped of Arg wrap
        # so this must start repeating itslef (to avaoid an unwrap in
        # isLiteralVal)

        #return self.isLiteralVal(val)
        return (
            isinstance(val, AggregateVals) or
            isinstance(val, int) or
            isinstance(val, float) or
            isinstance(val, str)
        )

    def __str__(self):
        return "AggregateTest({})".format(self.description)
                
#! should include standalone value
def aggregateAny():
    return AggregateTest("Literal, or nested lists of literals") 



#def listVal():
    #! With this mechanism, we can test internal types
    # Wgat does the ABOVE MEAN> tthere are no inner lists?
#    return InstanceTest("list (of something)", list) 
    
def anyVar():
    return InstanceTest("a Variable", Var) 

def anyType():
    return InstanceTest("Compiler Type", Type)

def numericType():
    return InstanceTest("Compiler Type", TypeNumeric)



class VarTypeTypeTest():
    '''
    Test for general var type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, description, varTypeType):
        self.description = description
        self.varTypeType = varTypeType
        
    def __call__(self, val):
        return (
            isinstance(val, Var)
            and isinstance(val.tpe, self.varTypeType)
        )

    def __str__(self):
        return "VarTypeTypeTest({})".format(self.description)
                

def numericVar():
    return VarTypeTypeTest("Numeric variable", TypeNumeric)

def stringVar():
    return VarTypeTypeTest("String variable", description)

def containerOffsetVar():
    return VarTypeTypeTest("ContainerOffset variable", TypeContainerOffset)



class VarLocTest():
    def __init__(self, description, locType):
        self.description = description
        self.locType = locType
        
    def __call__(self, val):
        return (
            (isinstance(val, Var))
            and (isinstance(val.loc, self.locType))
        )

    def __str__(self):
        return "VarLocTest({})".format(self.description)    

def regVar():
    return VarLocTest("Register variable", RegisterX64)
