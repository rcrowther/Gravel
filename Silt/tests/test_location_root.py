#!/usr/bin/env python3

import unittest
from template import *
import tpl_locationRoot as Loc



# python3 -m unittest tests.test_location_root
class TestInitialization(unittest.TestCase):
    
    def test_roData(self):
        Loc.RODataX64('str1')

    def test_roData_fail(self):
        with self.assertRaises(Exception):
            Loc.RODataX64(9)
        
    def test_register(self):
        Loc.RegisterX64('rbx')

    def test_register_fail(self):
        with self.assertRaises(Exception):
            Loc.RegisterX64('str1')

    def test_registered_address(self):
        Loc.RegisteredAddressX64('rbx')

    def test_register_address_fail(self):
        with self.assertRaises(Exception):
            Loc.RegisteredAddressX64(77)                

    def test_stack(self):
        Loc.StackX64(7)

    def test_stack_fail(self):
        with self.assertRaises(Exception):
            Loc.StackX64('rbx')        


class TestValue(unittest.TestCase):
    def test_roData(self):
        loc = Loc.RODataX64('str1')
        self.assertEqual(loc.value(), '[str1]')

    def test_register(self):
        loc = Loc.RegisterX64('rax')
        self.assertEqual(loc.value(), 'rax')

    def test_registered_address(self):
        loc = Loc.RegisteredAddressX64('rax')
        self.assertEqual(loc.value(), '[rax]')

    def test_registered_address(self):
        loc = Loc.StackX64(3)
        self.assertEqual(loc.value(), '[rbp-24]')


class TestAddr(unittest.TestCase):
    def test_roData(self):
        loc = Loc.RODataX64('str1')
        self.assertEqual(loc.address(), 'str1')

    def test_register(self):
        loc = Loc.RegisterX64('rax')
        with self.assertRaises(Exception): 
            loc.address()

    def test_registered_address(self):
        loc = Loc.RegisteredAddressX64('rax')
        self.assertEqual(loc.address(), 'rax')

    def test_registered_address(self):
        loc = Loc.StackX64(3)
        with self.assertRaises(Exception): 
            loc.address()
                    
# class TestToRegister(unittest.TestCase):

    # def test_roData(self):
        # loc = Loc.RODataX64('str1')
        # newLoc = loc.toRegister([], 'rax')
        # self.assertEqual(newLoc.lid, 'rax')


    # def test_loc_unrecognised_register(self):
        # loc = Loc.RODataX64('str1')
        # with self.assertRaises(Exception):
            # loc.toRegister([], 777)      

    # def test_toStackIndex(self):
        # loc = Loc.RegisterX64('rcx')
        # newLoc = loc.toStackIndex([], 5)
        # self.assertEqual(newLoc.lid, 5)

    # def test_toStackIndex_unrecognised_param(self):
        # loc = Loc.RegisterX64('rcx')
        # with self.assertRaises(Exception):
            # loc.toStackIndex([], 'rxx')   
        
        
###
    # def test_stackByteSize(self):
        # self.assertEqual(self.l.stackByteSize, 8)

    # def test_call(self):
        # self.assertEqual(self.l(), 'rbp - 24')

    # def test_mkRelative(self):
        # self.assertEqual(self.l.mkRelative()(), 'rbp-24')



# class TestLocationRegister(unittest.TestCase):

    # def setUp(self):
        # self.l = LocationRegister('rax')
                                        
    # def test_str(self):
        # self.assertEqual(str(self.l), 'rax')
        
    # def test_stackByteSize(self):
        # self.assertEqual(self.l.stackByteSize, 8)

    # def test_call(self):
        # self.assertEqual(self.l(), 'rax')

    # def test_mkRelative(self):
        # self.assertEqual(self.l.mkRelative()(), 'rax')
                        
                        
                        
if __name__ == '__main__':
    unittest.main()
