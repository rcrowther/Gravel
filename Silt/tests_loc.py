#!/usr/bin/env python3

import unittest
from template import *



class TestLocationROData(unittest.TestCase):
    
    def setUp(self):
        self.l = LocationROData('str1')
        
    def test_str(self):
        self.assertEqual(str(self.l), 'str1')

    def test_call(self):
        self.assertEqual(self.l(), 'str1')
        
    # def test_mkRelative(self):
        # l = LocationROData('str1')
        # self.assertEqual(l.mkRelative()(), 'str1')

#        with self.assertRaises(TypeError):


class TestLocationStack(unittest.TestCase):

    def setUp(self):
        self.l = LocationStack(3)
                        
    def test_str(self):
        self.assertEqual(str(self.l), '3')
        
    def test_stackByteSize(self):
        self.assertEqual(self.l.stackByteSize, 8)

    def test_call(self):
        self.assertEqual(self.l(), 'rbp - 24')

    def test_mkRelative(self):
        self.assertEqual(self.l.mkRelative()(), 'rbp-24')



class TestLocationRegister(unittest.TestCase):

    def setUp(self):
        self.l = LocationRegister('rax')
                                        
    def test_str(self):
        self.assertEqual(str(self.l), 'rax')
        
    def test_stackByteSize(self):
        self.assertEqual(self.l.stackByteSize, 8)

    def test_call(self):
        self.assertEqual(self.l(), 'rax')

    def test_mkRelative(self):
        self.assertEqual(self.l.mkRelative()(), 'rax')
                        
                        
                        
if __name__ == '__main__':
    unittest.main()
