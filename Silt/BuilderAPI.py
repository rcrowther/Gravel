import architecture
from syn_arg_tests import *
import math


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


#? Issues arrising
#- X What is PIC code?
#- Autostore must renew and stack stack allocation?
#- X Can ops like mov and sub accept double relaative adresses? If not, 
# what's the strategy?
#? lesser issues
#- X Full bytesize reporting
#- args reporting position
#- better code capture  
#- How to test for small numbers in a non-arch way?
#- Howto handle larger than arch numbers
#- What if a var is redefined? does it transfr type? If this a case that
# concerns me much? (setting data seems more critical)

#! Ok, we have an issue
# most data is on a pointer. Stack (effectively), heap, and labels 
# (when used for large types). However,
#- labels used for small types
#- registers used for small types
#- if we introduce small direct memory types (unlikely)
# all use data directly. If we move pointer data location to registers 
# then back
# is it's pointer preserved?
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
        'funcMainEnd': [intVal()],

        ## Register utilities
        'registersPush': [argListVal()],
        'registersVolatilePush': [],
        'registersPop': [],

        ## var action
        'set': [anyVar(), intOrVarNumeric()],
        'setPath': [anyVar(), Path, intVal()],
        'setPriority': [anyVar(), intVal()], 
        'delete': [anyVar()],
        
        ## Arithmetic
        'dec' : [numericVar()],
        'inc' : [numericVar()],
        #? should be int or float. Anyway...
        #? Should be more verbose
        #! and it's freer than these parameters define. Memory locations
        # are ok for destination too.
        # but not teo memory locs together
        'add' : [intOrVarNumeric(), intOrVarNumeric()],
        'sub' : [intOrVarNumeric(), intOrVarNumeric()],
        'mul' : [intOrVarNumeric(), intOrVarNumeric()],
        #'divi' : [intOrVarNumeric(), intOrVarNumeric()],
        #'div' : [intOrVarNumeric(), intOrVarNumeric()],
        'shl' : [numericVar(), intVal()],
        'shr' : [numericVar(), intVal()],
        
        ## Allocs
        'RODefine': [protoSymbolVal(), intVal(), anyType()],
        'ROStringDefine': [protoSymbolVal(), strVal()],
        'ROStringUTF8Define': [protoSymbolVal(), strVal()],
        'regDefine': [protoSymbolVal(), intOrVarNumeric(), numericType()],
        'regNamedDefine': [protoSymbolVal(), strVal(), intOrVarNumeric(), anyType()],
        'heapAlloc': [protoSymbolVal(), anyType()],
        'heapSet': [anyVar(), aggregateAny()],
        'heapStringDefine': [protoSymbolVal(), strVal()],     
        'heapBytesAlloc': [protoSymbolVal(), intVal()],
        'stackAllocSlots':  [intVal()],   
        'stackAlloc': [protoSymbolVal(), anyType()],
        'stackSet' : [anyVar(), aggregateAny()],
        'stackStringDefine': [protoSymbolVal(), strVal()],
        'stackBytesAlloc': [protoSymbolVal(), intVal()],

        #'stackDefine': [protoSymbolVal(), intVal(), anyType()],

        ## Conditional
        'ifRangeStart': [intOrVarNumeric(), intOrVarNumeric(), intOrVarNumeric()],
        'ifRangeEnd':[],
        'ifStart': [booleanFuncVal()],
        'ifEnd': [],
        'cmp': [anyVar(), booleanFuncVal()],
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

    # handles all var creation.update(location), delete
    # arch, sizeSlots, offset
    autoStore = AutoStoreX64(arch, 3, 1)

    def alignedSize16(self, byteSize):
        '''
        A number of bytes aligned to 2 byte boundaries
        So bytesize 1 returns 2, 2 returns 2, 3 returns 4, 4 returns 4,
        5 returns 6...
        For x64 assembluy, aligning the stack to 16bits is a call 
        convention. A stack without this alignment cannot call C or, 
        usually, exit.
        return 
            a bytesize rounded up to 2 byte/16bit boundaries
        '''
        return (math.ceil(byteSize/2) << 1)
        

    ## Arg handlers
    def varValueSnippet(self, var):
        '''
        Return accesss snippet for a variable value.
        Can't handle offsets or registers, but s useful func.
        usual args: strVal intVal, regVar 
        intOrVarNumeric strOrVarStr strOrVarAny
        stringVar etc.
        '''
        # var set of new or existing var
        # var access for single ops like 
        # - dec (no constants), 
        # - shift (only var and const)
        # - zero
        # We do use acces value api. For example, it may be a stack
        # offset location.
        return AccessValue(var.loc).result()

    def litOrVarValueSnippet(self, varOrConstant):
        '''
        Return access snippet for a literal/variable value.
        Can't handle offsets or registers, but s useful func.
        Usually args: anyVar intOrVarNumeric
        '''
        if (not(isinstance(varOrConstant, Var))):
            # its a constant
            return str(varOrConstant)
        else:
            return AccessValue(varOrConstant.loc).result()

    def regEnsure(self, b, var):
        '''
        Ensure a variable is on a register.
        This ensures register operations such as relative addressing or
        arithmetic can be performed.
        '''
        self.autoStore.toRegAny(b, var)

    def oneRegEnsure(self, b, litOrVarDst, litOrVarSrc):
        '''
        Ensure one of a pair of variable values is on a register.
        This ensures relative addressing does not appear as source and 
        destination on an op.
        If both of the args are off-register variables, one is moved 
        onto a register (the other can use relative addressing).
        For simplicity, both args can be literals. If either are, then
        the var, on or off register, will not be moved.
        '''
        # if both are vars and both are not on registers...
        if (
            isinstance(litOrVarDst, Var)
            and isinstance(litOrVarSrc, Var)
            and (not(
                isinstance(litOrVarDst.loc, Loc.LocationRegister)
                and isinstance(litOrVarSrc.loc, Loc.LocationRegister)
            ))):
                # One needs to go on a register. check prioritiies,
                # if similar, prefer the destination on the register
                if (litOrVarSrc.priority > litOrVarDst.priority):
                    self.autoStore.toRegAny(b, litOrVarSrc)
                else:
                    self.autoStore.toRegAny(b, litOrVarDst)

    #? Humm. Crossplatform build func
    def _extern(self, b, label):
        '''
        Append an extern.
        '''
        b.externsAdd("extern " + label)
        
    ## basics
    def comment(self, b, args):
        b._code.append("; " + args[0].value)
        return MessageOptionNone

    def _sysExit(self, b, exitCode):    
        b._code.append("mov rax, 60")
        b._code.append("mov rdi, " + exitCode)
        b._code.append("syscall")
        
    def sysExit(self, b, args):    
        b._code.append("mov rax, 60")
        exitCode = str(args[0].value)
        self._sysExit(b, exitCode)
        return MessageOptionNone

    def extern(self, b, args):
        '''
        Append an extern.
        '''
        b.externsAdd("extern " + args[0].value)
        return MessageOptionNone
        
    def raw(self, b, args):
        '''
        Append a line of code.
        '''
        b._code.append(args[0].value)
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
           
    def _func(self, b, protoSymbolLabel):
        b._code.append('{}:'.format(protoSymbolLabel))
        b._code.append('; beginFunc')
        self.compiler.scopeStackPush()
                
    #! symbol needs registering in globalenv
    def func(self, b, args):
        '''
        Start a function.
        '''
        protoSymbolLabel = args[0].value.toString()
        #print(protoSymbolLabel)
        self._func(b, protoSymbolLabel)
        return MessageOptionNone

        
    #def funcSetReturn(b, locationRoot):
    #    locationRoot.toRegister(self.arch['returnRegister'])

    # If these end frames, do they need to end frame inside?
    # If so, offer the frame option at begin, also?
    def funcEnd(self, b, args):
        '''
        End a function with ''ret' operand.
        '''
        self.autoStore.deleteAll([])
        self.compiler.scopeStackPop()
        b._code.append('ret')
        b._code.append('; endFunc')
        return MessageOptionNone

    def funcMain(self, b, args):
        self._func(b, 'main')
        return MessageOptionNone
        
    def funcMainEnd(self, b, args):
        '''
        Writes sysExit
            exitCode
            [intVal()]
        '''
        self.compiler.scopeStackPop()
        self._sysExit(b, str(args[0].value))
        b._code.append('; endFunc')
        return MessageOptionNone



    ## Register utilities
    def _registersPush(self, b, registerList):
        for r in registerList:
            b._code.append('push ' + r)
        self.compiler.closureDataPush(registerList)
        
    #! arg error pointer in wrong position
    def registersPush(self, b, args):
        '''
        Push registers.
            list of registers
            [argList]
        '''
        registerList = args[0].value
        
        # test list will not unbalance stack
        if (len(registerList) & 1):            
            self.compiler.warningWithPos(
                args[0].position,
                "Uneven number of pushes will unbalance the stack"
            )
            
        # test registers exist
        for regStr in registerList:
            if (not(regStr in self.arch['generalPurposeRegisters'])):
                self.compiler.errorWithPos(
                    args[0].position,
                    f"Register not recognised. register:'{regStr}'"
                )
        self._registersPush(b, registerList)
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
        self._registersPush(
            b,
            ArgList(self.arch['cParameterRegisters'].copy()),
        )
        return MessageOptionNone



    ## Alloc, set and define
    #? several possibilities here
    # def/alloc
    #- numbers
    #- containers
    #? Maybe containers/numbers together
    #- strings
    #- maybe UTF8
    # ...to
    #- RO
    #- register
    #- stack
    # rather a lot....

    ### RO Global
    #! sting/numeric could be joined?
    #! could be any numeric vla, including variables
    #! type cannot be container, or can it?
    #! tesst size
    #! no containers, how to define contents?
    def RODefine(self, b, args):
        '''
        Define a number to a label
             [protoSymbolVal(), intVal(), anyType()]
        '''
        protoSymbolLabel = args[0].value.toString()
        data = args[1].value
        tpe = args[2].value
        var = self.autoStore.varROCreate(
            protoSymbolLabel, 
            tpe, 
            1
        )
        #! check size limits?
        rodata = '{}: {} {}'.format(
            protoSymbolLabel,
            TypesToASMAbv[tpe],
            data
        )
        b.rodataAdd(rodata)
        self.compiler.symbolSetGlobal(var) 
        return MessageOptionNone

    def ROStringDefine(self, b, args):
        '''
        Define a byte-width string to a label
            [protoSymbolVal(), strVal()]
        '''
        protoSymbolLabel = args[0].value.toString()
        string = args[1].value
        var = self.autoStore.varROCreate(
            protoSymbolLabel, 
            Type.StrASCII,
            1
        )    
            
        # Trailing zero, though I believe NASM pads to align anyway
        rodata = protoSymbolLabel + ': db "' + string + '", 0'
        b.rodataAdd(rodata)       
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
        protoSymbolLabel = args[0].value.toString()
        string = args[1].value
        var = self.autoStore.varROCreate(
            protoSymbolLabel, 
            Type.StrUTF8,
            1
        )
        rodata = protoSymbolLabel + ": db `" + string + "`, 0"
        b.rodataAdd(rodata)
        self.compiler.symbolSetGlobal(var) 
        return MessageOptionNone


    ### register
    # For sure a number

    #! size test
    #! shouldn't this transfer the type, if destination is a var
    #! a general define is possible for heap, bit registers
    def regDefine(self, b, args):
        '''
        Define a variable with a numeric value.
        The value will usually go to a register but, if registers are 
        full, it will go to stack.
            var number type
            [protoSymbolVal(), intOrVarNumeric(), numericType()]
        '''
        protoSymbolLabel = args[0].value.toString()
        value = args[1].value
        tpe = args[2].value
        var = self.autoStore.varRegMaybeCreate(b, 
            protoSymbolLabel, 
            tpe, 
            1
        )
        b._code.append("mov {}, {}".format(
            #TypesToASMName[tpe],
            self.varValueSnippet(var),
            self.litOrVarValueSnippet(value),
        ))
        self.compiler.symSet(var)
        return MessageOptionNone

    #! test size
    def regNamedDefine(self, b, args):
        '''
        Define a value in a named register
        A speciality for debugging and tests, not intended for common 
        use.
            protoSymbol, registerName, intOrVarNumeric, type
            [protoSymbolVal(), strVal(), intOrVarNumeric(), anyType()]
         '''
        protoSymbolLabel = args[0].value.toString()
        register = args[1].value
        varOrConst = args[2].value
        tpe = args[3]
        var = self.autoStore.varRegCreate(b, 
            protoSymbolLabel, 
            register, 
            tpe, 
            1
        )
        b._code.append("mov {}, {}".format(
            #TypesToASMName[tpe],
            self.varValueSnippet(var),
            self.litOrVarValueSnippet(varOrConst),
        ))
        self.compiler.symSet(var)
        return MessageOptionNone
        
                        
    ### heap
    def heapAlloc(self, b, args):
        '''
        Alloc space for a type on the heap.
            varName type
            [protoSymbolVal(), anyType()]
        '''
        self._extern(b, 'malloc')
        protoSymbolLabel = args[0].value.toString()
        tpe = args[1].value

        # create a regVar for the pointer
        var = self.autoStore.varRegAddrCreate(b, 
            protoSymbolLabel, 
            self.arch['returnRegister'],
            tpe,
            1
        )        

        # allocate the size
        b._code.append("mov {}, {}".format(
            self.arch['cParameterRegisters'][0], 
            tpe.byteSize
        ))
        b._code.append("call malloc")

        # set the var on the context
        self.compiler.symSet(var)
        return MessageOptionNone

    #! worst recursion ever
    #! fixes
    #- need to limit ASMWord
    # def _literalAggregateTestRec(self, mo, tpe, literalAggregate):
        # #print("_literalAggregateTestRec")
        # #print(str(literalAggregate))
        # #print(str(mo))
        # #print(str(tpe))
        # #print(str(type(literalAggregate)))
        # # print(str(tpe))        
        # if (isinstance(tpe, Type.TypeInt)):
            # if (not(isinstance(literalAggregate, int))):
                # mo[0] = MessageOption.error(f'Type expects int. Found:{literalAggregate}')
                # #self.compiler.errorWithPos(
                # #    f'Type expects int. Found:{literalAggregate}'
                # #)
        # elif (isinstance(tpe, Type.TypeFloat)):
            # if (not(isinstance(literalAggregate, float))):
                # mo[0] = MessageOption.error(f'Type expects float. Found:{literalAggregate}')
        # elif (isinstance(tpe, Type.TypeString)):
            # if (not(isinstance(literalAggregate, str))):
                # mo[0] = MessageOption.error(f'Type expects string. Found:{literalAggregate}')

        # #! labeled not an existing attribute or subtype
        # # elif (isinstance(tpe, Type.Labeled)):
            # # if (not(isinstance(literalAggregate, KeyValue))):
                # # return MessageOption.error(f'Type expects key ~> value. Found:{literalAggregate}')
            
            # # #! error on key not available
            # # elemTpe = tpe.offsetTypePair[1]
            # # mo = self._literalAggregateTestRec(elemTpe, literalAggregate.value)
        # elif (isinstance(tpe, Type.TypeContainerOffset)):
            # if (not(isinstance(literalAggregate, AggregateVals))):
                # mo[0] = MessageOption.error(f'Type expects array of vals. Found:{literalAggregate}')
            # elif (literalAggregate[0] == '*'):
                # if (not(isinstance(tpe, Type.Array))):
                    # mo[0] = MessageOption.error(f'Repeat mark must referr to Array. Found:{tpe}')
                # else:
                    # #i syntaxer doesn't catch too few arguments
                    # if (len(literalAggregate) != 2):
                        # mo[0] = MessageOption.error(f'Repeat mark must be followed by one arg.')
                    # else:
                        # self._literalAggregateTestRec(
                            # mo,
                            # tpe.elementType,
                            # literalAggregate[1]
                        # )
            # elif (tpe.size != len(literalAggregate)):
                # mo[0] = MessageOption.error(f'LiteralAggregate size not match Type size. typeSize:{tpe.size}')
            # else:
                # i = 0
                # for offset, elemTpe in tpe.offsetIt():
                    # self._literalAggregateTestRec(
                        # mo,
                        # elemTpe, 
                        # literalAggregate[i]
                    # )
                    
                    # # if error in an element, abandon testing
                    # if (mo[0].notOk()):            
                        # break
                    # i += 1
        # else:
            # #i should never get here. It's a catch
            # mo[0] = MessageOption.warning(f"Type not recognised.  Found:{literalAggregate}, tpe:{tpe}")

    def _literalAggregateTestRec(self, tpe, literalAggregate):
        #print("_literalAggregateTestRec")
        #print(str(literalAggregate))
        #print(str(mo))
        #print(str(tpe))
        #print(str(type(literalAggregate)))
        # print(str(tpe))  
              
        if (isinstance(tpe, Type.TypeInt)):
            if (not(isinstance(literalAggregate, int))):
                self.compiler.errorWithPos(
                    literalAggregate.position,
                    f'Type expects int. Found:{literalAggregate}'
                )
        elif (isinstance(tpe, Type.TypeFloat)):
            if (not(isinstance(literalAggregate, float))):
                self.compiler.errorWithPos(
                    literalAggregate.position,
                    f'Type expects float. Found:{literalAggregate}'
                )
        elif (isinstance(tpe, Type.TypeString)):
            if (not(isinstance(literalAggregate, str))):
                self.compiler.errorWithPos(
                    literalAggregate.position,
                    f'Type expects string. Found:{literalAggregate}'
                )
        #! labeled not an existing attribute or subtype
        # elif (isinstance(tpe, Type.Labeled)):
            # if (not(isinstance(literalAggregate, KeyValue))):
                # return MessageOption.error(f'Type expects key ~> value. Found:{literalAggregate}')
            
            # #! error on key not available
            # elemTpe = tpe.offsetTypePair[1]
            # mo = self._literalAggregateTestRec(elemTpe, literalAggregate.value)
        elif (isinstance(tpe, Type.TypeContainerOffset)):
            if (not(isinstance(literalAggregate, AggregateVals))):
                self.compiler.errorWithPos(
                    literalAggregate.position,
                    f'Type expects array of vals. Found:{literalAggregate}'
                )
            elif (literalAggregate[0] == '*'):
                if (not(isinstance(tpe, Type.Array))):
                    self.compiler.errorWithPos(
                        literalAggregate[9].position,
                        f'Repeat mark must referr to Array. Found:{tpe}'
                    )
                else:
                    #i syntaxer doesn't catch too few arguments
                    if (len(literalAggregate) != 2):
                        self.compiler.errorWithPos(
                            literalAggregate.position,
                            'Repeat mark must be followed by one arg.'
                        )
                    else:
                        self._literalAggregateTestRec(
                            tpe.elementType,
                            literalAggregate[1]
                        )
            elif (tpe.size != len(literalAggregate)):
                self.compiler.errorWithPos(
                    literalAggregate.position,
                    f'LiteralAggregate size not match Type size. typeSize:{tpe.size}'
                )
            else:
                i = 0
                for offset, elemTpe in tpe.offsetIt():
                    r = self._literalAggregateTestRec(
                        elemTpe, 
                        literalAggregate[i]
                    )
                    i += 1
        else:
            #i should never get here. It's a catch
            self.compiler.errorWithPos(
                literalAggregate.position,
                f"Type not recognised.  Found:{literalAggregate}, tpe:{tpe}"
            )
            

    def _literalAggregateTest(self, tpe, literalAggregate):
        '''
        Test a literal agreegate against a type.
        This will report an error if the the size or structure of the 
        aggregate does not match the given type.
        It also reports if the types of the elements in the aggregate
        do not match those in the type. It does not test for boundaries
        and encoding, but it does test for the classes as seen by the 
        lexer, which are int, float, and string.
        return
            a MessageOption
        '''
        #i This list is just to make the messageOption a reference. So 
        # it can be updated in place. Not Pynthonic...
        # isLiteralVal)
        self._literalAggregateTestRec(tpe, literalAggregate)
        return MessageOptionNone
        
    # import BuilderAPI
    # import tpl_types as Type
    # from tpl_codeBuilder import Builder
    # api = BuilderAPI.BuilderAPIX64()
    # b = Builder()
    # dataRoot = 'rax'
    # tpe = Type.Bit64
    # literalAggregate = 33
    # tpe = Type.Array([Type.Bit64, 3])
    # literalAggregate = [33, 77, 99]
    # api._literalAggregateSet(b, dataRoot, tpe, literalAggregate)
    # b._code
    def _literalAggregateSetRec(self, b, dataRoot, offset, tpe, literalAggregate):
        if (isinstance(tpe, Type.TypeNumeric) or isinstance(tpe, Type.TypeString)):
            # aggregate is singular literal
            b._code.append("mov {} [{}+{}], {}".format(
                #! needs refinement, this
                'dword',
                dataRoot, 
                offset,
                literalAggregate
            ))
        elif (isinstance(tpe, Type.TypeContainerOffset)):
            if (literalAggregate[0] == '*'):
                #? undry
                i = 0
                for elemOff, elemTpe in tpe.offsetIt():
                    self._literalAggregateSetRec(
                        b,
                        dataRoot,
                        offset + elemOff,
                        elemTpe, 
                        literalAggregate[1]
                    )
                    i += 1                  
            else:
                # aggregate is [a, b, c....]
                #? undry
                i = 0
                for elemOff, elemTpe in tpe.offsetIt():
                    self._literalAggregateSetRec(
                        b,
                        dataRoot,
                        offset + elemOff,
                        elemTpe, 
                        literalAggregate[i]
                    )
                    i += 1       

    def _literalAggregateSet(self, b, dataRoot, tpe, literalAggregate):
        self._literalAggregateSetRec(b, dataRoot, 0, tpe, literalAggregate)

    # scala
    # a2: Array[Int] = Array(3, 6, 9)
    # Ada
    # https://learn.adacore.com/courses/intro-to-ada/chapters/more_about_types.html#aggregates
    # Lisp
    #(setq avector [1 two '(three) "four" [five]])
    # I guess we need something like
    # [[a, b, c,] [d, e, f]]
    def heapSet(self, b, args):
        '''
        Set data on a heap alloc.
            varName literalAggregate
            [anyVar(), aggregateAny()]
        '''
        var = args[0].value
        literalAggregate = args[1].value 
        mo = MessageOptionNone
        
        # By definition, RO is not possible
        if (var.loc.isReadOnly):
            mo = MessageOption.error('Cant set a RO variable!')

        # test the aggregate value against the type
        mo = self._literalAggregateTest(
            var.tpe, 
            literalAggregate
        )

        #i reg ensure, or relative addressing will fail 
        self.regEnsure(b, var)

        # Define contents
        if (mo.isOk()):            
            self._literalAggregateSet(
                b, 
                var.loc.lid,
                var.tpe, 
                literalAggregate
            )             
        return mo
        
    #! U can do lots better than this R.C.
    def _bytesToNumber(self, b, byteArray, bytesInNumber, func):
        size = len(byteArray)
        limit = bytesInNumber
        i = 0
        j = 0
        number = 0
        step = 0
        buff = bytearray(bytesInNumber)
        while (i < size):
            if (j >= limit):
                func(b, i - bytesInNumber, int.from_bytes(buff, 'little'))
                j = 0
                number = 0
            buff[j] = byteArray[i]
            j += 1
            i += 1
            
        # remainder
        if (j):
            func(b, (i - j), int.from_bytes(buff[0:j], 'little'))

    def _returnRegOffsetMove(self, b, offset, value):
        b._code.append("mov {} [{}+{}], {}".format(
            'dword',
            self.arch['returnRegister'],
            offset, 
            value
        ))              

    def _bytesToNumberWrite(self, b, pointerRegister, byteArray, bytesInNumber):
        size = len(byteArray)
        limit = bytesInNumber
        i = 0
        j = 0
        number = 0
        step = 0
        buff = bytearray(bytesInNumber)
        while (i < size):
            if (j >= limit):
                b._code.append("mov {} [{}+{}], {}".format(
                    'dword',
                    pointerRegister,
                    i - bytesInNumber, 
                    int.from_bytes(buff, 'little')
                )) 
                j = 0
                number = 0
            buff[j] = byteArray[i]
            j += 1
            i += 1
            
        # remainder
        if (j):
            b._code.append("mov {} [{}+{}], {}".format(
                'dword',
                pointerRegister,
                i - j, 
                int.from_bytes(buff[0:j], 'little')
            )) 

                
    #)
    def heapStringDefine(self, b, args):
        '''
        Define a byte-width string to heap.
        Uses malloc.
            varName string
            [protoSymbolVal(), strVal()]
        '''
        self._extern(b, 'malloc')
        protoSymbolLabel = args[0].value.toString()
        string = args[1].value
        
        # add string terminator now
        string += '\0'
        mo = MessageOptionNone
        #if not string.isascii():
        if False:
            mo = MessageOption.error(f'String is not ascii. string:{string}')
        else:
            asciiStr = string.encode("ascii")
            byteSize = len(asciiStr)

            # create a regVar for the pointer
            var = self.autoStore.varRegAddrCreate(
                b,
                protoSymbolLabel, 
                self.arch['returnRegister'],
                Type.StrASCII,
                1
            )

            # allocate the size
            b._code.append("mov {}, {}".format(
                self.arch['cParameterRegisters'][0], 
                byteSize
            ))
            b._code.append("call malloc")

            # convert string to numbers then write down
            #? why only a dword?
            #???
            self._bytesToNumber(
                b,
                asciiStr, 
                #? Humm. The 64Bit bussize is often 32Bit  
                #self.arch['bytesize'],
                4,
                self._returnRegOffsetMove
            )

            # set the var on the context
            self.compiler.symSet(var)
        return mo
        
    ## Unicode?
    # No I think what this might be about is not, how to creat a UTF 
    # string But more, what will our string handling be like?
    # Note the import utypes
    # https://unicode-org.github.io/icu-docs/apidoc/released/icu4c/utypes_8h.html
    # def heapStringUtf8Define(self, b, args):
        # '''
        # Alloc space for a type on the heap
            # [protoSymbolVal(), strVal()]
        # '''
        # protoSymbolLabel = args[0].value.toString()
        # string = args[1].value
        
        # self.extern(b, ['utypes'])

        # self.raw(b, ['; UTF here'])
        # # temp, until figure stringlen
        # var = self.regNamedDefine( b, [args[0], 20])
        
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

    def heapBytesAlloc(self, b, args):
        '''
        Allocate bytes on heap.
        Uses Malloc.
            var size
            [protoSymbolVal(), intVal()]
        '''
        #? Should that be number of slots, not raw bytes?
        self._extern(b, 'malloc')
        protoSymbolLabel = args[0].value.toString()
        size = args[1].value
        tpe = Type.Array([Type.Bit8, size])

        # create a regVar for the pointer
        var = self.autoStore.varRegAddrCreate(b, 
            protoSymbolLabel, 
            self.arch['returnRegister'],
            tpe,
            1
        )
        
        # allocate the size
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], size))
        b._code.append("call malloc")

        # set the var on the context
        self.compiler.symSet(var)
        return MessageOptionNone
             
             
                    
    ## Stack
    # Do we need a MaybeReg define? Or is that, varDefine?
    #! Deep issue: 
    # The coder sets a size by stackAllocSlots.
    # But that's irrelevant to autostore. Autostore hard-sets
    # its stack allocation.
    # To be effective
    # Autostores must be created/removed with scopes. 
    # Or at frame changes (which are not always scopes?)
    # Or the stack part of autostore should be replacable.
    def stackAllocSlots(self, b, args):
        '''
        Allocate stack storage for autostore.
        Resets the stack pointer register e.g. 'esp' etc. 
        The space is calculated from the index and bitsize, and is an
        absolute distance from the base pointer.
        The main (only?) use of this function is to allocate storage for
        use by autostore. So there is no var associated with this 
        function.
        args
            [slotCount]
            [intVal()]
        '''
        slotCount = args[0].value
        b._code.append("lea {}, [rbp - {}]".format(
            self.arch['stackPointer'],
            self.arch['bytesize'] * slotCount 
        ))         

        # a warning...
        msg = MessageOptionNone
        if (slotCount & 1):
            # i.e. not a count divisable by 2
            # Slots are busWidth. But in this architecture and 
            # by convention, stack must be aligned to double busWidth, or
            # calls will fail. This is a general allocation, so it seems
            # reasonable to request it results in an aligned stack.
            # Issue a warning. 
            msg = MessageOption.warning("API: SlotCount not divisible by 2. Calls in this frame will fail. slotCount: '{}'".format(
                slotCount
            ))
        return msg

        
    #! bad thing here, we don't know where stack starts, so only works 
    # on empty stackframe
    # If we use base pointer, we have issues. 
    # - We usually need 
    # to allocate some space for autostore vatrs, so we are not going
    # to start at xBP, but an offset from it.
    # - stack needs to be aligned (which heap disguises)
    # - using an offset value is sad. It's a valuable relative address 
    # argument reduction. And it means inconsistency with heap
    # - The xSP moves! in response to anything
    # I figure we have a few tactics,
    # - Store offset from the base pointer
    # : rock solid root, but auto allocations must be the first in the 
    # chain. Any manual allocations before that, xSP will be off. Also,
    # doesn't really know about autoStore allocation
    # - Store offset from the stack pointer
    # : if auto-allocation used, manual allocation disallowed, because
    # xSP must not be used. However, will work on top of autoStore
    # - Store an absolute address to stack (from xSP, like heap's absolute address return)
    # : rock solid root. Unaffected by other allocations. Unaffected by 
    # autoStore. But register spill creates a strange effect, a later
    # ''get' from a pointer spilled from a register must restore the 
    # pointer to a register by offset from the spill-space 
    # (on stack!), then access. That means an extra move. 
    # (
    # It also means a whole new set of stack processing, alongside
    # existing slot provision 
    # )
    # On the whole, I prefer version three all-round. It's the most
    # obvious, and allows manual stack tinkering. 
    def stackAlloc(self, b, args):
        '''
        Allocate space for a type on the stack.
        Like a heap allocation, returns a pointer to the stack. Works 
        from the stack pointer, not stackbase pointer. So
        is unaffected by state of the stack, manual adjustments etc.
            varName type
            [protoSymbol, anyType]
        '''
        protoSymbolLabel = args[0].value.toString()
        tpe = args[1].value

        # create a regVar for the pointer
        var = self.autoStore.varRegAnyAddrCreate(b, 
            protoSymbolLabel, 
            tpe,
            1
        ) 
        
        # allocate the size
        #! x64 this appears to be in bits, not bytes
        #i needs to be 2 byte aligned
        b._code.append("sub rsp, {}".format(
             self.alignedSize16(tpe.byteSize) << 3
        )) 

        # move the new address into the reg
        #i by doing this after the allocation, data is added by positive 
        # offsets into the newly allocated space
        #! do we go up stack or down? What does printf use, for example?
        b._code.append("mov {}, rsp".format(
             var.loc.lid
        ))
        
        # set the var on the context
        self.compiler.symSet(var)
        return MessageOptionNone

    #i why alloc and set what can in assembler be defined? Because a 
    # simple bitwidth numeric can be defined easily, but not a complex
    # data
    #! currently exactly the same as heapSet
    def stackSet(self, b, args):
        '''
        Set data on a stack alloc.
            varName literalAggregate
            [anyVar(), aggregateAny()]
        '''
        var = args[0].value
        literalAggregate = args[1].value 
        mo = MessageOptionNone
        
        # By definition, RO is not possible
        if (var.loc.isReadOnly):
            mo = MessageOption.error('Cant set a RO variable!')

        # test the aggregate value against the type
        mo = self._literalAggregateTest(
            var.tpe, 
            literalAggregate
        )

        #i reg ensure, or relative addressing will fail 
        self.regEnsure(b, var)

        # Define contents
        if (mo.isOk()):            
            self._literalAggregateSet(
                b, 
                var.loc.lid,
                var.tpe, 
                literalAggregate
            )             
        return mo

    #! somewhat limited. Since the dst is a relative address, con not 
    # use a relative address i.e. var as source
    # Or could we detect for a two-step process, so we can use vars too?
    # if var, move to reg
    # mov slot, valOrReg
    #? Currenttly looks very generalised, so would work for reg too?
    # def stackDefine(self, b, args):
        # '''
        # Alllocate a value to the stack.
        # Auto-allocated, the return ver knows the location.
        # Assumes space has been allocated on the stack.
            # [protoSymbolVal(), intVal(), anyType()]
        # '''
        # protoSymbolLabel = args[0].value.toString()
        # val = args[1].value
        # tpe = args[2].value

        # var = self.autoStore.varStackCreate(
            # protoSymbolLabel, 
            # tpe,
            # 1
         # )    

        # b._code.append("mov {} {}, {}".format(
            # TypesToASMName[var.tpe], 
            # self.varValueSnippet(var),
            # val
        # )) 
        # self.compiler.symSet(var)
        # return MessageOptionNone

    #)
    def stackStringDefine(self, b, args):
        '''
        Define a byte-width string to stack.
        Like a heap allocation, returns a pointer to the stack. Works 
        from the stack pointer, not stackbase pointer. So
        is unaffected by state of the stack, manual adjustments etc.
            varName string
            [protoSymbolVal(), strVal()]
        '''
        protoSymbolLabel = args[0].value.toString()
        string = args[1].value

        # add string terminator now
        string += '\0'
        mo = MessageOptionNone
        
        #if not string.isascii():
        if False:
            mo = MessageOption.error(f'String is not ascii. string:{string}')
        else:
            asciiStr = string.encode("ascii")
            byteSize = len(asciiStr)

            # create a regVar for the pointer
            var = self.autoStore.varRegAnyAddrCreate(b, 
                protoSymbolLabel, 
                Type.StrASCII,
                1
            ) 

            # allocate the size
            #! x64 this appears to be in bits, not bytes
            #i needs to be 2 byte aligned
            b._code.append("sub rsp, {}".format(
                 self.alignedSize16(byteSize) << 3
            )) 

            # move the new address into the reg
            #i by doing this after the allocation, data is added by positive 
            # offsets into the newly allocated space
            b._code.append("mov {}, rsp".format(
                 var.loc.lid
            ))
            
            # convert string to numbers then write down
            #? why only a dword?
            #???
            self. _bytesToNumberWrite(
                b, 
                var.loc.lid, 
                asciiStr, 
                #? Humm. The 64Bit bussize is often 32Bit  
                #self.arch['bytesize'],
                4
            )

            # set the var on the context
            self.compiler.symSet(var)
        return mo
        
    #! account for data types
    # and align
    # Unnecessary?
    # Look, one would allocate by type, one by bytes. But there
    # is some question wether bytes are needed anyhow?
    # May be better looking at fullBytes in types.
    def stackBytesAlloc(self, b, args):
        '''
        Allocate bytes on stack.
        Like a heap allocation, returns a pointer to the stack. Works 
        from the stack pointer, not stackbase pointer. So
        is unaffected by state of the stack, manual adjustments etc.
            protoSymbol, size
            [protoSymbolVal(), intVal()]
        '''
        protoSymbolLabel = args[0].value.toString()
        size = args[1].value
        tpe = Type.Array([Type.Bit8, size])
        
        # create a regVar for the pointer
        var = self.autoStore.varRegAnyAddrCreate(b, 
            protoSymbolLabel, 
            tpe,
            1
        ) 

        # allocate the size
        #! x64 this appears to be in bits, not bytes
        #i needs to be 2 byte aligned
        b._code.append("sub rsp, {}".format(
             self.alignedSize16(tpe.byteSize) << 3
        )) 
        
        # move the new address into the reg
        #i by doing this after the allocation, data is added by positive 
        # offsets into the newly allocated space
        #! do we go up stack or down? What does printf use, for example?
        b._code.append("mov {}, rsp".format(
             var.loc.lid
        ))
        
        # set the var on the context
        self.compiler.symSet(var)
        return MessageOptionNone
                    

    ## Var actions
    def set(self, b, args):
        '''
        Set a var to a value
            [Var, valOrVarInt],
            [anyVar(), intOrVarNumeric()]
        '''
        var = args[0].value
        valOrVarInt = args[1].value
        mo = MessageOptionNone
        
        # By definition, RO is not possible
        if (var.loc.isReadOnly):
            mo = MessageOption.error('Cant set a RO variable!')

        # Needs a path for deeper peeks
        if (not(isinstance(var.tpe, Type.TypeSingular))):
            mo = MessageOption.error('Need path to set on complex type? var:{}'.format(var))

        # if two vars, get one onto register
        self.oneRegEnsure(b, var, valOrVarInt)
            
        # Only if ok (could throw errors)
        if (mo.isOk()):
            b._code.append("mov {} {}, {}".format(
                TypesToASMName[var.tpe], 
                self.varValueSnippet(var),
                self.litOrVarValueSnippet(valOrVarInt)
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
        var = args[0].value
        path = args[1].value
        val = args[2].value
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

    def setPriority(self, b, args):
        '''
        Set the priority on a var.
            var value
            [anyVar(), intVal()]
        '''
        var = args[0].value
        priority = args[1].value
        var.priority = priority
        return MessageOptionNone        
        
    def delete(self, b, args):
        '''
        Define a variable with a value.
        The value will usually go to a register but, if registers are 
        full. it will go to stack.
            var
            [protoSymbolVal()],
        '''
        var = args[0].value
        self.autoStore.delete(
            var,
        )
        # No need to remove from wnv, attempts to use throw errors.
        return MessageOptionNone        

    ## arithmetic
    #! if we go unsigned, we need to extend these
    #! We need something works as var or val?
    #? Will need widths?
    def dec(self, b, args):
        '''
        [numericVar()]
        '''
        # Yes works with relative addresses
        var = args[0].value
        b._code.append("dec {} {}".format(
            TypesToASMName[var.tpe],
            self.varValueSnippet(var)
        ))      
        return MessageOptionNone

    def inc(self, b, args):
        '''
        [anyVar()]
        '''
        var = args[0].value
        b._code.append("inc {} {}".format(
            TypesToASMName[var.tpe],
            self.varValueSnippet(var)
        ))       
        return MessageOptionNone
        
        #! and it's freer than these parameters define. Memory locations
        # are ok for destination too.
        # but not two memory locs together
    #? should work signed
    #! can be anyyVar
    def add(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        varDst = args[0].value
        litOrVarSrc = args[1].value

        # if two vars, get one onto register
        self.oneRegEnsure(b, varDst, litOrVarSrc)
        b._code.append("add {} {}, {}".format(
            TypesToASMName[varDst.tpe],
            self.varValueSnippet(varDst),
            self.litOrVarValueSnippet(litOrVarSrc)
        ))       
        return MessageOptionNone
        
    def sub(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        varDst = args[0].value
        litOrVarSrc = args[1].value

        # if two vars, get one onto register
        self.oneRegEnsure(b, varDst, litOrVarSrc)
        b._code.append("sub {} {}, {}".format(
            TypesToASMName[varDst.tpe],
            self.varValueSnippet(varDst),
            self.litOrVarValueSnippet(litOrVarSrc)
        ))    
        return MessageOptionNone
        
    def mul(self, b, args):
        '''
        [regVar(), intOrVarNumeric()]
        '''
        # imul
        # https://www.felixcloutier.com/x86/imul
        varDst = args[0].value
        litOrVarSrc = args[1].value

        # if two vars, get one onto register
        self.oneRegEnsure(b, varDst, litOrVarSrc)
        b._code.append("imul {} {}, {}".format(
            TypesToASMName[varDst.tpe],
            self.varValueSnippet(varDst),
            self.litOrVarValueSnippet(litOrVarSrc)
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

    #! can accept anyVar, intLitOrVar arg
    def shr(self, b, args):
        '''
        [regVar(), intVal()]
        '''
        varDst = args[0].value
        litOrVarSrc = args[1].value
        
        # Keep numerics down
        if (
            not(isinstance(litOrVarSrc, Var)) 
            and (litOrVarSrc > self.arch['bytesize'] - 1)
        ):
            self.compiler.warning('Shiftsize too large for arch. Will compile, but not do as intended. size:{}'.format(
                litOrVarSrc
            ))
            
        # if two vars, get one onto register
        self.oneRegEnsure(b, varDst, litOrVarSrc)
        b._code.append("shr {} {}, {}".format(
            TypesToASMName[varDst.tpe],
            self.varValueSnippet(varDst),
            self.litOrVarValueSnippet(litOrVarSrc)
        ))       
        return MessageOptionNone

    #! can accept anyVar, intLitOrVar arg
    def shl(self, b, args):
        '''
        [regVar(), intVal()]
        '''
        varDst = args[0].value
        litOrVarSrc = args[1].value
        
         # Keep numerics down
        if (
            not(isinstance(litOrVarSrc, Var)) 
            and (litOrVarSrc > self.arch['bytesize'] - 1)
        ):
            self.compiler.warning('Shiftsize too large for arch. Will compile, but not do as intended. size:{}'.format(
                litOrVarSrc
            ))
     
        # if two vars, get one onto register
        self.oneRegEnsure(b, varDst, litOrVarSrc)
        b._code.append("shl {} {}, {}".format(
            TypesToASMName[varDst.tpe],
            self.varValueSnippet(varDst),
            self.litOrVarValueSnippet(litOrVarSrc)
        ))  
        return MessageOptionNone




    ### compare/if

    def ifRangeStart(self, b, args):
        '''
        Conditionally test between two numbers.
        Cantt test the variables so allows messing about. Underneath,
        the test is lessThan | GreaterThanEquals.
        var
            to test
        from
            the number to start on
        until
            advances until before this number
            [intOrVarNumeric(), intOrVarNumeric(), intOrVarNumeric()],
        '''
        #NB Range can't be tested, as it may be vars.
        # but both range numbers can be off-register, as the tests are 
        # seperate.
        var = args[0].value
        froom = args[1].value
        to = args[2].value
        falseLabel = self.labelGenerate('ifRangeFalse')
        accessSnippet = self.litOrVarValueSnippet(var)
        fromSnippet = self.litOrVarValueSnippet(froom)
        toSnippet = self.litOrVarValueSnippet(to)
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
            #! can comp operate with relative addresses on both sides?
            self.oneRegEnsure(b, logicTree.args[0], logicTree.args[1])
            arg0 = self.litOrVarValueSnippet(logicTree.args[0])
            arg1 = self.litOrVarValueSnippet(logicTree.args[1])
            b._code.append("cmp {}, {}".format(arg0, arg1))            
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
        #NB for now, has a scope too. Controversial
        boolLogic = args[0].value
        
        # Now need some boolean logic to get us there...
        falseLabel = self.labelGenerate('ifFalse')
        trueLabel = self.labelGenerate('ifTrue')
        self.logicBuilder(b, boolLogic, trueLabel, falseLabel)
        
        # Put the true label at block start
        b._code.append(trueLabel + ':')        
        b._code.append('; beginBlock')        
        self.compiler.closureDataPush(falseLabel)
        self.compiler.scopeStackPush()
        return MessageOptionNone
                
    def ifEnd(self, b, args):
        # Put the false label at block end
        falseLabel = self.compiler.closureDataPop()
        b._code.append('; endBlock')
        b._code.append(falseLabel + ':')        
        self.compiler.scopeStackPop()
        return MessageOptionNone

    def _toReG(self):
        '''
        Force a var to reg
        This is sometimes useful to turn anyReg into a variable that
        can be used effectively in 
        '''
        pass

    def _varZero(self, b, var):
        '''
        Set a var to zero
        This ibuilds various kinds of code, depends on the var.
        But avoids moving the var location.
        Can throw an error
        '''
        mo = MessageOptionNone
        #if (var.isReadOnly):
        #    mo = MessageOption.error(f'Read-only. var:{var}')
            
        if (isinstance(var.loc, Loc.LocationRegister)):
            b._code.append('xor {}, {}'.format(
                var.loc.lid,
                var.loc.lid
            ))        
        else:
            b._code.append('mov {}, 0'.format(
                self.varValueSnippet(var)
            ))
        return mo
            
    # Like an if
    # This has the problem we need a Boolean type, probably.
    # And to go with it, a compare flag location.
    # Presumably should make the var to bool?
    # how do we cast and allocate to bool?
    # Howsoever, it is working
    def cmp(self, b, args):
        '''
        Move a comparison result to a var
            [anyVar(), booleanFuncVal()]
        '''
        #! insist targetVar is a varReg
        # ZF is what we want Flag -> reg
        targetVar = args[0].value
        booleanFunc = args[1].value

        # zero the targetVar
        # b._code.append('xor {}, {}'.format(
            # targetVar.loc.lid,
            # targetVar.loc.lid
        # ))
        mo = self._varZero(b, targetVar)
        
        # Now need some boolean logic to get us a result...
        falseLabel = self.labelGenerate('ifFalse')
        trueLabel = self.labelGenerate('ifTrue')
        self.logicBuilder(b, booleanFunc, trueLabel, falseLabel)
        
        # Put the true label at block start
        b._code.append(trueLabel + ':')        
        b._code.append('; beginBlock') 

        # if true, set targetVar to one
        b._code.append('mov {}, 1'.format(
            self.varValueSnippet(targetVar)
        ))
                    
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
        varCondition = args[0].value
        
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
        whenIndex = args[0].value
        self.compiler.closureDataPush(
            whenIndex
        )   
        
        # Capture instructions until when end
        self.compiler.instructionsStore()

        # Create an environment
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
        reg = args[0].value
        froom = args[1].value
        
        # this can now be a numeric variable, so needs resolving
        to = args[2].value
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
        boolLogic = args[0].value
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
        protoSymbolLabel = args[0].value.toString()

        # Choice of genvar register...
        varGenRegister =  args[1].value

        # The original var
        varData = args[2].value
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
                #varGen.loc.lid, 
                self.varValueSnippet(varGen),
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
        protoSymbolLabel = args[0].value.toString()

        # Choice of genvar register...
        varGenRegister =  args[1].value
                
        # The original var
        varData = args[2].value
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
            #varGen.loc.lid, 
            self.varValueSnippet(varGen),
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
        var = args[0].value
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
