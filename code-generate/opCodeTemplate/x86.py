
#? # block is an anylength parameter. 
#? It's parameter lengths we are about, not overall length

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

# opcode [str], description 
# So far, proving very hard human compilation
# Try using NASM? Cross check?
# opCode, width, map reference
# 	81 		0 					L 	ADD 	r/m16/32/64 	imm16/32
[
# Storage
('8b1c25{}', 4), #"mov'  {}'ebx', {}'lit"
('8b0425{}', 4), #"mov'  {}'eax', {}'lit"
('488b0425{}' 4), #"mov'  {}'rax', {}'lit"
('488b1c25{}', 4), #"mov'  {}'rbx', {}'lit"
('488b0c25{}', 4), #"mov'  {}'rcx', {}'lit"
('488b1425{}', 4), #"mov'  {}'rdx', {}'lit"
('488b3425{}', 4), #"mov'  {}'rsi', {}'lit"
('488b3c25{}', 4), #"mov'  {}'rdi', {}'lit"
('488b2425{}', 4), #"mov'  {}'rsp', {}'lit"

# arithmetic
('48030425{}', 4), # add, 64, rax, lit 
('48031c25{}', 4), # add, 64, rbx, lit 
('48030c25{}', 4), # add, 64, rcx, lit 
('48031425{}', 4), # add, 64, rdx, lit 
('48033425{}', 4), # add, 64, rsi, lit 
('48033c25{}', 4), # add, 64, rdi, lit 

('482b0425{}', 4), # sub, 64, rax, lit 
('480faf0425{}', 4), # imul, 64, rax, lit 
#('4805{}', 6), # idiv, 64, rax, lit 
('48ffc0'), # inc rax
('48ffc8'), # dec rax

# Logic
('48230425', 4), # and, 64, rax, lit 
('480b0425', 4), # or, 64, rax, lit 
('48330425', 4), # xor, 64, rax, lit 
('48f7d0'), # not, 64, rax

# Type conversion

# Object manipulation

# stack manipulation
('58'), # pop rax
('50'), # push rax

# control transfer
# That's annoying, could use a simple calculation; len(block)
#? block is an anylength parameter. 
('483b0425{}75{}', 4, 1, '?'), # if0, cmp, block.size, block
('483b0425{}75{}eb{}{}', 4, 1, '?', '?'), # if0else, cmp, block1.size + 2 (for jmp), block1, block2.size, block2

# method calling
('{}c3e8{}', '?', 4), # simple call, body, method offset 
('c3'), #"ret"
]
