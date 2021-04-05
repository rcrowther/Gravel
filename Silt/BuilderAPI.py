import architecture
from syn_arg_tests import *



from tpl_Printers import PrintX64
import tpl_locationRoot as Loc
import tpl_types as Type
from tpl_vars import Var
from asm_db import TypesToASMAbv, TypesToASMName

#? dont like this imports. They're for arg types though.
from Syntaxer import ProtoSymbol, Path, FuncBoolean
from tpl_either import MessageOption, MessageOptionNone

# Humm. Build addresses here, not in locs?
#?x many not left
#from tpl_address_builder import AddressBuilder
from tpl_access_builders import AccessValue, AccessAddress

from tpl_label_generators import LabelGen

from tpl_autostore import AutoStoreX64



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

    labelGenerate = LabelGen()

    '''
    Type signature of API funcs
    '''
    #NB Can get rid of the brackets, but that's Pythonic
    funcNameToArgsType = {
        # basics
        'comment': [strVal()],
        'sysExit': [intVal()],
        'extern': [strVal()],
        'raw': [strVal()],
        
        ## Code structure 
        'frame': [],
        'frameEnd': [],
        'func': [protoSymbolVal()],
        'funcEnd': [],
        'funcMain': [],
        'funcMainEnd': [],

        ## Register utilities
        'registersPush': [argListVal()],
        'registersVolatilePush': [],
        'registersPop': [],

        ## var action
        'set': [anyVar(), intVal()],
        'setPath':  [anyVar(), Path, intVal()],

        
        ## Arithmetic
        'dec' : [anyVar()],
        'inc' : [anyVar()],
        #? should be int or float. Anyway...
        #? Should be more verbose
        #! and it's freer than these parameters define. Memory locations
        # are ok for destination too.
        # but not teo memory locs together
        'add' : [regVar(), intOrVarNumeric()],
        'sub' : [regVar(), intOrVarNumeric()],
        'mul' : [regVar(), intOrVarNumeric()],
        #'divi' : [regVar(), intOrVarNumeric()],
        #'div' : [regVar(), intOrVarNumeric()],
        'shl' : [regVar(), intVal()],
        'shr' : [regVar(), intVal()],
        
        ## Allocs
        'ROStringDefine': [protoSymbolVal(), strVal()],
        'ROStringUTF8Define': [protoSymbolVal(), strVal()],
        'RODefine': [protoSymbolVal(), intVal(), anyType()],
        'regDefine': [protoSymbolVal(), strVal(), intVal(), anyType()],
        'heapAllocBytes': [protoSymbolVal(), intVal()],
        'heapAlloc': [protoSymbolVal(), anyType()],
        'heapAlloc': [protoSymbolVal(), anyType()],        
        'stackAllocBytes': [protoSymbolVal(), intVal(), intVal()],
        'stackAlloc': [protoSymbolVal(), intVal(), anyType()],

        ## Conditional
        'ifRangeStart': [intOrVarNumeric(), intOrVarNumeric(), intOrVarNumeric()],
        'ifRangeEnd':[],
        'ifStart': [booleanFuncVal()],
        'ifEnd': [],
        'cmp': [regVar(), booleanFuncVal()],
        'switchStart': [regVar()],
        'whenStart': [intVal()],
        'whenDefaultStart': [],
        'whenEnd': [],
        'switchEnd': [],
                    
        ## loops
        'forRange': [strVal(), intVal(), intOrVarNumeric()],
        'forRangeEnd': [],
        'whileStart': [booleanFuncVal()],
        'whileEnd': [],
        'forEachUnrolled' : [protoSymbolVal(), strVal(), containerOffsetVar()],
        'forEachUnrolledEnd': [],
        'forEach': [protoSymbolVal(), strVal(), containerOffsetVar()],
        'forEachEnd': [],
                
        ## printers
        # Need a special argTes, strOrVarAny()
        'print' : [strOrVarAny()],
        'println': [strOrVarAny()],
        'printFlush': [],
    #'': [].
    }
     
    # AllPlatform utitlites
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

        
# Need to do something with these Compiler stack conveniences
class SwitchData(list):
    pass

class WhenDataBase():
    pass
    
class WhenData(WhenDataBase, list):
    pass
    
class _WhenDefault(WhenDataBase):
    pass
    
WhenDefault = _WhenDefault()



#! needs inherit arch
class BuilderAPIX64(BuilderAPI):
    arch = architecture.architectureSolve(architecture.x64)
    printers = PrintX64()

    # arch, sizeSlots, offset
    autoStore = AutoStoreX64(arch, 3, 1)

    def literalOrVarAccessValue(self, varOrConstant):
        '''
        Return snippets for literals and variables.
        Can't handle offsets or registers, but s useful func.
        '''
        if (not(isinstance(varOrConstant, Var))):
            # its a constant
            return str(varOrConstant)
        else:
            return AccessValue(varOrConstant.loc).result()

            
  


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
        protoSymbolLabel = args[0].toString()
        #print(protoSymbolLabel)
        b._code.append('{}:'.format(protoSymbolLabel))
        b._code.append('; beginFunc')
        #self.compiler.envAddClosure()
        self.compiler.scopeStackPush()
        return MessageOptionNone

        
    #def funcSetReturn(b, locationRoot):
    #    locationRoot.toRegister(self.arch['returnRegister'])

    # If these end frames, do they need to end frame inside?
    # If so, offer the frame option at begin, also?
    def funcEnd(self, b, args):
        '''
        End a function with return.
        '''
        self.autoStore.deleteAll([])
        #self.compiler.envDelClosure()
        self.compiler.scopeStackPop()
        b._code.append('ret')
        b._code.append('; endFunc')
        return MessageOptionNone

    def funcMain(self, b, args):
        self.func(b, [ProtoSymbol('@main')])
        #self.compiler.envAddClosure()
        self.compiler.scopeStackPush()
        return MessageOptionNone
        
    def funcMainEnd(self, b, args):
        #self.compiler.scopePrint()
        #self.compiler.envDelClosure()
        self.compiler.scopeStackPop()
        b._code.append('; endFunc')
        return MessageOptionNone



    ## Register utilities
    # #! needs datapush
    def registersPush(self, b, args):
        '''
            [argList]
        '''
        registerList = args[0]
        if (len(registerList) & 1):
            self.compiler.warning("Uneven n number of pushes will unbalance the stack?")
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
        self.registersPush(
            b, 
            [ArgList(self.arch['cParameterRegisters'].copy())]
        )
        return MessageOptionNone



    ## Allocs
    #! sting/numeric could be joined?
    #! could be any numeric vla, including variables
    #! type cannot be container, or can it?
    #? and its called RODataDefine
    def RODefine(self, b, args):
        '''
        Define a number to a label
             [protoSymbolVal(), intVal(), anyType()]
        '''
        protoSymbolLabel = args[0].toString()
        data = args[1]
        tpe = args[2]

        #! check size limits?
        rodata = '{}: {} {}'.format(
            protoSymbolLabel,
            TypesToASMAbv[tpe],
            data
        )
        b.rodataAdd(rodata)
        var = Var(
            protoSymbolLabel,
            Loc.RODataX64(protoSymbolLabel), 
            tpe
        )
        # self.compiler.symbolSetGlobal(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symbolSetGlobal(var) 
        return MessageOptionNone

    def ROStringDefine(self, b, args):
        '''
        Define a byte-width string to a label
            [protoSymbolVal(), strVal()]
        '''
        protoSymbolLabel = args[0].toString()
        string = args[1]
        
        # Trailing zero, though I believe NASM padds to align anyway
        rodata = protoSymbolLabel + ': db "' + args[1] + '", 0'
        b.rodataAdd(rodata)
        # isn't that to an addr?
        var = Var(
            protoSymbolLabel,
            Loc.RODataX64(protoSymbolLabel), 
            Type.StrASCII
        )
        # self.compiler.symbolSetGlobal(
            # protoSymbolLabel, 
            # var
        # )            
        self.compiler.symbolSetGlobal(var) 
        return MessageOptionNone
        
    def ROStringUTF8Define(self, b, args):
        '''
        Define a byte-width string to a label
            [protoSymbolVal(), strVal()]
        '''
        #! this is not a plain API. Just DefineStrEscapable()?
        # The difference here:
        # - the string is put in backquotes, NASM syntax. This allows
        # C style string escaping.
        # The delimiting zero is still there to work with C-type 
        # strings, though the encoding may have nothing to say about 
        # that.
        # NASM allows us also to convert to fixed-width using 
        # __?utf32?__. Do we want to do that? How does printf etc. work?
        # Have a look at how Glib implements its functions, which are 
        # pretty much what we would like 
        # https://developer.gnome.org/glib/stable/glib-Unicode-Manipulation.html
        protoSymbolLabel = args[0].toString()
        string = args[1]
        rodata = protoSymbolLabel + ": db `" + args[1] + "`, 0"
        b.rodataAdd(rodata)
        # isn't this an addr?
        var = Var(
            protoSymbolLabel,
            Loc.RODataX64(protoSymbolLabel), 
            Type.StrUTF8
            )
        # self.compiler.symbolSetGlobal(
            # protoSymbolLabel, 
            # var
        # )  
        self.compiler.symbolSetGlobal(var) 
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

        #!NB try to allocate the var first, to accont for data
        # shuffles, and revised positioning
        # var = self.autoStore.varRegCreate(b, register, tpe, 3)
         
        # # ... then do the write from the data in the var.
        # b._code.append("mov {}, {}".format(
            # #TypesToASMName[tpe],
            # register, 
            # data
        # ))

        b._code.append("mov {}, {}".format(
            #TypesToASMName[tpe],
            register, 
            data
        ))
        var = Var(
            protoSymbolLabel,
            Loc.RegisterX64(register), 
            tpe
        )
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symSet(var)

        # return (
            # protoSymbolLabel, 
            # #Var.RegX64(register, tpe)
            # Var.RegX64Either(register, tpe)
        # )
        return MessageOptionNone
                        
    def heapAllocBytes(self, b, args):
        '''
        Allocate bytes to malloc
            [protoSymbolVal(), intVal()]
        '''
        self.extern(b, ['malloc'])
        protoSymbolLabel = args[0].toString()
        byteSize = self.arch['bytesize'] * args[1]
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], byteSize))
        b._code.append("call malloc")
        #?! No, it has no ''Type', hence the Loc return above
        #? Ummm, proposal: Array[Bit8]
        var = Var(
            protoSymbolLabel,
            Loc.RegisterX64(self.arch['returnRegister'],), 
            Type.StrASCII
        )
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symSet(var)
        return MessageOptionNone
        
    def heapAlloc(self, b, args):
        '''
        Alloc space for a type on the heap
            [protoSymbolVal(), anyType()]
        '''
        self.extern(b, ['malloc'])
        #! but malloc works in bytes?
        protoSymbolLabel = args[0].toString()
        tpe = args[1]
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], tpe.byteSize))
        b._code.append("call malloc")
        var = Var(
            protoSymbolLabel,
            Loc.RegisteredAddressX64(self.arch['returnRegister']), 
            tpe
        )
        #print('huh?')
        #print(str(tpe))
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symSet(var)

        #return LocationRootRegisterX64(self.arch['returnRegister']) 
        # return (
            # protoSymbolLabel, 
            # #Var.RegAddrX64(self.arch['returnRegister'], tpe)
            # Var.RegAddrX64Either(self.arch['returnRegister'], tpe)
        # ) 
        return MessageOptionNone

    ## Unicode?
    # No I think what this might be about is not, how to creat a UTF 
    # string But more, what will our string handling be like?
    # Note the import utypes
    # https://unicode-org.github.io/icu-docs/apidoc/released/icu4c/utypes_8h.html
    # def heapDefineStringUtf8(self, b, args):
        # '''
        # Alloc space for a type on the heap
            # [protoSymbolVal(), strVal()]
        # '''
        # protoSymbolLabel = args[0].toString()
        # string = args[1]
        
        # self.extern(b, ['utypes'])

        # self.raw(b, ['; UTF here'])
        # # temp, until figure stringlen
        # var = self.heapAllocBytes( b, [args[0], 20])
        
        # # can I have a 'immediate' string in unicode?
        # # can it go to malloced, or do we copy?
        # # scanf("%s", stringa1);
        # # fgets( stringa1, n + 1, stdin );b
        # # strlen(s);
        # #       for(i=0;i<len;i++) 
        # #{
        # #  copy[i]=s[i];  //copy characters               
        # #}
        # # p[i] = '\0';
        # #memcpy( p, s, len );
        # #strcpy():
        # #strdup():
       
        # self.raw(b, ['; UTF unhere'])
        # return MessageOptionNone
            
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

        # No, it has no ''Type', hence the Loc return above
        #? really? this a Location, not a var
        var = Var(
            protoSymbolLabel,
            Loc.StackX64(index),
            #??? 
            Type.StrASCII
        )
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symSet(var)

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
        var = Var(
            protoSymbolLabel,
            index, 
            tpe
        )
        
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # var
        # )
        self.compiler.symSet(var)

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
        Set a var to a value
            [Var, val],
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
                AccessValue(var.loc).result(),
                val
            ))
            
        return mo

    #! Utility. Should not be here
    #? Currently only on registers
    #? and only two deep
    # etc.
    #x?
    # def _toCodeAccessDeep(self, lid, path, tpe):
        # addrB = AddressBuilder(lid)
        # #? protection against rogue pids
        # #? Could unroll, with only two elements max?
        # for pid in path:
            # offset, tpe = tpe.offsetTypePair(pid)
            # addrB.addOffset(offset)
            # if (not(isinstance(tpe, Type.TypeContainer))):
                # break
        # return (addrB.asAddress(), tpe)

    def _toCodeAccessDeep(self, lid, path, tpe):
        addrB = AccessValue(var.loc).result()
        #? protection against rogue pids
        #? Could unroll, with only two elements max?
        for pid in path:
            offset, tpe = tpe.offsetTypePair(pid)
            addrB.addOffset(offset)
            if (not(isinstance(tpe, Type.TypeContainer))):
                break
        return (addrB.result(), tpe)        
        
    def setPath(self, b, args):
        '''
        Set a path through a type to a value
            [ Var path val],
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



    ## arithmetic
    #! if we go unsigned, we need to extend these
    #! We need something works as var or val?
    #? Will need widths?
    def dec(self, b, args):
        '''
        [anyVar()]
        '''
        # Yes works with relative addresses
        var = args[0]
        b._code.append("dec {} {}".format(
            TypesToASMName[var.tpe],
            AccessValue(var.loc).result()
        ))      
        return MessageOptionNone

    def inc(self, b, args):
        '''
        [anyVar()]
        '''
        var = args[0]
        b._code.append("inc {} {}".format(
            TypesToASMName[var.tpe],
            AccessValue(var.loc).result()
        ))       
        return MessageOptionNone
        
        #! and it's freer than these parameters define. Memory locations
        # are ok for destination too.
        # but not two memory locs together

    def add(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        varD = args[0]
        varS = args[1]
        b._code.append("add {} {}, {}".format(
            TypesToASMName[varD.tpe],
            AccessValue(varD.loc).result(),
            self.literalOrVarAccessValue(varS)
        ))       
        return MessageOptionNone
        
    def sub(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        varD = args[0]
        varS = args[1]
        b._code.append("sub {} {}, {}".format(
            TypesToASMName[varD.tpe],
            AccessValue(varD.loc).result(),
            self.literalOrVarAccessValue(varS)
        ))       
        return MessageOptionNone
        
    def mul(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        # imul
        # https://www.felixcloutier.com/x86/imul
        varD = args[0]
        varS = args[1]
        b._code.append("imul {} {}, {}".format(
            TypesToASMName[varD.tpe],
            AccessValue(varD.loc).result(),
            self.literalOrVarAccessValue(varS)
        ))       
        return MessageOptionNone        

    
    #def div(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        # idiv, real problem, will not work from full-width, and 
        # restricted in registers, too!
        # https://www.felixcloutier.com/x86/imul
        # I don't have a current solution. Beteween the rgister splits
        # and linited arg positions, this is not whaat we want.
        # I want to divide one fulll register by another, and to heck
        # with consequences. maybe I need one of those multiply/divide
        # algorithms used by compilers?
        # e.g. https://board.flatassembler.net/topic.php?t=20099
                
    #def div(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''

    def shr(self, b, args):
        '''
        [regVar(), intVal()]
        '''
        varD = args[0]
        varS = args[1]
        
        # Keep numerics down
        if (
            not(isinstance(varS, Var)) 
            and (varS > self.arch['bytesize'] - 1)
        ):
            self.compiler.warning('Given shiftsize is too large for arch. Will compile, but not do as intended. size:{}'.format(varS))
        b._code.append("shr {} {}, {}".format(
            TypesToASMName[varD.tpe],
            AccessValue(varD.loc).result(),
            self.literalOrVarAccessValue(varS)
        ))       
        return MessageOptionNone

    def shl(self, b, args):
        '''
        [regVar(), intVal()]
        '''
        varD = args[0]
        varS = args[1]
        
        # Keep numerics down
        if (
            not(isinstance(varS, Var)) 
            and (varS > self.arch['bytesize'] - 1)
        ):
            self.compiler.warning('Given shiftsize is too large for arch. Will compile, but not do as intended. size:{}'.format(varS))
        b._code.append("shl {}, {}".format(
            AccessValue(varD.loc).result(),
            self.literalOrVarAccessValue(varS)
        ))       
        return MessageOptionNone




    ### compare/if

    def ifRangeStart(self, b, args):
        '''
        Conditionally ecaluate between two numbers.
        Cantt test the variables so allows messing about. Underneath,
        the test is lessThan | GreaterThanEqeals.
        var
            to test
        from
            the number to start on
        until
            advances until before this number
            [intOrVarNumeric(), intOrVarNumeric(), intOrVarNumeric()],
        '''
        #NB Range can't be tested, as it may be vars.
        # but both range numbers can be register, as the tests are 
        # seeperate.
        var = args[0]
        froom = args[1]
        to = args[2]
        falseLabel = self.labelGenerate('ifRangeFalse')
        accessSnippet = self.literalOrVarAccessValue(var)
        fromSnippet = self.literalOrVarAccessValue(froom)
        toSnippet = self.literalOrVarAccessValue(to)
        b._code.append("cmp {}, {}".format(accessSnippet, fromSnippet))
        b._code.append("jl " + falseLabel)
        b._code.append("cmp {}, {}".format(accessSnippet, toSnippet))
        b._code.append("jge " + falseLabel)
        self.compiler.closureDataPush(falseLabel)
        b._code.append('; beginBlock')
        return MessageOptionNone
        
    def ifRangeEnd(self, b, args):
        falseLabel = self.compiler.closureDataPop()
        b._code.append(falseLabel + ':')
        b._code.append('; endBlock')                
        return MessageOptionNone
                    
    jumpOps = {
        "lt": "jl",
        "lte": "jle",
        "gt": "jg",
        "gte": "jge",
        "eq": "je",
        "neq": "jne",
    }

    jumpOpsNot = {
        "lt": "jge",
        "lte": "jg",
        "gt": "jle",
        "gte":"jl",
        "eq": "jne",
        "neq": "je",
    }

    NamesBooleanCollators = [
        'and', 'or', 'xor', 
    ]
            
            
    def _logicBuilder(
        self, 
        b, 
        logicTree, 
        invertToFalse, 
        compareNot,
        trueLabel, 
        falseLabel
    ):
        '''
        Build shortcut comparison code from a logicTree.
        
        The default approch is to invert comparisions and send to false.
        This is the basic setup for AND functions. invertToFalse has no
        effect on the comparison, but changes the shortcut, and is used 
        for OR.
        logicTree
            A single instance of FuncBoolean
        invertToFalse
            invert comparisons as written, and drirect the jump to
            the false label (default true)
        compareNot
            Parent node is NOT
        '''
        #! not hadling XOR
        #? Tail recurse?
        if (logicTree.name in self.NamesBooleanCollators):
            #! with a negate end, invert, etc.
            collatorIsAND = (logicTree.name == 'and')

            # Now tricks.  Common Assemblty code, so I'm not going 
            # to stand them as optimisations
            #
            # - if we get a NOT into an AND/OR, we use DeMorgans rule 
            # backwards. We let the NOT trickle into the arguments, but 
            # must switch AND/OR e.g. NOT(AND(1 2)) = OR(NOT(1) NOT(2))
            if (compareNot):
                collatorIsAND = not()
                
            # - we set invertToFalse by the function. This 
            # introduces the shortcut behaviour. AND jumps to the false
            # label (on failure), OR jumps to the true label (on 
            # success)
            invertToFalse = collatorIsAND
            if (not(collatorIsAND)):
                # - OR comparisons should formally be followed by 
                # a jump to false label, since no comparison succeeded.
                # Otherise, it falls through to executing the block
                # anyway.
                # There's another solution, expensive on the compiler
                # but removing this last jump---invert the last comparison.
                argsc = logicTree.args.copy()
                lastArg = argsc.pop()
                for arg in argsc:
                    self._logicBuilder(b, arg, False, compareNot, trueLabel, falseLabel)
                self._logicBuilder(b, lastArg, True, compareNot, trueLabel, falseLabel)                
            else:    
                for arg in logicTree.args:
                    self._logicBuilder(b, arg, invertToFalse, compareNot, trueLabel, falseLabel)
        elif (logicTree.name == 'not'):
            self._logicBuilder(b, logicTree.args[0], invertToFalse, not(compareNot), trueLabel, falseLabel)                
        else:
            # Must be a Comparison
            # Resolve whatever has been sent
            #! MUST be a more appropriate place to place this little stunt
            # The stunt is, either pass the value, but if its a Var, run through
            # the builder---without any offsets or register relative addressing
            arg0 = logicTree.args[0]
            arg1 = logicTree.args[1]
            if isinstance(arg0, Var):
                arg0 = AccessValue(arg0.loc).result()
            if isinstance(arg1, Var):
                arg1 = AccessValue(logicTree.args[1].loc).result()
            b._code.append("cmp {}, {}".format(arg0, arg1))            
            #b._code.append("cmp {}, {}".format(logicTree.args[0], logicTree.args[1]))
            jumpOp = self.jumpOps[logicTree.name]
            label = trueLabel
            
            # Is the test inverted (Not)? Depending on our parameters?
            # This is XOR logic
            if (invertToFalse ^ compareNot):
                jumpOp = self.jumpOpsNot[logicTree.name]
            if (invertToFalse):
                label = falseLabel
            b._code.append("{} {}".format(jumpOp, label))
            
    #! shouldn't be here, but for now
    #! call them subbuilders?
    def logicBuilder(
        self, 
        b, 
        logicTree,
        trueLabel, 
        falseLabel
    ):
        '''
        Build shortcut comparison code from a logicTree.
        '''
        # Start with an AND configuration, invertToFalse = True
        # Start with no enabled NOT, compareNot = False
        #! Won't work on two literal numbers
        #! and wont work with literals on first parameter  
        self._logicBuilder(b, logicTree, True, False, trueLabel, falseLabel)
    
    
    
    def ifStart(self, b, args):
        '''
        if...then flow control from boolean logic.
            [booleanFuncVal()]
        '''
        boolLogic = args[0]
        
        # Now need some booleana logic to get us there...
        falseLabel = self.labelGenerate('ifFalse')
        trueLabel = self.labelGenerate('ifTrue')
        self.logicBuilder(b, boolLogic, trueLabel, falseLabel)
        
        # Put the true label at block start
        b._code.append(trueLabel + ':')        
        b._code.append('; beginBlock')        
        self.compiler.closureDataPush(falseLabel)
        return MessageOptionNone
                
    def ifEnd(self, b, args):
        # Put the false label at block end
        falseLabel = self.compiler.closureDataPop()
        #self.compiler.envDelClosure()
        #self.compiler.scopeStackPop()
        b._code.append('; endBlock')
        b._code.append(falseLabel + ':')        
        return MessageOptionNone

    # Like an it
    # This has the problem we need a Boolean type, probably.
    # And to go with it, a compare flag location.
    # Howsoever, it is working
    def cmp(self, b, args):
        '''
        Move a comparison reault to a var
            [anyVar(), booleanFuncVal()]
        '''
        #! insist targetVar is a varReg
        # ZF is what we want Flag -> reg
        targetVar = args[0]
        booleanFunc = args[1]

        # zero the targetVar
        b._code.append('xor {}, {}'.format(
            targetVar.loc.lid,
            targetVar.loc.lid
        ))

        # Now need some boolean logic to get us a result...
        falseLabel = self.labelGenerate('ifFalse')
        trueLabel = self.labelGenerate('ifTrue')
        self.logicBuilder(b, booleanFunc, trueLabel, falseLabel)
        
        # Put the true label at block start
        b._code.append(trueLabel + ':')        
        b._code.append('; beginBlock') 

        # if true, set targetVar to one
        b._code.append('mov {}, 1'.format(targetVar.loc.lid))
        
        # Then end it
        b._code.append('; endBlock')
        b._code.append(falseLabel + ':')  
        
        ## Test
        #Load FLAGS into AH register. AH is xAX high
        # b._code.append('lahf')
        # b._code.append("shr rax, 14")
        # nask that bit
        # b._code.append("and rax, 0x01")
        # move to the var.
        # b._code.append("mov rbx, rax")
       
        mo = MessageOptionNone
        return mo



    def switchStart(self, b, args):
        '''
            [regVar()]
        '''
        varCondition = args[0]
        
        #! fence the closuredata       
        self.compiler.closureDataPush(
            SwitchData((varCondition.loc.lid,))
        )
        mo = MessageOptionNone
        return mo
        
    #! environments
    def whenStart(self, b, args):
        '''
            [intVal()]
        '''
        whenIndex = args[0]
        self.compiler.closureDataPush(
            whenIndex
        )   
        
        # Capture instructions until when end
        self.compiler.instructionsStore()

        # Create an environment
        #self.compiler.envAddClosure()
        self.compiler.scopeStackPush()
        mo = MessageOptionNone
        return mo

    def whenDefaultStart(self, b, args):
        '''
            []
        '''
        return self.whenStart(b, [WhenDefault])

    def whenEnd(self, b, args):
        # Delete the environment
        #self.compiler.envDelClosure()
        self.compiler.scopeStackPop()

        # Revert builders and 
        # get content data
        funcsWhen = self.compiler.instructionsGet()
        
        # Pop the index, push back as a WhenData pair
        whenIndex = self.compiler.closureDataPop()
        self.compiler.closureDataPush(
            WhenData([whenIndex, funcsWhen])
        )        
        
        mo = MessageOptionNone
        return mo

    def switchEnd(self, b, args):
        '''
        '''
        # Map[index, funcs]
        whenMap = {}
        defaultWhen = None
        
        # get when data
        # We need to make Map(index, funcs)
        #? what if no data accident?
        #! other protections, 
        # should be a WhenData
        while (True):
            data = self.compiler.closureDataPop()
            if (isinstance(data, SwitchData)):
                break

            #? We could check this as we push WhenDatas, thus catching the error earlier?
            # previous is a WhenData or a SwitchData  (the first)
            # But then we need to peek te closeure =stack
            if (not(isinstance(data, WhenDataBase))):
                self.compiler.warning('CodeBlock stack not found WhenData. A codeblock in a When is not colosed. data:{}'.format(data))
            if (data[0] == WhenDefault):
                defaultWhen = data
            else:
                indexWhen = str(data[0]) 
                if (indexWhen in whenMap):
                    self.compiler.warning('When index repeated? index:{}'.format(data[0]))
                whenMap[indexWhen] = data[1]
             
        if (not(whenMap)):
            self.compiler.warning('No When in Switch block?')
            
        # get the register from the data
        reg = data[0]
        
        # basics
        labelEnd = self.labelGenerate('switchEnd')
        
        #! more tests, is exhaustive/has default
        # Map[whenIndex, label]
        switchConditions = {}
        for whenIndex in whenMap.keys():
            labelWhen = self.labelGenerate('whenStart')
            switchConditions[whenIndex] = labelWhen 

        # build switch
        b._code.append('; beginBlock')
        
        # write switch condition
        for  whenIndex, whenLabel in switchConditions.items():
            b._code.append("cmp	{}, {}".format(reg, whenIndex))
            b._code.append("je " + whenLabel)
        # default jump? Fall through, surely?
        
                
        # if present, write default
        if (defaultWhen):
            self.compiler.instructionsPlay(defaultWhen[1])
        else:
            self.compiler.warning('Switch, no default?')
            
        # always go to end, default or not
        b._code.append("jmp " + labelEnd)
            
        # write whens
        for index, funcsWhen in whenMap.items():
            b._code.append(switchConditions[index] + ':')
            b._code.append('; beginBlock') 
            # replay instructions
            self.compiler.instructionsPlay(funcsWhen)
            b._code.append("jmp " + labelEnd)
            b._code.append('; endBlock')        
        
        # Finish switch
        b._code.append(labelEnd + ':')
        b._code.append('; endBlock')        
        
        mo = MessageOptionNone
        return mo
                        



                
    ## loops
    def forRange(self, b, args):
        '''
        Increment or decrement between two numbers.
        reg
            the resister to increment on
        from
            the number to start on
        until
            advances until before this number
            
            [strVal(), intVal(), intOrVarNumeric()]            
        '''
        # From a given numeric point to a given numeric point. Beats a 
        # for...next loop, no probs...
        #? needs to step (ugly, optional var time. Is there another 
        # way if things are that awkward?)
        #! double rangers... Got a problem there with fixed vars?
        #! needs to handle variables etc.
        reg = args[0]
        froom = args[1]
        
        # this can now be a numeric variable, so needs resolving
        to = args[2]
        if (froom == to):
            self.compiler.warning("'from' is equal to 'to'. Loop will not be executed.")
        # assessment
        #? first, are they asessable i.e. given integers?
        #? if not, we need to do write a calculation for the symbol
        mustCountDown = (froom >= to)
            
        # from will always be oprated on by the counter.
        # currently sown, so up
        if (mustCountDown):
            froom += 1
        else:
            froom -= 1
        trueLabel = self.labelGenerate('forRangeTrue')
        entryLabel = self.labelGenerate('forRangeEntry')
        b._code.append('; beginBlock')   
        b._code.append("mov {}, {}".format(reg, froom))  
        b._code.append("jmp {}".format(entryLabel))                
        b._code.append(trueLabel + ':')        
        self.compiler.closureDataPush((trueLabel, entryLabel, reg, mustCountDown, to))
        return MessageOptionNone
                
    def forRangeEnd(self, b, args):
        trueLabel, entryLabel, reg, mustCountDown, to = self.compiler.closureDataPop()
        b._code.append(entryLabel + ':') 
        # or if using vars we write code to do this?  
        if (mustCountDown):
            b._code.append("dec {}".format(reg)) 
        else:
            b._code.append("inc {}".format(reg)) 
        b._code.append("cmp {}, {}".format(reg, to))        
        if (mustCountDown):
            b._code.append("jg {}".format(trueLabel))  
        else:     
            b._code.append("jl {}".format(trueLabel))        
        b._code.append('; endBlock')
        return MessageOptionNone

    # When you need to react to what's in the loop
    def whileStart(self, b, args):
        '''
            [booleanFuncVal()]
        '''
        #! undone
        boolLogic = args[0]
        trueLabel = self.labelGenerate('whileTrue')
        entryLabel = self.labelGenerate('whileEntry')
        b._code.append(trueLabel + ':')        
        b._code.append('; beginBlock')   
        self.compiler.closureDataPush((entryLabel, boolLogic,))
        return MessageOptionNone
                
    def whileEnd(self, b, args):
        entryLabel, boolLogic = self.compiler.closureDataPop()
        b._code.append(entryLabel + ':')          
        b._code.append('; endBlock')
        return MessageOptionNone


    def forEachUnrolled(self, b, args):
        '''
            [ProtoSymbol register containerOffsetVar]
        '''
        protoSymbolLabel = args[0].toString()

        # Choice of genvar register...
        varGenRegister =  args[1]

        # The original var
        varData = args[2]
        if(varGenRegister == varData.loc.lid):
            self.compiler.error("genVar is the same register as dataVar. register:'{}'".format(varGenRegister))

        #NB no need for regCount

        # add a new environment
        #self.compiler.envAddClosure()
        self.compiler.scopeStackPush()

        # create the varGen
        # This needs to be registered at the start so parsing of the
        # susequent functions can reference the var from the 
        # environment.
        # As it happens, the loc will stay the same. The type is 
        # anything, maybe different for each unroll. It's set later.
        varGen = Var(
            protoSymbolLabel,
            Loc.RegisterX64(varGenRegister),
            Type.NoType
        )
        
        # important, varGen on the env
        # self.compiler.symbolSet(
            # protoSymbolLabel,
            # varGen
        # )
        self.compiler.symSet(var)

        #NB so far, similar
        
        #NB ignore loop setup
        
        # build
        #NB stripped
        b._code.append('; beginLoop')

        #NB ignore Alloc to varGen
        
        # push data
        self.compiler.closureDataPush((varGen, varData, varGenRegister))

        # Capture instructions until loop end
        self.compiler.instructionsStore()
        mo = MessageOptionNone
        return mo

        
    def forEachUnrolledEnd(self, b, args):
        '''
            []
        '''
        # The passed builder is the subbuilder. Ignore it.
        # Revert builders and 
        # get content data
        loopContents = self.compiler.instructionsGet()

        # get the data
        varGen, varData, varGenRegister = self.compiler.closureData.pop()

        #print(protoSymbolLabel)

        
        # build the loop
        for offset, elemTpe in varData.tpe.offsetIt():
            # change the varGen type, if necessary
            # The vargen is pushed to the env. Do we change the env, or replace?

            # create the vargen and set in the environment
            # this looks expensive. it probably is. It creates a new vargen,
            # despite the location not changing, for the sake of the type changing.
            # It then overwrites on the environment.
            # It's got stuff all to do with mutability. I don't like
            # poking the contents of a structure like env. 
            #??? cqant change here. Its lookg for it AS WE PARSE
            #?? so we must modify it, because thats the one the syntaxer found.
            #?? and we must set it first, or it will not be present
            varGen.tpe = elemTpe
            
            #self.compiler.envPrint()            
            #Alloc to varGen
            srcB = AccessValue(varData.loc)
            srcB.addOffset(offset)

            b._code.append("mov {}, {}".format(
                # shortcut. It's always a register, got to be the lid.
                varGen.loc.lid, 
                srcB.result()
            ))
            
            # replay instructions
            self.compiler.instructionsPlay(loopContents)
           
        b._code.append('; endLoop')
        
        # Dispose of the inner environment (goodbye varGen)
        #self.compiler.envDelClosure()
        self.compiler.scopeStackPop()
        return MessageOptionNone


                
    #? What about multiple calls together? Need to think over that
    #! then handle clutch data
    #???
    #For a clutch, we need the offset stored in *code output* someplace.
    #They can not be calculated from the root, unless unrolling.
    #Does that mean we unroll them all?
    #! lot of repetition with forRange()
    def forEach(self, b, args):
        '''
            [ProtoSymbol register containerOffsetVar],
        '''        
        #NB so what we are saying is, the generated variable is
        # assembled froma protosymbol and a reg. Is that so bad? No.
        # Onwards. 
        # We can't have the varData and the varGen both off-register 
        # because of the move. 
        # So
        # the varGen is in a register. Maybe not forever, but for 
        # now. 
        # So the DataVar is allowed to be anywhere. 
        # The counter and the varGen in seperate registers. They could 
        # be push/pulled, but that's tweaky.
        protoSymbolLabel = args[0].toString()

        # Choice of genvar register...
        varGenRegister =  args[1]
                
        # The original var
        varData = args[2]
        if(varGenRegister == 'rcx'):
            self.compiler.warning("Defence required, forEach uses 'rcx'")
        if(varGenRegister == varData.loc.lid):
            self.compiler.error("genVar is the same register as dataVar. register:'{}'".format(varGenRegister))
        
        # Choice of count register...
        countReg = 'rcx'

        # add a new environment
        #self.compiler.envAddClosure()
        self.compiler.scopeStackPush()

        # create the varGen
        # set on the new env
        #! Not going to work for clutches, as type changes
        # ...but would start type[0]...
        varGen = Var(
            protoSymbolLabel,
            Loc.RegisterX64(varGenRegister), 
            #! for a clutch
            #var.tpe.elementType[0]
            varData.tpe.elementType
        )
        # self.compiler.symbolSet(
            # protoSymbolLabel, 
            # varGen
        # )
        self.compiler.symSet(var)

        # loop start
        #! array
        step = varData.tpe.elementType.byteSize
        froom = -(step)
        until = varData.tpe.byteSize
        trueLabel = self.labelGenerate('forEachTrue')
        entryLabel = self.labelGenerate('forEachEP')
               
        # build
        b._code.append('; beginLoop')
        b._code.append("mov {}, {}".format(countReg, froom))  
        b._code.append("jmp {}".format(entryLabel))                
        b._code.append(trueLabel + ':') 

        # alloc to the varGen.
        #! this is crude. It should be generated from the vars. 
        # Especially, one could be on the stack (but not both).
        # The varData especially could be on the stack.
        # b._code.append("mov {}, [{} + {}]".format(
            # varGen.loc.lid, 
            # varData.loc.lid, 
            # countReg
        # ))
        #? compact generalisation of above
        srcB = AccessValue(varData.loc)
        srcB.addRegister(countReg)
        #print()
        b._code.append("mov {}, {}".format(
            varGen.loc.lid, 
            srcB.result()
        ))
        
        # push data
        self.compiler.closureDataPush((trueLabel, entryLabel, countReg, until, step))
        mo = MessageOptionNone
        return mo
        
    def forEachEnd(self, b, args):
        '''
            []
        '''
        # get the data
        trueLabel, entryLabel, countReg, until, step  = self.compiler.closureData.pop()

        # build the loop
        #! for an array
        b._code.append(entryLabel + ':') 
        b._code.append("add {}, {}".format(countReg, step)) 
        b._code.append("cmp {}, {}".format(countReg, until))        
        b._code.append("jl {}".format(trueLabel))  
        b._code.append('; endLoop')

        # Dispose of the inner environment too (goodbye varGen)
        #self.compiler.envDelClosure()
        self.compiler.scopeStackPop()
        return MessageOptionNone

        
        
    ## Printers
    def print(self, b, args):
        '''
            [strOrVarAny()]
        '''
        # We could print out using printf semantics....
        # No, print singly. figue out the slowness later.
        var = args[0]
        if isinstance(var, str):
            # It's a constant/atom/immediate/idFunc. Currently, we do 
            # nothing with the type, calling the special function 
            # constant() directly.
            #! I thought we could immediate, but I admit it makes no sense.
            # Try a C test
            # Like ROStringUTF8Define except no variable

            # need a label
            textLabel = self.labelGenerate('TextInternal')

            #! this is not a plain API. Just DefineStrEscapable()?
            # The difference here:
            # - String in backquotes, for C style string escaping.
            # The delimiting zero as C-type  string, though the encoding 
            # may have a say.
            rodata = textLabel + ": db `" + var + "`, 0"
            b.rodataAdd(rodata)
            self.printers.constant(b, textLabel)
        else:
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
                #print(str(var))
                # tpe, offset(lid)
                # tpe.offsetDeep(self, path)
                srcSnippet = AccessValue(var.loc).result()
                #NB if I moved to widechar for strlen() and the like,
                # I'd need to use a different format string.
                if (
                    tpe == Type.StrASCII
                    or tpe == Type.StrUTF8
                ):
                    # For a string, printf wants the address, not the value
                    srcSnippet = AccessAddress(var.loc).result()
                #print('snippet:')
                #print(str(srcSnippet))
                self.printers(b, tpe, srcSnippet)
        return MessageOptionNone
            
    def println(self, b, args):
        '''
            [strOrVarAny()]
        '''
        self.print(b, args)
        self.printers.newline(b)
        return MessageOptionNone
        
    def printFlush(self, b, args):
        self.printers.flush(b)
        return MessageOptionNone
