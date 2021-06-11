from tpl_types import (
    Type, 
    TypeNumeric,
    TypeInt, 
    TypeFloat,
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

from ci_the import *

#! Umm, the unused base
class ArgTest():
    def __call__(self, arg):
        raise NotImplementedError()

                
                
class InstanceTest(ArgTest):
    """
    Test an arg for type of The.
    Will work ok for general groups, like a string.
    """
    def __init__(self, description, argType):
        self.description = description
        self.argType = argType
        
    def __call__(self, arg):
        return isinstance(arg, self.argType)

    def __str__(self):
        return "InstanceTest({})".format(self.description)
    
def numericVal():
    return InstanceTest("Int or Float", TheNumeric)
        
def intVal():
    return InstanceTest("Integer", TheInt)

def floatVal():
    return InstanceTest("Float", TheFloat)
    
def strVal():
    return InstanceTest("String", TheString)

def protoSymbolVal():
    return InstanceTest("ProtoSymbol", TheProtoSymbol)

def argListVal():
    return InstanceTest("List (of strings)", TheArgList)
    
def pathVal():
    return InstanceTest("Path (array of indeces and labels)", ThePath)
    
def booleanFuncVal():
    return InstanceTest("(tree of) Boolean logic", TheFuncBoolean) 

def anyType():
    return InstanceTest("Compiler Type", TheType)



# class AggregateTest(ArgTest):
    # def __init__(self, description):
        # self.description = description
        
    # def isLiteralVal(self, arg):
        # print('...isLiteralVal')
        # print(str(arg))
        # if (isinstance(arg, TheAggregateVals)):
            # r = True
            # for e in arg.value:
                # r = (r and self.isLiteralVal(e))
            # print(str(r))
            # return r
        # elif (isinstance(arg, TheKeyValue)):
            # return self.isLiteralVal(arg.value.value)
        # else:
            # return (
                # isinstance(arg, TheInt) or
                # isinstance(arg, TheFloat) or
                # isinstance(arg, TheString) or
                # isinstance(arg, TheRepeatMark)
                # )
                
    # def __call__(self, arg):
        # # Problem is, outer has been stripped of Arg wrap
        # # so this must start repeating itself (to avaoid an unwrap in
        # # isLiteralVal)
        # # TheAggregateVals(Position(83, 17), [TheInt(Position(83, 19), 333), TheInt(Position(83, 23), 55)])
        # # TheAggregateVals(Position(96, 17), [
        # # TheRepeatMark(Position(96, 19), *),
        # # TheAggregateVals(Position(96, 21),
        # #  [TheInt(Position(96, 23), 33),
        # #   TheInt(Position(96, 26), 77)])]
        # #)
        # #print('...isAggregate')
        # #print(str(self.isLiteralVal(arg)))
        # return self.isLiteralVal(arg)
        # # return (
            # # isinstance(val, AggregateVals) or
            # # isinstance(val, int) or
            # # isinstance(val, float) or
            # # isinstance(val, str)
        # # )

    # def __str__(self):
        # return f"AggregateTest({self.description})"

#? A shallow version. Since we now parse heavily and also check 
# against type
class AggregateTest(ArgTest):
    def __init__(self, description):
        self.description = description
        
    def __call__(self, arg):
        #print('...isAggregate')
        #print(str(self.isLiteralVal(arg)))
        return (
            isinstance(arg, TheAggregateVals) or
            isinstance(arg, TheInt) or
            isinstance(arg, TheFloat) or
            isinstance(arg, TheString) or
            isinstance(arg, TheKeyValue)
            )

    def __str__(self):
        return f"AggregateTest({self.description})"
                      
#! should include standalone value
def aggregateAny():
    return AggregateTest("Literal, or aggregate of literals") 



class SymbolTest(ArgTest):
    """
    Test an arg for TheType and it's top level type
    """
    def __init__(self, description, argType):
        self.description = description
        self.argType = argType
        
    def __call__(self, arg):
        return (
            isinstance(arg, TheSymbol) and 
            isinstance(arg.value, self.argType)
            )

    def __str__(self):
        return f"SymbolTest({self.description})"
        
def anyVar():
    return SymbolTest("a Variable", Var) 

#def anyFuncVar():
#    return SymbolTest("a Variable", str) 



class TypeTest(ArgTest):
    """
    Test an arg for TheType and it's top level type
    """
    def __init__(self, description, argType):
        self.description = description
        self.argType = argType
        
    def __call__(self, arg):
        return (
            isinstance(arg, TheType) and 
            isinstance(arg.value, self.argType)
            )

    def __str__(self):
        return f"TypeTest({self.description})"

def numericType():
    return TypeTest("Numeric Type", TypeNumeric)        

def intType():
    return TypeTest("Int Type", TypeInt)          

def floatType():
    return TypeTest("Int Type", TypeFloat)  

def stringType():
    return TypeTest("String Type", TypeString) 
        
        

class ValOrVarTest():
    '''
    Test for value or general var type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, description, valType, varTpe):
        self.description = description
        self.valType = valType
        self.varTpe = varTpe
        
    def __call__(self, arg):
        return (
            isinstance(arg, self.valType) 
            or (
                isinstance(arg, TheSymbol) and 
                isinstance(arg.value, Var) and 
                isinstance(arg.value.tpe, self.varTpe)
            )
        )

    def __str__(self):
        return f"ValOrVarTest({self.description})"

#def intOrVarNumeric():
def valOrVarInt():
    return ValOrVarTest("Int value or variable", TheInt, TypeInt)

def valOrVarFloat():
    return ValOrVarTest("Float value or variable", TheFloat, TypeFloat)

def valOrVarNumeric():
    return ValOrVarTest("Numeric value or variable", TheNumeric, TypeNumeric)
    
#def strOrVarStr():
def valOrVarStr():
    return ValOrVarTest("String value or variable", TheString, TypeString)    
    
def strOrVarAny():
    # specifically for string functions, allows a constant str through too
    return ValOrVarTest("String value or string variable", TheString, Type)    
    





class VarAndTypeTest():
    '''
    Test for var and type.
    Such as StringType, or NumericType.
    '''
    def __init__(self, description, varTypeType):
        self.description = description
        self.varTypeType = varTypeType
        
    def __call__(self, arg):
        return (
            isinstance(arg, Var)
            and isinstance(arg.tpe, self.varTypeType)
        )

    def __str__(self):
        return f"VarAndTypeTest({self.description})"

def intVar():
    return VarAndTypeTest("Int variable", TypeUnt)

def floatVar():
    return VarAndTypeTest("Float variable", TypeFloat)
                    
def numericVar():
    return VarAndTypeTest("Numeric variable", TypeNumeric)

def stringVar():
    return VarAndTypeTest("String variable", TypeString)

def containerOffsetVar():
    return VarAndTypeTest("ContainerOffset variable", TypeContainerOffset)


#def listVal():
    #! With this mechanism, we can test internal types
    # Wgat does the ABOVE MEAN> tthere are no inner lists?
#    return InstanceTest("list (of something)", list) 






#?
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

        
        
#! typeString is displayString, or somesuch
#? Need a specific type test?
#! unused
# class ValOrVarTypeTest():
    # def __init__(self, typeString, valType, varTpe):
        # self.description = description
        # self.valType = valType
        # self.varTpe = varTpe
        
    # def __call__(self, val):
        # return (
            # isinstance(val, self.valType) 
            # or (hasattr(val, 'tpe') and val.tpe.equals(self.varTpe))
        # )
        
    # def __str__(self):
        # return f"ValOrVarTypeTest({self.description})"

