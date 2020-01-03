#!/usr/bin/env python3

import argparse
from code_generate.assembly import File
import os

from PhasePipeline import PhasePipeline
from reporters.ConsoleStreamReporter import ConsoleStreamReporter
from gio.Sources import FileSource
from CompilationUnit import CompilationUnit

from phases.Basic import (
    PrintTokensPhase, 
    SyntaxPhase, 
    TreePrint, 
    TreePrintDisplay, 
    StripComments,
    #NamesValidate
    )

from phases.Parsers import (
    MakeMarkTable,
    MarkTableKindDetermine,
    )

from phases.Checks import (    
    MarkTableValidate
    )
    
"""
MAIN
"""

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="compiler for Gravel code")

    parser.add_argument(
        '-s',
        '--src-dir',
        type=str,
        default = "src",
        help="folder to find source files in",
        )
        
    parser.add_argument(
        '-d',
        '--build-dir',
        type=str,
        default = "buildDir",
        help="folder to build in (need not exist)",
        )
        
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
        # "--auto-asm", 
        # help="search for asm files in the build directory, then compile. Overrides other options.",
        # action="store_true"
        # )
                
    # parser.add_argument(
        # "-x",
        # "--destroy-asm", 
        # help="remove generated asm files (from code, not disk)",
        # action="store_true"
        # )


    # parser.add_argument(
        # "-l",
        # "--link-only", 
        # help="Link object files in the build directory into an executable. Overrides other options.",
        # action="store_true"
        # )

    # parser.add_argument(
        # "-X",
        # "--destroy-objects", 
        # help="remove object files",
        # action="store_true"
        # )

        
    parser.add_argument(
        "-v",
        "--verbose", 
        help="talk about what is being done",
        action="store_true"
        )
        
    args = parser.parse_args()
    print(str(args))

    if (args.verbose):
        print(phaseTitle('source resolution')) 
    os.makedirs(args.build_dir, exist_ok=True)
    
    # All ''gv' files in the srcDir
    if (not os.path.exists(args.src_dir)):
        raise KeyError( "Directory for source files not exists; dir;'{}'".format(
            args.src_dir,        
            )
        )

    l = File.List(args.src_dir)
    b = []
    for fp in l.filterExtensionFP('gv'):
        b.append(CompilationUnit(FileSource(fp)))
    print(str(b))


    reporter = ConsoleStreamReporter()

    ## Treeprint
    from Syntaxer import Syntaxer
    from trees.Visitors import RawPrint
    src = FileSource('test/syntax.gv')
    r = ConsoleStreamReporter()
    s = Syntaxer(src, r)
    RawPrint(s.ast)

    ## Stock pipe
    # cu = CompilationUnit(FileSource('test/syntax.gv'))

    # phaseList = [
        # SyntaxPhase(),
        # StripComments(),
        # #TreeChainsReverse(),
        # MakeMarkTable(),
        # MarkTableValidate(),
        # MarkTableKindDetermine(),
        # TreePrintDisplay(),
        # ]

    # pipeline = PhasePipeline( 
        # phaseList,
        # #codeGenContext, 
        # )

    # pipeline.run(cu, reporter)
