#!/usr/bin/env python3

import unittest
from template import *
#from tpl_types import *


class TestRelativeAddress(unittest.TestCase):
    #def setUp(self):

    def test_build(self):
        ra = AddressRelative()
        ra.base('rax')
        ra.index('rcx')
        ra.scale(4)
        ra.displacement(42)
        self.assertEqual(ra(), 'rax+rcx*4+42')

    def test_negative_displacement(self):
        ra = AddressRelative()
        ra.base('rax')
        ra.index('rcx')
        ra.scale(4)
        ra.displacement(-42)
        self.assertEqual(ra(), 'rax+rcx*4-42')
        

#LocationRelariveBuilder

class TestAddressRelative(unittest.TestCase):
    def test_build(self):
        b = AddressRelativeBuilder()
        b.register('rax')
        b.register('rcx')
        b.offset(42)
        self.assertEqual(b.result(), 'rax+rcx+42')    

    def test_build_throws_register(self):
        b = AddressRelativeBuilder()
        b.register('rax')
        b.register('rcx')
        with self.assertRaises(ValueError):
            b.register('rbx')

    def test_build_throws_offset(self):
        b = AddressRelativeBuilder()
        b.offset(64)
        with self.assertRaises(ValueError):
            b.offset(32)

    def test_type_split(self):
        tpe = Pointer(Array(Pointer(Bit64)))
        split = relativeGettableSplit(tpe, [4])
        #self.assertEqual(split.loadable, [Pointer, Array, Pointer, Bit64])    
        self.assertEqual(split.relative, [Pointer, Array, Pointer, Bit64])    
        
if __name__ == '__main__':
    unittest.main()
