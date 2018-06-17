from trees.Trees import *



class Visitor():
  
    def __init__(self, tree):
      self._dispatch(tree)

    def multiLineComment(self, t):
        pass

    def singleLineComment(self, t):
        pass
                      
    def parameterDefinition(self, t):
        pass

    def namelessDataBase(self, t):
        pass

    def monoOpExpressionCall(self, t):
        pass
        
    def dataDefine(self, t):
        pass
                    
    def contextDefine(self, t):
        pass
        
    def contextCall(self, t):
        pass 
                
    def conditionalCall(self, t):
        pass
        
    def conditionalContextCall(self, t):
        pass
        
    def namelessFunc(self, t):
        pass  
              
    def _dispatch(self, t):
        if (isinstance(t, SingleLineComment)):
            self.singleLineComment(t)
        elif (isinstance(t, MultiLineComment)):
            self.multiLineComment(t)
        elif (isinstance(t, ParameterDefinition)):
            self.parameterDefinition(t)
        elif (isinstance(t, NamelessDataBase)):
            self.namelessDataBase(t)
        elif (isinstance(t, MonoOpExpressionCall)):
            self.monoOpExpressionCall(t)
        elif (isinstance(t, ExpressionWithBodyBase)):
            if (isinstance(t, DataDefine)):
                self.dataDefine(t)
            elif (isinstance(t, ContextDefine)):
                self.contextDefine(t)
            elif (isinstance(t, ContextCall)):
                self.contextCall(t)
            elif (isinstance(t, ConditionalCall)):
                self.conditionalCall(t) 
            elif (isinstance(t, ConditionalContextCall)):
                self.conditionalContextCall(t)           
            elif (isinstance(t, NamelessFunc)):
                self.namelessFunc(t)            
            for e in t.body:
                self._dispatch(e)
        else:
            print("tree.Visitor: unrecognised tree. Kind:'{}'".format(type(t).__name__))


class VisitorWithDepth():
    indent = 2
    chainIndent = 1
    
    def __init__(self, tree):
      self._dispatch(0, tree, False)

    def multiLineComment(self, depth, chained, t):
        pass

    def singleLineComment(self, depth, chained, t):
        pass
        
    def parameterDefinition(self, depth, chained, t):
        pass

    def namelessDataBase(self, depth, chained, t):
        pass

    def monoOpExpressionCall(self, depth, chained, t):
        pass
        
    def dataDefine(self, depth, chained, t):
        pass
        
    def contextDefine(self, depth, chained, t):
        pass

    def contextCall(self, depth, chained, t):
        pass 
                                            
    def conditionalCall(self, depth, chained, t):
        pass

    def conditionalContextCall(self, depth, chained, t):
        pass
        
    def namelessFunc(self, depth, chained, t):
        pass
        
    def _dispatch(self, depth, t, chained=False):
        if (isinstance(t, SingleLineComment)):
            self.singleLineComment(depth, chained, t)
        elif (isinstance(t, MultiLineComment)):
            self.multiLineComment(depth, chained, t)
        elif (isinstance(t, ParameterDefinition)):
            self.parameterDefinition(depth, chained, t)
        elif (isinstance(t, NamelessDataBase)):
            self.namelessDataBase(depth, chained, t)
        elif (isinstance(t, MonoOpExpressionCall)):
            self.monoOpExpressionCall(depth, chained, t)
        elif (isinstance(t, ExpressionWithBodyBase)):
            if (isinstance(t, DataDefine)):
                self.dataDefine(depth, chained, t)
            elif (isinstance(t, ContextDefine)):
                self.contextDefine(depth, chained, t) 
            elif (isinstance(t, ContextCall)):
                self.contextCall(depth, chained, t)
            elif (isinstance(t, ConditionalCall)):
                self.conditionalCall(depth, chained, t) 
            elif (isinstance(t, ConditionalContextCall)):
                self.conditionalContextDefinition(depth, chained, t)           
            elif (isinstance(t, NamelessFunc)):
                self.namelessFunc(depth, chained, t)   
            newDepth = depth + self.indent
            for e in t.body:
                self._dispatch(newDepth, e, False)      
        else:
            print("tree.VisitorWithDepth: unrecognised tree. Kind:'{}'".format(type(t).__name__))

        if ((isinstance(t, Expression) or isinstance(t, NamelessDataBase)) and t.chain):
            #self.chainedFunctions(depth + self.chainIndent, t.chain)
            chainDepth = depth + self.chainIndent
            for ct in t.chain: 
                self._dispatch(chainDepth, ct, True)            



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
        print("{}[{}, {}]".format(indent, t._in, t._out))
        print("{}{}('{}')".format(indent, type(t).__name__, t.parsedData))

    def multiLineComment(self, depth, chained, t):
        self._print(depth, chained, t)

    def singleLineComment(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def parameterDefinition(self, depth, chained, t):
        self._print(depth, chained, t)

    def namelessData(self, depth, chained, t):
        self._print(depth, chained, t)

    def monoOpExpressionCall(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def dataDefine(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def contextDefine(self, depth, chained, t):
        self._print(depth, chained, t)

    def contextCall(self, depth, chained, t):
        self._print(depth, chained, t)
                      
    def conditionalCall(self, depth, chained, t):
        self._print(depth, chained, t)
               
    def conditionalContextCall(self, depth, chained, t):
        self._print(depth, chained, t)
        
    def namelessFunc(self, depth, chained, t):
        self._print(depth, chained, t)



#class VisitorTransformer():
  
    #def __init__(self, tree):
      #self._dispatch(tree)

    #def comment(self, t):
        #pass
              
    #def parameterDefinition(self, t):
        #pass

    #def namelessData(self, t):
        #pass

    #def monoOpExpressionCall(self, depth, chained, t):
        #pass
        
    #def dataDefine(self, t):
        #pass
                    
    #def contextDefine(self, t):
        #pass
        
    #def contextCall(self, t):
        #pass 
                
    #def conditionalCall(self, t):
        #pass
        
    #def conditionalContextCall(self, t):
        #pass
        
    #def namelessFunc(self, t):
        #pass  
              
    #def _dispatch(self, t):
        #if (isinstance(t, Comment)):
            #self.comment(t)
        #elif (isinstance(t, ParameterDefinition)):
            #self.parameterDefinition(t)
        #elif (isinstance(t, NamelessData)):
            #self.namelessData(t)
        #elif (isinstance(t, MonoOpExpressionCall)):
            #self.monoOpExpressionCall(t)
        #elif (isinstance(t, ExpressionWithBodyBase)):
            #if (isinstance(t, DataDefine)):
                #self.dataDefine(t)
            #elif (isinstance(t, ContextDefine)):
                #self.contextDefine(t)
            #elif (isinstance(t, ContextCall)):
                #self.contextCall(t)
            #elif (isinstance(t, ConditionalCall)):
                #self.conditionalCall(t) 
            #elif (isinstance(t, ConditionalContextCall)):
                #self.conditionalContextCall(t)           
            #elif (isinstance(t, NamelessFunc)):
                #self.namelessFunc(t)            
            #for e in t.body:
                #self._dispatch(e)
        #else:
            #print("tree.Visitor: unrecognised tree. Kind:'{}'".format(type(t).__name__))
