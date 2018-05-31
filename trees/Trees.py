from Position import NoPosition
from Kinds import *
from Mark import Mark, UndefinedMark




# Now, we could do a LISP thing and make everything a list,
# but future? typechecking may go easier if we model the common groups
# of constructs.
class Tree():
    '''
    Tree init() should be designed so the class will accept the 
    parsed and identifying data. The init should not contain 
    supplementary information. This is so toString() will print working 
    code.
    Use a factory for other inits e.g. for tree builders.
    Note this base can be leaf or branch---it has no children.
    '''
    # For parsed data
    data_str = None
    # for final data
    data = None
    position = NoPosition
    #def __init__(self):
    #    self.position = position

    def toString(self):
        return 'Tree()'
        
    def __repr__(self):
        return self.toString()
        
        
        
class Comment(Tree):
    #def __init__(self, data = None):
      #self.data_str = text
      #self.data = text.strip()

    def toString(self):
        return 'Comment("{}")'.format(self.data)

def mkComment(position, text):
    t = Comment()
    t.data_str = text 
    t.data = text.strip()
    t.position = position   
    return t


#! do all marks have a kind?
#! if so, should it be in here? As an expression?
class MarkNode(Tree):
    '''
    Marks are a name attached to some action.
    In other languages, a ''symbol' or 'label'.
    marks may be defined by the user (e.g. vars, action names, data names, etc)
    or builtin (e.g. arithmetic operators)
    '''
    # at the very least, the Mark carries a position, over and above
    # the name.
    # A concrete class. See MarkTable.
    def __init__(self, mark = UndefinedMark):
        assert isinstance(mark, Mark), "Value for 'mark' must be an instance of Mark: value: {} type:{}".format(mark, type(mark))
        self.data = mark

    def toString(self):
        return "MarkNode({})".format(self.data.toString())


#! whats this for?
class _NoMarkNode(MarkNode):
    def __init__(self):
        self.data = UndefinedMark

    def toString(self):
        return "NoMarkNode"
        
NoMarkNode = _NoMarkNode()




#? very like an atom with a mark....
class ParameterDefinition(Tree):
    '''
    A parameter definition.
    These nodes are distinctive, they have,
    - explicit marking of kind
    - are tree leaves (no body) always???
    They also print out with explicit kind.
    '''
    data = UndefinedMark
    kindStr = None
    returnKind = UnknownKind
    
    def __init__(self, mark = UndefinedMark):
        self.data = mark    

    def toString(self):
        return "{}:{}".format(self.data, self.returnKind)
        
def mkParameterDefinition(position, markStr, kindStr):
    t = ParameterDefinition()
    t.data_str = markStr
    t.kindStr = kindStr
    t.position = position   
    return t
    
    
    
    
#? Sort out some parsed types
class Atom(Tree):
    '''
    A definition of data - a literal.
    In lisp terms, an ''atom'.
    '''
    returnKind = UnknownKind
    typ_str = "Call on base Atom, do not do this, use subtypes"
    
    def __init__(self, data = None):
        self.data = data
    #data_type = None
    #def __init__(self, position, data, tpe):

    def toString(self):
        return "{}({})".format(self.typ_str, self.data)




class IntegerAtom(Atom):
    returnKind = IntegerKind
    typ_str = 'IntegerAtom'



class FloatAtom(Atom):
    returnKind = FloatKind
    typ_str = 'FloatAtom'

    def toString(self):
        return 'FloatAtom({})'.format(self.data)
        


class StringAtom(Atom):
    returnKind = StringKind
    typ_str = 'StringAtom'

    def toString(self):
        return 'StringAtom("{}")'.format(self.data)



    
class Expression(Tree):
    '''
    Joins a mark and a list of Atom/Expression.
    The list is ''parameters'.
    e.g. +(3,2)
    '''
    kindStr = None
    returnKind = UnknownKind
    #mark = NoMarkNode
    # Params is separate from child lists, which are for bodies.
    #params = []
    
    def __init__(self, mark = UndefinedMark, params=[]):
        self.mark = mark
        self.params = params
        
    def toString(self):
        return "Expression({}, {})".format(self.mark.toString(), self.params)



#class Assignment(Tree):
    #'''
    #Joins a mark and a list of Atom/Expression.
    #The list is ''parameters'.
    #e.g. val e = 4
    #=(e, 4)
    #'''
    #returnKind = NoKind
    #mark = NoMark
    #body = []




class ExpressionWithBodyBase(Expression):
    '''
    Expression with a body.
    The body is a list which will be handled in context of the params. 
    '''
    def __init__(self, mark = UndefinedMark, params=[], body=[]):
        self.body = body
        super().__init__(mark, params)
        
        
        
        
class ConditionalNode(ExpressionWithBodyBase):
    '''
    Expression where the body is executed conditional on the params.
    Special case
    e.g. if gt(x, y) { *(x, y) }
    '''
    def toString(self):
        return "Conditional({}, {})".format(self.mark.toString(), self.params, self.body)
        
        
        
class ContextNode(ExpressionWithBodyBase):
    '''
    Expression where the body is executed in context of the params.
    Or, a ''function' or ''proceedure' of some kind
    Special case
    e.g. def mult(x, y) { *(x, y) }
    '''
    def toString(self):
        return "ParameterContext({}, {})".format(self.mark.toString(), self.params, self.body)
        
        
def mkContextNode(position, markStr):
    t = ContextNode()
    t.data_str = markStr
    t.position = position
    return t
    
    
    
    
class ConditionalContextNode(ExpressionWithBodyBase):
    '''
    Expression where the body is executed conditionally in context of the params.
    loops
    Special case
    e.g. def while(x, y) { *(x, y) }
    '''    
    def toString(self):
        return "ConditionalContext({}, {})".format(self.mark.toString(), self.params, self.body)
       


class Lambda(ExpressionWithBodyBase):
    '''
    Body expression with no mark.
    Also serves as the base for a main() parse.
    Special case.
    '''
    def __init__(self, params=[], body=[]):
        super().__init__(NoMark, params=params, body=body)

    def toString(self):
        return "Lambda({}, {})".format(self.params, self.body)
       
