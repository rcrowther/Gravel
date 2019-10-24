#!/usr/bin/env python3

import subprocess
import collections
import sys
import os

#! add filehandling
#! sort out errors
def subprocessRun(args, errorMsg):
    try:
        subprocess.run(
            args, 
            stdin=None, input=None, stdout=None, 
            stderr=subprocess.PIPE, 
            universal_newlines=True, 
            shell=False, 
            timeout=None, 
            check=True
            )
    except subprocess.CalledProcessError  as e:
        # Non-zero oputput
        print("[Error] {}".format(errorMsg))
        #print("    {}".format(e.stderr.decode("utf-8") ))
        print("    {}".format(e.stderr))
        #! wont exit?
        sys.exit()
        

class PhaseData():
    # object file creation makes no sense if srcs not established
    FirstPhases = ['src', 'mchn', 'link', 'run']
    LastPhases = ['src', 'mchn', 'link', 'run']
    
    def __init__(self):
        self.buildPath = "buildDir"
        self.__firstPhase = "src"
        self.__lastPhase = "run"
        self.destroyAsm = False
        self.destroyObjects = True
        self.verbose = True
        self.code = ""
        self.srcNames = []
        self.baseNames = []
        self.asmNames = []
        self.objectNames = []
        self.executablePath = ""
        
    @property    
    def firstPhase(self):
        return self.__firstPhase
    @firstPhase.setter
    def firstPhase(self, value):
        if not value in PhaseData.FirstPhases:
            raise KeyError( "Must be one of:{}".format(PhaseData.FirstPhases))
        self.__firstPhase=value

    @property    
    def lastPhase(self):
        return self.__lastPhase
    @lastPhase.setter
    def lastPhase(self, value):
        if not value in PhaseData.LastPhases:
            raise KeyError( "Must be one of:{}".format(PhaseData.LastPhases))
        self.__lastPhase=value

def baseName(srcPath):
    name = os.path.basename(srcPath)
    idx = name.rfind(".")
    return name[:idx]
    
def phaseTitle(name):
    return "[{} phase]".format(name)
    
#! need a proper object to keep track of files and code     
def createAF(d):
    #! half-ass effort
    #! it should verify things about asm source files
    #! internally split namespaces
    #! and also accept code directly as test input.
    if (d.verbose):
        print(phaseTitle('source')) 
    os.makedirs(d.buildPath, exist_ok=True)
    d.baseNames.append(baseName(d.srcNames[0]))
    d.asmNames.append(os.path.join(d.buildPath, d.baseNames[0] + ".asm"))
    with open(d.asmNames[0], "w") as f:
        f.write(d.code)


def createObject(d):
    if (d.verbose):
        print(phaseTitle('object')) 
    compilerArgs = "nasm -f elf64 -F stabs".split()
    #d.objectNames.append(os.path.join(d.buildPath, d.baseNames[0] + ".o"))
    d.objectNames.append(os.path.join(d.buildPath, "test.o"))
    ##compilerArgs.extend(['-o', d.objectNames[0], d.asmNames[0]])
    compilerArgs.extend(['-o', d.objectNames[0], 'buildDir/test.asm'])
    if (d.verbose):
        print("compiler line:\n    {}".format(" ".join(compilerArgs)))
    subprocessRun(compilerArgs, "Assembler returned non-zero!")
    if (d.destroyAsm):
        os.remove(d.asmNames[0])
        if (d,verbose):
            print("assembly file removed")

def filesList(dirPath):
    (_, _, names) = next(os.walk(dirPath))
    return [os.path.join(dirPath, name) for name in names ]
    
def pathExtension(path):
    idx = path.rfind('.')
    o = ''
    if (idx != -1):
        o = path[idx + 1:]
    return o
    
def extensionFilter(paths, extension):
    return [path for path in paths if (pathExtension(path) == extension)]
    
def linkObjects(d):    
    if (d.verbose):
        print(phaseTitle('link')) 
    linkerArgs = "gcc -Wall -no-pie ".split()
    #! need better name heuristic than using everything or one file
    #! For now
    #d.executablePath = os.path.join(d.buildPath, d.baseNames[0])
    d.executablePath = os.path.join(d.buildPath, "test")
    # This is ''every .o in the dir', not derived from past path
    # collections.
    d.objectPaths = extensionFilter(filesList(d.buildPath), 'o')
    linkerArgs.extend(['-o', d.executablePath])
    linkerArgs.extend(d.objectPaths)
    if (d.verbose):
        print("linker line:\n    {}".format(" ".join(linkerArgs)))    
    subprocessRun(linkerArgs, "Link and generate (GCC) returned non-zero!")
    if (d.destroyObjects):
        os.remove(d.objectNames[0])
        if (d.verbose):
            print("object file removed")

        
def runRunnable(d):
    if (d.verbose):
        print(phaseTitle('run')) 
    args = ['./' + d.executablePath]
    subprocessRun(args, "Run returned non-zero!")

def fullChain(
    code, 
    buildPath, 
    fileBaseStr, 
    deleteAssemblyFile, 
    deleteObjectFile,
    run,
    verbose
    ):
    # Write assembly code to an intermediate file, then run 
    # tools to create an executable.
    # No PIC
    #
    # fileBaseStr: has ''asm' appended for the assembly file path, etc.

    # also assures build directory
    asmFPath = createAF(code, buildPath, fileBaseStr)
    
    objectFPath = createObject(buildPath, fileBaseStr, asmFPath, verbose)
    if (deleteAssemblyFile):
        os.remove(asmFPath)
        if (verbose):
            print("assembly file removed")
            
    executablePath = linkObjects(buildPath, fileBaseStr, objectFPath, verbose)
    if (deleteObjectFile):
        os.remove(objectFPath)
        if (verbose):
            print("object file removed")

    if (verbose):
        print('compile done')        

    if (run):
        runRunnable(executablePath)

Pipe = collections.OrderedDict()
Pipe['src'] = createAF
Pipe['mchn'] = createObject
Pipe['link'] = linkObjects
Pipe['run'] = runRunnable


def runPipe(phaseData):
    firstPhase = phaseData.firstPhase
    lastPhase = phaseData.lastPhase
    it = iter(Pipe)
    process = False 
        
    for n,p in Pipe.items():
        if (n == firstPhase):
           process = True
        if(process):
            p(phaseData)
        if (n == lastPhase):
           break            
        
        

        
#nasm -f elf64 -F stabs -o nasm64Trailer.o nasmUnlinkedTrailer.asm
##ld -m elf_x86_64 -s -o nasm64Trailer nasm64Trailer.o
#gcc -Wall -fPIC  -s -nostdlib -o nasm64Trailer  nasm64Trailer.o
#ld -s -o nasm64Trailer  nasm64Trailer.o

#rm nasm64Trailer.o

#./nasm64Trailer ; echo $?

#rm nasm64Trailer



########
# TEST #
########
def main():
    pass
    #fileBaseStr = "nasmFrame64"
    #ret = codeFrame("", {"data":"", "bss":"", "rodata": ""}, "")
    #print(ret)
    
if __name__== "__main__":
    main()


