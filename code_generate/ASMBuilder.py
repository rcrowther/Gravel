#!/usr/bin/env python3

import assembly.assemble

#! Not building this correctly?
#! try something smaller.
def build(headers, sectionData, code):
    fileBaseStr = "test"
    buildPath = "buildDir"
    # deleteAssemblyFile = False
    assembly.assemble.frameAssemble(
        headers, sectionData, code, 
        buildPath, fileBaseStr, 
        deleteAssemblyFile=False, 
        verbose=True
        )


b = []
#program(b)
code = '\n'.join(b)
# if verbose:
#print(str(code))
#fileBaseStr = "frameASMTest"
#assemble.frameAssemble(headers, sectionData, code, fileBaseStr, False)
build(headers=[], sectionData={"data":"", "bss":"", "rodata": ""}, code=code)
