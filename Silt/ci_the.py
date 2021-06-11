#!/usr/bin/env python3

from tpl_types import Type

#? Selc

class The():
    '''
    An object within the code.
    Thes are identified or generated by the parser. They are not 
    punctuation. Beyond that, they can be anything a parse identifies as 
    representing data (in LISP an atom), or a label (such as variable 
    names). Some Thes, such as Aggregate and BooleanFunc, are not in the 
    original parse, but implicit in the punctuation of the source.
    
    Thes do not ever themselves become containers, only contain 
    containers.
    
    A The gathers,
    - A typed version of what was written 
    - A source position, for after-parse error reporting.
    
    Thes bridge between parsed code and the generation of assembly 
    code. They are subtyped so their information can readily be 
    identified. The types of a The are not the same as Rubble's data 
    Types. A The, for example theInt, can contain data represented by 
    many data Types. And Thes exist that have no type representation, 
    such as comments.    
    
    The class ensures the presence of the attributes name, type and some 
    sort of data.
    '''
    name = 'The'
    # data would be a big refactor, and anyhow I want it specifically 
    #named for now
    def __init__(self, position, value):
        self.value = value
        self.position = position
        
    def __repr__(self):
        return f"{self.name}({self.position}, {self.value})"



# Not interested what the type of a builtin func is? Not at present...
class TheNumeric(The):
    pass
    
class TheInt(TheNumeric):
    name = 'TheInt'

class TheFloat(TheNumeric):
    name = 'TheFloat'    

class TheString(The):
    name = 'TheString'
    

class TheOffsetSymbol(The):
    name = 'TheOffsetSymbol'
    
class TheProtoSymbol(The):
    name = 'TheProtoSymbol'

#! unused. decide if we will
class TheBuiltinSymbol(The):
    name = 'TheBuiltinSymbol'
    
class TheSymbol(The):
    name = 'TheSymbol'

class TheFuncBoolean(The):
    name = 'TheFuncBoolean'            
    
class TheType(The):
    name = 'TheType'            

class TheArgList(The):
    name = 'TheArgList'     

class ThePath(The):
    name = 'ThePath' 

class TheKeyValue(The):
    name = 'TheKeyValue' 
    
class TheRepeatMark(The):
    name = 'TheRepeatMark' 
    
class TheAggregateVals(The):
    name = 'TheAggregateVals' 

class TheArgs(The):
    name = 'TheArgs' 

# SymbolFuncProto
# SymbolFunc
# SymbolVar
# KeyValue

