#!/usr/bin/env python3

# debian ''elfutils' contains eu-readelf, and eu-elflint, among others.
# Tiny ELF discussion on linking and tables,
# http://www.muppetlabs.com/~breadbox/software/tiny/somewhat.html
import subprocess
import os
import sys
import stat
import argparse

#? Some consistency checks e.g. only shared data has a section header 
# file
# From Spec:
# Files used to build a process image (execute a program) must have a 
# program header table; relocatable files do not need one. 
# Files used during linking must have a section header table; other 
# object files may or may not have one

#? Now up to 32Bit header adjustments...
#? and need to test on Intel machines
#? and file name output
def write(data, filename):
    with open(filename, "wb") as f:
        f.write(data)

## Load addresses 
#https://stackoverflow.com/questions/7187981/whats-the-memory-before-0x08048000-used-for-in-32-bit-machine
BASE_ADDRESS32 = int('0x08048000', 16)
BASE_ADDRESS64 = int('0x00400000', 16)

def error(msg):
    print("error: " + msg)
    sys.exit()
    
def addReturnProgram(b):
    # From Tiny. 
    # Close, or close enough, to the (working) 64bit a.out
    #00000000 B801000000                  mov     rax, 1
    #00000005 BB2A000000                  mov     rbx, 42  
    #0000000A CD80                        int     0x80
    
    # Parameter to command 'exit'
    # B801000000                  mov     rax, 1
    b.append(int('B8', 16))
    b.extend(int(1).to_bytes(4, byteorder='little'))
    
    # Return numeric code to exit with
    # BB2A000000                  mov     rbx, 42  
    b.append(int('BB', 16))
    b.extend(int('2A', 16).to_bytes(4, byteorder='little'))
    
    # Make system call---to exit
    #CD80                        int     0x80
    b.append(int('CD', 16))
    b.append(int('80', 16))
    
    
    
def toAddress32(offset):
    return BASE_ADDRESS32 + offset

def toAddress64(offset):
    return BASE_ADDRESS64 + offset 


class PosValue:
    def __init__(self):
        self.pos = {}
        self.value = {}          

    def __repr__(self):
        b = 'PosValue('
        b += 'pos:'
        b += str(self.pos)
        b += ', value:'
        b += str(self.value)
        b = b + ')'
        return b
        
    def __str__(self):
        return self.__repr__()
        
        
class ElfData:
    def __init__(self):
        self.eHeader = PosValue()
        self.pHeaders = []
        self.sHeaders = []

    def addProgramHeader(self, programHeaderOffset):
        pv = PosValue()
        pv.pos['Off'] = programHeaderOffset
        self.pHeaders.append(pv)
        return pv
         
    def __repr__(self):
        b = 'ElfData('
        b += 'eHeader:'
        b = b + str(self.eHeader)
        b += ', pHeaders:'
        b = b + str(self.pHeaders)
        b += ', sHeaders:'
        b = b + str(self.sHeaders)
        b = b + ')'
        return b
        
    def __str__(self):
        return self.__repr__()


def numberInsert4(b, insertPos, i):
    # 4 bytes, 32 bit
    #print('inserting 32bit num: {}'.format(i))
    b2 = int(i).to_bytes(4, byteorder='little')
    for i, x in enumerate(range(insertPos, insertPos + 4)):
        b[x] = b2[i]

        
def numberInsert8(b, insertPos, i):
    # 8 bytes, 64 bit
    #print('inserting 64bit num: {}'.format(i))
    b2 = int(i).to_bytes(8, byteorder='little')
    for i, x in enumerate(range(insertPos, insertPos + 8)):
        b[x] = b2[i]
        
        
            

def elfHeader32(b, pvData, fileType=2, machineType=3):
    #! Untested
    genericChecks(fileType, machineType)
    
    # Magic
    # magic lead
    b.append(int('0x7F', 16))
    
    # magic id
    # 'ascii' for standard, though 'utf-8' would work.
    b.extend(bytearray('ELF', 'ascii'))
    
    
    # EI_CLASS, 32-bit = 1, 64-bit = 2
    # Not checked, Linux
    b.append(1)
    
    # EI_DATA, endian little = 1, big = 2
    # Not checked, Linux
    b.append(1)
    
    # EI_VERSION (always 1)
    # Not checked, Linux
    b.append(1)
    
    # EI_OSABI OS System 5 = 0
    # Not checked, Linux???
    # (often ignored for 0)
    b.append(0)
    
    # EI_ABIVERSION + EI_PAD
    # Not checked, Linux
    b.extend(bytearray(8))
    
    # e_type, file type Relocatable = 1, executable = 2, shared = 3, 
    # 2 bytes
    b.extend(int(fileType).to_bytes(2, byteorder='little'))
    
    # e_machine x86 = 0x03, x86-64 = 0x3E (used?)
    # 2 bytes
    b.extend(int(machineType).to_bytes(2, byteorder='little'))

    # e_version, nearly always 1
    # 4 bytes
    b.extend(int(1).to_bytes(4, byteorder='little'))

    ## variable length fields 32 = 4bytes, 64 = 8bytes
    # e_entry, entry point for executables
    # offset = 24
    pvData.pos['Entry'] = len(b)
    b.extend(bytearray(4))
    
    # e_phoff, program header offset
    # Assuming immediate follows ELF header, saving
    # 'PHoff' if it is not.
    pvData.pos['PHoff'] = len(b)
    b.extend(int('0x34', 16).to_bytes(4, byteorder='little'))
    
    # e_shoff, section header offset
    pvData.pos['SHoff'] = len(b)
    b.extend(bytearray(4))
    
    # e_flags (unused on Intel)
    # 4 bytes
    b.extend(bytearray(4))
    
    # e_ehsize, size of this header, usually 64-bit = 64, 32-bit = 52
    # 2 bytes
    # Not checked, Linux
    b.extend(int(52).to_bytes(2, byteorder='little'))

    # e_phentsize, size of a program header table entry.
    # 2 bytes
    # Surely e_phentsize/e_shentsize are fixed for architecture?
    # and not read by linux?
    b.extend(int(32).to_bytes(2, byteorder='little'))
    
    # e_phnum, number of entries in the program header table. 
    # 2 bytes
    b.extend(int(1).to_bytes(2, byteorder='little'))
    
    # e_shentsize, the size of a section header table entry. 
    # 2 bytes
    # Surely e_phentsize/e_shentsize are fixed for architecture?
    # and not read by linux?
    b.extend(bytearray(2))
    
    # e_shnum, number of entries in the section header table. 
    # Assume 0, 'SHnum' if it is not.
    pvData.pos['SHnum'] = len(b)
    b.extend(bytearray(2))
    
    # e_shstrndx, index of the section header table entry that contains 
    # the section names. 
    # Assume 0, 'SHstrndx' if it is not.
    pvData.pos['SHstrndx'] = len(b)
    b.extend(bytearray(2))    
    
    
def genericChecks(fileType, machineType):
    if (fileType < 0 or fileType > 4):
        error("filetype = {}\n  Must be Relocatable = 1, executable = 2, shared = 3".format(fileType))
    #  AMD x86-64 = 17???
    # What is this test if 62 for intel64 is valid??
    if (machineType < 0):
        #error("machineType = {}\n Common values are 1 = AT&T WE, 2 = SPARC, 3 = Intel Architecture, 4 Motorola 6800, 5= Motorola 88000, 7 = Intel 80860, 8 = MIPS RS3000 Big-Endian, 10 = MIPS RS4000 Big-Endian".format(machineType))
        error("machineType = {}\n Common values are 3 = Intel Architecture, 62 = AMD x86-64".format(machineType))



def programHeaderInsertAddresses64(b, PVAddrPos, PPAddrPos, programHeaderAddress):
    # Virtual and physical addresses missing. Add them here.
    numberInsert8(b, PVAddrPos, programHeaderAddress)
    numberInsert8(b, PPAddrPos, programHeaderAddress)

def programHeaderInsertSizes64(b, PFileszPos, PMemszPos, fileSize):
    # headers want filesizes and mem sizes. For now, not flexible.
    numberInsert8(b, PFileszPos, fileSize)
    numberInsert8(b, PMemszPos, fileSize)

# fileType relocatable = 1, executable = 2, shared = 3, core file = 4    
def elfHeader64(b, pvData, fileType=2, machineType=62):
    genericChecks(fileType, machineType)

    # Magic
    # magic lead
    b.append(int('0x7F', 16))
    
    # magic id
    # 'ascii' for standard, though 'utf-8' would work.
    b.extend(bytearray('ELF', 'ascii'))
    
    # EI_CLASS, 32-bit = 1, 64-bit = 2
    # Not checked, Linux
    b.append(2)
    
    # EI_DATA, endian little = 1, big = 2
    # Not checked, Linux
    b.append(1)
    
    # EI_VERSION (always 1)
    # Not checked, Linux
    b.append(1)
    
    # EI_OS ABI OS System 5 = 0
    # Not checked, Linux???
    # (often ignored for 0)
    b.append(0)
    
    #EI_ABI VERSION + EI_PAD
    # Not checked, Linux
    b.extend(bytearray(8))
    
    # e_type, file type Relocatable = 1, executable = 2, shared = 3, 
    # 2 bytes
    b.extend(int(fileType).to_bytes(2, byteorder='little'))
    
    # e_machine x86 = 0x03, x86-64 = 0x3E (used?)
    # 2 bytes
    # machineType 0x3E = 64
    b.extend(int(machineType).to_bytes(2, byteorder='little'))

    # e_version, nearly always 1
    # 4 bytes
    b.extend(int(1).to_bytes(4, byteorder='little'))

    
    ## variable length fields 32 = 4bytes, 64 = 8bytes
    # e_entry, entry point for executables. Start of code under a 
    # program header, so not yet known. Placeholder.
    # offset = 24
    pvData.pos['Entry'] = len(b)
    b.extend(bytearray(8))
    
    # e_phoff, program header offset
    # Assuming this is almost always this value, but saving
    # 'PHoff' if it is not.
    # offset = 32 = 64
    pvData.pos['PHoff'] = len(b)
    b.extend(int('0x40', 16).to_bytes(8, byteorder='little'))
    
    # e_shoff, section header offset
    # offset = 40
    pvData.pos['SHoff'] = len(b)
    b.extend(bytearray(8))
    
    # e_flags (unused on Intel)
    # 4 bytes
    b.extend(bytearray(4))
    
    # e_ehsize, size of this header, usually 64-bit = 64
    # 2 bytes e.g. 64
    # Not checked, Linux
    b.extend(int(64).to_bytes(2, byteorder='little'))

    # e_phentsize, size of a program header table entry.
    # 2 bytes, e.g. 56
    b.extend(int(56).to_bytes(2, byteorder='little'))
    
    # e_phnum, number of entries in the program header table. 
    # 2 bytes
    b.extend(int(1).to_bytes(2, byteorder='little'))
    
    # e_shentsize, the size of a section header table entry. Typical 64 
    # 2 bytes e.g. 64
    b.extend([0, 0])
    
    # e_shnum, number of entries in the section header table. 
    # Assume 0, 'SHnum' if it is not.
    pvData.pos['SHnum'] = len(b)
    b.extend(bytearray(2))
    
    # e_shstrndx, index of the section header table entry that contains 
    # the section names. 
    # Assume 0, 'SHstrndx' if it is not.
    pvData.pos['SHstrndx'] = len(b)
    b.extend(bytearray(2))

def programHeader32(b):
    # program headers
    # 32bit = 32 bits long

    #? Not completed
    
    # p_type, type of the segment.
    # 4 bytes
    b.extend(int(1).to_bytes(4, byteorder='little'))
    
    # p_offset, offset of the segment in the file image. 
    # 4 bytes. Usually 0
    # (0 in 32bits) 4 bytes
    b.extend(bytearray(4))

    #p_vaddr, virtual address of the segment in memory. Usually $$???
    # 4 bytes
    PVAddrPos = len(b)
    b.extend(bytearray(4))
    
    #p_paddr, on systems where physical address is relevant, reserved 
    # for segment's physical address. Usually $$???
    # 4 bytes
    PPAddrPos = len(b)
    b.extend(bytearray(4))    

    # p_filesz, size of the segment in the file image, often filesize
    # 4 bytes
    PFileszPos = len(b)
    b.extend(bytearray(4))
    
    #p_memsz, size of the segment in memory, often filesize
    # 4 bytes
    PMemszPos = len(b)
    b.extend(bytearray(4))

    # p_flags, segment-dependent flags (position for 32-bit structure).
    # 4 bytes
    b.extend(int(5).to_bytes(4, byteorder='little'))

    # p_align, 0 and 1 specify no alignment. 
    # 4 bytes
    # '0x1000' = 4096
    #b.extend(int('0x1000', 16).to_bytes(4, byteorder='little'))
    b.extend(int(8).to_bytes(4, byteorder='little'))
    
    return (PVAddrPos, PPAddrPos, PFileszPos, PMemszPos)


def phChecks(phType):
    if (phType < 1 or phType > 4):
        error("program header type = {}\n  Must be 1 = Loadable segment, 2 = Dynamic linking information, 3 = Interpreter information, 4 = Auxiliary information".format(phType))

    
def programHeader64(b, data, phType = 1):
    # program headers
    # 64bit = 56bits long
    phChecks(phType)

    #? Not completed

    # p_type, type of the segment.
    # 4 bytes
    b.extend(int(phType).to_bytes(4, byteorder='little'))

    # p_flags
    # 4 bytes
    #??? Why 5
    b.extend(int(5).to_bytes(4, byteorder='little'))

    # p_offset, offset of the segment in the file image. 
    # 8 bytes. Usually 0
    # (0 in 32bits) 4 bytes
    b.extend(bytearray(8))

    #p_vaddr, virtual address of the segment in memory. 
    # Placeholder
    # 8 bytes
    data.pos['VAddr'] = len(b) 
    b.extend(bytearray(8))
    
    #p_paddr, on systems where physical address is relevant, reserved 
    # for segment's physical address.
    # 8 bytes
    data.pos['PAddr'] = len(b) 
    b.extend(bytearray(8))    

    # p_filesz, size of the segment in the file image, usually filesize
    # 8 bytes
    data.pos['Filesz'] = len(b) 
    b.extend(bytearray(8))

    #p_memsz, size of the segment in memory, usually filesize
    # 8 bytes
    data.pos['Memsz'] = len(b) 
    b.extend(bytearray(8))

    # p_align
    # 8 bytes
    # '0x1000' = 4096
    #???Taken from Tiny code -> needs research 
    # is significant?
    b.extend(int('0x1000', 16).to_bytes(8, byteorder='little'))



    
ETypeToCode = {'rel': 1, 'exec': 2, 'dyn': 3, 'core': 4}

# bits: bit width as str, '64'/'32' 
# code: function taking a builder to append code
def mkELF(bits, etype, sections, code):
    b = bytearray()
    
    elfData = ElfData()
    
    ## ELF header
    tpe = ETypeToCode[etype]
    if (bits == '32'):
        elfHeader32(b, elfData.eHeader, fileType=tpe, machineType=3)
    else:
        elfHeader64(b, elfData.eHeader, fileType=tpe, machineType=62)

    
    ## program header
    programHeaderOffset = len(b)
    pv = elfData.addProgramHeader(programHeaderOffset) 
    # Needs this now
    #if (bits == '32'):
    #programHeader32(b, pv)
    #else:
    programHeader64(b, pv)
    
    
    # Program header addresses
    # These may not be as basic as this,
    # which loads the whole file from start.
    #programHeaderAddress = toAddress64(programHeaderOffset)
    pheaders0Pos = pv.pos
    programHeaderInsertAddresses64(b, pheaders0Pos['VAddr'], pheaders0Pos['PAddr'], BASE_ADDRESS64)
    
    # Last ELF header data - Entry point
    # know this because all headers in place
    numberInsert8(b, elfData.eHeader.pos['Entry'], toAddress64(len(b)))
    
    # Put in a simple program
    if (code):
        code(b)
      
    ## Finish with last inserts into program header
    fileSize = len(b)
    elfData.eHeader.value['FileSize'] = fileSize
    
    # Program headers need to see this
    # Basic, loading everything using filesize.
    pheaders0Pos = elfData.pHeaders[0].pos
    programHeaderInsertSizes64(b, pheaders0Pos['Filesz'], pheaders0Pos['Memsz'], fileSize)
    
    print('data:')
    print(str(elfData))
    
    write(b, 'elfTest')
    
    # Change permissions, so don't be evil to users or me.
    # also stat.S_IXGRP, stat.S_IXOTH
    os.chmod('elfTest', stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IXUSR)


parser = argparse.ArgumentParser(description='A runner for ELFWrite.')
parser.add_argument('-addCode', 
    action="store_true",
    dest="addCode",
    help='Add a snippet of code to the ELF to return 42.'
    )
    
parser.add_argument('-bits', 
    default='64',  
    choices=['64', '32'], 
    help='Choose a bit-width (default=64).'
    )

parser.add_argument('-type',
    default = 'exec',
    dest= 'etype',
    #choices=['rel', 'exec', 'dyn', 'core'], 
    choices=ETypeToCode.keys(), 
    help='Type (or intended usage) of the file.',
    )
    
# Only needed for shared objects.
# Do not implement yet? 
parser.add_argument('-sections',
    choices=['rodata', 'lrodata', 'data', 'ldata', 'bss', 'tdata', 'tbss', 'lbss', 'debug', 'comment'], 
    nargs='*',
    help='Add sections to the ELF.',
    )
    
args = parser.parse_args()
#print (args.etype)

# Do this all the time until valid alternatives.
givenCode = addReturnProgram
if (args.addCode):
    givenCode=addReturnProgram
    
mkELF(args.bits, args.etype, args.sections, givenCode)
