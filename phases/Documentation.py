from Phases import Phase

from trees.Visitors import Visitor
from trees.Trees import *


def HTMLWrap(path, title, description, body):
    b = []
    b.append('<html>')
    b.append('<head>')
    b.append('<title>')
    b.append(title)
    b.append('</title>')
    b.append('<link href="lib/graveldoc.css" media="screen" type="text/css" rel="stylesheet">')
    b.append('</head>')
    b.append('<body>')
    b.append('<section class="contents">')
    b.append('<header>')
    b.append('<span class="path"><a href="#">')
    b.append(path)
    b.append('</a></span>')
    b.append('<h1>')
    b.append(title)
    b.append('</h1>')
    b.append('<div class="description">')
    b.append(description)
    b.append('</div>')
    b.append('</header>')
    b.append('<ul class="children">')
    b.extend(body)
    b.append('</ul>')
    b.append('</section>')
    b.append('</body>')
    b.append('</html>')
    return b
    
class HTMLVisitor(Visitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def namelessData(self, t):
        # only on the module?
        pass

    def renderMarkSelector(self, text):
        self.b.append('<span class="mark-selector">')
        self.b.append(text)
        self.b.append('</span>')

    def renderName(self, name):
        self.b.append('<span class="name">')
        self.b.append(name)
        self.b.append('</span>')


    def renderParameterDefinitions(self, t):
        for p in t.params:
            self.b.append(p.parsedData)
            self.b.append(': ')
            self.b.append('<a href="#">')
            self.b.append('???')
            self.b.append('</a>')
            self.b.append(' ')

    def renderKind(self):
        self.b.append(': ')
        self.b.append('<span class="kind">')
        self.b.append('</span>')
        
    def renderComment(self, text):
        self.b.append("<p class='comment'>")
        self.b.append(text.strip())
        self.b.append("</p>")      
                  
                  
    def dataDefine(self, t):
        name = t.parsedData
        self.b.append('<li class="definition">')
        self.renderMarkSelector('val')
        self.renderName(name)
        self.renderKind()
        #self.b.append('{')
        #self.b.append('}')
        prev = t.prev
        if(isinstance(prev, MultiLineComment)):
            self.renderComment(prev.parsedData)
        self.b.append('</li>')
            
    def contextDefine(self, t):
        name = t.parsedData
        self.b.append('<li class="">')
        self.renderMarkSelector('fnc')
        self.renderName(name)
        self.b.append('<span class="params">(')
        self.renderParameterDefinitions(t)
        self.b.append(')</span>')
        self.renderKind()
        prev = t.prev
        if(isinstance(prev, MultiLineComment)):
            self.renderComment(prev.parsedData)
        self.b.append('</li>')

    
    
    
class PlaintextVisitor(Visitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def namelessData(self, t):
        # only on the module?
        pass

    def renderParameterDefinitions(self, t):
        for p in t.params:
            self.b.append(p.parsedData)
            self.b.append(': ')
            self.b.append('???')
            self.b.append(' ')
            
    def dataDefine(self, t):
        name = t.parsedData
        self.b.append('\n\nval ')
        self.b.append(name)
        self.b.append('{')
        self.b.append('}: ')
        prev = t.prev
        if(isinstance(prev, MultiLineComment)):
            self.b.append('\n    ')
            self.b.append(prev.parsedData.strip())
            
    def contextDefine(self, t):
        name = t.parsedData
        self.b.append('\n\nfnc ')
        self.b.append(name)
        self.b.append('(')
        self.renderParameterDefinitions(t)
        self.b.append('): ')
        prev = t.prev
        if(isinstance(prev, MultiLineComment)):
            self.b.append('\n    ')
            self.b.append(prev.parsedData.strip())
    
          
#? could do this using a setting in the pipeline,
#? but this may be useful too
class GravelDoc(Phase):
    #? after Syntax (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Assemble Graveldoc",
            "Take the AST, remove data other than defines and prefix multiline comments",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        #! 
        tree = compilationUnit.tree
        #v = PlaintextVisitor(tree)
        v = HTMLVisitor(tree)
        o = HTMLWrap(compilationUnit.source.srcPath, 'Graveldoc Test', 'Test description.', v.b)
        print(''.join(o))
        #! would write by packae, not file
        with open('test/graveldoc.htm', 'w') as f:
            f.write(''.join(o))
