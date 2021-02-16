from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder
from Message import messageWithPos


class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)


class Compiler(Syntaxer):

    def __init__(self, tokenIt, builderAPI):
        self.b = Builder()
        self.envStd = builderAPI
        self.envFunc = {}
        self.envGlobal = {}
        self.closureData = []
        super().__init__(tokenIt)
        
    def findIdentifier(self, pos, sym):
        if (sym in self.envStd):
            return self.envStd[sym]
        if (sym in self.envFunc):
            return self.envFunc[sym]
        if (sym in self.envGlobal):        
            return self.envGlobal[sym]
        msg = "[Error] Symbol requested but not found in scope. symbol '{}'".format(
             sym
             )
        msgp = messageWithPos(pos, msg)
        raise ValueError(msgp)

    def hasDataToPush(self):
        return sym in {
        }

             
    def commentCB(self, text):
        print('Compiler comment with "' + text)

    def exprCB(self, pos, name, args):
        print('Compiler expr {}({})'.format(name, args))
        func = self.findIdentifier(pos, name)
        
        # stacked data protection
        if ((name == "funcEnd" or name == "funcMainEnd") and len(self.closureData) > 0):
            msg = "[Error] End of func with unclosed instructions. unused instruction args:{}".format(
                self.closureData,
                )
            msgp = messageWithPos(pos, msg)
            raise SyntaxError(msgp)
                          
        #? Hefty, but how to dry? return from every func cuts stuff 
        # down a little, but is obscure                            
        #print(str(self.envStd.mustPushData(name)))
        #print(str(self.envStd.mustPopData(name)))
        if (self.envStd.mustPushData(name)):
                self.closureData.append(func(self.b, args))
        elif (self.envStd.mustPopData(name)):
            poppedData = self.closureData.pop()
            #print(str(poppedData))
            try:
                func(self.b, poppedData, args)
            except TypeError:
                msg = "[Error] Symbol not accept given args. symbol '{}', args:{}".format(
                     name,
                     args
                     )
                msgp = messageWithPos(pos, msg)
                raise TypeError(msgp)
        else:
            try:
                func(self.b, args)
            except TypeError:
                msg = "[Error] Symbol not accept args. symbol '{}', args:{}".format(
                     name,
                     args
                     )
                msgp = messageWithPos(pos, msg)
                raise TypeError(msgp)
        
    def result(self):
        return self.b
        
if __name__ == "__main__":
    main()
