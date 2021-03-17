#!/usr/bin/env python3

import unittest
from tpl_access_builders import AccessValue, AccessAddress
import tpl_locationRoot as Loc
#from tpl_types import *

 
 
# python3 -m unittest test.test_access_builders
class TestAccessValueBuilder(unittest.TestCase):
    #def setUp(self):

    def test_ro(self):
        loc = Loc.RODataX64('label')
        b = AccessValue(loc)
        self.assertEqual(b.result(), '[label]')

    def test_reg(self):
        loc = Loc.RegisterX64('r12')
        b = AccessValue(loc)
        self.assertEqual(b.result(), 'r12')

    def test_reg_no_offset(self):
        loc = Loc.RegisterX64('r12')
        b = AccessValue(loc)
        b.addOffset(8)
        with self.assertRaises(AssertionError):
            self.assertEqual(b.result(), '[r12]')

    def test_reg_no_register(self):
        loc = Loc.RegisterX64('r12')
        b = AccessValue(loc)
        b.addRegister('r12')
        with self.assertRaises(AssertionError):
            self.assertEqual(b.result(), '[r12]')
                    
    def test_reg_addr(self):
        loc = Loc.RegisteredAddressX64('r12')
        b = AccessValue(loc)
        self.assertEqual(b.result(), '[r12]')

    def test_stack(self):
        loc = Loc.StackX64(3)
        b = AccessValue(loc)
        self.assertEqual(b.result(), '[rbp-24]')                

    def test_stack_offset(self):
        loc = Loc.StackX64(3)
        b = AccessValue(loc)
        b.addOffset(8)
        self.assertEqual(b.result(), '[rbp-32]')                

    def test_stack_offset_register(self):
        loc = Loc.StackX64(3)
        b = AccessValue(loc)
        b.addOffset(8)
        b.addRegister('r12')
        self.assertEqual(b.result(), '[rbp-r12-32]')  

    def test_stack_addr(self):
        loc = Loc.StackedAddressX64(3)
        b = AccessValue(loc)
        with self.assertRaises(AssertionError):
            self.assertEqual(b.result(), '[rbp-24]')
        
        

class TestAccessAddressBuilder(unittest.TestCase):

    def test_ro(self):
        loc = Loc.RODataX64('label')
        b = AccessAddress(loc)
        self.assertEqual(b.result(), 'label')

    def test_reg(self):
        loc = Loc.RegisterX64('r12')
        b = AccessAddress(loc)
        with self.assertRaises(AssertionError):
            self.assertEqual(b.result(), 'r12')

    def test_reg_addr(self):
        loc = Loc.RegisteredAddressX64('r12')
        b = AccessAddress(loc)
        self.assertEqual(b.result(), 'r12')        

    def test_stack(self):
        loc = Loc.StackX64(3)
        b = AccessAddress(loc)
        with self.assertRaises(AssertionError):
            self.assertEqual(b.result(), '[rbp-24]')                

    def test_stack_addr(self):
        loc = Loc.StackedAddressX64(3)
        b = AccessAddress(loc)
        self.assertEqual(b.result(), '[rbp-24]')
            
               
if __name__ == '__main__':
    unittest.main()
