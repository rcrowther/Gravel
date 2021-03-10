#!/usr/bin/env python3

import unittest
from tpl_address_builder import *
#from tpl_types import *

#! Status of this object unknow, though unlikely to disappear
# python3 -m unittest tests.test_address_builder
class TestAddressBuilder(unittest.TestCase):
    #def setUp(self):

    def test_build(self):
        b = AddressBuilder('rsp')
        self.assertEqual(b.result(False), 'rsp')

    def test_offset(self):
        b = AddressBuilder('rsp')
        b.addOffset(8)
        self.assertEqual(b.result(False), 'rsp+8')

    def test_negative_offset(self):
        b = AddressBuilder('rsp')
        b.addOffset(-8)
        self.assertEqual(b.result(False), 'rsp-8')
        
    def test_cumulative_offset(self):
        b = AddressBuilder('rsp')
        b.addOffset(8)
        b.addOffset(8)
        self.assertEqual(b.result(False), 'rsp+16')        

    def test_asAdress(self):
        b = AddressBuilder('rsp')
        b.addOffset(8)
        self.assertEqual(b.result(True), '[rsp+8]') 
        

if __name__ == '__main__':
    unittest.main()
