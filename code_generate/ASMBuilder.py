#!/usr/bin/env python3

import argparse

import CodeBuilder 
import assembly.BuildTools
import x86ASMBF
from assembly.nasmFrames import Frame64
import assembly.File


def pDataTest():
    phaseData = assembly.BuildTools.PhaseData()
    phaseData.destroyGeneratedAsm=False
    return phaseData
    
def autoASM(phaseData):
    phaseData.firstPhase='mchn'
    # All ''asm' files in the buildDir
    l = assembly.File.List(phaseData.buildPath)
    for fp in l.filterExtensionFP('asm'):
        phaseData.srcs.append(assembly.BuildTools.VirtualFileSource(fp))
    #print(str(phaseData))
    assembly.BuildTools.runPipe(phaseData)
    
def linkOnly(phaseData):
    phaseData.firstPhase='link'
    # All ''o' files in the buildDir
    # assembler searches builddir automatically.
    assembly.BuildTools.runPipe(phaseData)
    
#! better builders
def fromVirtualCode(phaseData, code):
    #phaseData.srcs.append(assembly.BuildTools.VirtualFileSource("buildDir/codeFile0.asm"))
    phaseData.srcs.append(assembly.BuildTools.VirtualFileCode(code))
    #phaseData.firstPhase='mchn'
    #phaseData.lastPhase='link'
    assembly.BuildTools.runPipe(phaseData)


    
"""
MAIN
"""

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="compiler for intermediate code")

    # parser.add_argument(
        # '-d',
        # '--build-dir',
        # type=str,
        # default = "buildDir",
        # help="folder to build in (need not exist)",
        # )
        
    # parser.add_argument(
        # "-f",
        # "--first-phase", 
        # help="first action of compile chain",
        # choices=['src', 'link', 'run'],
        # default='src'
        # )

    # parser.add_argument(
        # "-l",
        # "--last-phase", 
        # help="last action of compile chain",
        # choices=['src', 'mchn', 'link', 'run'],
        # default='run'
        # )

    parser.add_argument(
        "-a",
        "--auto-asm", 
        help="search for asm files in the build directory, then compile. Overrides other options.",
        action="store_true"
        )
                
    parser.add_argument(
        "-x",
        "--destroy-asm", 
        help="remove generated asm files (from code, not disk)",
        action="store_true"
        )


    parser.add_argument(
        "-l",
        "--link-only", 
        help="Link object files in the build directory into an executable. Overrides other options.",
        action="store_true"
        )

    parser.add_argument(
        "-X",
        "--destroy-objects", 
        help="remove object files",
        action="store_true"
        )
        
    parser.add_argument(
        "-v",
        "--verbose", 
        help="talk about what is being done",
        action="store_true"
        )

    # parser.add_argument(
        # 'SOURCES',
        # type=argparse.FileType('r'),
        # help="input file sources",
        # )  
              
    args = parser.parse_args()

    #print(args)

    pData = pDataTest()
    if (args.destroy_asm):
        pData.destroyGeneratedAsm = True
    if (args.destroy_objects):
        pData.destroyObjects = True

        
    if (args.link_only == True):
        linkOnly(pData)
    elif (args.auto_asm == True):
        autoASM(pData)
    else:  
        b = CodeBuilder.Builder()
        #x86ASMBF.testPrint(b)
        #x86ASMBF.testPrintDebug(b)
        #x86ASMBF.testStaticAlloc(b)
        #x86ASMBF.testStackInt(b)
        #x86ASMBF.testStackString(b)
        #x86ASMBF.testHeapData(b)
        #x86ASMBF.testHeapInt(b)
        #x86ASMBF.testHeapStr(b)
        #x86ASMBF.testIf(b)
        x86ASMBF.testWhile(b)
        
        print('go')
        #x86ASMBF.testStruct(b)
        fromVirtualCode(pData, b.frame(Frame64))
