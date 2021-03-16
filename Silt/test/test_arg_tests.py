#!/usr/bin/env python3

import unittest
from syn_arg_tests import *
import tpl_types as Type
from tpl_locationRoot import *
from Syntaxer import ProtoSymbol, Path, FuncBoolean
from tpl_vars import Base, Var



#python3 -m unittest test.test_arg_tests
class TestArgTests(unittest.TestCase):

    def test_numeric(self):
        loc = RegisterX64('rax')
        tpe = Type.Bit64
        val = Var(loc, tpe)
        self.assertTrue(numericVar()(val))

    def test_numeric_fail(self):
        loc = RegisterX64('rax')
        tpe = Type.Array([Type.Bit64, 3])
        val = Var(loc, tpe)
        self.assertFalse(numericVar()(val))

    def test_str(self):
        loc = RegisterX64('rax')
        tpe = Type.StrASCII
        val = Var(loc, tpe)
        self.assertTrue(stringVar()(val))

    def test_str_fail(self):
        loc = RegisterX64('rax')
        tpe = Type.Array([Type.Bit64, 3])
        val = Var(loc, tpe)
        self.assertFalse(stringVar()(val))
                
    def test_container_offset(self):
        loc = RegisterX64('rax')
        tpe = Type.Array([Type.Bit64, 3])
        val = Var(loc, tpe)
        self.assertTrue(containerOffsetVar()(val))

    def test_container_offset_fail(self):
        loc = RegisterX64('rax')
        tpe = Type.Bit64
        val = Var(loc, tpe)
        self.assertFalse(containerOffsetVar()(val))

    #! complete
    def test_int(self):
        val = 9
        self.assertTrue(intVal()(val))

    def test_int_fail(self):
        val = "9"
        self.assertFalse(intVal()(val))

    def test_anyvar(self):
        loc = RegisterX64('rax')
        tpe = Type.Bit64
        val = Var(loc, tpe)
        self.assertTrue(anyVar()(val))

    def test_anyvar_fail(self):
        val = "9"
        self.assertFalse(anyVar()(val))

    def test_anytype(self):
        val = Type.Bit64
        self.assertTrue(anyType()(val))

    def test_anytype_fail(self):
        val = "9"
        self.assertFalse(anyType()(val))

    #! complete
    def test_int_or_numeric(self):
        loc = RegisterX64('rax')
        tpe = Type.Bit64
        val = Var(loc, tpe)
        self.assertTrue(intOrVarNumeric()(val))

    def test_int_or_numeric_int(self):
        val = 9
        self.assertTrue(intOrVarNumeric()(val))
        
    def test_int_or_numeric_fail(self):
        val = "9"
        self.assertFalse(intOrVarNumeric()(val))
                
if __name__ == '__main__':
    unittest.main()
