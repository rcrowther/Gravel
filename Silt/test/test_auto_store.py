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
        self.a = AutoStoreX64(arch, 3, 1)
        self.var = Var(#
            Loc.RegisterX64('r14'), 
            Type.Bit64
        )
                
    def test_varRegCreate(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        self.assertTrue(self.a.autoReg('rsi'), var) 

    def test_varRegCreate_build(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        self.assertEqual(b._code, []) 
        
    def test_varRegCreate_double_relocate_toRegister(self):
        b = Builder()
        var1 = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        var2 = self.a.varRegCreate(b, 'rsi', Type.Bit8, 3)
        #print('test')
        #print(str(self.a.autoReg)) 
        self.assertTrue(self.a.autoReg.isAllocated('r15'))  

    #! to stack also
    
    def test_varRegCreate_double_build(self):
        b = Builder()
        var1 = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        var2 = self.a.varRegCreate(b, 'rsi', Type.Bit8, 3) 
        self.assertEqual(b._code[0], 'mov qword r15, rsi')


    # def test_varRegAnyCreate(self):
        # b = Builder()
        # var = self.a.varRegAnyCreate(b, Type.Bit64, 3) 
        # self.assertTrue(self.a.autoReg('rsi'), var) 

    # def test_varRegAnyCreate_build(self):
        # b = Builder()
        # var = self.a.varRegAnyCreate(b, Type.Bit64, 3) 
        # self.assertEqual(b._code, []) 

    def test_delete(self):
        b = Builder()
        var = self.a.varRegCreate(b, 'rsi', Type.Bit64, 3) 
        self.a.delete(var)
        with self.assertRaises(BuilderError):
            self.a.autoReg('rsi')  

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
        
######################
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
        
        

            
               
if __name__ == '__main__':
    unittest.main()
