#!/usr/bin/env python3

import unittest
from tpl_types import *



class TestTypes(unittest.TestCase):

    def setUp(self):
        self.ptr = Pointer(Bit64)
        self.ary = Array(Bit64)
        self.clh = Clutch({'x': Bit32, 'y': Bit32})
        
    def test_encoding(self):
        self.assertEqual(Bit64.encoding, Signed)

    def test_byteSize(self):
        self.assertEqual(Bit64.byteSize, 8)
        self.assertEqual(self.ptr.byteSize, None)        
        self.assertEqual(self.ary.byteSize, None)        
        self.assertEqual(self.clh.byteSize, 8)
        
    def test_typeDepth(self):
        self.assertEqual(self.ptr.typeDepth(), 2)        
        self.assertEqual(self.ary.typeDepth(), 2)        
        self.assertEqual(self.clh.typeDepth(), 2) 
               
    def test_containsTypeSingular(self):
        # l = LocationROData('str1')
        # self.assertEqual(l.mkRelative()(), 'str1')
        self.assertTrue(self.ptr.containsTypeSingular()) 
        self.assertTrue(self.ary.containsTypeSingular()) 
        self.assertTrue(self.clh.containsTypeSingular()) 

    def test_children_ptr(self):
        self.assertEqual(len(self.ptr.children(['x'])), 2)
        self.assertEqual(self.ptr.children([]), [self.ptr, Bit64])
        
    def test_children_clh(self):
        self.assertEqual(len(self.clh.children(['x'])), 2)
        self.assertEqual(self.clh.children(['x']), [self.clh, Bit32])

    def test_children_complex(self):
        tpe = Pointer(Array(Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)})))
        self.assertEqual(len(tpe.children([5, 'direction'])), 5)
        self.assertEqual(tpe.children([5, 'direction'])[0], tpe)
        self.assertEqual(tpe.children([5, 'direction'])[4], Bit32)
        # self.assertEqual(tpe.children([5, 'direction']), [
            # Pointer(Array(Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)}))), 
            # Array(Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)})), 
            # Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)}), 
            # Pointer(Bit32), 
            # Bit32
        # ])


# class TestLocationStack(unittest.TestCase):

                        
    # def test_str(self):
        # self.assertEqual(str(self.l), '3')
        
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