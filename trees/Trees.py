from Position import NoPosition
from Kinds import *
from TreeInfo import TreeInfo, UndefinedTreeInfo, NoTreeInfo



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
    code which re[resents a working tree.
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
    
    def __init__(self):
        self.parsedData = None
        self.treeInfo = UndefinedTreeInfo
        self.position = NoPosition
        self.isChained = False

    def toString(self):
        return 'Tree()'
        
    def __repr__(self):
        return self.toString()



class CommentBase(Tree):
    typeStr = "Call on CommentBase, do not do this, use subtypes"
    
    def __init__(self, text):
        super().__init__()
        self.parsedData = text

    def toString(self):
        return '{}("{}")'.format(self.typeStr, self.parsedData)



class SingleLineComment(CommentBase):
    typeStr = "SingleLineComment"

def mkSingleLineComment(position, text): 
    t = SingleLineComment(text)
    t.position = position   
    return t
    
    
    
class MultiLineComment(CommentBase):
    typeStr = "MultiLineComment"

def mkMultiLineComment(position, text): 
    t = MultiLineComment(text)
    t.position = position   
    return t
    

    
#? very like a NamelessData with a TreeInfo....
class ParameterDefinition(Tree):
    '''
    A parameter definition.
    These nodes are distinctive, they
    - have explicit treeInfoing of kind
    - are tree leaves (no body) always???
    They also print out with explicit kind??? (no)
    '''
    parsedKind = ''
    
    def __init__(self, name):
        super().__init__()
        self.parsedData = name    

    def toString(self):
        return "ParameterDefinition('{}')".format(self.parsedData)
        
def mkParameterDefinition(position, name):
    t = ParameterDefinition(name)
    t.position = position   
    return t
    
    

class BodyParameterMixin():
    '''
    Mixin for any Tree accepting a body as a parameter.
    a body is a sequence of expressions, with the last expression
    auto-returning a value (the value may be None).
    
    As a parameter, a body will be loaded in an in an init,
    and printed in a toString().
    
    There is usually but not always one body parameter only. Since they 
    are used and consulted often, and shape much of the tree structure
    in an AST, body parameters are placed on a seperate attribute to 
    other parameters,
    
    This Mixin does little but establish that body parameters exist in
    a tree node.
    '''
    pass
        
    
#? Sort out some parsed types
#! how to handle chains?
class NamelessDataBase(Tree):
    '''
    A definition of data - a literal.
    In lisp terms, an ''atom'.
    '''
    parsedKind = ''
    typeStr = "Call on base NamelessDataBase, do not do this, use subtypes"
    
    def __init__(self, valueStr):
        super().__init__()
        self.parsedData = valueStr
        self.chain = []
        
    def toString(self):      
        #chainStr = '.'.join([e.toString for e in self.chain])
        return "{}({})".format(self.typeStr, self.parsedData)



class IntegerNamelessData(NamelessDataBase):
    typeStr = 'IntegerNamelessData'

def mkIntegerNamelessData(position, valueStr):
    t = IntegerNamelessData(valueStr)
    t.position = position
    return t



class FloatNamelessData(NamelessDataBase):
    typeStr = 'FloatNamelessData'

def mkFloatNamelessData(position, valueStr):
    t = FloatNamelessData(valueStr)
    t.position = position
    return t



class StringNamelessData(NamelessDataBase):
    typeStr = 'StringNamelessData'

    def toString(self):
        return 'StringNamelessData("{}")'.format(self.parsedData)

def mkStringNamelessData(position, valueStr):
    t = StringNamelessData(valueStr)
    t.position = position
    return t



    
#! is ExpressionCall
class Expression(Tree):
    '''
    Joins a name and a list of NamelessData/Expression.
    The list is ''parameters'.
    e.g. +(3,2)
    '''
    parsedKind = ''
    
    def __init__(self, nameStr, params):
        super().__init__()
        self.parsedData = nameStr
        self.params = params
        # chain contains reviever-notated expressions. 
        # ask the chain to be by instance, not classwide.
        self.chain = []

    def toString(self):
        chainStr = '.'.join([e.toString for e in self.chain])
        return "Expression('{}', {}){}".format(self.parsedData, self.params, chainStr)



#class Assignment(Tree):
    #'''
    #Joins a treeInfo and a list of NamelessData/Expression.
    #The list is ''parameters'.
    #e.g. val e = 4
    #=(e, 4)
    #'''
    #returnKind = NoKind
    #treeInfo = NoTreeInfo
    #body = []





class ExpressionWithBodyBase(Expression, BodyParameterMixin):
    '''
    Expression with a body.
    The body is a list which will be handled in context of the params. 
    '''
    def __init__(self, nameStr, params, body):
        super().__init__(nameStr, params)
        self.body = body
        
        
        
class DataDefine(ExpressionWithBodyBase):
    '''
    Expression where the body is executed for data.
    Or, a ''val' or ''var' of some kind
    No params
    e.g. val pi { 3.142 }
    '''
    def __init__(self, nameStr, body):
        super().__init__(nameStr, params=[], body=body)

    def toString(self):
        return "DataDefine('{}', {})".format(self.parsedData, self.body)
                
def mkDataDefine(position, nameStr):
    t = DataDefine(nameStr, [])
    t.position = position
    return t
    
    
    
class ContextDefine(ExpressionWithBodyBase):
    '''
    Expression where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def toString(self):
        return "ContextDefine('{}', {})".format(self.parsedData, self.params, self.body)
                
def mkContextDefine(position, nameStr):
    t = ContextDefine(nameStr, [], [])
    t.position = position
    return t
    


class ContextCall(ExpressionWithBodyBase):
    '''
    Call on a function/operator.
    Like a ContextCall, can take a name, parameters and a body (for closures).
    '''
    def toString(self):
        return "ContextCall('{}', {})".format(self.parsedData, self.params, self.body)
            
def mkContextCall(position, nameStr):
    t = ContextCall(nameStr, [], [])
    t.position = position
    return t
        

class MonoOpExpressionCall(Expression):
    '''
    Operator Expression with one parameter 
    Parameter can be a chain
    '''
    def toString(self):
        chainStr = '.'.join([e.toString for e in self.chain])
        return "MonoOpExpression('{}', {}){}".format(self.parsedData, self.params, chainStr)

            
def mkMonoOpExpressionCall(position, nameStr):
    t = MonoOpExpressionCall(nameStr, [])
    t.position = position
    return t

#?

class ConditionalCall(ExpressionWithBodyBase):
    '''
    Expression where the body is executed conditional on the params.
    Special case
    e.g. if gt(x, y) { *(x, y) }
    '''
    def toString(self):
        return "ConditionalCall('{}', {})".format(self.parsedData, self.params, self.body)


                
        
class ConditionalContextCall(ExpressionWithBodyBase):
    '''
    Expression where the body is executed conditionally in context of the params.
    loops
    Special case
    e.g. def while(x, y) { *(x, y) }
    '''    
    def toString(self):
        return "ConditionalContextCall('{}', {})".format(self.parsedData, self.params, self.body)
       


class NamelessFunc(ExpressionWithBodyBase):
    '''
    Body expression with no treeInfo.
    Also serves as the base for a main() parse.
    Special case.
    '''    
    def __init__(self, body):
        super().__init__(NoTreeInfo, params=[], body=body)

    def toString(self):
        return "NamelessFunc({})".format(self.body)
       
def mkNamelessFunc(position):
    t = NamelessFunc([])
    t.position = position
    return t
