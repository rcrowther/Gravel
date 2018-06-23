

# used for typechecking
# Traverses the AST to put returns mostly in order
# so 
class ASTToLinear(NonTraversingVisitor):
    def __init__(self, tree):
        self.b = []
        self.visit(tree)
        
        
    #for AST?
    def multiLineComment(self, t):
        # not interested
        pass

    def singleLineComment(self, t):
        # not interested
        pass
                      
    def parameterDefinition(self, t):
        # not interested
        #change of scope
        pass

    def namelessDataBase(self, t):
        self.b.append(t)

    def monoOpExpressionCall(self, t):
        self.b.append(t)
        
    def dataDefine(self, t):
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                 
    def namelessBody(self, t):
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                
    def contextDefine(self, t):
        #change of scope
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                
    def contextCall(self, t):
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                        
    def conditionalCall(self, t):
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                
    def conditionalContextCall(self, t):
        for e in t.body:
            self.visit(e) 
        self.b.append(t)
                
    def namelessFunc(self, t):
        #print('twaddle')
        for e in t.body:
            self.visit(e) 
        self.b.append(t)

    def result(self):
        return self.b
