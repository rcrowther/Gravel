

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
1 : ('mov ebx, {}', 4), #"mov'  {}'ebx', {}'lit"
2 : ('mov eax, {}', 4), #"mov'  {}'eax', {}'lit"
#3 : ('488b0425{}', 4), #"mov'  {}'rax', {}'lit"
3 : ('mov rax, {}', 4), #"mov'  {}'rax', {}'lit"
4 : ('mov rbx, {}', 4), #"mov'  {}'rbx', {}'lit"
5 : ('mov rcx, {}', 4), #"mov'  {}'rcx', {}'lit"
6 : ('mov rdx, {}', 4), #"mov'  {}'rdx', {}'lit"
7 : ('mov rsi, {}', 4), #"mov'  {}'rsi', {}'lit"
#8 : ('488b3c25{}', 4), #"mov'  {}'rdi', {}'lit"
8 : ('mov rdi, {}', 4), #"mov'  {}'rdi', {}'lit"
9 : ('mov rsp, {}', 4), #"mov'  {}'rsp', {}'lit"

# arithmetic
20 : ('add rax, {}', 4), # add, 64, rax, lit 
21 : ('add rbx, {}', 4), # add, 64, rbx, lit 
22 : ('add rcx, {}', 4), # add, 64, rcx, lit 
23 : ('add rdx, {}', 4), # add, 64, rdx, lit 
24 : ('add rsi, {}', 4), # add, 64, rsi, lit 
25 : ('add rdi, {}', 4), # add, 64, rdi, lit 

30 : ('sub rax, {}', 4), # sub, 64, rax, lit 
31 : ('imul rax, {}', 4), # imul, 64, rax, lit 
#32 : ('idiv rax, {}', 6), # idiv, 64, rax, lit 
33 : ('inc rax'), # inc rax
34 : ('inc rcx'), # inc rax
38 : ('dec rax'), # dec rax
39 : ('dec rcx'), # dec rax

# Logic
40 : ('and rax, {}', 4), # and, 64, rax, lit 
41 : ('or rax,{}', 4), # or, 64, rax, lit 
42 : ('xor rax, {}', 4), # xor, 64, rax, lit 
43 : ('not rax'), # not, 64, rax

# Type conversion

# Object manipulation

# stack manipulation
50 : ('pop rax',), # pop rax
51 : ('push rax',), # push rax

# control transfer
# That's annoying, could use a simple calculation; len(block)
#? block is an anylength parameter. 
#60 : ('cmp{}jmp{}', 4, 1, '?'), # if0, cmp, block.size, block

# method calling
62 : ('{}: {}\nret', '?', '?'), # simple call, name, body 
63 : ('ret\n',), #"ret"
64 : ('syscall\n',), # syscall (complex, needs rax for number, exit status in rdi)

    
# Snippets
# Print num
101 : ('push rax, {}\npop rax', 4), # print str, addr
102 : ('{}', 4), # println str, addr
103 : ('{}', 4), # println str, addr
}

# opCode -> (opcodeTemplate, width of 1st param, width of 2nd param...)
#!
# https://blog.packagecloud.io/eng/2016/04/05/the-definitive-guide-to-linux-system-calls/#64-bit-fast-system-calls
def printInt(args):
    # return """
    # push rax
    # push rdi
    # push rsi
    # push rcx ; destroyed by syscall
    # push r11 ; destroyed by syscall
    # mov rax, -42      ;system call number (sys_write)
    # ; if rax < 0 print -VE
    # cmp rax, 0
    # jge printNum    
    # neg rax         ;for the printout, negate rax
    # mov rax, 1      ;system call number (sys_write)
    # mov	rdi, 1      ;file descriptor (stdout)
    # mov rsi, asciiMinus   ;print '-'
    # mov rdx, 1     ;1 byte length
    # syscall
# printNum:
    # mov rax, 1      ;system call number (sys_write)
    # mov	rdi, 1      ;file descriptor (stdout)
    # mov rsi, rax  ;address of thing to print
    # mov rdx, 5     ;5 bytes (numeric, 1 for sign)
    # syscall
    # pop rax
    # pop rdi
    # pop rsi
    # pop rcx ; destroyed by syscall
    # pop r11 ; destroyed by syscall
    # """

    return """
    push rax
    push rdi
    push rsi
    push rcx ; destroyed by syscall
    push r11 ; destroyed by syscall
    ;push rbp
    mov rdi, fmtInt
	mov	rsi, {address}
    call printf
    pop rax
    pop rdi
    pop rsi
    pop rcx ; destroyed by syscall
    pop r11 ; destroyed by syscall
    ;pop rbp
    """.format(address = args[0])

def printStr(args):
    # return """
    # push rax
    # push rdi
    # push rsi
    # mov rax, 1      ;system call number (sys_write)
    # mov	rdi, 1      ;file descriptor (stdout)
    # mov rsi, {label}     ;label for message to write
    # mov rdx, {length}     ;message length
    # syscall
    # pop rax
    # pop rdi
    # pop rsi
    # """.format(label = args[0], length = args[1])    
    return """
    push rdi
    push rsi
    mov rdi, fmtStr
	mov	rsi, {address}
    call printf
    pop rdi
    pop rsi
    """.format(address = args[0])
    
def printlnStr(args):
    return """
    push rax
    push rdi
    push rsi
    mov rax, 1      ;system call number (sys_write)
    mov	rdi, 1      ;file descriptor (stdout)
    mov rsi, {label}     ;label for message to write
    mov rdx, {length}      ;message length
    syscall
    mov rax, 1      ;system call number (sys_write)
    mov	rdi, 1      ;file descriptor (stdout)
    mov rsi, asciiLF     ;linefeed
    mov rdx, 1    ;linefeed length
    syscall
    pop rax
    pop rdi
    pop rsi
    """.format(label = args[0], length = args[1])  
    
OpcodeSnippets = {
 # if0, cmp, block.size, block
1000 : lambda args: 'cmp {}\njmp :end\n{}\nend:'.format(arg[0], arg[1]),
#1 : lambda args: 'cmp {}\njmp :end\n{}\nend:'.format(arg[0], arg[1]),
1020 : printInt,
1025 : printStr,
1026 : printlnStr,
}



def buildSimpleOpcode(b, code, args):
    opcodeData = Opcodes[code]
        
    # test the count
    parameterCount = len(opcodeData) - 1
    #print(parameterCount)
    if (parameterCount != len(args)):
        #! make an error
        print("Error: Incorrect number of parameters. count:{} args:{}".format(parameterCount, args))

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
    mapName = '\'x86ASM\''
    try:
        buildSimpleOpcode(b, code, args)
    except KeyError:
        try:
            buildSnippetOpcode(b, code, args)
        except KeyError:
            print("OpCode not in given map. code: {} map: {}".format(code, mapName))
            sys.exit()
