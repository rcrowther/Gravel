from MarkTable import ScopeTable
#from Marks import BuiltinMark
import sys



# Make the integer table
#BuiltinScopeTable = ScopeTable()

#== TraversableOnce {

#} 

#'! looks like we need a new Mark. And Marktable?
#! Wouldn't be doing this if not off integer scaope, which provides a parameter.
# However, some scopes will not provide a parameter, like a namespace?
#! add name
#Integer = ScopeTable('Integer')
Integer = ScopeTable()

def add(a, b):
    return a + b
        
# code, recievesReturn, type of params, returnType, interpreter func, description
Integer.builtinAdd('+', True, ['Integer'], 'Integer', add, "Returns the sum of this value and x")

def subtract(a, b):
    return a - b
      
Integer.builtinAdd('-', True, ['Integer'], 'Integer', subtract, "Returns the difference of this value and x")     

def multiply(a, b):
    return a * b
      
Integer.builtinAdd('*', True, ['Integer'], 'Integer', multiply, "Returns the product of this value and x")     

def divide(a, b):
    return a / b

Integer.builtinAdd('%', True, ['Integer'], 'Integer', divide, "Returns the quotient of this value and x")     


def lThan(a, b):
    return a < b

Integer.builtinAdd('<', True, ['Integer'], 'Boolean', lThan, "Returns true if this value is less than x, false otherwise.")     

def gThan(a, b):
    return a > b

Integer.builtinAdd('>', True, ['Integer'], 'Boolean', gThan, "Returns true if this value is greater than x, false otherwise.")     



def rShift(a, b):
    return a >> b

Integer.builtinAdd('>>', True, ['Integer'], 'Integer', rShift, "Returns this value bit-shifted right by the specified number of bits.")     


def lShift(a, b):
    return a << b

Integer.builtinAdd('<<', True, ['Integer'], 'Integer', lShift, "Returns this value bit-shifted left by the specified number of bits.")     


#def maxI(a):
    #return sys.maxsize

#Integer.builtinAdd('max', True, ['Integer'], 'Integer', maxI, "Returns the difference of this value and x")     


#def minI(a):
    #return -sys.maxint - 1

#Integer.builtinAdd('min', True, ['Integer'], 'Integer', minI, "Returns the difference of this value and x")     
