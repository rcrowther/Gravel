#!/usr/bin/env python3

import unittest
from exceptions import BuilderError
import architecture
from tpl_autostore import (
    AutoStoreReg,
    AutoStoreStack,
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
        self.a.remove('r15')
        self.assertFalse(self.a.isAllocated('r15'))

        
from tpl_codeBuilder import *


class TestAutoStoreStack(unittest.TestCase):

    def setUp(self):
        self.a = AutoStoreStack(arch['bytesize'], 3, 1)
        self.var = Var(
            Loc.RegisterX64('rsi'), 
            Type.Bit64
        )
                
    # def test_push_code(self):
        # b = Builder()
        # self.a.pushStack(self.var)
        # self.assertEqual(b._code[0], 'push rsi')

    # def test_push_offset(self):
        # self.a.pushStack(self.var)
        # self.assertEqual(self.a.stackTrack[0].offset, -8)  

    # def test_push_track_offset(self):
        # self.a.pushStack(self.var)
        # self.assertEqual(self.a.currOffset, -8)        

    # def test_pop_offset(self):
        # self.a.pushStack(self.var)
        # dataStack = self.a.popStack()
        # self.assertEqual(dataStack.offset, -8) 
        
    # def test_pop_track_offset(self):
        # self.a.pushStack(self.var)
        # dataStack = self.a.popStack()
        # self.assertEqual(self.a.currOffset, 0)  

    # def test_push_offset_space(self):
        # self.a.pushStack(self.var)
        # self.a.addUntrackedSlotsToStack(3)
        # self.a.pushStack(self.var)
        # self.assertEqual(self.a.stackTrack[1].offset, -40)  


    # def test_pop_offset_space(self):
        # self.a.pushStack(self.var)
        # self.a.addUntrackedSlotsToStack(3)
        # self.a.pushStack(self.var)
        # dataStack = self.a.popStack()        
        # self.assertEqual(self.a.currOffset, -32)  

    # def test_pop_double_offset_space(self):
        # self.a.pushStack(self.var)
        # self.a.addUntrackedSlotsToStack(3)
        # self.a.pushStack(self.var)
        # dataStack = self.a.popStack()        
        # dataStack = self.a.popStack()        
        # self.assertEqual(self.a.currOffset, 0) 
                    
    # def test_reg_no_register(self):
        # loc = Loc.RegisterX64('r12')
        # b = AccessValue(loc)
        # b.addRegister('r12')
        # with self.assertRaises(AssertionError):
            # self.assertEqual(b.result(), '[r12]')
                    
    # def test_reg_addr(self):
        # loc = Loc.RegisteredAddressX64('r12')
        # b = AccessValue(loc)
        # self.assertEqual(b.result(), '[r12]')

    # def test_stack(self):
        # loc = Loc.StackX64(3)
        # b = AccessValue(loc)
        # self.assertEqual(b.result(), '[rbp-24]')                

    # def test_stack_offset(self):
        # loc = Loc.StackX64(3)
        # b = AccessValue(loc)
        # b.addOffset(8)
        # self.assertEqual(b.result(), '[rbp-32]')                

    # def test_stack_offset_register(self):
        # loc = Loc.StackX64(3)
        # b = AccessValue(loc)
        # b.addOffset(8)
        # b.addRegister('r12')
        # self.assertEqual(b.result(), '[rbp-r12-32]')  

    # def test_stack_addr(self):
        # loc = Loc.StackedAddressX64(3)
        # b = AccessValue(loc)
        # with self.assertRaises(AssertionError):
            # self.assertEqual(b.result(), '[rbp-24]')
        
        

# class TestAccessAddressBuilder(unittest.TestCase):

    # def test_ro(self):
        # loc = Loc.RODataX64('label')
        # b = AccessAddress(loc)
        # self.assertEqual(b.result(), 'label')

    # def test_reg(self):
        # loc = Loc.RegisterX64('r12')
        # b = AccessAddress(loc)
        # with self.assertRaises(AssertionError):
            # self.assertEqual(b.result(), 'r12')

    # def test_reg_addr(self):
        # loc = Loc.RegisteredAddressX64('r12')
        # b = AccessAddress(loc)
        # self.assertEqual(b.result(), 'r12')        

    # def test_stack(self):
        # loc = Loc.StackX64(3)
        # b = AccessAddress(loc)
        # with self.assertRaises(AssertionError):
            # self.assertEqual(b.result(), '[rbp-24]')                

    # def test_stack_addr(self):
        # loc = Loc.StackedAddressX64(3)
        # b = AccessAddress(loc)
        # self.assertEqual(b.result(), '[rbp-24]')
            
               
if __name__ == '__main__':
    unittest.main()
