#!/usr/bin/env python3

import argparse

import CodeBuilder 
import assembly.BuildTools
import x86ASMBF
from assembly.nasmFrames import Frame64

#! better builders
def build(code):
    phaseData = assembly.BuildTools.PhaseData()
    phaseData.destroyGeneratedAsm=False
    phaseData.srcs.append(assembly.BuildTools.VirtualFileSource("buildDir/codeFile0.asm"))
    #phaseData.srcs.append(assembly.BuildTools.VirtualFileCode(code))
    #phaseData.firstPhase='mchn'
    #phaseData.lastPhase='link'
    assembly.BuildTools.runPipe(phaseData)

"""
MAIN
"""

# if __name__ == "__main__":
    
    # parser = argparse.ArgumentParser(description="compiler for intermediate code")

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

    # parser.add_argument(
        # "-a",
        # "--destroy-asm", 
        # help="remove asm files",
        # action="store_true"
        # )
        
    # parser.add_argument(
        # "-o",
        # "--destroy-objects", 
        # help="remove object files",
        # action="store_true"
        # )
        
    # parser.add_argument(
        # "-v",
        # "--verbose", 
        # help="talk about what is being done",
        # action="store_true"
        # )

    # parser.add_argument(
        # 'SOURCES',
        # type=argparse.FileType('r'),
        # help="input file sources",
        # )  
              
    # args = parser.parse_args()


    #print(args)
#! asm only rebuild
b = CodeBuilder.Builder()
x86ASMBF.test(b)
build(b.frame(Frame64))
