

import sys

#? # block is an anylength parameter. 
#? Need a 'print'

registerEnumerate = [
"rax", 
"rbx",
"rcx",
"rdx",
"rbp",
"rsi",
"rdi"
"rsp",
]


# So far, proving very hard human compilation 
# Try using NASM? Cross check?
# opCode -> (opcodeTemplate, width of 1st param, width of 2nd param...)
# 	81 		0 					L 	ADD 	r/m16/32/64 	imm16/32
Opcodes = {
# Storage
#! think used references accidentally, not literals?
1 : ('8b1c25{}', 4), #"mov'  {}'ebx', {}'lit"
2 : ('8b0425{}', 4), #"mov'  {}'eax', {}'lit"
#3 : ('488b0425{}', 4), #"mov'  {}'rax', {}'lit"
3 : ('B8{}', 4), #"mov'  {}'rax', {}'lit"
4 : ('488b1c25{}', 4), #"mov'  {}'rbx', {}'lit"
5 : ('488b0c25{}', 4), #"mov'  {}'rcx', {}'lit"
6 : ('488b1425{}', 4), #"mov'  {}'rdx', {}'lit"
7 : ('488b3425{}', 4), #"mov'  {}'rsi', {}'lit"
#8 : ('488b3c25{}', 4), #"mov'  {}'rdi', {}'lit"
8 : ('bf{}', 4), #"mov'  {}'rdi', {}'lit"
9 : ('488b2425{}', 4), #"mov'  {}'rsp', {}'lit"

# arithmetic
20 : ('48030425{}', 4), # add, 64, rax, lit 
21 : ('48031c25{}', 4), # add, 64, rbx, lit 
22 : ('48030c25{}', 4), # add, 64, rcx, lit 
23 : ('48031425{}', 4), # add, 64, rdx, lit 
24 : ('48033425{}', 4), # add, 64, rsi, lit 
25 : ('48033c25{}', 4), # add, 64, rdi, lit 

30 : ('482b0425{}', 4), # sub, 64, rax, lit 
31 : ('480faf0425{}', 4), # imul, 64, rax, lit 
#32 : ('4805{}', 6), # idiv, 64, rax, lit 
33 : ('48ffc0'), # inc rax
34 : ('48ffc8'), # dec rax

# Logic
40 : ('48230425', 4), # and, 64, rax, lit 
41 : ('480b0425', 4), # or, 64, rax, lit 
42 : ('48330425', 4), # xor, 64, rax, lit 
43 : ('48f7d0'), # not, 64, rax

# Type conversion

# Object manipulation

# stack manipulation
50 : ('58',), # pop rax
51 : ('50',), # push rax

# control transfer
# That's annoying, could use a simple calculation; len(block)
#? block is an anylength parameter. 
60 : ('483b0425{}75{}', 4, 1, '?'), # if0, cmp, block.size, block
61 : ('483b0425{}75{}eb{}{}', 4, 1, '?', '?'), # if0else, cmp, block1.size + 2 (for jmp), block1, block2.size, block2

# method calling
62 : ('{}c3e8{}', '?', 4), # simple call, body, method offset 
63 : ('c3',), #"ret"
64 : ('0f05',), # syscall (complex, needs rax for number, exit status in rdi)

    
# Snippets
100 : ('B801000000BF0100000048BE{}BA050000000F05', 8),  # print num, addr
101 : ('B801000000BF0100000048BE{}BA0E0000000F05', 4), # print str, addr
102 : ('{}', 4), # println str, addr
103 : ('{}', 4), # println str, addr
}

# opCode -> (opcodeTemplate, width of 1st param, width of 2nd param...)

OpcodeSnippets = {
 # if0, cmp, block.size, block
1 : lambda args: '483b0425{}75{}{}'.format(arg[0].ljust(8, '0'), len(arg[1]), arg[1]),
}

def builderToBytes(b):
    c = ''.join(b)
    c = bytearray.fromhex(c)
    return c #c.encode()


def buildSimpleOpcode(b, code, args):
    opcodeData = Opcodes[code]
        
    # test the count
    parameterCount = len(opcodeData) - 1
    #print(parameterCount)
    if (parameterCount != len(args)):
        #! make an error
        print("Error: Incorrect number of parameters. count:{} args:{}".format(parameterCount, args))

    # pad args
    for x, arg in enumerate(args):
        # + 1 because the template is first in the data
        padLen = opcodeData[x + 1]
        if (padLen != '?'):
            # for numbers
            # convert dec str to padded hex str
            args[x] = format(arg, 'x').ljust(padLen * 2, '0')
            #args[x] = arg.to_bytes(length=padLen, byteorder='little', signed=True)
            #print(args[x]) 
        #else:
            
    opcodeTemplate = opcodeData[0]
    # print (opcodeTemplate)
    formattedOpcode = opcodeTemplate.format(*args)
    b.append(''.join(formattedOpcode))

def buildSnippetOpcode(b, code, args):
    formattedOpcode = OpcodeSnippets[code](args)
    b.append(''.join(formattedOpcode))
    
        
# Place string representations of bytes on a builder.
# Dedcimal numbers are turned to hex, then padded to a width specified 
# in the template.
# When complete, the builder needs joining and changing to bytes.
# c = ''.join(b)
# c.encode()
#
# b: array used as a builder. 
# code: for template
# args: args for the template. A decimal number, or if the arg code 
#     is '?', a string of hex codes.
#! using strings is inefficient? and prone to error (big numbers? 
#! negatives? floats?). However, it lets me use string templates,
#! which is tidy on top. No byte array templater. 
def build(b, code, args):
    #! test
    #? build is an iterable
    #! code
    mapName = '\'x86\''
    try:
        buildSimpleOpcode(b, code, args)
    except KeyError:
        try:
            buildSnippetOpcode(b, code, args)
        except KeyError:
            print("OpCode not in given map. code: {} map: {}".format(code, mapName))
            sys.exit()
