
def architectureSolve(architecture):
    architecture['bytesize'] = architecture['bitsize'] >> 3
    return architecture
    
x64 = {
    # bitsize of the architecture
    'bitsize' : 64,
    "ASMName" : 'qword',
    'registers' : [
        "rax", 
        "rbx",
        "rcx",
        "rdx",
        "rbp",
        "rsi",
        "rdi",
        "rsp",
        "r8",
        "r9",
        "r10",
        "r11",
        "r12",
        "r13",
        "r14",
        "r15",
    ],    
    # remove stack pointer and base stack registers.
    # In the future this may rewquire hints an weighing, for specialist
    # registers
    'generalPurposeRegisters' : [
        "rax", 
        "rbx",
        "rcx",
        "rdx",
        #"rbp",
        "rsi",
        "rdi",
        #"rsp",
        "r8",
        "r9",
        "r10",
        "r11",
        "r12",
        "r13",
        "r14",
        "r15",
    ],
    'stackPointer': 'rsp',
    'stackBasePointer' : 'rbp',
    #   %ebp, %ebx, %edi and %esi must be preserved   
    # clobbers r10, r11 and any parameter registers 
    #! stack must be balanced
    'cParameterRegisters' : [
        "rdi", "rsi", "rdx", "rcx", "r8", "r9"
    ],
    'cParameterFloatRegisters' : [
        "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5", "xmm6"
    ],
    'returnRegister' : 'rax',

}
