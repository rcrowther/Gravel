#!/usr/bin/env python3

#? Last malloc can stay on its reg, but only if no func calls? (is that woth it?)


# C++ name mangling
# http://itanium-cxx-abi.github.io/cxx-abi/abi.html#demangler
# Will we be calling in on C++ mangled names? I don't think so.
# Beyond that, what name mangling do we need?
#? Always do returns
#?
typeEncoding = {
    "void": "v" ,
    #"wchar_t": "w" ,
    "bool": "b" ,
    #"char": "c" ,
    #"signed char": "a" ,
    "int8": "a" ,
    #"unsigned char": "h" ,
    "uint8": "h" ,
    #"short": "s" ,
    "int16": "s" ,
    #"unsigned short": "t" ,
    "uint16": "t" ,
    #"int": "i" ,
    #"unsigned int": "j" ,
    #"long": "l" ,
    "int32": "l" ,
    #"unsigned long": "m" ,
    "uint32": "m" ,
    #"long long: "x" , __int64",
    "int64": "x" ,
    #"unsigned long long: "y" , __int64",
    "uint64": "y" ,
    #"__int128": "n" ,
    "int128": "n" ,
    #"unsigned __int128": "o" ,
    "uint128": "o" ,
    #"float": "f" ,
    "float32": "f" ,
    #"double": "d" ,
    "float64": "d" ,
    #"long double: "e" , __float80",
    #"__float128": "g" ,
    "addr": "R"
    }    
       
def mangleScope(nameList):
    scopeB = []
    if (len(nameList) > 0):
        scopeB = ["N"]
        for n in nameList:
            scopeB.append(str(len(n)))          
            scopeB.append(n) 
    return scopeB
    
def mangleFunc(scopeB, name, typeList):
    scopeB.append(str(len(name)))          
    scopeB.append(name) 
    scopeB.append("E")
    typeB = []
    first = True
    for t in typeList:
        tEncode =  ''
        if (not first):
            tEncode =  '|'
        first = False
        if not t in typeEncoding:
            tEncode += t
        if t in typeEncoding:
            tEncode += typeEncoding[t]
        typeB.append(tEncode)
    return "-Z{}{}".format("".join(scopeB), "".join(typeB))


# func entry
# If there are any following calls, then parameters into a function 
# must be localised, or parameter data will be lost.
#? This would be more efficient to be only to the parameter depth of the
# called functions?
# both below
#List({param, correctPosition, localIdx})
allParams = []
localizedParams = []
if (not func.isLeafCode):    
    #func.localiseParameters
    i = 0
    for param in allParams:
        if (not param.correctPosition):
            param.localIdx = i
            i += 1
        b.append("l.alloc(byteSpace.bit64)")
        b.append("localSet(b, l({}), cParamSrc({}))".format(i) )

# Now sources are
def paramSrc(idx):
    param = allParams[idx]
    if (param.isCorrect):
        return "cParamSrc({})".format(idx)
    return "l({})".format(idx)

# func call
    funcName = ???
    # Not including correct positioned params
    # src may be a localIdx if unmodified?
    # List((pos, src))
    paramSrcList = []
    for paramSrc in paramSrcList:
        b.append("cParamSet(b, {}, {})".format(paramSrc.pos, paramSrc.src) )
    b.append("funcCall(b, \"{}\")".format(funcName))
    
def main():
    scopeB = mangleScope(["StringBuilder", "Heap"])
    mangledName = mangleFunc(scopeB, "clutch", ["StringBuilder", "int64"])
    print(mangledName)
    
if __name__== "__main__":
    main()
