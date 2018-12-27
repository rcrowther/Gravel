#!/usr/bin/env python3
"""
Generate some CSV files from online sources.
Copy,
http://www-01.sil.org/iso639-3/iso-639-3.tab
to
iso3.txt
attributation: www.sil.org/iso639-3/ 
"""
import os
import re
import codecs
from urllib import request


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
