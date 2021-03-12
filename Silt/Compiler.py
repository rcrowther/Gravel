from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder, SubBuilder
from tpl_either import Option

# from exceptions import (
    # FuncError,
    # FuncWarning,
    # FuncInfo,
# )

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
        self.builderStack = []
        
        self.envStd = builderAPI
        self.envStd.compiler = self
        self.funcNameToArgsType = builderAPI.funcNameToArgsType
        #self.envStd.error  = self.error
        #self.envStd.warning  = self.warning
        #self.envStd.info  = self.info

        self.envFunc = {}
        self.envGlobal = {}
        self.closureData = []
        
        # distance in bytes of the stack pointer from the stack base 
        # pointer
        # Measured in bytes.
        # Is measured positively, though the intel architectures move 
        # negatively
        # This is massively useful to know, for compiling, debugging,
        # even for writing hard offsets as opposed to calculating them.
        # There is one but... the figure can not be relied on, as coders
        # may tamper with the stack outside of this code. And we want to
        # allow that.
        #?x
        self.stackSize = 0
        super().__init__(tokenIt)

    def builderNew(self):
        '''
        Set a new builder as the current builder,
        For local manipilation of built code, such as repetitions
        or multiple inserts.
        '''
        self.builderStack.append(self.b)
        self.b = SubBuilder()
        
    def builderOld(self):
        '''
        Return the current builder as a result. 
        This will revert the current builder to the previous builder.
        '''
        #finishedBuilder = self.b 
        assert (len(self.builderStack) > 0), "This error should not occur!!! On builderResult builderStack is empty."
        self.b = self.builderStack.pop(-1)
        #return finishedBuilder
        
    def stringTypeNamesMk(self, typeList):
        '''
        print a list of typenames 
        '''
        # Used on argument signatures to tidy error reports
        return "[" + ", ".join([tpe.__name__ for tpe in typeList]) + "]"
        
    def argsCheck(self, pos, name, args, argsTypes):
        '''
        Check args for length and type.
        
        argsTypes can be any Rubble type, also,
        - OrotoSymbol
        
        argsTypes
            a list of types
        '''
        if (len(args) > len(argsTypes)):
            msg = "Too many args. symbol:'{}', expected:{}, args:{}".format(
                 name,                 
                 self.stringTypeNamesMk(argsTypes),
                 args
                 )
            self.errorWithPos(pos, msg)
        if (len(args) < len(argsTypes)):
            msg = "Not enough args. symbol:'{}', expected:{}, args:{}".format(
                 name,
                 self.stringTypeNamesMk(argsTypes),
                 args,
                 )
            self.errorWithPos(pos, msg)
            
        for argType, arg in zip(argsTypes, args):
            if (not(isinstance(arg, argType))):
                msg = "Arg type not match signature. symbol:'{}', expected:{}, args:{}".format(
                    name,
                    self.stringTypeNamesMk(argsTypes),
                    args
                 )
                self.errorWithPos(pos, msg)

    def eitherError(self, posArgs, either):
        if (either.status == Option.ERROR):
            self.errorWithPos(posArgs, either.msg)
        if (either.status == Option.WARNING):
            self.warningWithPos(posArgs, either.msg)
        if (either.status == Option.INFO):
            self.info(either.msg)
            
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

    def exprCB(self, pos, posArgs, name, args):
        #! such a useful print---enhance and be part of a debug?
        print('Compiler expr {}({})'.format(name, args))
        func = self.findIdentifier(pos, name)
        
        # stacked data protection
        #? assert?
        if ((name == "funcEnd" or name == "funcMainEnd") and len(self.closureData) > 0):
            msg = "End of func with unclosed instructions. unused instruction args:{}".format(
                self.closureData,
                )
            self.errorWithPos(pos, msg)
            
        # localEnv reset
        if (name == "funcEnd"):
            self.envFunc = {}
            
        # Test args for type and/or count
        if name in self.funcNameToArgsType:
            self.argsCheck(posArgs, name, args, self.funcNameToArgsType[name])
                   
        #try:
        #? Hefty, but how to dry? return from every func would cut stuff 
        # down a little, but is obscure
        if (self.envStd.mustPushData(name)):
            self.closureData.append(func(self.b, args))                
        elif (self.envStd.mustPopData(name)):
            poppedData = self.closureData.pop()
            func(self.b, poppedData, args)
        elif (self.envStd.mustSetData(name)):
            ret = func(self.b, args)        

            label = ret[0]
            varObj = ret[1]
            # tmp, checking...
            if (not(isinstance(varObj, Option))):
                print('.........not Eiyther')
                print(str(varObj))  
                self.error('internal')
                
            # Print any message
            self.eitherError(posArgs, varObj)
                
            # Salvage the object.
            # If it was no good, code above would Except on message
            # Why is this working when it has a new-style Var?
            # probablly duck-typing
            varObj = varObj.obj

            #? has not been used?
            # Used RO on builder?
            # Is needed, with main as the outer environment?          
            if(not(self.envStd.isGlobalData)):
                print('isGlobalData')
                self.envFunc[label] = varObj
            else:
                self.envGlobal[label] = varObj
        #? Umm, this has gone unused because the Syntaxer has been 
        # typing completed symbols
        elif (self.envStd.mustGetData(name)):
            print('.........mustGetData')
            print(str(name))
            k = args.pop(0)
            func(self.b, k, args)
        else:
            # Wow--now can do a simple call 
            msgOption = func(self.b, args)
            
            # If an message came from the API, its a kind of ValueError
            # in the args
            self.eitherError(posArgs, msgOption)

        # Execution of a func can produce many errors and warnings
        # These arrors are not basic lexer or syntax, they are of
        # code integrity. 
        # The code throws rather than passing the reporter funcs
        # in, to keep function code uncluttered.
        # The warning and info throws are not raised.
        # except FuncError as e:
            # self.errorWithPos(pos, e.args[0])            
            # # errors currently halt the compiler
            # raise e
        # except FuncWarning:
                # msg = "Too many args. symbol:'{}', expected:{}, args:{}".format(
                 # name,                 
                 # self.stringTypeNamesMk(argsTypes),
                 # args
                 # )
            # self.warningWithPos(pos, msg)
        # except FuncInfo:
                        # msg = "Too many args. symbol:'{}', expected:{}, args:{}".format(
                 # name,                 
                 # self.stringTypeNamesMk(argsTypes),
                 # args
                 # )
            # self.infoWithPos(pos, msg)
        #! Since args are enow checked, these errors are now code errors
        #! allow to rise?
        # except TypeError:
            # msg = "[Error] Symbol too many args. symbol:'{}', args:{}".format(
                 # name,
                 # args
                 # )
            # self.errorWithPos(pos, msg)
        # except IndexError:
            # msg = "[Error] Symbol not enough args. symbol:'{}', args:{}".format(
                 # name,
                 # args
                 # )
            # self.errorWithPos(pos, msg)
                
    def result(self):
        assert (len(self.builderStack) == 0), "This error should not occur!!! On Compiler result, builderStack is not empty."
        return self.b
        
if __name__ == "__main__":
    main()
