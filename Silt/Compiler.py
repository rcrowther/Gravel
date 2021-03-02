from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder


#x
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
        #print(str(self.envStd))
        msg = "Symbol requested but not found in scope. symbol '{}'".format(
             sym
             )
        self.errorWithPos(pos, msg)
             
    def commentCB(self, text):
        print('Compiler comment with "' + text)

    def exprCB(self, pos, name, args):
        #! such a useful print---enhance and be part of a debug?
        print('Compiler expr {}({})'.format(name, args))
        func = self.findIdentifier(pos, name)
        
        # stacked data protection
        #? assert?
        if ((name == "funcEnd" or name == "funcMainEnd") and len(self.closureData) > 0):
            msg = "[Error] End of func with unclosed instructions. unused instruction args:{}".format(
                self.closureData,
                )
            self.errorWithPos(pos, msg)
            
        # localEnv reset
        if (name == "funcEnd"):
            self.envFunc = {}
            
        #! if tested args for type and/or number, likely here.
        
        #? Hefty, but how to dry? return from every func would cut stuff 
        # down a little, but is obscure
        try:
            if (self.envStd.mustPushData(name)):
                self.closureData.append(func(self.b, args))                
            elif (self.envStd.mustPopData(name)):
                poppedData = self.closureData.pop()
                func(self.b, poppedData, args)
            elif (self.envStd.mustSetData(name)):
                ret = func(self.b, args)                  
                if(not(self.envStd.isGlobalData)):
                    self.envFunc[ret[0]] = ret[1]
                else:
                    self.envGlobal[ret[0]] = ret[1]  
            elif (self.envStd.mustGetData(name)):
                #print(str(poppedData))
                k = args.pop(0)
                func(self.b, k, args)
            else:
                # Wow--now can do a simple call
                func(self.b, args)

        except TypeError:
            msg = "[Error] Symbol too many args. symbol:'{}', args:{}".format(
                 name,
                 args
                 )
            self.errorWithPos(pos, msg)
        except IndexError:
            msg = "[Error] Symbol not enough args. symbol:'{}', args:{}".format(
                 name,
                 args
                 )
            self.errorWithPos(pos, msg)
                
    def result(self):
        return self.b
        
if __name__ == "__main__":
    main()
