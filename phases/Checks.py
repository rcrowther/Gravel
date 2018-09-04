from Phases import Phase


'''
Checks.
Test consistency of structures.
e.g. stated kinds are consistent.
'''


from trees.Visitors import VisitorNodeDispatch
from Marks import Mark
from Kinds import Any
from reporters.Message import Message


class MarkTableValidate(Phase):
    #? after MakeMarkTable so there is a tree (and typecheck)
    def __init__(self):
        Phase.__init__(self,
            "Check the marktable for consistency.",
            "Currently checks there is a defintion, and only one definition..",
            True
            )

    def run(self, compilationUnit, reporter, settings):
        marks = compilationUnit.markTable.toList()
        for m in marks:
            l = len(m.definitionTrees)
            if (l != 1):
                if (l < 1):
                   instanceList = [m.position.toDisplayString() for m in m.instanceTrees[1:5]]
                   msg = 'Name has no definition. name:"{}" first positions:{}'.format(
                      m.name,
                      ', '.join(instanceList)
                      )                     
                else:
                   definitionList = [m.position.toDisplayString() for m in m.definitionTrees]
                   msg = 'Name definition repeated. name:"{}" declaration positions:{}'.format(
                      m.name,
                      ', '.join(definitionList)
                      )

                reporter.error(
                    Message.withSrc(msg, compilationUnit.source)
                    )


#class NameTypeVerifyVisitor(VisitorNodeDispatch):

    #def node(self, t):
        ## check something is there
        #if (isinstance(t, NameMixin)):
            #if (
                ##! establishes a new scope
                ##isinstance(t, ParameterDefinition)
                #isinstance(t, DataDefine)
                #or isinstance(t, ContextDefine)
            #):
                ##r = self.table.define(t.parsedData, t)
                #??? need to know where we parse the kind
                #r = self.table.create(Mark(t.parsedData, t.parsedKind))
                #if (not r):
                   ## oh dear, double definition
                   #name = t.parsedData
                   #nameNode = self.table(name)
                   #msg = 'Name definition repeated. name:"{}" first declaration position:{}'.format(
                      #name,
                      #nameNode.definitionTree.position.toDisplayString()
                      #)
                   #self.reporter.error(msg, r.position)
                #return
            #print('named item: ' + str(t.parsedData))
            ##self.table.note(t.parsedData, t)
            ##r = self.table.create(Mark(t.parsedData, t.parsedKind))



#class NameTypeVerify(Phase):
    ##? after Syntax so there is a tree (and typecheck)
    #def __init__(self):
        #Phase.__init__(self,
            #"Convert parsed names and types to internal representation.",
            #"This will also build, on the compilation unit, a name tree.",
            #True
            #)

    #def run(self, compilationUnit, reporter, settings):
        ##! settings for everything
        #NameTypeVerifyVisitor(compilationUnit.tree, reporter)

