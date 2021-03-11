import architecture
#x
#from tpl_LocationRoot import LocationRootRODataX64, LocationRootRegisterX64, LocationRootStackX64
#x
#import tpl_locationRoot as LocRoot
from tpl_Printers import PrintX64
import tpl_vars as Var
import tpl_types as Type
from asm_db import TypesToASMAbv, TypesToASMName

#? dont like this import
from Syntaxer import ProtoSymbol


class BuilderAPI():
    '''
    A base for building code.
    Mostly this is a builder for machine code instructions. This is
    the base. Subclasses will target an architecture.
    Mostly, it is functions that take a builder followed by a generic
    'args' parameter.
    Some builder funcs return data. This is so 
    compilers/interpreters recieve data to store in environments,
    either for symbol registration or block closure. These functions 
    must be registered in the (architecture-specific) functions
    mustPushData, mmustSetData, isGlobalData etc.
    '''
    # NB arg checking would not be done here. This assumes args are
    # correct, it is just a builder
    arch = None
    
    # Anchor for a seperate API for printing 
    printers = None

    # def error(self, msg):
        # raise NotImplementedError('error not implemented on this API')
    # def warning(self, msg):
        # raise NotImplementedError('error not implemented on this API')
    # def info(self, msg):
        # raise NotImplementedError('error not implemented on this API')
        
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
        
        ## Allocs
        'ROStringDefine': [ProtoSymbol, str],
        'RODefine': [ProtoSymbol, int, Type.Type],
        'regDefine': [ProtoSymbol, str, int, Type.Type],
        'heapAllocBytes': [ProtoSymbol, int],
        'heapAlloc': [ProtoSymbol, Type.Type],
        'stackAllocBytes': [ProtoSymbol, int],
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

    # Yuck. Total yuck. Preferably, this data would be on the method as 
    # an assert. But that means passing spurious information like
    # position---for the error---and oassing the error method in from 
    # the compiler.
    # Data gathering from a method is possible in Python, there are 
    # decorators and so forth, which are pythonic, so we avoid that.
    # Inheritance would avoid this, but seems a small reason to generate
    # potentially many specialised compintler classes, vrs. a setup by 
    # parameter 

    def isGlobalData(self, name):
        return name in [
            'ROStringDefine',
        ] 
        
    def mustPushData(self, name):
        return name in [
            'registersPush',
            'registersVolatilePush',
            'if',
            'while',
        ]
        
    def mustPopData(self, name):
        return name in [
            'registersPop',
            'registersVolatilePop',
            'ifEnd',
            'whileEnd',
        ]

    def mustSetData(self, name):
        return name in [
            'ROStringDefine',
            'RODefine',
            #'stringHeapDefine',
            'stackAlloc',
            'regDefine',
            'heapAlloc',
            #'varHeap',
            #'varStack',
        ]

    def mustGetData(self, name):
        return name in [
        ]

    #def stack
    #    self.stackSize = 0
                
    #def __init___():
    #    builderAPI = architecture.architectureSolve(architecture.x64)

####
    ## basics
    def comment(self, b, args):
        b._code.append("; " + args[0])
        
    def sysExit(self, b, args):    
        b._code.append("mov rax, 60")
        b._code.append("mov rdi, " + str(args[0]))
        b._code.append("syscall")



    def extern(self, b, args):
        '''
        Append an extern.
        '''
        b.externsAdd("extern " + args[0])
        
    def raw(self, b, args):
        '''
        Append a line of code.
        '''
        b._code.append(args[0])
        


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

    def frameEnd(self, b, args):
        '''
        End a stack frame.
        '''
        # mov rsp, rbp
        b._code.append("mov {}, {}".format(self.arch['stackPointer'], self.arch['stackBasePointer']))
        # pop pop rbp
        b._code.append("pop {}".format(self.arch['stackBasePointer']))
           
           
    def func(self, b, args):
        '''
        Start a function.
        '''
        b._code.append('{}:'.format(args[0].toString()))
        b._code.append('; beginFunc')

        
    #def funcSetReturn(b, locationRoot):
    #    locationRoot.toRegister(self.arch['returnRegister'])

    # If these end frames, do they need to end frame inside?
    # If so, offer the frame option at begin, also?
    def funcEnd(self, b, args):
        '''
        End a function with return.
        '''
        b._code.append('ret')
        b._code.append('; endFunc')

    def funcMain(self, b, args):
        self.func(b, [ProtoSymbol('@main')])
        
    def funcMainEnd(self, b, args):
        b._code.append('; endFunc')



    ## Register utilities
    # #! needs datapush
    def registersPush(self, b, args):
        registerList = args
        for r in registerList:
            b._code.append('push ' + r)
        return registerList

    def registersPop(self, b, popData, args):
        for r in reversed(popData):
            b._code.append('pop ' + r)

    def registersVolatilePush(self, b, args):
        '''
        Protect the volatile registers 
        i.e. those used for parameter passing.
        '''
        return self.registersPush(b, self.arch['cParameterRegisters'].copy())

    #?x
    #def registersVolatilePop(self, b, popData, args):
    #    self.registersPop(b, popData, args)



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
        return (
            protoSymbolLabel, 
            #Var.ROX64(protoSymbolLabel, tpe)
            Var.ROX64Either(protoSymbolLabel, tpe)
        )

    def ROStringDefine(self, b, args):
        '''
        Define a numeruc string to a label
            protoSymbol, string
        '''
        protoSymbolLabel = args[0].toString()
        string = args[1]
        rodata = protoSymbolLabel + ': db "' + args[1] + '", 0'
        b.rodataAdd(rodata)
        return (
            protoSymbolLabel, 
            Var.ROX64(protoSymbolLabel, Type.StrASCII)
        )                
   

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
            # TypesToASMName[tpe],
            register, 
            data
        ))
        return (
            protoSymbolLabel, 
            #Var.RegX64(register, tpe)
            Var.RegX64Either(register, tpe)
        )
                        
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
        return (
            protoSymbolLabel, 
            #Var.RegX64(self.arch['returnRegister'], tpe)
            Var.RegX64Either(self.arch['returnRegister'], tpe)
        ) 
        
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
        #return LocationRootRegisterX64(self.arch['returnRegister']) 
        return (
            protoSymbolLabel, 
            #Var.RegAddrX64(self.arch['returnRegister'], tpe)
            Var.RegAddrX64Either(self.arch['returnRegister'], tpe)
        ) 

    #! account for data types
    # and align
    def stackAllocBytes(self, b, args):
        '''
        Allocate stack storage
            protoSymbol, slotIndex
        '''
        protoSymbolLabel = args[0].toString()
        byteSize = self.arch['bytesize'] * args[1]
        b._code.append("sub rsp, {}".format(byteSize)) 
        index = args[1]
        return (
            protoSymbolLabel, 
            #Var.StackX64(index, Type.StrASCII)
            Var.StackX64Either(index, Type.StrASCII)
        ) 
        
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
            protoSymbol, slotIndex, type
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
        return (
            protoSymbolLabel, 
            #Var.StackX64(index, tpe)
            Var.StackX64Either(index, tpe)
        ) 
                        
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
        var = args[0]
        val = args[1]
        if (isinstance(var, Var.ROX64)):
            raise ValueError('cant set a RO variable!')
        #! would only work for singular types. 
        # Also, variable doesn't know if it's a pointer, or value
        #print(str(type(var.tpe))) 
        b._code.append("mov {} {}, {}".format(TypesToASMName[var.tpe], var.toCodeValue(), val))
        
            
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
            # we got to do something recursive with it
            # printStr(b, tpe.name, StrASCII)
            # printStr(b, ['(' StrASCII])
            # print(b, tpe.foreach(args => print(b, [args])))
            # printStr(b, [')' StrASCII])
            raise NotImplementedError()
            # etc.
        else:
            # Figure out what will print or not
            #var.accessMk()
            #var.accessDeepMk(path)
            # tpe, offset(lid)
            # tpe.offsetDeep(self, path)
            srcSnippet = var.toCodeValue()
            #! Obviously, very temproary!
            # What we need is probably something that separates string 
            # types from numbers
            #print(str(tpe))
            if (tpe == Type.StrASCII):
                # For a string, printf wants the address, not the value
                srcSnippet = var.toCodeAddress()
            print('snippet:')
            print(str(srcSnippet))
            self.printers(b, tpe, srcSnippet)
            

    # def println(self, b, args):
        # self.printers(b, args[0], args[1])
        # self.printers.newline(b)

    def println(self, b, args):
        '''
        var
        '''
        self.print(b, args)
        self.printers.newline(b)
        
    def printFlush(self, b, args):
        self.printers.flush(b)
