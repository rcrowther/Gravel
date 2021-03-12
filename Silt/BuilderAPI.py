import architecture
#x
#from tpl_LocationRoot import LocationRootRODataX64, LocationRootRegisterX64, LocationRootStackX64
#x
import tpl_locationRoot as Loc
from tpl_Printers import PrintX64
import tpl_vars as Var
import tpl_types as Type
from asm_db import TypesToASMAbv, TypesToASMName

#? dont like this imports. They're for arg types though.
from Syntaxer import ProtoSymbol, Path
from tpl_either import MessageOption, MessageOptionNone

# Humm. Build addresses here, not in locs?
from tpl_address_builder import AddressBuilder



class BuilderAPI():
    '''
    A base for building code.
    Mostly this is a builder for machine code instructions. This is
    the base. Subclasses will target an architecture.
    Mostly, it is functions that take a builder followed by a generic
    'args' parameter.
    Some builder funcs return data. Messages to  compilers/interpreters 
    to adapt environments go through the 'compiler' attribute,
    Erros are passed back on return to generic code in the 
    compiler/interpreter.
    '''
    # NB arg checking would not be done here. This assumes args are
    # correct signature, it is a builder
    # For messages, use the MessageOption mechanism and return. It puts
    # indicators in a better position at te start of args.
    #! Also, there is now no need for it to carry data. Its a message
    # not messageOption
    #! 
    arch = None
    
    # Anchor for a seperate API for printing 
    printers = None

    # tis bizzare, but....
    # This is a reference back down to the compiler. It is wired in
    # on initialisation of the compiler.
    compiler = None

    '''
    Type signature of API funcs
    '''
    funcNameToArgsType = {
        # basics
        'comment': [str],
        'sysExit': [int],
        'extern': [str],
        'raw': [str],
        
        ## Code structure 
        'frame': [],
        'frameEnd': [],
        'func': [ProtoSymbol],
        'funcEnd': [],
        'funcMain': [],
        'funcMainEnd': [],

        ## Register utilities
        'registersPush': [list],
        'registersVolatilePush': [],
        'registersPop': [],

        ## var action
        'set': [Var.Base, int],
        #!? Path should be a Type. Probably
        'setPath':  [Var.Base, Path, int],
        'forEachRoll' : [ProtoSymbol, Var.Base],
        'forEachRollEnd': [],
        'forEach': [ProtoSymbol, Var.Base],
        'forEachEnd': [],
        
        ## Allocs
        'ROStringDefine': [ProtoSymbol, str],
        'RODefine': [ProtoSymbol, int, Type.Type],
        'regDefine': [ProtoSymbol, str, int, Type.Type],
        'heapAllocBytes': [ProtoSymbol, int],
        'heapAlloc': [ProtoSymbol, Type.Type],
        'stackAllocBytes': [ProtoSymbol, int, int],
        'stackAlloc': [ProtoSymbol, int, Type.Type],

        
        ## printers
        'print' : [Var.Base],
        'println': [Var.Base],
        'printFlush': [],
    #'': [].
    }
    
    def isGlobalData(self, name):
        '''
        Test if a function defines global instructions.
        return 
            If True, places in global environment (else data is local) 
        '''
        raise NotImplementedError()

        
    def mustPushData(self, name):
        '''
        Test if a function pushes to the stack.
        return 
            If True, builder pushes data to the stack (a closure mark)
        '''
        raise NotImplementedError()

        
    def mustPopData(self, name):
        '''
        Test if a function pops from the stack.
        return 
            If True, builder pops data from the stack (a closure mark)
        '''
        raise NotImplementedError()


    def mustSetData(self, name):
        '''
        Test if a function sets data in an environment.
        return 
            If True, builder sets data on the environment (a var symbol).
        '''
        raise NotImplementedError()


    def mustGetData(self, name):
        '''
        Test if a function gets data from an environment.
        return 
            If True, builder gets data from the environment (a var symbol).
        '''
        raise NotImplementedError()
            
    def byteSize(self, bitsize):
        return bitsize >> 3

    #!!! Python specific code turns this class into an imitation of a
    # map of func pointers. Probably what is needed is a map of func 
    # pointers (but that is not templatable). 
    def __contains__(self, k):
        # python 'in' syntax
        return k in dir(self)
            
    def __getitem__(self, name):
        # python '[id]' syntax
        return getattr(self, name)



#! needs inherit arch
class BuilderAPIX64(BuilderAPI):
    arch = architecture.architectureSolve(architecture.x64)
    printers = PrintX64()


    ## basics
    def comment(self, b, args):
        b._code.append("; " + args[0])
        return MessageOptionNone
        
    def sysExit(self, b, args):    
        b._code.append("mov rax, 60")
        b._code.append("mov rdi, " + str(args[0]))
        b._code.append("syscall")
        return MessageOptionNone

    def extern(self, b, args):
        '''
        Append an extern.
        '''
        b.externsAdd("extern " + args[0])
        return MessageOptionNone
        
    def raw(self, b, args):
        '''
        Append a line of code.
        '''
        b._code.append(args[0])
        return MessageOptionNone
        


    ## Code structure 
    def frame(self, b, args):
        '''
        Start a stack frame.
        '''
        # push rbp
        b._code.append("push {}".format(self.arch['stackBasePointer']))
        # mov rbp, rsp
        b._code.append("mov {}, {}".format(self.arch['stackBasePointer'], self.arch['stackPointer']))
        self.stackSize = 0
        return MessageOptionNone

    def frameEnd(self, b, args):
        '''
        End a stack frame.
        '''
        # mov rsp, rbp
        b._code.append("mov {}, {}".format(self.arch['stackPointer'], self.arch['stackBasePointer']))
        # pop pop rbp
        b._code.append("pop {}".format(self.arch['stackBasePointer']))
        return MessageOptionNone
           
           
    def func(self, b, args):
        '''
        Start a function.
        '''
        b._code.append('{}:'.format(args[0].toString()))
        b._code.append('; beginFunc')
        self.compiler.envAddClosure()
        return MessageOptionNone

        
    #def funcSetReturn(b, locationRoot):
    #    locationRoot.toRegister(self.arch['returnRegister'])

    # If these end frames, do they need to end frame inside?
    # If so, offer the frame option at begin, also?
    def funcEnd(self, b, args):
        '''
        End a function with return.
        '''
        self.compiler.envDelClosure()
        b._code.append('ret')
        b._code.append('; endFunc')
        return MessageOptionNone

    def funcMain(self, b, args):
        self.func(b, [ProtoSymbol('@main')])
        self.compiler.envAddClosure()
        return MessageOptionNone
        
    def funcMainEnd(self, b, args):
        self.compiler.envDelClosure()
        b._code.append('; endFunc')
        return MessageOptionNone



    ## Register utilities
    # #! needs datapush
    def registersPush(self, b, args):
        registerList = args
        for r in registerList:
            b._code.append('push ' + r)
        self.compiler.closureDataPush(registerList)
        return MessageOptionNone

    def registersPop(self, b, args):
        registerList = self.compiler.closureDataPop()
        for r in reversed(registerList):
            b._code.append('pop ' + r)
        return MessageOptionNone

    def registersVolatilePush(self, b, args):
        '''
        Protect the volatile registers 
        i.e. those used for parameter passing.
        '''
        self.registersPush(b, self.arch['cParameterRegisters'].copy())
        return MessageOptionNone



    ## Allocs
    def RODefine(self, b, args):
        '''
        Define a numeruc string to a label
            protoSymbol, string
        '''
        protoSymbolLabel = args[0].toString()
        data = args[1]
        tpe = args[2]
        #? wrap as string if necessary
        rodata = '{}: {} {}'.format(
            protoSymbolLabel,
            TypesToASMAbv[tpe],
            data
        )
        b.rodataAdd(rodata)
        self.compiler.symbolSetGlobal(
            protoSymbolLabel, 
            Var.ROX64(protoSymbolLabel, tpe)
        )
        # return (
            # protoSymbolLabel, 
            # #Var.ROX64(protoSymbolLabel, tpe)
            # Var.ROX64Either(protoSymbolLabel, tpe)
        # )
        return MessageOptionNone

    def ROStringDefine(self, b, args):
        '''
        Define a numeric string to a label
            protoSymbol, string
        '''
        #! cant be this, must generate a label
        protoSymbolLabel = args[0].toString()
        string = args[1]
        rodata = protoSymbolLabel + ': db "' + args[1] + '", 0'
        b.rodataAdd(rodata)
        self.compiler.symbolSetGlobal(
            protoSymbolLabel, 
            Var.ROX64(protoSymbolLabel,  Type.StrASCII)
        )
        # return (
            # protoSymbolLabel, 
            # Var.ROX64(protoSymbolLabel, Type.StrASCII)
        # )                
        return MessageOptionNone
   

    def regDefine(self, b, args):
        '''
        Define a value in a register
            protoSymbol, registerName value type
        '''
        protoSymbolLabel = args[0].toString()
        register = args[1]
        data = args[2]
        tpe = args[3]
        b._code.append("mov {}, {}".format(
            #TypesToASMName[tpe],
            register, 
            data
        ))
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            Var.RegX64(register, tpe)
        )
        # return (
            # protoSymbolLabel, 
            # #Var.RegX64(register, tpe)
            # Var.RegX64Either(register, tpe)
        # )
        return MessageOptionNone
                        
    def heapAllocBytes(self, b, args):
        '''
        Allocate bytes to malloc
            protoSymbol, slotIndex
        '''
        self.extern(b, ['malloc'])
        protoSymbolLabel = args[0].toString()
        byteSize = self.arch['bytesize'] * args[1]
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], byteSize))
        b._code.append("call malloc")
        #return LocRoot.RegisterX64(self.arch['returnRegister'])
        # No, it has no ''Type', hence the Loc return abovr
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            Var.RegX64(self.arch['returnRegister'], Type.StrASCII)
        )
        return MessageOptionNone
        
    def heapAlloc(self, b, args):
        '''
        Alloc space for a type on the heap
        protosymbol, type
        '''
        self.extern(b, ['malloc'])
        #! but malloc works in bytes?
        protoSymbolLabel = args[0].toString()
        tpe = args[1]
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], tpe.byteSize))
        b._code.append("call malloc")
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            Var.RegX64(self.arch['returnRegister'], tpe)
        )
        #return LocationRootRegisterX64(self.arch['returnRegister']) 
        # return (
            # protoSymbolLabel, 
            # #Var.RegAddrX64(self.arch['returnRegister'], tpe)
            # Var.RegAddrX64Either(self.arch['returnRegister'], tpe)
        # ) 
        return MessageOptionNone

    #! account for data types
    # and align
    def stackAllocBytes(self, b, args):
        '''
        Allocate stack storage
            protoSymbol, slotIndex, int
        '''
        protoSymbolLabel = args[0].toString()
        index = args[1]
        allocSpace = args[2]
        BPRoffset = allocSpace + (self.arch['bytesize'] * index)
        b._code.append("lea rsp, [rbp - {}]".format(BPRoffset)) 
        # No, it has no ''Type', hence the Loc return abovr
        # self.compiler.symbolSetClosure(
            # protoSymbolLabel, 
            # Var.StackX64(index, Type.StrASCII)
        # )
        return MessageOptionNone
        
    #! bad thing here, we don't know where stack starts, so only works 
    # on empty stackframe
    def stackAlloc(self, b, args):
        '''
        Allocate stack storage
        Resets the Stack pointer register e.g. 'esp' etc. 
        The calculation is absolute, from the index
        So set index to a calculated top (unless you are writing trick 
        code).
        It's ok to alloc at a slot above the current stack hight, 
        but an alloc below the stack height will reset the pointer 
        towards the base pointer. Subsequent action could overwrite
        required data. 
            [protoSymbol, slotIndex, type]
        '''
        protoSymbolLabel = args[0].toString()
        index = args[1]
        tpe = args[2]
        #tpe.byteSize
        #self.arch['bytesize']
        # We can not account for bytesize, only allocate the slot
        # must be aligned on 16 bytes?
        b._code.append("lea rsp, [rbp - {}]".format(
             self.arch['bytesize'] * index 
        )) 
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            Var.StackX64(index, tpe)
        )
        # return (
            # protoSymbolLabel, 
            # #Var.StackX64(index, tpe)
            # Var.StackX64Either(index, tpe)
        # ) 
        return MessageOptionNone
                        
    # def stringHeapDefine(self, b, args):
        # '''
        # Allocate and define a malloced string
        # UTF-8
        # '''
        # byteSize = self.byteSize() * size
        # b._code.append("mov {}, {}".format(arch['cParameterRegister'][0], byteSize))
        # b._code.append("call malloc")
        # return LocationRootRegisterX64('rax') 

                  
    ## Var action
    def set(self, b, args):
        '''
            [Var.Base, val],
        '''
        var = args[0]
        val = args[1]
        mo = MessageOptionNone
        
        # By definition, RO is not possible
        if (isinstance(var.loc, Loc.RODataX64)):
            mo = MessageOption.error('Cant set a RO variable!')
            #self.compiler.error('Cant set a RO variable!')

        # Needs a path for deeper peeks
        if (not(isinstance(var.tpe, Type.TypeSingular))):
            mo = MessageOption.error('Need path to set on complex type? var:{}'.format(var))
            #self.compiler.error('Need path to set on complex type? var:{}'.format(var))
            
        # Only if ok (could throw errors)
        if (mo.isOk()):
            b._code.append("mov {} {}, {}".format(
                TypesToASMName[var.tpe], 
                var.toCodeValue(), 
                val
            ))
            
        return mo

    #! Utility. Should not be here
    #? Currently only on registers
    #? and only two deep
    # etc.
    def _toCodeAccessDeep(self, lid, path, tpe):
        addrB = AddressBuilder(lid)
        #? protection against rogue pids
        #? Could unroll, with only two elements max?
        for pid in path:
            offset, tpe = tpe.offsetTypePair(pid)
            addrB.addOffset(offset)
            if (not(isinstance(tpe, Type.TypeContainer))):
                break
        return (addrB.result(True), tpe)
        
    def setPath(self, b, args):
        '''
            [ Var.Base path val],
        '''
        var = args[0]
        path = args[1]
        val = args[2]
        mo = MessageOptionNone
        if (len(path) > 2):
            mo = MessageOption.error('Path can only access max 2 types deep. Needs load?')
        
        #? and maybe only on register vars?
        
        # Only if ok (could throw errors)
        if (mo.isOk()):
            # Build address
            tpe = var.tpe
            codeAccess = self._toCodeAccessDeep(var.loc.lid, path, tpe)
            b._code.append("mov {} {}, {}".format(
                # las type, is singular (we hope)
                TypesToASMName[codeAccess[1]], 
                #? True always here
                codeAccess[0], 
                val
            ))                    
        return mo


        # rolled would look like
    # a loop...
    # loopLabel = 
    #innerCode = 
    # b._code.append(':' + loopLabel)
    # b._code.append(innerCode)
    # b._code.append('dec rcx')
    # b._code.append('cmp rcx, 0')
    # b._code.append('jgtzo loopLabel')
     
     
    def forEachRoll(self, b, args):
        '''
            [ProtoSymbol Var.Base],
        '''
        innerVar = args[0]
        var = args[1]
        mo = MessageOptionNone
        return mo

        
    def forEachRolleEnd(self, b, args):
        '''
            []
        '''
        b._code.append('; endForEach')
        return MessageOptionNone

    def forEach(self, b, args):
        '''
            [ProtoSymbol Var.Base],
        '''
        # Get the original var
        var = args[1]
        #! if it's unrollable type
        # ???
        
        # Will need these bits of info
        # InnerVar name...
        protoSymbolLabel = args[0].toString()
        
        # Choice of innervar register...
        #! tmp for now
        register = 'rcx'
        
        # Original var... then push that data
        self.compiler.closureData.append((protoSymbolLabel, register, var,)) 
                
        # add a new environment
        #???
        self.compiler.envAddClosure()

        # set the innervar on it
        # Not going to work for clutches
        #varObj = Var.RegX64(register, var.tpe.elementType)

        #! this is on envEverything
        #self.compiler.envFunc[protoSymbolLabel] = varObj
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            Var.RegX64(register, var.tpe.elementType)
        )
           
        # Set up the new builder
        b._code.append('; beginLoop')
        self.compiler.builderNew()

        mo = MessageOptionNone
        return mo
        
    def forEachEnd(self, b, args):
        '''
            []
        '''
        # The passed builder is the subbuilder
        innerCode = b.result()
        
        # Revert builders in the compiler
        self.compiler.builderOld()
        
        # Make tha builder revertion explicit by setting 'b' to the 
        # previous builder
        b = self.compiler.b


        # get the data
        protoSymbolLabel, register, var = self.compiler.closureData.pop()
        
        # Dispose of the inner environment too (and rid of innervar)
        # ???
        #del self.compiler.envFunc[protoSymbolLabel]
        self.compiler.envDelClosure()
        

        lid = var.loc.lid
        # build the unroll
        #??? fix offsets good
        for offset, tpe in var.tpe.offsetIt():
            b._code.append("mov {}, [{} + {}]".format(register, lid, offset))
            # add the innercode
            b.addAll(innerCode)    
        b._code.append('; endLoop')
        return MessageOptionNone

        
        
    ## Printers
    def print(self, b, args):
        '''
        var
        '''
        # We could print out using printf semantics....
        # No, print singly. figue out the slowness later.
        var = args[0]
        tpe = var.tpe
        if (not isinstance(tpe, Type.TypeSingular)):
            #! Need a foreach here. lets get to thatt....
            # we got to do something recursive with it
            # printStr(b, tpe.name, StrASCII)
            # printStr(b, ['(' StrASCII])
            # print(b, tpe.foreach(args => print(b, [args])))
            # printStr(b, [')' StrASCII])
            raise NotImplementedError('Currently, container type can not be printed')
            # etc.
        else:
            # Figure out what will print or not
            #var.accessMk()
            print(str(var))
            # tpe, offset(lid)
            # tpe.offsetDeep(self, path)
            srcSnippet = var.toCodeValue()
            #! Obviously, very temproary!
            # What we need is probably something that separates string 
            # types from numbers
            print(str(tpe))
            if (tpe == Type.StrASCII):
                # For a string, printf wants the address, not the value
                srcSnippet = var.toCodeAddress()
            print('snippet:')
            print(str(srcSnippet))
            self.printers(b, tpe, srcSnippet)
        return MessageOptionNone
            
    def println(self, b, args):
        '''
        var
        '''
        self.print(b, args)
        self.printers.newline(b)
        return MessageOptionNone
        
    def printFlush(self, b, args):
        self.printers.flush(b)
        return MessageOptionNone
