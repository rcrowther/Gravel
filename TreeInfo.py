

#? could stash definition position, value, state, scope. And flags like 
# inline, constant, etc.
#? however, not kind. 
#? compainion modules
#? establish owners
#! printers
#? makes a lot of sense to
#  Symbols (for typechecking)
#   - Name (for example, ‘x’, ‘y’, ‘number’)
#   - Category (Is it a variable, subroutine, or built-in type?)
#   - Type (INTEGER, REAL)

# Here is the bracket issue
# 2 + 1 / 3
# Simply,
# 2 (+ 1) (/ 3) = 1
# But,
# 2 + (1/3) = 2.3333...
# Classic AST,
#  +
# 2
#    /
#   1 3
# Would be evaluated by depth-first, bottom-up traversal (postorder),
#  2 + (1/3)
# but we have no binop. We have (raw),
# 2
#  + 1
#     / 3
# unless we use UnnamedExpression
# 2
#   + UnnamedExpression
#       + 1
#          / 3
# which builds the structure in. 
# Next problem, evaluation/codegen.
# As it happens, eval is no biggie, since we do not care about 
# evaluation order, we can evaluate in much the 
# same way as as convention---recursivly follow down, evaluate from
# contained to container.
# Codegen is not more difficult, it's a register change, then summation?

class TreeInfo:
    '''
    Carries data about a treenode.
    Note that information that applies to unlabeled data (literals)
    and unlabeled functions (lambdas) will not be here, it should be
    on trees. Kind is a returntype for any expression, so is on 
    the trees.
    Value is intended as the name of an expression, or the value of 
    noNameData.
    
    '''
    is_defined = False
    #is_reference = False
    
    def __init__(self, name):
        self.value = None
        self.name = name

    def toString(self):
        return "TreeInfo('{}')".format(self.name)

    def __repr__(self):
        return self.toString()


class _UndefinedTreeInfo(TreeInfo):
    '''
    Only used to init parsed trees.
    '''
    def __init__(self):
        self.name = None

    def toString(self):
        return "UndefinedTreeInfo"
  
UndefinedTreeInfo = _UndefinedTreeInfo()

class _NoTreeInfo(TreeInfo):
    #@property
    #def name(self):
        #raise AttributeError("'name' not available on the NoTreeInfo object")

    #@name.setter
    #def name(self, value):
        #raise AttributeError("'name' not available on the NoTreeInfo object")

    def __init__(self):
        self.name = None

    def toString(self):
        return "NoTreeInfo"
  
NoTreeInfo = _NoTreeInfo()
