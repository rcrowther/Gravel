#!/usr/bin/env python3

import CodeBuilder 
import assembly.BuildTools
import opCodeTemplate.x86ASMBF
from assembly.nasmFrames import Frame64

#! Not building this correctly?
#! try something smaller.
#def build(headers, sectionData, code):
def build(code):
    fileBaseStr = "test"
    buildPath = "buildDir"
    # deleteAssemblyFile = False
    
    assembly.BuildTools.fullChain(
        code, 
        buildPath, fileBaseStr, 
        deleteAssemblyFile=False, 
        deleteObjectFile=True,
        run=True,
        verbose=True
        )


b = []
code = CodeBuilder.Empty
#b = opCodeTemplate.x86ASMBF.test()

#program(b)
#code = '\n'.join(b)
# if verbose:
#print(str(code))
#fileBaseStr = "frameASMTest"
#assemble.frameAssemble(headers, sectionData, code, fileBaseStr, False)
#build(headers=[], sectionData={"data":"", "bss":"", "rodata": ""}, code=code)
build(code.framedCode(Frame64))
