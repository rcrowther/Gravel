from Position import NoPosition
from Kinds import *
#from TreeInfo import TreeInfo, UndefinedTreeInfo, NoTreeInfo


#! needs rework
#! probably replace with simple attributes, like isDefinition
class BodyParameterMixin():
    '''
    Mixin for any Tree accepting a body as a parameter.
    a body is a sequence of expressions, with the last expression
    auto-returning a value (the value may be None).

    Applied to both definitions and calls.
    
    As a parameter, a body will be loaded in an init,
    and printed in a toString().
    
    There is usually but not always one body parameter only. Since they 
    are used and consulted often, and shape much of the tree structure
    in an AST, body parameters are placed on a seperate attribute to 
    other parameters,
    
    This Mixin does little but establish that a tree node contains 
    bodies.
    '''
    #self.body = body
    pass
     
     
        
class NameMixin():
    '''
    Mixin for any Tree accepting a name.

    Applied to both definitions and calls.
    
    As a parameter, a name will be loaded in an init,
    and printed in a toString().
        
    There is one name per tree. Since they 
    are used and consulted often, and have checks and references,
    name are placed on a seperate attribute to 
    other parameters,
    
    This Mixin does little but establish that tree node contains a name.
    '''
    #self.parsedData = nameStr
    pass
    

#! may well need module defs etc. See,
#! /home/rob/Downloads/scala-2.12.0/src/reflect/scala/reflect/api/Trees.scala
#! assignment tree
#! 
# Now, we could do a LISP thing and make everything a list,
# but future? typechecking may go easier if we model the common groups
# of constructs.
# NB: This looks like odd Python. It is. It is a little delicate.
# In particular, do not put defaults on the inits. If you need
# defaults, put them in the factories. Defaults on inits that match
# classwide attribute values will not change classwide attributes to 
# instance-specific values.
class Tree():
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
    # For parsed data
    #dataStr = None
    # for final data
    #data = None
    #position = NoPosition
    #* Would be a recusive definition, so None
    #?
    _in = None
    _out = None
    
    _prev = None
    _next = None
    
    isDefinition =  False
    isMark =  False
    
    def __init__(self):
        self.parsedData = None
        self.position = NoPosition
        self.isChained = False

    def toString(self):
        return 'Tree()'
        
    def __repr__(self):
        return self.toString()


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
                
def mkCodeSeqContextDefine(position, nameStr, paramCount):
    t = CodeSeqContextDefine()
    t.isDef = True
    t.isName = True
    t.parsedData = nameStr
    t.paramCount = paramCount
    t.position = position
    return t
    
???    
class OperatorContextDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isDefinition = True
        self.isMark = True

    def toString(self):
        return "OperatorContextDefine('{}', {}, {})".format(
            self.parsedData,
            self.params,
            self.body
            )
                
def mkOperatorContextDefine(position, nameStr):
    t = OperatorContextDefine(nameStr, [], [])
    t.position = position
    return t

class MonoOperatorContextDefine(ActionWithBodyBase):
    '''
    Action where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isDefinition = True
        self.isMark = True

    def toString(self):
        return "MonoOperatorContextDefine('{}', {}, {})".format(
            self.parsedData,
            self.params,
            self.body
            )
                
def mkMonoOperatorContextDefine(position, nameStr):
    t = MonoOperatorContextDefine(nameStr, [], [])
    t.position = position
    return t
    
    
class ContextCall(ActionWithBodyBase):
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isMark = True

    def toString(self):
        return "ContextCall('{}', {})".format(self.parsedData, self.params, self.body)
            
def mkContextCall(position, nameStr):
    t = ContextCall(nameStr, [], [])
    t.position = position
    return t
        

class OperatorCall(ActionWithBodyBase):
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isMark = True

    def toString(self):
        return "OperatorCall('{}', {})".format(self.parsedData, self.params, self.body)
            
def mkOperatorCall(position, nameStr):
    t = OperatorCall(nameStr, [], [])
    t.position = position
    return t


class OperatorCallMark():
    '''
    Call on a function/operator.
    Can take a name, parameters and a body (for closures).
    '''
    def __init__(self, opStr, paramCount):
        self.opStr = opStr
        self.paramCount = paramCount
        self.position = NoPosition


    def __repr__(self):
        return "OperatorCallMark('{}', {})".format(
            self.opStr, 
            self.paramCount
            )
            
def mkOperatorCallMark(position, opStr):
    t = OperatorCallMark(opStr, 2)
    t.position = position
    return t                

            
# should this exist, or should we drop it?
# was here for infixing, I recall
class MonoOpActionCall(Action):
    '''
    Operator Action with one parameter 
    Parameter can be a chain
    '''
    def __init__(self, nameStr, params):
        super().__init__(nameStr, params)
        self.isMark = True

    def toString(self):
        chainStr = '.'.join([e.toString for e in self.chain])
        return "MonoOpAction('{}', {}){}".format(self.parsedData, self.params, chainStr)

            
def mkMonoOpActionCall(position, nameStr):
    t = MonoOpActionCall(nameStr, [])
    t.position = position
    return t

#?

class ConditionalCall(ActionWithBodyBase):
    '''
    Action where the body is executed conditional on the params.
    Special case
    e.g. if gt(x, y) { *(x, y) }
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isMark = True
        
    def toString(self):
        return "ConditionalCall('{}', {})".format(self.parsedData, self.params, self.body)


                
        
class ConditionalContextCall(ActionWithBodyBase):
    '''
    Action where the body is executed conditionally in context of the params.
    loops
    Special case
    e.g. def while(x, y) { *(x, y) }
    ''' 
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params, body)
        self.isMark = True
        
    def toString(self):
        return "ConditionalContextCall('{}', {})".format(self.parsedData, self.params, self.body)
       


class NamelessFunc(ActionWithBodyBase):
    '''
    Body expression with no name or params.
    Has no name, so has no params.
    Used to break chain sequences into small units
    1 + {2/3}
    and as closures
    '''    
    #? difference between this and NamelessBody
    #! Currently serves as the base for a main() access point?? (which needs parameters, no?)
    def __init__(self, body):
        #! the name needs some thought
        # diven a valid name because the attribute is tested, 
        # here and there
        super().__init__('namelessFunc', [], body)
        self.body = body

    def toString(self):
        return "NamelessFunc({})".format(self.body)
       
def mkNamelessFunc(position):
    t = NamelessFunc([])
    t.position = position
    return t

