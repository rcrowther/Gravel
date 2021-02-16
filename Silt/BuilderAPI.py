import architecture
from LocationRoot import mkLocationRoot

class BuilderAPI():
    arch = None
    
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
class BuilderAPI64(BuilderAPI):
    arch = architecture.architectureSolve(architecture.x64)

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
        
    #def __init___():
    #    builderAPI = architecture.architectureSolve(architecture.x64)

    # def stringRODefine(self, b, string):
        # rodata = label + ': db "' + string + '", 0'
        # b.rodataAdd(rodata)
        # return LocationRootROData(label)

    # def stringHeapDefine(self, b, stackIndex, string):
        # '''
        # Allocate and define a malloced string
        # UTF-8
        # '''
        # byteSize = byteSize(elemByteSize) * size
        # b._code.append("mov {}, {}".format(cParameterRegister[0], byteSize))
        # b._code.append("call malloc")
        # return LocationRootRegister('rax')        

    def sysExit(self, b, args):    
        b._code.append("mov rax, 60")
        b._code.append("mov rdi, " + str(args[0]))
        b._code.append("syscall")

        
    #! account for data types
    # and align
    def stackAlloc(self, b, args):
        byteSize = args[0] * self.arch['bytesize']
        b._code.append("sub rsp, {}".format(byteSize)) 

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
