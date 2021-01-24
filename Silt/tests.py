#!/usr/bin/env python3

import unittest
from template import *



class TestLocationROData(unittest.TestCase):
    
    def test_str(self):
        l = LocationROData('str1')
        self.assertEqual(str(l), 'str1')

    def test_call(self):
        l = LocationROData('str1')
        self.assertEqual(l(), 'str1')
        
    # def test_mkRelative(self):
        # l = LocationROData('str1')
        # self.assertEqual(l.mkRelative()(), 'str1')


class TestLocationStack(unittest.TestCase):
                
    def test_str(self):
        l = LocationStack(3)
        self.assertEqual(str(l), '3')
        
    def test_stackByteSize(self):
        l = LocationStack(3)    
        self.assertEqual(l.stackByteSize, 8)

    def test_call(self):
        l = LocationStack(3)
        self.assertEqual(l(), 'rbp - 24')

    def test_mkRelative(self):
        l = LocationStack(3)
        self.assertEqual(l.mkRelative()(), 'rbp-24')



class TestLocationRegister(unittest.TestCase):
                
    def test_str(self):
        l = LocationRegister('rax')
        self.assertEqual(str(l), 'rax')
        
    def test_stackByteSize(self):
        l = LocationRegister('rax')
        self.assertEqual(l.stackByteSize, 8)

    def test_call(self):
        l = LocationRegister('rax')
        self.assertEqual(l(), 'rax')

    def test_mkRelative(self):
        l = LocationRegister('rax')
        self.assertEqual(l.mkRelative()(), 'rax')
                        
if __name__ == '__main__':
    unittest.main()
