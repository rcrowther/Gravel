from Phases import Phase

from trees.Visitors import Visitor
from trees.Trees import *



#! put doc visitors elsewhere, for other usage e.g. interactive?
#! Probaly the major item---construct Kind documentation properly 
#!     e.g. Builder[B, Iterable[B]]
#! devise some callback for scoped data, not just members
#! structure indenting for scopeing
#! Get scope data here i.i. do more than the HTML wrap
#! should abstract this so it can work on a tree. Only wrap in a phase
#! afterwards. Then it can work on generated subtrees.
#? should put brackets on methods, empty or not
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
    
    
from collections import namedtuple    
Entity = namedtuple('Entity', 'selector name params kind comment')
KindData = namedtuple('KindData', 'name params')




#! not use Visotor, because we only need defs?
#! break parameters into a namedTuple also?
class DocVisitor(Visitor):
    '''
    Gather documentation information into a consistent format.
    You dont need to use this, but it povides a start for a consistent 
    entry point.
    Designed for a builder (no returns)
    '''

    def _kindToKindData(self, t):
        #! this needs to be a recursive tree
        return KindData(t.parsedKind, None)

    def renderKindName(self, name):
        pass

    def renderKindOpen(self):
        pass
        
    def renderKindClose(self):
        pass
        
    def renderEntitySelector(self, selector):
        pass

    def renderEntityName(self, name):
        pass

    def renderParameterName(self, name):
        pass

    def renderParametersOpen(self):
        pass
        
    def renderParametersClose(self):
        pass

    def renderParameterDefinitions(self, params):
        if (params):
            self.renderParametersOpen()
            first = True
            for p in params:
                if first:
                    first = False
                else:
                    self.b.append(', ')
                #print('p: ' + str(p))
                # Ultimately, no, the Kind itself.
                self.renderParameterName(p.parsedData)
                self.renderKindOpen()
                kindData = self._kindToKindData(p)
                #print('kindData: ' + str(kindData))
                self.renderKind(kindData)
                self.renderKindClose()
            self.renderParametersClose()

    def renderKind(self, kind):
        self.renderKindName(kind.name)
        params = kind.params
        if (params):
            first = True
            for p in params:
                if first:
                    first = False
                else:
                    self.b.append(', ')
                if isinstance(p, KindData):
                    self.renderKind(p)
                    continue
                self.b.append(p)

    def renderComment(self, text):
        pass  
                                
    def renderMember(self, data):
        self.renderEntitySelector(data.selector)
        self.renderEntityName(data.name)
        self.renderParameterDefinitions(data.params)
        self.renderKind(data.kind)
        if(data.comment):
            self.renderComment(data.comment)
                                        
    def dataDefine(self, t):
        #? More than the selector, modifiers also
        selector = 'val'
        name = t.parsedData
        kindData = self._kindToKindData(t)
        prev = t.prev
        comment = ''
        if(isinstance(prev, MultiLineComment)):
            comment = prev.parsedData
        e = Entity(selector=selector, name=name, params=None, kind=kindData, comment=comment)
        self.renderMember(e)
            
    def contextDefine(self, t):
        #? More than the selector, modifiers also
        selector = 'fnc'
        name = t.parsedData
        kindData = self._kindToKindData(t)
        prev = t.prev
        comment = None
        if(isinstance(prev, MultiLineComment)):
            comment = prev.parsedData
        #print('params' + str(t.params))
        e = Entity(selector=selector, name=name, params=t.params, kind=kindData, comment=comment)
        self.renderMember(e)



class HTMLVisitor(DocVisitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def renderKindName(self, name):
        self.b.append('<a href="#">')
        self.b.append(name)
        self.b.append('</a>')

    def renderKindOpen(self):
        self.b.append(': ')

    #def renderKindClose(self):
    #    pass
        
    def renderEntitySelector(self, selector):
        self.b.append('<span class="selector">')
        self.b.append(selector)
        self.b.append('</span>')

    def renderEntityName(self, name):
        #self.b.append(' ')
        self.b.append('<span class="name">')
        self.b.append(name)
        self.b.append('</span>')
        
    def renderParameterName(self, name):
        self.b.append(name)

    def renderParametersOpen(self):
        self.b.append('<span class="params">(')
        
    def renderParametersClose(self):
        self.b.append(')</span>')
        
    def renderComment(self, text):
        self.b.append("<p class='comment'>")
        self.b.append(text.strip())
        self.b.append("</p>")      
                  
    def dataDefine(self, t):
        self.b.append('<li class="def-data">')
        super().dataDefine(t)
        self.b.append('</li>')
            
    def contextDefine(self, t):
        self.b.append('<li class="def-context">')
        super().contextDefine(t)
        self.b.append('</li>')



class PlaintextVisitor(DocVisitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def renderKindName(self, name):
        self.b.append(name)

    def renderKindOpen(self):
        self.b.append(': ')

    #def renderKindClose(self):
    #    pass
        
    def renderEntitySelector(self, selector):
        self.b.append('\n\n')
        self.b.append('    ')
        self.b.append(selector)

    def renderEntityName(self, name):
        self.b.append(' ')
        self.b.append(name)
        
    def renderParameterName(self, name):
        self.b.append(name)

    def renderParametersOpen(self):
        self.b.append('(')
        
    def renderParametersClose(self):
        self.b.append(')')
        
    def renderComment(self, text):
        self.b.append('\n')
        self.b.append('        ')
        self.b.append(text.strip())




from library.io.AnsiColor import *

class TerminalVisitor(DocVisitor):

    def __init__(self, tree):
      self.b = []
      super().__init__(tree)

    def renderKindName(self, name):
        self.b.append(UNDERLINED)
        self.b.append(name)
        self.b.append(RESET)

    def renderKindOpen(self):
        self.b.append(': ')

    #def renderKindClose(self):
    #    pass
        
    def renderEntitySelector(self, selector):
        self.b.append('\n\n')
        self.b.append('    ')
        self.b.append(selector)

    def renderEntityName(self, name):
        self.b.append(' ')
        self.b.append(BOLD)
        self.b.append(name)
        self.b.append(RESET)
        
    def renderParameterName(self, name):
        self.b.append(name)

    def renderParametersOpen(self):
        self.b.append('(')
        
    def renderParametersClose(self):
        self.b.append(')')
        
    def renderComment(self, text):
        self.b.append('\n')
        self.b.append('        ')
        self.b.append(text.strip())




          
#? could do this using a setting in the pipeline,
#? but this may be useful too
class GravelDoc(Phase):
    #? after Syntax (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Write documentation",
            "Write defines and prefixed multiline comments to files",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        #! 
        tree = compilationUnit.tree
        v = HTMLVisitor(tree)
        o = HTMLWrap(compilationUnit.source.srcPath, 'Graveldoc Test', 'Test description.', v.b)
        print(''.join(o))
        #! would write by package, not file
        with open('test/graveldoc.htm', 'w') as f:
            f.write(''.join(o))



class GDocToTerminal(Phase):
    #? after Syntax (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Print documentation to the terminal",
            "Print documentation of the AST tree to the terminal",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        #! settings for everything
        #! 
        tree = compilationUnit.tree
        v = TerminalVisitor(tree)
        print(''.join(v.b))
