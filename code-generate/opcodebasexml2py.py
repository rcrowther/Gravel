#!/usr/bin/env python3

import xml.etree.ElementTree as ET

import collections

opcodeData = []
opCodeNmcIndex = {}
opCodeCodeIndex = {}


DataRecord = collections.namedtuple('Record', 'opCode mnemomic description')

def opEntryAdd(opCode, mnemonic, desc):
    record = DataRecord(opCode, mnemonic, desc)
    opcodeData.append( record )
    if mnemonic in opCodeNmcIndex:
        opCodeNmcIndex[mnemonic].append(record)
    else:
        opCodeNmcIndex[mnemonic] = [record]
    opCodeCodeIndex[opCode] = record

def printData():
	#! improve
	for e in opcodeData:
		print(e)
		 
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
        print("expected text,in element: '{}'".format(elem))
        print("exiting...")        
        exit()			
    return t
	
def printAll(elem):
	"Print the element and sub elements"
	for e in elem.iter():
		print(e)
		
def readCode(opCodeElem):
    #opNode = getNamedNext(it, 'pri_opcd') 
    opCode = opCodeElem.attrib.get('value')
    if (not opCode):
        print("expected opcode attribute value: " + str(opCodeElem))
        exit()	
    #print(opCode)
	# <entry direction="0" op_size="1" r="yes" lock="yes">
    #    <syntax><mnem>
    # entry, always there
    entryElem = findOrFail(opCodeElem, 'entry')
    syntaxElem = findOrFail(entryElem, 'syntax')
    #printAll(syntaxElem)
    #nmonicElem = findOrFail(syntaxElem, 'mnem')
    nmonicElem = findOrNone(syntaxElem, 'mnem')
    if(nmonicElem is None):
        nmonic = '-'
    else:
        nmonic = textOrFail(nmonicElem)
    #print(nmonic)

    
    #<note><brief>
    noteElem = findOrFail(entryElem, 'note')
    briefElem = findOrFail(noteElem, 'brief')
    desc = textOrFail(briefElem)

    opEntryAdd(opCode, nmonic, desc)
        
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
print('data version: ' + root.attrib['version'])
print()

#! why fails?
oneByteBranch = findOrFail(root, 'one-byte')
opIt = oneByteBranch.iter('pri_opcd')
for e in opIt:
    readCode(e)
	
twoByteBranch = findOrFail(root, 'two-byte')
opIt = twoByteBranch.iter('pri_opcd')
for e in opIt:
    readCode(e)

# Look at this....
#printData()

print('find by opCode...')
print(searchByOpCode('FB'))
#print(str(opCodeCodeIndex))
print('find by mnemonic...')
print(searchByMnemonic('MOV'))
