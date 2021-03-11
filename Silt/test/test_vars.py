#!/usr/bin/env python3

import unittest
from tpl_types import *
import tpl_vars as Var


class TestRO(unittest.TestCase):
    def setUp(self):
        tpe = StrASCII
        self.var = Var.ROX64('ro1', tpe)

    def test_accessMk(self):
        self.assertEqual(self.var.accessMk(), 'ro1')



class TestAcessDeepMk(unittest.TestCase):
    def setUp(self):
        innerTpe = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64]) 
        self.tpe = Array([innerTpe, 7])
        #self.var = Var.ROX64('ro1', tpe)
        #self.var = Var.StackX64(4, tpe)
        
    def test_reg(self):
        self.var = Var.RegX64('rbx', self.tpe)
        self.assertEqual(self.var.accessDeepMk([6, 'color']), '[rbx+111]')

        
    def test_stack(self):
        var = Var.StackX64('rbx', self.tpe)
        self.assertEqual(var.accessDeepMk([6, 'color']), '[rbp+111]')                        
                        
if __name__ == '__main__':
    unittest.main()
