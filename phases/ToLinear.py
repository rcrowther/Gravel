from Phases import Phase
from trees.Visitors import VisitorForBodies



#! needs to visit call parameters too
class ChainsReverse(VisitorForBodies):
      def chainReverse(self, b, it, firstChild):
          #print('trverse:' + str(firstChild))
          cb = [firstChild]
          # The last unmarked child ends the chain
          # hence this unusual, natural loop
          while (True):
              child = next(it)
              cb.append(child)
              if (not child.isChained):
                  break
          b.extend(reversed(cb))
         
      def nodeWithBody(self, t):
          b = []
          it = iter(t.body)
          try:
              while(True):
                  child = next(it)
                  #print('handle:' + str(child))
                  #print('cfn:' + str(child.isChained))
                  if(child.isChained):
                      self.chainReverse(b, it, child)
                      #print('chld:' + str(child))
                  else:
                      b.append(child)
          except StopIteration:
              pass
          t.body = list(b)
  
class TreeChainsReverse(Phase):
    #? after Syntax so there is a tree
    def __init__(self):
        Phase.__init__(self,
            "Reverse chains in the AST Tree",
            "Chains are reversed so they can be easily processed.",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        ChainsReverse(compilationUnit.tree)
        
# used for typechecking
# Traverses the AST to put returns mostly in order
# so 
#x ?
#class ASTToLinear(NonTraversingVisitor):
    #def __init__(self, tree):
        #self.b = []
        #self.visit(tree)
        
        
    ##for AST?
    #def multiLineComment(self, t):
        ## not interested
        #pass

    #def singleLineComment(self, t):
        ## not interested
        #pass
                      
    #def parameterDefinition(self, t):
        ## not interested
        ##change of scope
        #pass

    #def namelessDataBase(self, t):
        #self.b.append(t)

    #def monoOpExpressionCall(self, t):
        #self.b.append(t)
        
    #def dataDefine(self, t):
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                 
    #def namelessBody(self, t):
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                
    #def contextDefine(self, t):
        ##change of scope
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                
    #def contextCall(self, t):
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                        
    #def conditionalCall(self, t):
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                
    #def conditionalContextCall(self, t):
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)
                
    #def namelessFunc(self, t):
        ##print('twaddle')
        #for e in t.body:
            #self.visit(e) 
        #self.b.append(t)

    #def result(self):
        #return self.b
