#!/usr/bin/env python3

import xml.etree.ElementTree as ET

import collections

from sys import exit

#? Check if this is all instructions
# 427 according to a bit of text editing searching for 'pri_opcd'
# This has more!

# Simple list of opcodes as DataRecords
# [DataRecord, DataRecord, ...]
opcodeData = []
# {mnemonic : [Datarecord]}
opCodeNmcIndex = {}
# {opcode : Datarecord}
opCodeCodeIndex = {}


DataRecord = collections.namedtuple('Record', 'opCode op1 op2 mnemomic description')

generatorReport = {}

def printReport(report):
    print('generatorReport:')
    for k,v in report.items():
        print("  {}: {}".format(k,v))

def printData():
	#! improve -- How?
	for e in opcodeData:
		print(e)

                
def opEntryAdd(opCode, op1, op2, mnemonic, desc):
    # Add a record to the database
    record = DataRecord(opCode, op1, op2, mnemonic, desc)
    opcodeData.append( record )
    if mnemonic in opCodeNmcIndex:
        opCodeNmcIndex[mnemonic].append(record)
    else:
        opCodeNmcIndex[mnemonic] = [record]
    opCodeCodeIndex[opCode] = record

def searchByMnemonic(nmc):
	return opCodeNmcIndex.get(nmc)

def searchByOpCode(opCode):
	return opCodeCodeIndex.get(opCode)
	
def getNamedNext(it, tag):
    try:
        node = it.__next__()
    except StopIteration:
        print('no tag found')
        exit()	
    if (node.tag != tag):
        print("expected tag: '" + tag)
        print("on node: '{}'".format(node))
        print("not found, exiting...")
        exit()	
    return node

def findOrFail(elem, tag):
    e = elem.find(tag)
    # NB: My version of the parser still returns False for elements 
    # with no children
    if (e is None):
        print("expected element tag: '{}'".format(tag))
        print("in element: '{}'".format(elem))
        print("sub elements:")
        printAll(elem)
        print('dump:')
        printData()
        print("not found, exiting...")
        exit()	
    return e
  
def findOrNone(elem, tag):
    return elem.find(tag)
    
def textOrFail(elem):
    t = elem.text
    if (not t):
        #print("expected text: element: '{}'".format("".join(elem.itertext())))
        print("expected text: element: '{}'".format(elem))
        print("exiting...")        
        exit()			
    return t
	
def printAll(elem):
	"Print the element and sub elements"
	for e in elem.iter():
		print(e)
		
def readCode(opCodeElem):
    # Read a single opcode from the XML
    #opNode = getNamedNext(it, 'pri_opcd') 
    opCode = opCodeElem.attrib.get('value')
    if (not opCode):
        #print("expected opcode attribute value: " + "".join(opCodeElem.itertext()))
        print("expected opcode attribute value: " + str(opCodeElem))
        exit()	
    #print(opCode)

    # entry, always there
    entryElem = findOrFail(opCodeElem, 'entry')
    syntaxElem = findOrFail(entryElem, 'syntax')
    # Some entries do not have a nmonic, so don't fail
    nmonicElem = findOrNone(syntaxElem, 'mnem')
    if(nmonicElem is None):
        nmonic = '-'
    else:
        nmonic = textOrFail(nmonicElem)

    # Some entries do not have a dstElem, so don't fail  
    dstElem = findOrNone(syntaxElem, 'dst')
    if(dstElem is None):
        dstOp = None
    else:
        dstOp = dstElem.text

    # Many entries do not have a srcElem, so don't fail 
    # Also, there are sub-elements in several,
    # so .text will fail? 
    srcElem = findOrNone(syntaxElem, 'src')
    if(srcElem is None):
        srcOp = None
    else:
        srcOp = srcElem.text
    #print(srcOp)
    #? Notes unused
    noteElem = findOrFail(entryElem, 'note')
    briefElem = findOrFail(noteElem, 'brief')
    desc = textOrFail(briefElem)

    opEntryAdd(opCode, dstOp, srcOp, nmonic, desc)


count = 0
        
tree = ET.parse('x86reference.xml')
root = tree.getroot()
it = root.iter()
#for child in root:
#	print(child.tag, child.attrib)
#refTag = root.find('x86reference')
# try:
    # root = it.__next__()
# except StopIteration:
    # print('no root tag found')
    # exit()

# if (root.tag != 'x86reference' ):
    # print('no root tag is not "x86reference"')
    # exit()
# print('data version: ' + root.attrib['version'])

#! findOrFail
root = getNamedNext(it, 'x86reference' )
generatorReport['Data version'] = root.attrib['version']

#! why fails?
oneByteBranch = findOrFail(root, 'one-byte')
opIt = oneByteBranch.iter('pri_opcd')
count1byte = 0
for e in opIt:
    count1byte += 1
    readCode(e)
	
generatorReport["One-byte instruction count"] = count1byte
# No nemonics are indexed at '-'
noNmonic1ByteCount = len(searchByMnemonic('-'))
generatorReport["One-byte no-nmonic count"] = noNmonic1ByteCount

twoByteBranch = findOrFail(root, 'two-byte')
opIt = twoByteBranch.iter('pri_opcd')
count2byte = 0
for e in opIt:
    count2byte += 1
    readCode(e)

generatorReport["Two-byte instruction count"] = count2byte
# No nemonics are indexed at '-'
noNmonic2ByteCount = len(searchByMnemonic('-'))
generatorReport["Two-byte no-nmonic count"] = noNmonic2ByteCount - noNmonic1ByteCount

generatorReport["Instruction count"] = count1byte + count2byte


# Look at this....
printData()

printReport(generatorReport)
#print('find by opCode...')
#print(searchByOpCode('FB'))
#print(str(opCodeCodeIndex))
#print('find by mnemonic...')
#print(searchByMnemonic('MOV'))
#print('find by mnemonic...')
#print(searchByMnemonic('-'))
