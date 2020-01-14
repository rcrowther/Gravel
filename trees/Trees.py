from Position import NoPosition
from Kinds import *
#from TreeInfo import TreeInfo, UndefinedTreeInfo, NoTreeInfo


## Replaces tree
class CodeMark():
    '''
    Tree init() should be designed so the class will accept the 
    parsed and identifying data. The init should not contain 
    supplementary information. This is so toString() can print 
    code which represents a working tree.
    Use a factory for other inits e.g. for tree builders.
    Note this base can be leaf or branch---it has no children.
    Both parsedData and parsedKind exist so later tree functionality can 
    change them to Python values, or, for example, test symbolic names 
    against tables.
    '''    
    def __init__(self):
        # paramcount of this expression
        self.paramCount = 0
        # has a body
        self.hasBody = False
        # for data which parses to a string.
        self.parsedData = None
        # parsefd names of objects will be in parsedData. But some
        # common names will be tokenised, and are stored here
        self.token = 0
        # position in source code
        self.position = NoPosition
        # is this a definition or usage of an expression 
        self.isDef = False
        # I thought this would be useful...
        self.isName = False
        # definition flags like inline, constant, etc.
        self.flags = []
        # Link to the owning namespace of this expression
        self.owner = None
        # The kind of this expression. For literals, a value, for an
        # expression, the process of parameters to return
        self.kind = Any
        # carries a value for literals/atoms
        self.value = None
        
    def __repr__(self):
        return "Call on CodeMark, do not do this, use subtypes"
            
            
# class BuiltinCall(Tree):
    # '''
    # Represents a builtin call.
    # This tree will never appear in an AST, which cares not where the 
    # call is located.
    # It is useful in places where a tree is needed but can not be 
    # provided, for example as a reference for keywords in the name 
    # tables. 
    # '''
    # def toString(self):
        # return 'BuiltinCall()'    



class CommentBase(CodeMark):
    def __repr__(self):
        return  "Call on CommentBase, do not do this, use subtypes"




class SingleLineComment(CommentBase):
    def __repr__(self):
        return 'SingleLineComment("{}")'.format(self.parsedData)

def mkSingleLineComment(position, text): 
    t = SingleLineComment()
    t.parsedData = text
    t.position = position   
    return t
    
    
    
class MultiLineComment(CommentBase):
    def __repr__(self):
        return 'MultiLineComment("{}")'.format(self.parsedData)

def mkMultiLineComment(position, text): 
    t = MultiLineComment()
    t.parsedData = text
    t.position = position   
    return t
    

    
class ParameterDefinition(CodeMark):
    '''
    A parameter definition.
    These nodes are distinctive, they
    - ? have explicit kind
    - are leaves (no body) always
    - no body
    '''
    def __repr__(self):
        return "ParameterDefinition('{}')".format(self.parsedData)
        
def mkParameterDefinition(position, name):
    t = ParameterDefinition()
    t.position = position   
    t.isDef = True
    t.isName = True
    t.parsedData = name
    return t
    
    


    
#? Sort out some parsed types
#! how to handle chains?
class Data(CodeMark):
    '''
    A definition of data - a literal.
    In lisp terms, an ''atom'.
    '''        
    def __repr__(self):
        return  "Call on base class Data, do not do this, use subtypes"



class IntegerData(Data):
    def __repr__(self):
        return 'IntegerData({})'.format(self.parsedData)
        
def mkIntegerData(position, valueStr):
    t = IntegerData()
    t.parsedData = valueStr
    t.position = position
    return t



class FloatData(Data):
    def __repr__(self):
        return 'FloatData({})'.format(self.parsedData)
        
def mkFloatData(position, valueStr):
    t = FloatData()
    t.parsedData = valueStr
    t.position = position
    return t



class StringData(Data):
    def __repr__(self):
        return 'StringData("{}")'.format(self.parsedData)
        
def mkStringData(position, valueStr):
    t = StringData()
    t.parsedData = valueStr
    t.position = position
    return t



class CodeSeqNameless(CodeMark):
    #? difference between this and NamelessFunc
    '''
    Body expression with no name or params.
    Has no name, so has no params.
    Is a definition.
    Used as closures
    '''
    def __repr__(self):
        return "CodeSeqNameless({})".format(self.paramCount)
       
def mkCodeSeqNameless(position, paramCount):
    t = CodeSeqNameless()
    t.paramCount = paramCount
    t.isDef = True
    t.position = position
    return t

    
#! we need to figure what is useful in tree manipulation i.e. DefMixin
# may be useful? ParamMixin?
#! is ExpressionCall
#! so what about definitions? They are expressions.
#! is the definition hasParams = True?
#x not necessary. Main/EntryPoint can be a context func. Namespace also.
# Others are just a Seq (NamelessBody)?
class Action(CodeMark):
    '''
    Define/call something to do with data.
    '''
    def __repr__(self):
        return  "Call on base class Action, do not do this, use subtypes"


#class NamelessListCall(CodeMark, ParameterMixin):
    #'''
    #Has return value
    #'''
    #def __init__(self, params):
        #super().__init__()    
        #self.params = params
        ## chain contains reviever-notated expressions. 
        ## ask the chain to be by instance, not classwide.
        ##self.chain = []

    #def toString(self):
        #return "NamelessListCall('{}', {})".format(self.parsedData, self.params)

#class Assignment(CodeMark):
    #'''
    #Joins a treeInfo and a list of NamelessData/Action.
    #The list is ''parameters'.
    #e.g. val e = 4
    #=(e, 4)
    #'''
    #returnKind = NoKind
    #treeInfo = NoTreeInfo
    #body = []


class ActionWithBodyBase(Action):
    '''
    Action with a body.
    The body is a list which will be handled in context of the params. 
    '''
    def __repr__(self):
        return  "Call on base class ActionWithBodyBase, do not do this, use subtypes"

        
#? intruiging. Are variables like this then?
class DataDefine(ActionWithBodyBase):
    '''
    Action where the body is executed for data.
    Or, a ''val' or ''var' of some kind
    No params
    e.g. dc pi = { 3.142 }
    '''
    def __repr__(self):
        return "DataDefine('{}')".format(self.parsedData)
                
def mkDataDefine(position, nameStr):
    t = DataDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.position = position
    return t
    
    
# NameSpaceDefine
class CodeSlotNamedDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of surrounding code.
    Or, a ''closure' or 'inline'.
    Special case
    e.g. sc log {  }
    '''
    def __repr__(self):
        return "CodeSlotNamedDefine('{}' {})".format(
        self.parsedData,
        self.paramCount
        )

def mkCodeSlotNamedDefine(position, nameStr):
    t = CodeSlotNamedDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.position = position
    return t
    
    
class CodeSeqNamedDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of surrounding code.
    Or, a ''closure' or 'inline'.
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def __repr__(self):
        return "CodeSeqNamedDefine('{}')".format(
        self.parsedData
        )

def mkCodeSeqNamedDefine(position, nameStr):
    t = CodeSeqNamedDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.position = position
    return t
    
# UnboundContextDefine
class CodeSeqUnnamedDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of surrounding code.
    Or, a ''closure' or 'inline'.
    Special case
    e.g. { *(x, y) }
    '''
    def __repr__(self):
        return "CodeSeqUnnamedDefine()"

def mkCodeSeqUnnamedDefine(position):
    t = CodeSeqUnnamedDefine()
    t.isDef = True
    t.position = position
    return t
                   
                   
class CodeSeqContextDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def __repr__(self):
        return "CodeSeqContextDefine('{}', {})".format(
            self.parsedData,
            self.paramCount
            )
                
def mkCodeSeqContextDefine(position, nameStr):
    t = CodeSeqContextDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.position = position
    return t
    
   
class OperatorContextDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    The paramcount is always 3.
    e.g. ac > x, y { x > y }
    '''
    def __repr__(self):
        return "OperatorContextDefine('{}')".format(
            self.parsedData,
            )
                            
def mkOperatorContextDefine(position, nameStr):
    t = OperatorContextDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.paramCount = 3
    t.position = position
    return t


class MonoOperatorContextDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    The paramcount is always 2.
    e.g. def -x { -x }
    '''        
    def __repr__(self):
        return "MonoOperatorContextDefine('{}')".format(
            self.parsedData,
            )
                        
def mkMonoOperatorContextDefine(position, nameStr):
    t = MonoOperatorContextDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.paramCount = 2
    t.position = position
    return t
    

class ContextCall(ActionWithBodyBase):
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __repr__(self):
        return "ContextCall('{}', {})".format(
            self.parsedData,
            self.paramCount
            )
                
def mkContextCall(position, nameStr):
    t = ContextCall()
    t.isName = True
    t.parsedData = nameStr
    t.position = position
    return t                
           

class OperatorCall(ActionWithBodyBase):
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __repr__(self):
        return "OperatorCall('{}')".format(
            self.parsedData
            )            

def mkOperatorCall(position, nameStr):
    t = OperatorCall()
    t.isName = True
    t.parsedData = nameStr
    t.paramCount = 2
    t.position = position
    return t  

#? do we need?
class MonoOperatorCall(ActionWithBodyBase):
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __repr__(self):
        return "MonoOperatorCall('{}')".format(
            self.parsedData
            )            

def mkMonoOperatorCall(position, nameStr):
    t = MonoOperatorCall()
    t.isName = True
    t.parsedData = nameStr
    t.paramCount = 1
    t.position = position
    return t  
    
#?

class ConditionalStartCall(ActionWithBodyBase):
    '''
    Action where the body is executed conditional on the param.
    The two params are a condition and a body.
    e.g. if gt(x, y) { *(x, y) }
    '''
    def __repr__(self):
        return "ConditionalStartCall()"

def mkConditionalStartCall(position):
    t = ConditionalStartCall()
    t.paramCount = 2
    t.position = position
    return t  
                
        
class ConditionalEndCall(ActionWithBodyBase):
    '''
    Action where the body is executed conditionally in context of the params.
    loops
    Special case
    e.g. while(x, y) { *(x, y) }
    ''' 
    def __repr__(self):
        return "ConditionalEndCall()"
        

def mkConditionalEndCall(position):
    t = ConditionalEndCall()
    t.paramCount = 2
    t.position = position
    return t  
    
