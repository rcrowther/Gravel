from trees.Trees import *



class NonTraversingVisitor():
    '''
    A visitor which makes no attempt to auto-traverse a tree.
    visit() must be called directly.
    Each enabled visit method must make decisions and call visit() to 
    move through a tree structure.
    '''
    #? Reusable class (no init)
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
         
    def namelessBody(self, t):
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
              
    def visit(self, t):
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
        elif (isinstance(t, BodyParameterMixin)):
            if (isinstance(t, DataDefine)):
                self.dataDefine(t)
            elif (isinstance(t, NamelessBody)):
                self.namelessBody(t)                
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
        else:
            print("tree.NonTraversingVisitor: unrecognised tree. Kind:'{}'".format(type(t).__name__))


class VisitorNodeDispatch():
    '''
    A visitor which traverses the entire tree.
    The nodes are only dispatched t one method. This can be useful for
    visiting where only a small number of nodes need to be looked at.
    The downside is that most code that uses this visitor must test for
    tree type manually.
    Params are visited first, then bodies. 
    '''
    def __init__(self, tree):
      self._dispatch(tree)

    def node(self, t):
        pass
              
    def _dispatch(self, t):
        self.node(t)
        if (isinstance(t, Expression)): 
            for e in t.params:
                self._dispatch(e)                     
        if (isinstance(t, BodyParameterMixin)):           
            for e in t.body:
                self._dispatch(e)


class Visitor():
    '''
    A visitor which traverses the entire tree.
    '''
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
         
    def namelessBody(self, t):
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
        elif (isinstance(t, BodyParameterMixin)):
            if (isinstance(t, DataDefine)):
                self.dataDefine(t)
            elif (isinstance(t, NamelessBody)):
                self.namelessBody(t)                
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



class VisitorForBodies():
    '''
    Visit all nodes that contain a body.
    Note that this will not explore chains.
    Note also that his can mutate the body, as the body is traversed 
    after the tree is dispatched.
    '''  
    def __init__(self, tree):
      self._dispatch(tree)
        
    def nodeWithBody(self, t):
        pass  
              
    def _dispatch(self, t):
        if (isinstance(t, BodyParameterMixin)):
            self.nodeWithBody(t)
            for e in t.body:
                self._dispatch(e)


#x
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
        
    def namelessBody(self, depth, chained, t):
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
        elif (isinstance(t, BodyParameterMixin)):
            if (isinstance(t, DataDefine)):
                self.dataDefine(depth, chained, t)
            elif (isinstance(t, NamelessBody)):
                self.namelessBody(depth, chained, t)
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



#class RawPrintOld(VisitorWithDepth):
    #'''    
    #Print a representation of the data in a tree.
    
    #Designed for easy reading.
    #Helpful especially in the first phases, when Marks have not been
    #allocated, so are not visible through toString().
    #'''
    #chainIndent = 4
        
    #def _print(self, depth, chained, t):
        #indent = ' ' * depth            
        ##if (chained):
        #if (t.isChained):
            ## U+2500 BOX DRAWINGS LIGHT HORIZONTAL
            ## U+2514 BOX DRAWINGS LIGHT UP AND RIGHT
            ## U+251C BOX DRAWINGS LIGHT VERTICAL AND RIGHT
            #indent += '┌── '
        ##print("{}[{}, {}]".format(indent, t._in, t._out))
        #print("{}{}('{}')".format(indent, type(t).__name__, t.parsedData))

    #def multiLineComment(self, depth, chained, t):
        #self._print(depth, chained, t)

    #def singleLineComment(self, depth, chained, t):
        #self._print(depth, chained, t)
        
    #def parameterDefinition(self, depth, chained, t):
        #self._print(depth, chained, t)

    #def namelessDataBase(self, depth, chained, t):
        #self._print(depth, chained, t)

    #def monoOpExpressionCall(self, depth, chained, t):
        #self._print(depth, chained, t)
        
    #def dataDefine(self, depth, chained, t):
        #self._print(depth, chained, t)

    #def namelessBody(self, depth, chained, t):
        #self._print(depth, chained, t)
        
    #def contextDefine(self, depth, chained, t):
        #self._print(depth, chained, t)

    #def contextCall(self, depth, chained, t):
        #self._print(depth, chained, t)
                      
    #def conditionalCall(self, depth, chained, t):
        #self._print(depth, chained, t)
               
    #def conditionalContextCall(self, depth, chained, t):
        #self._print(depth, chained, t)
        
    #def namelessFunc(self, depth, chained, t):
        #self._print(depth, chained, t)


# class RawPrint(VisitorWithDepth):
    # '''    
    # Print a representation of the data in a tree.
    
    # Designed for easy reading.
    # '''
    # indent = 2
    # chainIndent = 4

    # def __init__(self, tree, showParams=True):
        # self.showParams = showParams
        # self._dispatch(0, tree, False)
      
    # def _print(self, depth, t, isParam):
        # indent = ' ' * depth            
        # if (isParam):
            # indent += 'param: '
        # if (t.isChained):
            # # U+2500 BOX DRAWINGS LIGHT HORIZONTAL
            # # U+2514 BOX DRAWINGS LIGHT UP AND RIGHT
            # # U+251C BOX DRAWINGS LIGHT VERTICAL AND RIGHT
            # indent += '┌── '
        # #print("{}[{}, {}]".format(indent, t._in, t._out))
        # print("{}{}('{}')".format(indent, type(t).__name__, t.parsedData))

    # def _dispatch(self, depth, t, isParam):
        # self._print(depth, t, isParam)
        # newDepth = depth + self.indent
        # if (self.showParams and isinstance(t, Expression)):
            # for e in t.params:
                # self._dispatch(newDepth, e, True)                     
        # if (isinstance(t, BodyParameterMixin)):           
            # for e in t.body:
                # self._dispatch(newDepth, e, False)

def RPNToPN():
    it = iter(tree)
    paramStash = []
    outParams = []
    out = []
    try:
        while (True):
            # gather params
            while(True):
                e = next(it)
                if (e.paramCount > 0):
                    break
                paramStash.append(e)
            # Append the element taking params
            out.append(e)
            # attach params in original order, popping paramStash as we go
            paramStash = []
            for i in range(0, e.paramCount):
                outParams.append(paramStash.pop())
            out.extend(outParams)
    except StopIteration:
        pass
    return out
    

            
      
def RawPrint(tree, showParams=True):
    '''    
    Print a representation of the data in a tree.
    
    Designed for easy reading.
    '''
    for e in tree:
        print(str(e))

# def rawElemPrint(e, depth):
    # indent = " " * depth
    # print("{}{}".format(indent, e))        

    # '''    
    # Print a representation of the data in a tree.
    
    # Designed for easy reading.
    # '''
    # indentInc = 2
    # depth = 0
    # actionStack = []
    # out = []
    # it = tree.reverse()
    
        # paramCount = e.paramCount
        # if (paramCount > 0):
            # actionStack.append((i + actionStack, e))
        # else:
            # out.append(e)  
            # paramsWritten += 1
        
def _elemReverse(paramedElem, it, out):
        paramCount = paramedElem.paramCount
        for i in range(0, paramCount):
            e = next(it)
            #! quick fix, remove (most) comments
            while(isinstance(e, CommentBase)):
                e = next(it)
            if (e.paramCount > 0):
                _elemReverse(e, it, out)
            else:
                out.append(e)
        out.append(paramedElem)
                
def treeReverse(tree):
    #NB in Python, returns an iterator
    it = reversed(tree)
    out = []
    try:
        while(True):
            e = next(it)
            #! quick fix, remove (most) comments
            while(isinstance(e, CommentBase)):
                e = next(it)
            if (e.paramCount > 0):
                _elemReverse(e, it, out)
            else:
                out.append(e)        
    except StopIteration:
         pass
    out.reverse()
    return out
    
    
#? No point pluging into definitions unless called?
#? but since we only have a name table, we need to allocate memory? Maybe.
#class DepthFirstLRVisitor():
    #'''
    #A visitor which auto-traverses a tree in post-op order.
    #Post-op means the tree is traversed left-right depth-first. Another
    #way to say this is that it pulls out of the deepest leaves, but 
    #otherwise traverses left-right.
    #This visitor also traverses chains as tree branches, and traverses 
    #them in post-op order (i.e. last item first).
    #'''
    ##? Reusable class (no init)
    #def multiLineComment(self, t):
        #pass

    #def singleLineComment(self, t):
        #pass
                      
    #def parameterDefinition(self, t):
        #pass

    #def namelessDataBase(self, t):
        #pass

    #def monoOpExpressionCall(self, t):
        #pass
        
    #def dataDefine(self, t):
        #pass
         
    #def namelessBody(self, t):
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
        #if (isinstance(t, Expression)): 
            #for e in t.params:
                #self._dispatch(e)                     
        #if (isinstance(t, BodyParameterMixin)):           
            #for e in t.body:
                #self._dispatch(e)

        #if (isinstance(t, SingleLineComment)):
            #self.singleLineComment(t)
        #elif (isinstance(t, MultiLineComment)):
            #self.multiLineComment(t)
        #elif (isinstance(t, ParameterDefinition)):
            #self.parameterDefinition(t)
        #elif (isinstance(t, NamelessDataBase)):
            #self.namelessDataBase(t)
        #elif (isinstance(t, MonoOpExpressionCall)):
            #self.monoOpExpressionCall(t)
        #elif (isinstance(t, BodyParameterMixin)):
            #for e in t.body:
                #self._dispatch(e) 
            #if (isinstance(t, DataDefine)):
                #self.dataDefine(t)
            #elif (isinstance(t, NamelessBody)):
                #self.namelessBody(t)                
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
        #else:
            #print("tree.NonTraversingVisitor: unrecognised tree. Kind:'{}'".format(type(t).__name__))
