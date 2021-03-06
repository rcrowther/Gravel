from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder, SubBuilder
from tpl_either import Option



class Compiler(Syntaxer):

    def __init__(self, tokenIt, builderAPI):
        self.b = Builder()        
        self.builderStack = []
        
        # EnvStd is builtin symbol definitions
        self.envStd = builderAPI
        
        # These need explaining.
        # This is a link auto-wired into the API so the API can refer 
        # back to this class.
        # Really the API is a specialism of this class, and should 
        # inherit it. But then it is not an API, and inherits plenty
        # of methods and attributes that may get awkware.
        # So the API is composed, and cleanly encapsulated.
        # Main issuw with that is that the API benefits from access to 
        # this class. It will recieve further errors from construction
        # classes, and sometimes needs to signal the overall handlers 
        # here to work like make a new environment.
        # If the API was interited, it could do that, but composed, no.
        # For a while the solution was to sens data back with 
        # structures like Options and Eithers. But this got messy, as 
        # there is a lot of it. And the API knows what it wants to do,
        # no need for ifs...
        # So the API is now given a hard link back here to do it's
        # tinkering. If there is one problen, you can see a link loop 
        # now exists, the API can call into the Compiler affecting the 
        # API... However, the concerns and information are clearly 
        # outlined, sh this should never occur.
        self.envStd.compiler = self
        self.funcNameToArgsType = builderAPI.funcNameToArgsType

        # EnvClosure holds symbiol definitions local to patches of 
        # code, such as codeblocks for whiles etc.
        # As such, it can be stacked.
        self.envClosure = []
        
        # EUsed for the occasional sectoion vars.
        #? Policy  undecided
        self.envGlobal = {}
        
        # Closure data is not part of the env group at all.
        # Rubble does not have bracketting, and does not enable
        # bracketting, prefering to mark start and end locations with 
        # sitandalone functions. So we need to keep track of those.
        # Of course, environments will be enabled within these blocks.
        self.closureData = []
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
        
    def _stringTypeNamesMk(self, typeList):
        '''
        print a list of typenames 
        '''
        # Used on argument signatures to tidy error reports
        #return "[" + ", ".join([tpe.__name__ for tpe in typeList]) + "]"
        return "[" + ", ".join([argTest.typeString for argTest in typeList]) + "]"
        
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
                 self._stringTypeNamesMk(argsTypes),
                 args
                 )
            self.errorWithPos(pos, msg)
        if (len(args) < len(argsTypes)):
            msg = "Not enough args. symbol:'{}', expected:{}, args:{}".format(
                 name,
                 self._stringTypeNamesMk(argsTypes),
                 args,
                 )
            self.errorWithPos(pos, msg)
        
        i = 0
        for argTest, arg in zip(argsTypes, args):
            # is it argtype that could be fichanged, to reflect differences?
            # 
            #if (not(isinstance(arg, argType))):
            print(str(argTest))
            if (not(argTest(arg))):
                # msg = "Arg type not match signature. symbol:'{}', expected:{}, args:{}".format(
                    # name,
                    # self._stringTypeNamesMk(argsTypes),
                    # args
                 # )
                msg = "Arg type not match signature. arg:{}, expected:{}, got:{}".format(
                    i,
                    argTest.typeString,
                    arg
                 )
                self.errorWithPos(pos, msg)
            i += 1
            
    def eitherError(self, posArgs, either):
        if (either.status == Option.ERROR):
            self.errorWithPos(posArgs, either.msg)
        if (either.status == Option.WARNING):
            self.warningWithPos(posArgs, either.msg)
        if (either.status == Option.INFO):
            self.info(either.msg)



    ## ClosureData
    def closureDataPush(self, data):
        return self.closureData.append(data)
                        
    def closureDataPop(self):
        if (not(self.closureData)):
            self.error('Close a codeblock close when no block open.')
        return self.closureData.pop()


            
    ## environments
    #! it would maybe be faster to make this mutable
    # Then put an env on tracking new vars
    # Then delete the new vars at the end.
    # This would be a lot faster, actually, rather than the copy()
    def envAddClosure(self):
        newEnv = {}
        if (self.envClosure):
            # Copy all lower symbols into top layer
            # Probably slow to copy, but easy to
            # find and search for symbols. 
            # Coppy because don't want adaptions seeping back to wider
            # blocks.
            newEnv = dict(self.envClosure[-1])
        self.envClosure.append(newEnv)

    def envDelClosure(self):
        assert(self.envClosure), "Celete non-existant envCloseure."
        del(self.envClosure[-1])
                
    def symbolSetClosure(self, protoSymbol, value):
        #? Do a value test, or not 
        assert(self.envClosure and (len(self.envClosure) > 0)), "Symbol offered, but no envClosure. protoSymbol:{}".format(
            protoSymbol
        )
        self.envClosure[-1][protoSymbol] = value
        
    def symbolSetGlobal(self, protoSymbol, value):
        # Used in RO on builder
        #? Do a value test, or not 
        self.envGlobal[protoSymbol] = value
                

    def findIdentifier(self, pos, sym):
        # envStd overrides all
        if (sym in self.envStd):
            return self.envStd[sym]
        # All envClosures have wider closures loaded too
        if (self.envClosure and (sym in self.envClosure[-1])):
            return self.envClosure[-1][sym]            
        # last shot, globals
        if (sym in self.envGlobal):        
            return self.envGlobal[sym]
        #print(str(self.envStd))
        msg = "Symbol requested but not found in scope. symbol '{}'".format(
             sym
             )
        self.errorWithPos(pos, msg)



    ## Syntacxer callbacks
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
            
        # Test args for type and/or count
        if name in self.funcNameToArgsType:
            self.argsCheck(posArgs, name, args, self.funcNameToArgsType[name])
                   
        # Wow--now can do a simple call 
        msgOption = func(self.b, args)
        
        # If an message came from the API, its an integrity
        # error from the args (not a format issue)
        # Outright throws are throws. Throws to be caught are in custom 
        # exceptions of this code.
        self.eitherError(posArgs, msgOption)

                
    def result(self):
        assert (len(self.builderStack) == 0), "This error should not occur!!! On Compiler result, builderStack is not empty."
        return self.b
        
if __name__ == "__main__":
    main()
