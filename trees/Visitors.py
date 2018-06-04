from trees.Trees import *



class Visitor():
  
    def __init__(self, tree):
      self._dispatch(tree)

    def comment(self, t):
        pass
              
    def constant(self, t):
        pass

    def parameterDefinition(self, t):
        pass

    def atom(self, t):
        pass
                            
    def conditionalNode(self, t):
        pass
                      
    def contextNode(self, t):
        pass
        
    def contextCall(self, t):
        pass 
               
    def conditionalContextNode(self, t):
        pass
        
    def lambdaDefine(self, t):
        pass  
              
    def _dispatch(self, t):
        if (isinstance(t, Comment)):
            self.comment(t)
        elif (isinstance(t, ParameterDefinition)):
            self.parameterDefinition(t)
        elif (isinstance(t, Atom)):
            self.atom(t)
        elif (isinstance(t, ExpressionWithBodyBase)):
            if (isinstance(t, ConditionalNode)):
                self.conditionalNode(t) 
            elif (isinstance(t, ContextNode)):
                self.contextNode(t) 
            elif (isinstance(t, ContextCall)):
                self.contextCall(t)
            elif (isinstance(t, ConditionalContextNode)):
                self.conditionalContextNode(t)           
            elif (isinstance(t, Lambda)):
                self.lambdaDefine(t)            
            for e in t.body:
                self._dispatch(e)
        else:
            print("unrecognised tree. Kind:''".format(type(t).__name__))


class VisitorWithDepth():
    indent = 2
    chainIndent = 1
    
    def __init__(self, tree):
      self._dispatch(0, tree, False)

    def comment(self, depth, chained, t):
        pass
              
    def constant(self, depth, chained, t):
        pass

    def parameterDefinition(self, depth, chained, t):
        pass

    def atom(self, depth, chained, t):
        pass
                            
    def conditionalNode(self, depth, chained, t):
        pass
                      
    def contextNode(self, depth, chained, t):
        pass
        
    def contextCall(self, depth, chained, t):
        pass 
               
    def conditionalContextNode(self, depth, chained, t):
        pass
        
    def lambdaDefine(self, depth, chained, t):
        pass
        
    def _dispatch(self, depth, t, chained=False):
        if (isinstance(t, Comment)):
            self.comment(depth, chained, t)
        elif (isinstance(t, ParameterDefinition)):
            self.parameterDefinition(depth, chained, t)
        elif (isinstance(t, Atom)):
            self.atom(depth, chained, t)
        elif (isinstance(t, ExpressionWithBodyBase)):
            if (isinstance(t, ConditionalNode)):
                self.conditionalNode(depth, chained, t) 
            elif (isinstance(t, ContextNode)):
                self.contextNode(depth, chained, t) 
            elif (isinstance(t, ContextCall)):
                self.contextCall(depth, t)
            elif (isinstance(t, ConditionalContextNode)):
                self.conditionalContextNode(depth, chained, t)           
            elif (isinstance(t, Lambda)):
                self.lambdaDefine(depth, chained, t)   
            newDepth = depth + self.indent
            for e in t.body:
                self._dispatch(newDepth, e, False)      
        else:
            print("[Error] Unrecognised tree. Kind:''".format(type(t).__name__))

        if (isinstance(t, Expression) and t.chain):
            #self.chainedFunctions(depth + self.chainIndent, t.chain)
            self._dispatch(depth + self.chainIndent, t.chain[0], True)            



class RawPrint(VisitorWithDepth):
    '''
    Print parsed string data from a tree.
    Helpful especially in the first phases, when Marks have not been
    allocated, so are not visible through toString().
    '''
    chainIndent = 4
        
    def _print(self, depth, chained, t):
        indent = ' ' * depth            
        if (chained):
            # U+2500 BOX DRAWINGS LIGHT HORIZONTAL
            # U+2514 BOX DRAWINGS LIGHT UP AND RIGHT
            # U+251C BOX DRAWINGS LIGHT VERTICAL AND RIGHT
            indent += '└── '
        print("{}{}('{}')".format(indent, type(t).__name__, t.dataStr))

    def comment(self, depth, chained, t):
        self._print(depth, chained, t)
              
    def constant(self, depth, chained, t):
        self._print(depth, chained, t)

    def parameterDefinition(self, depth, chained, t):
        self._print(depth, chained, t)

    def atom(self, depth, chained, t):
        self._print(depth, chained, t)
              
    def conditionalNode(self, depth, chained, t):
        self._print(depth, chained, t)
                      
    def contextNode(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def contextCall(self, depth, chained, t):
        self._print(depth, chained, t)
               
    def conditionalContextNode(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def lambdaDefine(self, depth, chained, t):
        self._print(depth, chained, t)
