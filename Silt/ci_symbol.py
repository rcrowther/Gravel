#!/usr/bin/env python3

from tpl_types import Type


class Symbol():
    '''
    A symbol within the code.
    Symbols are a limited item in Rubble. They are not like LISP labels.
    They represent only user-defined labels e.g. var and function 
    labels. Their main purpose is to place user labels in scopes for 
    easy user reference. 
    
    This is a base for use in other kinds of symbols e.g. SymbolVar,
    SymbolGlobal, SymbolFunc etc.
    
    The class ensures the presence of the attributes name, type and some 
    sort of data.
    '''
    # data would be a big refactor, and anyhow I want it specifically 
    #named for now
    def __init__(self, name, tpe):
        assert isinstance(tpe, Type), "Parameter not a Type. tpe: '{}'".format(tpe)
        self.name = name
        #self.data = data
        self.tpe = tpe
        
    def __repr__(self):
        return f"Symbol({self.name}, {self.tpe})"



# Not interested what the type of a builtin func is? Not at present...
class SymbolBuiltinFunc(Symbol):
    def __init__(self, name, data, tpe):
        super().__init__(name, tpe)
        self.data = data

    def __repr__(self):
        return f"SymbolBuiltinFunc('{self.name}')"
