import architecture
from syn_arg_tests import *



import tpl_locationRoot as Loc
from tpl_Printers import PrintX64
import tpl_vars as Var
import tpl_types as Type
from asm_db import TypesToASMAbv, TypesToASMName

#? dont like this imports. They're for arg types though.
from Syntaxer import ProtoSymbol, Path, FuncBoolean
from tpl_either import MessageOption, MessageOptionNone

# Humm. Build addresses here, not in locs?
from tpl_address_builder import AddressBuilder

from tpl_label_generators import LabelGen


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
    # funcNameToArgsType = {
        # # basics
        # 'comment': [str],
        # 'sysExit': [int],
        # 'extern': [str],
        # 'raw': [str],
        
        # ## Code structure 
        # 'frame': [],
        # 'frameEnd': [],
        # 'func': [ProtoSymbol],
        # 'funcEnd': [],
        # 'funcMain': [],
        # 'funcMainEnd': [],

        # ## Register utilities
        # 'registersPush': [list],
        # 'registersVolatilePush': [],
        # 'registersPop': [],

        # ## var action
        # 'set': [Var.Base, int],
        # #!? Path should be a Type. Probably
        # 'setPath':  [Var.Base, Path, int],
        # 'forEachRoll' : [ProtoSymbol, Var.Base],
        # 'forEachRollEnd': [],
        # 'forEach': [ProtoSymbol, Var.Base],
        # 'forEachEnd': [],
        
        # ## Arithmetic
        # #'dec' : [Var.Base],
        # #'inc' : [Var.Base],
        # #? should be int or float. Anyway...
        # 'add' : [Var.Base, int],
        # 'sub' : [Var.Base, int],
        # 'mul' : [Var.Base, int],
        # 'divi' : [Var.Base, int],
        # 'div' : [Var.Base, int],
        
        # ## Allocs
        # 'ROStringDefine': [ProtoSymbol, str],
        # 'RODefine': [ProtoSymbol, int, Type.Type],
        # 'regDefine': [ProtoSymbol, str, int, Type.Type],
        # 'heapAllocBytes': [ProtoSymbol, int],
        # 'heapAlloc': [ProtoSymbol, Type.Type],
        # 'stackAllocBytes': [ProtoSymbol, int, int],
        # 'stackAlloc': [ProtoSymbol, int, Type.Type],

        # ## boolean
        # 'cmp': [Var.Base, FuncBoolean],
        # 'ifStart': [FuncBoolean],
        # 'ifEnd': [],
        
        # ## loops
        # 'forRange': [str, int, int],
        # 'forRangeEnd': [],
        # 'whileStart': [FuncBoolean],
        # 'whileEnd': [],
        
        # ## printers
        # 'print' : [Var.Base],
        # 'println': [Var.Base],
        # 'printFlush': [],
    # #'': [].
    # }
    
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
        #'dec' : [anyVar()],
        #'inc' : [anyVar()],
        #? should be int or float. Anyway...
        'add' : [anyVar(), intVal()],
        'sub' : [anyVar(), intVal()],
        'mul' : [anyVar(), intVal()],
        'divi' : [anyVar(), intVal()],
        'div' : [anyVar(), intVal()],
        
        ## Allocs
        'ROStringDefine': [protoSymbolVal(), strVal()],
        'RODefine': [protoSymbolVal(), intVal(), anyType()],
        'regDefine': [protoSymbolVal(), strVal(), intVal(), anyType()],
        'heapAllocBytes': [protoSymbolVal(), intVal()],
        'heapAlloc': [protoSymbolVal(), anyType()],
        'stackAllocBytes': [protoSymbolVal(), intVal(), intVal()],
        'stackAlloc': [protoSymbolVal(), intVal(), anyType()],

        ## boolean
        'cmp': [anyVar(), booleanFuncVal()],
        'ifStart': [booleanFuncVal()],
        'ifEnd': [],
        
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
        'print' : [anyVar()],
        'println': [anyVar()],
        'printFlush': [],
    #'': [].
    }    

            
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
            #Var.ROX64(protoSymbolLabel, tpe)
            Var.Var(
                LocRoot.RODataX64(protoSymbolLabel),
                tpe
            )
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
        var = Var.Var(Loc.RODataX64(protoSymbolLabel), Type.StrASCII)
        self.compiler.symbolSetGlobal(
            protoSymbolLabel, 
            var
        )            
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
        var = Var.Var(
            Loc.RegisterX64(register), 
            tpe
        )
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            var
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
        var = Var.Var(
            Loc.RegisterX64(self.arch['returnRegister'],), 
            Type.StrASCII
        )
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            var
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
        var = Var.Var(
            Loc.RegisterX64(self.arch['returnRegister']), 
            tpe
        )
        #print('huh?')
        #print(str(tpe))
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            var
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

        # No, it has no ''Type', hence the Loc return above
        #? really? this a Location, not a var
        var = Var.Var(
            Loc.StackX64(index),
            #??? 
            Type.StrASCII
        )
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            var
        )

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
        var = Var,Var(index, tpe)
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            var
        )
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
    #! We need something works as var or val?
    #? Will need widths?
    def dec(self, b, args):
        var = args[0]
        b._code.append("dec {}".format(var))      
        return MessageOptionNone

    def inc(self, b, args):
        var = args[0]
        b._code.append("inc {}".format(var))       
        return MessageOptionNone
        
    #def add(self, b, args):

    #def sub(self, b, args):

    #def mult(self, b, args):

    #def divi(self, b, args):

    #def div(self, b, args):



    ### compare/if
    # This has the problem we need a Boolean type, probably.
    # And to go with it, a compare flag location.
    def cmp(self, b, args):
        var = args[0]
        var = args[0]
        booleanFunc = args[1]
        #print(str(booleanFunc))
        mo = MessageOptionNone
        # need two registers?? one for comparision,  current reesult?
        p1 = 'var???'
        p2 = 'constant' 
        b._code.append("cmp {}, {}".format(
            p1,
            p2,
        ))     
        funcName = booleanFunc.name
        p2 = '[label]'
        b._code.append("j{}, {}".format(
            funcName,
            p2,
        ))         
        return mo

            
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

    from tpl_address_builder import AddressBuilder

    def buildDataCode(self, val):
        if (not(isinstance(val, Var.Var))):
            # its a constant
            return val
        else:
            return var.loc.value()
            
            
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
            b._code.append("cmp {}, {}".format(logicTree.args[0], logicTree.args[1]))
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
        '''
        boolLogic = args[0]
        #??? Now need some booleana logic to get us there...
        #b._code.append("cmp rax, 4")        
        falseLabel = self.labelGenerate('ifFalse')
        trueLabel = self.labelGenerate('ifTrue')
        #jumpLogic = "jne"
        #b._code.append(jumpLogic + " " + falseLabel)
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
        b._code.append('; endBlock')
        b._code.append(falseLabel + ':')        
        return MessageOptionNone
        
        
        
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
        '''
        # From a given numeric point to a given numeric point. Beats a 
        # for...next loop, no probs...
        #? needs to step (ugly, optional var time. Is there another 
        # way if things are that awkward?)
        #! What about until? Humm. This is a feature of 'to' loops
        # they behave weird at 1 to 1 type rigs.
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



        
        # rolled would look like
    # a loop...
    # loopLabel = 
    #innerCode = 
    # b._code.append(':' + loopLabel)
    # b._code.append(innerCode)
    # b._code.append('dec rcx')
    # b._code.append('cmp rcx, 0')
    # b._code.append('jgtzo loopLabel')
     
     
    def forEachUnrolled(self, b, args):
        '''
            [ProtoSymbol containerOffsetVar],
        '''
        innerVar = args[0]
        var = args[1]

        # Set up the new builder
        b._code.append('; beginLoop')

        self.compiler.builderNew()
        mo = MessageOptionNone
        return mo

        
    def forEachUnrolledEnd(self, b, args):
        '''
            []
        '''
        # The passed builder is the subbuilder
        innerCode = b.result()

        
        # Make tha builder revertion explicit by setting 'b' to the 
        # previous builder
        b = self.compiler.b        

        # Revert builders in the compiler
        self.compiler.builderOld()

        #! for an aeeay 
        #??? fix offsets good
        for offset, tpe in var.tpe.offsetIt():
            b._code.append("mov {}, [{} + {}]".format(register, lid, offset))
            # add the innercode
            b.addAll(innerCode)            
        b._code.append('; endForEach')
        return MessageOptionNone

    #? is register really our input?
    #! problems with register clobbering
    #? protection round calls, but not automatic, what about multiple 
    # calls together? Need to think over that
    #! Weve got three vars kicking about here. Need to make this clear,
    # - original data root
    # - counter
    # - [;ace for results
    #! then handle clutch data
    #! lot or repetition with forRange()
    def forEach(self, b, args):
        '''
            [ProtoSymbol register containerOffsetVar],
        '''        
        # InnerVar name...
        protoSymbolLabel = args[0].toString()

        # Choice of count register...
        #! tmp for now
        register =  args[1]
        
        # Choice of innervar register...
        genVarRegister = 'r12'
                
        # The original var
        var = args[2]

        # add a new environment
        self.compiler.envAddClosure()

        # create the new generated innervar
        # set on the new env
        #! Not going to work for clutches, as type changes
        # ...but would be type[0]...
        genVar = Var.Var(
            Loc.RegisterX64(genVarRegister), 
            #! for a clutch
            #var.tpe.elementType[0]
            var.tpe.elementType
        )
        self.compiler.symbolSetClosure(
            protoSymbolLabel, 
            genVar
        )

        # loop start
        #! array
        step = var.tpe.elementType.byteSize
        froom = -(step)
        until = var.tpe.byteSize
        trueLabel = self.labelGenerate('forEachTrue')
        entryLabel = self.labelGenerate('forEachEP')
               
        # build
        b._code.append('; beginLoop')
        b._code.append("mov {}, {}".format(register, froom))  
        b._code.append("jmp {}".format(entryLabel))                
        b._code.append(trueLabel + ':') 

        # alloc to the genvar. Ah, that means we need a counter AND
        # a genVar place. I'd overlooked that....!
        b._code.append("mov {}, [{} + {}]".format(genVarRegister, var.loc.lid, register)) 
        
        # push data
        self.compiler.closureDataPush((trueLabel, entryLabel, register, until, step))
        mo = MessageOptionNone
        return mo
        
    def forEachEnd(self, b, args):
        '''
            []
        '''
        # get the data
        trueLabel, entryLabel, register, until, step  = self.compiler.closureData.pop()

        # build the loop
        #! for an array
        b._code.append(entryLabel + ':') 
        b._code.append("add {}, {}".format(register, step)) 
        b._code.append("cmp {}, {}".format(register, until))        
        b._code.append("jl {}".format(trueLabel))  
        b._code.append('; endLoop')

        # Dispose of the inner environment too (and rid of innervar)
        self.compiler.envDelClosure()
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
            #print(str(var))
            # tpe, offset(lid)
            # tpe.offsetDeep(self, path)
            srcSnippet = var.loc.value()
            #! Obviously, very temproary!
            # What we need is probably something that separates string 
            # types from numbers
            #print(str(tpe))
            if (tpe == Type.StrASCII):
                # For a string, printf wants the address, not the value
                srcSnippet = var.loc.address()
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
