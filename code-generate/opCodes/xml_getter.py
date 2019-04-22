#!/usr/bin/env python3
"""
Grab Intel opcodes from online sources.
http://ref.x86asm.net/
Works from
http://ref.x86asm.net/x86reference.xml
Also on github
https://github.com/Barebit/x86reference
"""
import os
import re
import codecs
from urllib import request

#? Not enough info to identify opCodes and define usage.
#? Opcodes visited, but not pretty printed like
#? website HTML.
#? Also, operator codes are subtrees in XML source.
#? Not currently being visited.
#? http://ref.x86asm.net/#Instruction-Operand-Codes
def X86OpcodeData():
    location='http://ref.x86asm.net/x86reference.xml'
    data = request.urlopen(location)    
    content = data.read().decode('utf-8')
    print('writing...')
    languages = []
    with open('X86OpcodeReference.xml', 'w') as f:
        for line in content.splitlines():
            f.write(line)
            f.write('\n')

#  Grab the XML Opcode data file from the website
#? The project is someplace on github, I think?
X86OpcodeData()
print('done')
