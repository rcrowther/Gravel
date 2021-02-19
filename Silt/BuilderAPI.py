import architecture
from tpl_LocationRoot import LocationRootRODataX64, LocationRootRegisterX64
from tpl_Printers import PrintX64


class BuilderAPI():
    arch = None
    printers = None
    
    def byteSize(self, bitsize):
        return bitsize >> 3

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

    #!!! Python specific code turns this class into an imitation of a
    # map of func pointers. Probably what is needed is a map of func 
    # pointers (but thatt is not templatable). 
    def __contains__(self, k):
        return k in dir(self)
            
    def __getitem__(self, name):
        return getattr(self, name)



#! needs inherit arch
class BuilderAPIX64(BuilderAPI):
    arch = architecture.architectureSolve(architecture.x64)
    printers = PrintX64()

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
            'stringRODefine',
            'stringHeapDefine'
        ]

    def isGlobalData(self, name):
        return name in [
            'stringRODefine',
        ] 
               
    def mustGetData(self, name):
        return name in [
        ]
                
    #def __init___():
    #    builderAPI = architecture.architectureSolve(architecture.x64)

       

    def sysExit(self, b, args):    
        b._code.append("mov rax, 60")
        b._code.append("mov rdi, " + str(args[0]))
        b._code.append("syscall")

        
    #! account for data types
    # and align
    def stackAlloc(self, b, args):
        byteSize = args[0] * self.arch['bytesize']
        b._code.append("sub rsp, {}".format(byteSize)) 

    def comment(self, b, args):
        b._code.append("; " + args[0])
        
    def frame(self, b, args):
        '''
        Start a stack frame.
        '''
        # push rbp
        b._code.append("push {}".format(self.arch['stackBasePointer']))
        # mov rbp, rsp
        b._code.append("mov {}, {}".format(self.arch['stackBasePointer'], self.arch['stackPointer']))

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
        b._code.append('{}:'.format(args[0]))
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
        self.func(b, ['main'])
        
    def funcMainEnd(self, b, args):
        b._code.append('; endFunc')

    def stringRODefine(self, b, args):
        label = args[0]
        rodata = label + ': db "' + args[1] + '", 0'
        b.rodataAdd(rodata)
        return (label, LocationRootRODataX64(label))

    def stringHeapAlloc(self, b, args):
        '''
        Malloc string space
        Bytesize API
        '''
        self.extern(b, ['malloc'])
        #! but malloc works in bytes?
        byteSize = self.arch['bytesize'] * args[0]
        b._code.append("mov {}, {}".format(self.arch['cParameterRegisters'][0], byteSize))
        b._code.append("call malloc")
        return LocationRootRegisterX64(self.arch['returnRegister']) 
        
    # def stringHeapDefine(self, b, args):
        # '''
        # Allocate and define a malloced string
        # UTF-8
        # '''
        # byteSize = self.byteSize() * size
        # b._code.append("mov {}, {}".format(arch['cParameterRegister'][0], byteSize))
        # b._code.append("call malloc")
        # return LocationRootRegisterX64('rax') 
                
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
    def registersVolatilePop(self, b, popData, args):
        self.registersPop(b, popData, args)


    def print(self, b, args):
        self.printers(b, args[0], args[1])

    def println(self, b, args):
        self.printers(b, args[0], args[1])
        self.printers.newline(b)

    def printFlush(self, b, args):
        self.printers.flush(b)
