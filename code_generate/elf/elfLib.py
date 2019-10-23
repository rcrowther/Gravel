#!/usr/bin/env python3

# debian ''elfutils' contains eu-readelf, and eu-elflint, among others.
# Tiny ELF discussion on linking and tables,
# http://www.muppetlabs.com/~breadbox/software/tiny/somewhat.html
import subprocess
import os
import sys
import stat

#? Some consistency checks e.g. only shared data has a section header 
# file
# From Spec:
# Files used to build a process image (execute a program) must have a 
# program header table; relocatable files do not need one. 
# Files used during linking must have a section header table; other 
# object files may or may not have one

#? Now up to 32Bit header adjustments...
#? and need to test on Intel machines

## Load addresses 
#https://stackoverflow.com/questions/7187981/whats-the-memory-before-0x08048000-used-for-in-32-bit-machine
BASE_ADDRESS32 = int('0x08048000', 16)
BASE_ADDRESS64 = int('0x00400000', 16)

def error(msg):
    print("error: " + msg)
    sys.exit()
    
    
def toAddress32(offset):
    return BASE_ADDRESS32 + offset

def toAddress64(offset):
    return BASE_ADDRESS64 + offset 


class PosValue:
    # Why do these gather hashes?
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
        self.shStrTab = {}

    def addProgramHeader(self, programHeaderOffset):
        pv = PosValue()
        #? isnt this...
        #? Unused, I think
        #pv.pos = 'Off'
        #pv.value = programHeaderOffset
        pv.pos['Off'] = programHeaderOffset
        self.pHeaders.append(pv)
        return pv

    def addSectionHeader(self, sectionHeaderOffset):
        pv = PosValue()
        #pv.pos = 'Off'
        #pv.value = programHeaderOffset
        pv.pos['Off'] = sectionHeaderOffset
        self.sHeaders.append(pv)
        return pv
                 
    def __repr__(self):
        b = 'ElfData('
        b += 'elfHeader:'
        b = b + str(self.eHeader)
        b += ', pHeaders:'
        b = b + str(self.pHeaders)
        b += ', shStrTable:'
        b = b + str(self.shStrTab)
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

#! Unused, but close to usable
# ProgramHeader(phType = 1)
class ProgramHeader:

    attrNames = [
    "p_type",
    "p_flags64",
    "p_offset",
    "p_vaddr",
    "p_paddr",
    "p_filesz",
    "p_memsz",
    "p_flags32",
    "p_align",
    ]
	
    # numerical values can be a number or a string. If a string, in 
    # deciaml.
    def __init__(self, phType = 1):   
        self.p_type = ELFField(phType, 4, 4)  
        self.p_flags64 = ELFField(int(5), 0, 4)  
        self.p_offset = ELFField(0, 4, 8)  
        self.p_vaddr = ELFField(0, 4, 8)  
        self.p_paddr = ELFField(0, 4, 8)   
        self.p_filesz = ELFField(0, 4, 8)   
        self.p_memsz = ELFField(0, 4, 8)   
        self.p_flags32 = ELFField(0, 4, 0)   
        self.p_align = ELFField(int('0x1000', 16), 4, 8)  

    def buildField(self, b, attrName, attrNameWidth):
        attr = getattr(self, attrName)
        v = attr.value
        width = getattr(attr, attrNameWidth)
        b.extend(int(v).to_bytes(width, byteorder='little'))
            
    def build(self, b, pv, width):
        #programHeaderOffset = len(b)
        #pv = data.addProgramHeader(programHeaderOffset) 

        attrNameWidth = 'width' + width

        #NB no loop because need to gather offsets
        # ...which is easy by length
        self.buildField(b, "p_type", attrNameWidth)
        self.buildField(b, "p_flags64", attrNameWidth)
        self.buildField(b, "p_offset", attrNameWidth)
        pv.pos['VAddr'] = len(b) 
        self.buildField(b, "p_vaddr", attrNameWidth)
        pv.pos['PAddr'] = len(b) 
        self.buildField(b, "p_paddr", attrNameWidth)
        pv.pos['Filesz'] = len(b) 
        self.buildField(b, "p_filesz", attrNameWidth)
        pv.pos['Memsz'] = len(b) 
        self.buildField(b, "p_memsz", attrNameWidth)
        self.buildField(b, "p_flags32", attrNameWidth)
        self.buildField(b, "p_align", attrNameWidth)
                
    def __repr__(self):
        b = 'ProgramHeader('
        for attrName in self.attrNames:
            b += '{}:{}, '.format(attrName, getattr(self, attrName).value)
        b = b + ')'
        return b
        
    def __str__(self):
        return self.__repr__()
        
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

class ELFField:
    def __init__(self, value, width32, width64):
        self.value = value 
        self.width32 = width32
        self.width64 = width64

    def __repr__(self):
        b = 'ELFField('
        b += 'value:'
        b = b + str(self.value)
        b += ', width32:'
        b = b + str(self.width32)
        b += ', width64:'
        b = b + str(self.width64)
        b = b + ')'
        return b

        
    def __str__(self):
        return self.__repr__()
                
                
# .symtab 
# .strtab
# Name     Type         Addr             Off      Size     ES Flags  Lk Inf Al
# .rodata  PROGBITS     0000000000000680 00000680 00000011  0 A      0   0  4


SectionType = {
"SHT_PROGBITS" : 0x1, 
"SHT_STRTAB" : 0x3,
}

# Need to
#X - Write a string table under the program headers
# - Write the section header table at end
# -- .text, rodata, .shstrtab
# - Adjust offsets and other data
# - ElfHead
# -- Entry point address:               0x400080
# -- Start of section headers:          168 (bytes into file)
# -- Number of section headers entries: 4
# -- Section header string table index: 3
# (presumimg section headers are 64 bytes...)
 
# name, flags, align
#roSh = SectionHeader('.rodata', SectionType["SHT_PROGBITS"], 'AX', 4)
# roSh.build(b, data, '64')
# strTab = SectionHeader('.shstrtab', SectionType["SHT_STRTAB"], 'A', 1)
# strTab.build(b, data, '64')

#! not ready to go, but getting there...
# Need data on NASM files for positioning etc.
class SectionHeader:

    attrNames = [
     "sh_name",
     "sh_type",
     "sh_flags",
     "sh_addr",
     "sh_offset",
     "sh_size",
     "sh_link",
     "sh_info",
     "sh_addralign",
     "sh_entsize"
     ]
     
    # numerical values can be a number or a string. If a string, in 
    # deciaml.
    def __init__(self, name, tpe, offset, sectionSize, align):   
        self.sh_name = ELFField(name, 4, 4)  
        self.sh_type = ELFField(tpe, 4, 4)  
        self.sh_flags = ELFField(11, 4, 8)  
        self.sh_addr = ELFField(0, 4, 8)  
        self.sh_offset = ELFField(offset, 4, 8)   
        self.sh_size = ELFField(sectionSize, 4, 8)   
        self.sh_link = ELFField(0, 4, 4)   
        self.sh_info = ELFField(0, 4, 4)   
        self.sh_addralign = ELFField(align, 4, 8)   
        self.sh_entsize = ELFField(0, 4, 8)  


    def build(self, b, data, width):
        #! wrong, it gets a PV
        sectionHeaderOffset = len(b)
        pv = data.addSectionHeader(sectionHeaderOffset) 

        attrNameWidth = 'width' + width
        #! may need to roll out loop for data writing
        for attrName in self.attrNames:
            attr = getattr(self, attrName)
            v = attr.value
            width = getattr(attr, attrNameWidth)
            #print(str(v))
            b.extend(int(v).to_bytes(width, byteorder='little'))
        
    def __repr__(self):
        b = 'SectionHeader('
        for attrName in self.attrNames:
            b += '{}:{}, '.format(attrName, getattr(self, attrName).value)
        b = b + ')'
        return b
        
    def __str__(self):
        return self.__repr__()

#! need to keep track of offsetds?
def stringTableBuild(b, data, strings):
    # so we record offsets
    base = len(b)
    # null byte
    b.append(0)
    for string in strings:
        #b.extend(int(v).to_bytes(width, byteorder='little'))
        data.shStrTab[string] = len(b) - base
        b.extend(string.encode('ascii'))
        #null byte
        b.append(0)

    
ETypeToCode = {'rel': 1, 'exec': 2, 'dyn': 3, 'core': 4}

# outpath: can be str/file/stream
# bits: bit width as str, '64'/'32' 
# sections: can be None
# code: function taking a builder to append code. The function must 
#     take a bytearray.
def mkElf(outpath, bits, etype, sections, code, verbose):
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
    #    programHeader32(b, pv)
    #else:
    #    programHeader64(b, pv)
    #! Seems ok?
    ph = ProgramHeader(phType = 1)  
    ph.build(b, pv, bits)

    # Program header addresses
    # These may not be as basic as this,
    # which loads the whole file from start.
    #programHeaderAddress = toAddress64(programHeaderOffset)
    pheaders0Pos = pv.pos
    programHeaderInsertAddresses64(
        b, 
        pheaders0Pos['VAddr'], 
        pheaders0Pos['PAddr'], 
        BASE_ADDRESS64
        )
    
    
    # Last ELF header data - Entry point
    # know this because all headers in place
    numberInsert8(b, elfData.eHeader.pos['Entry'], toAddress64(len(b)))
    
    # Put in program code
    if (code):
        code(b)
      
    # rodata here?
    
    # Add the stringtable
    #! this is a collection of section headers, or should be...
    #! only do if necessary (currently unused!)
    stringTableBuild(b, elfData, ['.shstrtab', '.text', '.rodata'])
    
    ## Finish with last inserts into program header
    fileSize = len(b)
    elfData.eHeader.value['FileSize'] = fileSize
    
    # Program headers need to see this
    # Basic, loading everything using filesize.
    pheaders0Pos = elfData.pHeaders[0].pos
    programHeaderInsertSizes64(
        b, 
        pheaders0Pos['Filesz'], 
        pheaders0Pos['Memsz'], 
        fileSize
        )
    
    if (verbose):
        #print('data:')
        print(str(elfData))
    
    # allow streams strings etc.
    #? done anyway?
    outStr = outpath
    try:
        with open(outpath, "wb") as f:
            f.write(b)
    except:
        outStr = outpath.name
        with outpath as f:
            f.write(b)

    # Change permissions, so don't be evil to users or me.
    # also stat.S_IXGRP, stat.S_IXOTH
    os.chmod(outStr, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH | stat.S_IXUSR)

    if (verbose):
        print("Written to file: {}".format(outStr))
