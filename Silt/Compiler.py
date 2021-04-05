from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder, SubBuilder
from ci_scope import Scope
from ci_symbol import SymbolBuiltinFunc
from tpl_types import NoType
from tpl_either import Option





class Compiler(Syntaxer):

    def __init__(self, tokenIt, builderAPI):
        '''
        builderAPI
        '''
        self.b = Builder()        
        self.instructionStack = []
        self.instructionsStoreTrigger = False
        
        
        # EnvStd is builtin symbol definitions from BuilderAPI
        #x
        self.envStd = builderAPI
        
        self.builderAPI = builderAPI
        builderFuncSymbols = [ SymbolBuiltinFunc(funcName, getattr(builderAPI, funcName), NoType) for funcName in builderAPI.funcNameToArgsType.keys()]
        self.scopeStd = Scope(builderFuncSymbols)
        
        # These need explaining.
        # This is a link auto-wired into the API so the API can refer 
        # back to this class.
        # Really the API is a specialism of this class, and should 
        # inherit it. But then it is not an API, and inherits plenty
        # of methods and attributes that may get awkward.
        # So the API is composed, and so cleanly encapsulated.
        # Main issue with that is that the API benefits from access to 
        # this class. It will recieve further errors from construction
        # classes, and sometimes needs to signal the overall handlers 
        # here to work e.g. make a new environment.
        # If the API was interited, it could do that, but composed, no.
        # For a while the solution was to send data back with 
        # structures like Options and Eithers. But this got messy, as 
        # there is a lot of it. And the API knows what it wants to do,
        # no need for ifs...
        # So the API is now given a hard link back here to do it's
        # tinkering. If there is one problen, you can see a link loop 
        # now exists, the API can call into the Compiler affecting the 
        # API... However, the concerns and information are clearly 
        # outlined, this should never occur.
        #x
        self.envStd.compiler = self

        self.builderAPI.compiler = self
        
        self.funcNameToArgsType = builderAPI.funcNameToArgsType

        # EnvClosure holds symbiol definitions local to patches of 
        # code, such as codeblocks for whiles etc.
        # As such, it can be stacked.
        #x
        self.envClosure = []
        self.scopeStack = []
        
        # Used for the occasional section vars.
        #? Policy  undecided
        #x
        #self.envGlobal = {}
        self.scopeGlobal = Scope.empty()
        
        # Closure data is not part of the env group at all.
        # Rubble does not have bracketing, and does not enable
        # bracketing, prefering to mark start and end locations with 
        # sitandalone functions. So we need to keep track of those.
        # Of course, environments will be enabled within these blocks.
        self.closureData = []
        super().__init__(tokenIt)

    def instructionsStore(self):
        '''
        Set a new builder as the current builder,
        For local manipilation of built code, such as repetitions
        or multiple inserts.
        '''
        self.instructionStack.append([])
        self.instructionsStoreTrigger = True
        
    def instructionsGet(self):
        '''
        Return the current builder as a result. 
        This will revert the current builder to the previous builder.
        '''
        #assert (len(self.instructionStack) > 0), "This error should not occur!!! On builderResult instructionStack is empty."
        return self.instructionStack.pop(-1)

    def instructionsPlay(self, instructions):
        '''
        Play stored instructions
        '''
        #! currently works on new env but current builder, which is wrong
        # what about embedded loops, huh?
        for ins in instructions:
            # Aye, unPythonic
            pos = ins[0]
            posArgs = ins[1]
            name = ins[2]
            args = ins[3]
            self.exprCB(pos, posArgs, name, args)
        
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
            if (not(argTest(arg))):
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

    def closureDataPeek(self):
        if (not(self.closureData)):
            self.error('Peek codeblock data when no block open.')
        return self.closureData[-1]
                                
    def closureDataPop(self):
        if (not(self.closureData)):
            self.error('Close a codeblock when no block open?')
        return self.closureData.pop()


            
    ## environments
    #! it would maybe be faster to make this mutable
    # Then put an env on tracking new vars
    # Then delete the new vars at the end.
    # This would be a lot faster, actually, rather than the copy()
    #x
    # def envAddClosure(self):
        # newEnv = {}
        # if (self.envClosure):
            # # Copy all lower symbols into top layer
            # # Probably slow to copy, but easy to
            # # find and search for symbols. 
            # # Coppy because don't want adaptions seeping back to wider
            # # blocks.
            # newEnv = dict(self.envClosure[-1])
        # self.envClosure.append(newEnv)

    def scopeStackPush(self):
        scope = Scope.empty()
        
        # link up symbols from the super-scope
        if (self.scopeStack):
            scope.addScope(self.scopeStack[-1])
        self.scopeStack.append(scope)
        
    #x
    # def envDelClosure(self):
        # assert(self.envClosure), "Celete non-existant envCloseure."
        # del(self.envClosure[-1])

    def scopeStackPop(self):
        assert(self.scopeStack), "Celete non-existant scope."
        del(self.scopeStack[-1])
        
    #x
    # def symbolSet(self, protoSymbol, value):
        # '''
        # Register a symbol to the current environment.
        # ''' 
        # assert(self.envClosure), "Symbol offered, but no envClosure. protoSymbol:{}".format(
            # protoSymbol
        # )
        # #print('setting: ' + protoSymbol)
        # self.envClosure[-1][protoSymbol] = value

    def symSet(self, sym):
        '''
        Register a symbol to the current environment.
        ''' 
        assert(self.scopeStack), "Symbol offered, but no scopeStack. protoSymbol:{}".format(
            protoSymbol
        )
        #print('setting: ' + protoSymbol)
        self.scopeStack[-1].add(sym)
                
    #x
    # def symbolUpdateType(self, name, tpe):
        # '''
        # A brute mutation of a already registered type
        # Used for genVars
        # '''
        # self.envClosure[-1][name].tpe = tpe

    # May yet be used for clutch iteration on genVars?
    def symUpdateType(self, name, tpe):
        '''
        A brute mutation of a already registered type
        Used for genVars
        '''
        self.scopeStack[-1](name).tpe = tpe

    #x
    # def symbolUpdateLoc(self, name, loc):
        # '''
        # Unregister a symbol from the current environment.
        # Despite environment cleanup, this is required. It is needed for
        # the circumstance where a var is overwritten, so presumably
        # has no further purpose.
        # '''
        # self.envClosure[-1][name].loc = loc

    #x done by pokes in UpdateLocationBuilder. Anything else necessary?
    def symUpdateLoc(self, name, loc):
        '''
        Unregister a symbol from the current environment.
        Despite environment cleanup, this is required. It is needed for
        the circumstance where a var is overwritten, so presumably
        has no further purpose.
        '''
        self.scopeStack[-1](name).loc = loc
        
    #x is this now used? We kill and create scopes even for small items
    # def symbolDelete(self, protoSymbol, value):
        # '''
        # A brute mutation of a already registered type
        # '''
        # #? Used for genVars
        # assert(self.envClosure), "Symbol offered, but no envClosure. protoSymbol:{}".format(
            # protoSymbol
        # )
        # #print('setting: ' + protoSymbol)
        # del(self.envClosure[-1][protoSymbol])
    #x
    # def envPrint(self):
        # #! oh so yes! Sadly, the same bad defaults noted in exprCB()
        # #print(str(self.envClosure[-1]))
        # print('env:')
        # for k,v in self.envClosure[-1].items():
            # print(k + ': ' + str(v))

    def scopeGlobalPrint(self):
        print('env Global:')
        for e in self.scopeGlobal.toList():
            print(f"    {e.name}: {e.tpe}")
                        
    def scopePrint(self):
        #! oh so yes! Sadly, the same bad defaults noted in exprCB()
        #print(str(self.scopeStack[-1]))
        print('env Usr:')
        #print(str(self.scopeStack[-1]))
        #? Be nice to print args aifs too?
        for e in self.scopeStack[-1].toListAll():
            print(f"    {e.name}:{e.tpe}")
        self.scopeGlobalPrint()
                    
    def scopeStdPrint(self):
        #! oh so yes! Sadly, the same bad defaults noted in exprCB()
        #print(str(self.scopeStack[-1]))
        print('env Builtin:')
        
        #? Be nice to print args sigs too?
        for e in self.scopeStd.toList():
            print('    ' + e.name)

    #x
    # def symbolSetGlobal(self, protoSymbol, value):
        # # Used in RO on builder
        # #? Do a value test, or not 
        # print('Global setting: ' + protoSymbol)
        # self.envGlobal[protoSymbol] = value

    def symbolSetGlobal(self, symVar):
        # Used in RO on builder
        #? Do a value test, or not 
        #print('Global setting: ' + symVar.name)
        self.scopeGlobal.add(symVar)                
    #x
    # def findIdentifier(self, pos, sym):
        # # envStd overrides all
        # if (sym in self.envStd):
            # return self.envStd[sym]
        # # All envClosures have wider closures loaded too
        # if (self.envClosure and (sym in self.envClosure[-1])):
            # return self.envClosure[-1][sym]            
        # # last shot, globals
        # #if (sym in self.envGlobal):        
        # #    return self.envGlobal[sym]
        # # last shot, globals
        # #print(sym)
        # symMaybe = self.scopeGlobal(sym)
        # if (symMaybe):
            # return symMaybe 
        # self.envPrint()
        # msg = "Symbol requested but not found in scope. symbol '{}'".format(
             # sym
             # )
        # self.errorWithPos(pos, msg)

    def symbolBuiltinFind(self, pos, symName):
        symMaybe = self.scopeStd(symName)
        if (symMaybe):
            return symMaybe
        self.scopePrint()
        msg = "Symbol requested but not found in scope. symName '{}'".format(
             symName
             )
        self.errorWithPos(pos, msg)
                    
    def symbolUsrFind(self, pos, symName):
        #? Used in two places, and I'm thinking it souldn't be?
        # - To find builtin funcnames in the dispatcher below
        # - in the syntaxer, to type arguments
        # scopeStd overrides all
        #symMaybe = self.scopeStd(symName)
        #if (symMaybe):
        #    return symMaybe
            
        # All scopeStacks have wider scopes loaded too
        if (self.scopeStack):
            symMaybe = self.scopeStack[-1](symName)
            if (symMaybe):
                return symMaybe 
                      
        # last shot, globals
        symMaybe = self.scopeGlobal(symName)
        if (symMaybe):
            return symMaybe 
        #print('findIdentifier')
        self.scopePrint()
        msg = "Symbol requested but not found in scope. symName '{}'".format(
             symName
             )
        self.errorWithPos(pos, msg)


    ## Syntaxer callbacks
    def commentCB(self, text):
        print('Compiler comment with "' + text)

    def exprCB(self, pos, posArgs, name, args):
        #! such a useful print---enhance and be part of a debug?
        # printing a list always REPRs, think this is due a change in 
        # 3.7 I prefer the string marks to a gross repr. So the 
        # list comprehension. 
        print('Compiler expr {}({!s})'.format(
            name, 
            [str(a) for a in args]
        ))
        if (self.instructionsStoreTrigger):
            #! need something more general than this hardcode
            # I do want to control this, because it will lead to incomprehensible arrors,
            # so catch whenever, hardcoded? e.g.
            # if (name in storeCloseFuncs):
            if (
                name == 'forEachUnrolledEnd'
                or name == 'whenEnd'
            ):
                self.instructionsStoreTrigger = False
                
                # play the end instruction
                self.exprCB(pos, posArgs, name, args)
            else:
                self.instructionStack[-1].append((pos, posArgs, name, args,))
        else:
            #x
            #func = self.findIdentifier(pos, name)
            #! No, this dispatcher only needs to search in stdSymbols 
            # and funcDefs, I think?
            #self.scopeStdPrint()
            func = self.symbolBuiltinFind(pos, name)
            
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
            msgOption = func.data(self.b, args)
            
            # If an message came from the API, its an integrity
            # error from the args (not a format issue)
            # Outright throws are throws. Throws to be caught are in custom 
            # exceptions of this code.
            self.eitherError(posArgs, msgOption)

                
    def result(self):
        assert (len(self.instructionStack) == 0), "This error should not occur!!! On Compiler result, instructionStack is not empty. len:{}".format(len(self.instructionStack))
        return self.b
        
if __name__ == "__main__":
    main()
