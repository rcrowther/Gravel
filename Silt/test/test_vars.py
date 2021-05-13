#!/usr/bin/env python3

import unittest
from tpl_types import *
import tpl_vars as Var
import tpl_locationRoot as Loc
from tpl_codeBuilder import Builder



# python3 -m unittest test.test_vars
class TestInit(unittest.TestCase):

    def test_init(self):
        tpe = Bit64
        loc = Loc.RegisterX64('rsi')
        var = Var.Var('testVar', loc, tpe)
        self.assertEqual(var.tpe, Bit64)

    def test_init_fail1(self):
        tpe = Bit64
        loc = 'rsi'
        with self.assertRaises(Exception):
            Var.Var('testVar', loc, tpe)

    def test_init_fail2(self):
        tpe = 'rsi'
        loc = Loc.RegisterX64('rsi')
        with self.assertRaises(Exception):
            Var.Var('testVar', loc, tpe)
        
        
        
#? Potentially a LOT of these
import architecture
arch = architecture.architectureSolve(architecture.x64)

class TestUpdateLocationROToReg(unittest.TestCase):
    def setUp(self):
        self.ul = Var.UpdateLocationBuilder(arch)
        tpe = Bit64
        loc = Loc.GlobalROAddressX64('pi')
        self.var = Var.Var('testVar', loc, tpe) 
        self.b = Builder()        
        self.ul.toRegister(self.b, self.var, 'rbx')  
    
    def test_toReg_reg(self):
        self.assertEqual(self.var.loc.lid, 'rbx')                        

    def test_toReg_tpe(self):
        self.assertEqual(self.var.tpe, Bit64)   

    def test_toReg_build(self):
        self.assertEqual(self.b._code[0], 'mov qword rbx, pi')  
        
        
        
class TestUpdateLocationRegToReg(unittest.TestCase):
    def setUp(self):
        self.ul = Var.UpdateLocationBuilder(arch)
        tpe = Bit64
        loc = Loc.RegisterX64('rsi')
        self.var = Var.Var('testVar', loc, tpe) 
        self.b = Builder()        
        self.ul.toRegister(self.b, self.var, 'rax')  
    
    def test_toReg_reg(self):
        self.assertEqual(self.var.loc.lid, 'rax')                        

    def test_toReg_tpe(self):
        self.assertEqual(self.var.tpe, Bit64)   

    def test_toReg_build(self):
        self.assertEqual(self.b._code[0], 'mov qword rax, rsi')  
        
        
        
class TestUpdateLocationRegToStack(unittest.TestCase):
    def setUp(self):
        self.ul = Var.UpdateLocationBuilder(arch)
        tpe = Bit64
        loc = Loc.RegisterX64('rax')
        self.var = Var.Var('testVar', loc, tpe) 
        self.b = Builder()        
        self.ul.toStack(self.b, self.var, 3)  
    
    def test_toReg_slot(self):
        self.assertEqual(self.var.loc.lid, 3)                        

    def test_toReg_tpe(self):
        self.assertEqual(self.var.tpe, Bit64)   

    def test_toReg_build(self):
        self.assertEqual(self.b._code[0], 'mov qword[rbp - 24], rax')  



# class TestAcessDeepMk(unittest.TestCase):
    # def setUp(self):
        # innerTpe = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64]) 
        # self.tpe = Array([innerTpe, 7])
        # #self.var = Var.ROX64('ro1', tpe)
        # #self.var = Var.StackX64(4, tpe)
        
    # def test_reg(self):
        # self.var = Var.RegX64('rbx', self.tpe)
        # self.assertEqual(self.var.accessDeepMk([6, 'color']), '[rbx+111]')

        
    # def test_stack(self):
        # var = Var.StackX64('rbx', self.tpe)
        # self.assertEqual(var.accessDeepMk([6, 'color']), '[rbp+111]')                        
                        
if __name__ == '__main__':
    unittest.main()
