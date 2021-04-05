#!/usr/bin/env python3

import unittest
from exceptions import BuilderError
import architecture
from tpl_autostore import (
    AutoStoreReg,
    AutoStoreStack,
    AutoStoreX64
)
import tpl_locationRoot as Loc
from tpl_vars import Var, NoVar
import tpl_types as Type


 
arch = architecture.architectureSolve(architecture.x64)

# python3 -m unittest test.test_auto_store
class TestAutoStoreRegEmpty(unittest.TestCase):
    def setUp(self):
        self.a = AutoStoreReg(arch['generalPurposeRegisters'])
        
    def test_regcount(self):        
        self.assertEqual(self.a.regCount, 14)

    def test_call(self):        
        with self.assertRaises(BuilderError):
            self.a('r14')

    def test_isAllocated(self):        
        self.assertFalse(self.a.isAllocated('r14'))

    def test_regBest(self):
        self.assertEqual(self.a.regBest(), 'r15')

    def test_findReg(self):
        self.assertEqual(self.a.findReg(2), 'r15')
        
    def test_findReg_error(self):
        with self.assertRaises(BuilderError):
            self.assertEqual(self.a.findReg(0), 'r15')
    


class TestAutoStoreReg(unittest.TestCase):
    def setUp(self):
        self.a = AutoStoreReg(arch['generalPurposeRegisters'])
        self.var = Var(
            Loc.RegisterX64('r14'), 
            Type.Bit64
        )
        self.a._set('r14', self.var)

    def test_call(self):
        self.assertEqual(self.a('r14'), self.var)
                        
    def test_isAllocated(self):        
        self.assertTrue(self.a.isAllocated('r14'))

    def test_regBest(self):
        self.assertEqual(self.a.regBest(), 'r15')

    def test_findReg(self):
        self.assertEqual(self.a.findReg(2), 'r15')
        
    def test_findReg_error(self):
        with self.assertRaises(BuilderError):
            self.assertEqual(self.a.findReg(0), 'r15')

    def test_remove(self):
        self.a.remove('r14')
        self.assertFalse(self.a.isAllocated('r14'))

    def test_remove_fail(self):
        with self.assertRaises(BuilderError):
            self.a.remove('r15')

    def test_delete(self):
        self.a.delete('r14')
        with self.assertRaises(BuilderError):
            self.a('r14')
            
            
        
from tpl_codeBuilder import *

class TestAutoStoreStackEmpty(unittest.TestCase):

    def setUp(self):
        self.a = AutoStoreStack(arch['bytesize'], 3, 1)
        self.var = Var(
            Loc.RegisterX64('rsi'), 
            Type.Bit64
        )

    def test_byteWidth(self):        
        self.assertEqual(self.a.byteWidth, 8)
        
    def test_call_fail1(self):        
        with self.assertRaises(BuilderError):
            self.a(999)

    def test_call_fail2(self):        
        with self.assertRaises(BuilderError):
            self.a(2)

    def test_findSlot(self):
        self.assertEqual(self.a.findSlot(), 2)
        
    def test_getOffset(self):
        self.assertEqual(self.a.getOffset(2), 24)

        
        
class TestAutoStoreStack(unittest.TestCase):

    def setUp(self):
        self.a = AutoStoreStack(arch['bytesize'], 3, 1)
        self.var = Var(
            Loc.StackX64(1), 
            Type.Bit64
        )
        # mimic the allocation action
        # Will be slot 2
        freeSlot = self.a.findSlot()
        self.a._set(freeSlot, self.var)

    def test_call(self):
        self.assertEqual(self.a(2), self.var) 

    def test_remove(self):
        r = self.a.remove(2)
        self.assertEqual(r, self.var)
              
    def test_remove_fail(self):
        with self.assertRaises(BuilderError):
            self.a.remove(1)
            
    def test_delete(self):
        self.a.delete(2)
        with self.assertRaises(BuilderError):
            self.a(2)
            
            
            
from tpl_codeBuilder import Builder

class TestAutoStoreX64Label(unittest.TestCase):
    def setUp(self):
        self.a = AutoStoreX64(arch, 3, 1)
        # self.var = Var(
            # Loc.RegisterX64('r14'), 
            # Type.Bit64
        # )

    def test_varROCreate(self):
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        self.assertTrue(isinstance(var.loc, Loc.RODataX64)) 

    def test_delete(self):
        var = self.a.varROCreate('ro1', Type.Bit64, 3)
        #NB for sake, its read-only
        with self.assertRaises(BuilderError):
            self.a.delete(var)

    def test_toReg_removes(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3)
        self.a.toReg(b, var, 'rsi')
        self.assertFalse(self.a.autoReg.isAllocated('r15'))  

    def test_toReg_reallocs(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3)
        self.a.toReg(b, var, 'rsi')
        self.assertTrue(self.a.autoReg.isAllocated('rsi'))  

    def test_toReg_build(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3)
        self.a.toReg(b, var, 'rsi')
        self.assertEqual(b._code[0], 'mov qword rsi, ro1') 




class TestAutoStoreX64Stack(unittest.TestCase):
    def setUp(self):
        self.a = AutoStoreX64(arch, 3, 1)
        self.var = Var(
            Loc.StackX64(2), 
            Type.Bit64
        )
                        
    def test_varStackCreate_type(self):
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.assertTrue(isinstance(var.loc, Loc.StackX64)) 
                            
    def test_varStackCreate_slot(self):
        # should allocate at last slot
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.assertEqual(var.loc.lid, 2)                             
                      
    def test_delete(self):
        # should allocate at last slot
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.delete(var)
        with self.assertRaises(BuilderError):
            self.a.autoStack(2)                       
                      
    def test_toReg_removes(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertFalse(self.a.autoReg.isAllocated('r15'))  

    def test_toReg_reallocs(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertTrue(self.a.autoReg.isAllocated('rsi'))  

    def test_toReg_build(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertEqual(b._code[0], 'mov rsi, qword [rbp - 16]')  
        
        
        
class TestAutoStoreX64Reg(unittest.TestCase):
    def setUp(self):
        # arch, sizeSlots, offset
        self.a = AutoStoreX64(arch, 3, 1)
        self.var = Var(#
            Loc.RegisterX64('r14'), 
            Type.Bit64
        )
        
    # reg create
    def test_varLabelCreate(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        self.assertEqual(var.loc.lid, 'ro1') 
        
    def test_varRegCreate(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        self.assertTrue(self.a.autoReg('rsi'), var) 

    def test_varStackCreate(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.assertTrue(self.a.autoStack.isAllocated(var.loc.lid)) 
        
        
    # Reg Reallocate
    def test_varRegCreate_double_relocate_toRegister(self):
        b = Builder()
        var1 = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        var2 = self.a.varRegCreate(b, 'rsi', Type.Bit8, 3)
        self.assertTrue(self.a.autoReg.isAllocated('r15'))  
    
    def test_varRegCreate_double_build(self):
        b = Builder()
        var1 = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        var2 = self.a.varRegCreate(b, 'rsi', Type.Bit8, 3) 
        self.assertEqual(b._code[0], 'mov qword r15, rsi')


    # delete
    def test_label_delete(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        with self.assertRaises(BuilderError):
            self.a.delete(var)
            
    def test_reg_delete(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        self.a.delete(var)
        with self.assertRaises(BuilderError):
            self.a.autoReg('rsi')  

    def test_stack_delete(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.delete(var)
        with self.assertRaises(BuilderError):
            self.a.autoStack(var.loc.lid) 
            
    # toReg
    def test_toReg_removes(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertFalse(self.a.autoReg.isAllocated('r15'))  

    def test_toReg_reallocs(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertTrue(self.a.autoReg.isAllocated('rsi'))  

    def test_toReg_build(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toReg(b, var, 'rsi')
        self.assertEqual(b._code[0], 'mov qword rsi, r15')  

    # toRegAny
    def test_toRegAny_label(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        self.a.toRegAny(b, var)
        self.assertTrue(self.a.autoReg.isAllocated(var.loc.lid))  

    def test_toRegAny_label_build(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        self.a.toRegAny(b, var)
        self.assertEqual(b._code[0], 'mov qword r15, ro1')  

    def test_toRegAny_reg(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toRegAny(b, var)
        self.assertTrue(self.a.autoReg.isAllocated(var.loc.lid))  
        
    def test_toRegAny_stack(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.toRegAny(b, var)
        self.assertTrue(self.a.autoReg.isAllocated(var.loc.lid))  

    def test_toRegAny_stack_build(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        self.a.toRegAny(b, var)
        self.assertEqual(b._code[0], 'mov r15, qword [rbp - 16]')  
                                
    # reg toStack
    def test_toStack_removes(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        slot = self.a.toStack(b, var)
        self.assertFalse(self.a.autoReg.isAllocated('r15'))  

    def test_toStack_reallocs(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toStack(b, var)
        self.assertTrue(self.a.autoStack.isAllocated(var.loc.lid))

    # other locations to stack
    def test_labelToStack_build(self):
        b = Builder()
        var = self.a.varROCreate('ro1', Type.Bit64, 3) 
        self.a.toStack(b, var)
        self.assertEqual(b._code[0], 'mov qword[rbp - 16], ro1')          

    def test_regToStack_build(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'r15', Type.Bit64, 3) 
        self.a.toStack(b, var)
        self.assertEqual(b._code[0], 'mov qword[rbp - 16], r15')      

    def test_stackToStack_build(self):
        b = Builder()
        var = self.a.varStackCreate(Type.Bit64, 3) 
        with self.assertRaises(AssertionError):
            self.a.toStack(b, var)

            
               
if __name__ == '__main__':
    unittest.main()
