#!/usr/bin/env python3

import unittest
from tpl_types import *


class TestTypesSize(unittest.TestCase):

    def test_pointer(self):
        ptr = Pointer([Bit64])
        self.assertEqual(ptr.size, 1)

    def test_array(self):
        ary = Array([Bit64, 7])
        self.assertEqual(ary.size, 7)        

    def test_array_labeled(self):
        ary = ArrayLabeled([Bit64, 'x', 'y', 'z'])
        self.assertEqual(ary.size, 3)
        
    def test_clutch(self):
        clc = Clutch([Bit32, Bit64])
        self.assertEqual(clc.size, 2)        
        
    def test_clutch_labeled(self):
        clc = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64])       
        self.assertEqual(clc.size, 4)
        
        
        
class TestTypeContainersForBytesize(unittest.TestCase):

    def test_pointer(self):
        ptr = Pointer([Bit64])
        self.assertEqual(ptr.byteSize, 8)

    def test_array(self):
        ary = Array([Bit64, 3])
        self.assertEqual(ary.byteSize, 24)        

    def test_array_labeled(self):
        ary = ArrayLabeled([Bit64, 'x', 'y', 'z'])
        self.assertEqual(ary.byteSize, 24)
        
    def test_clutch(self):
        clc = Clutch([Bit32, Bit64])
        self.assertEqual(clc.byteSize, 12)        
        
    def test_clutch_labeled(self):
        clc = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64])       
        self.assertEqual(clc.byteSize, 17)

    def test_clutch_in_array(self):
        tpe = Array([Clutch([Bit32, Bit64]), 7])
        self.assertEqual(tpe.byteSize, 84)


        
class TestTypesOffsetForOffset(unittest.TestCase):
    # test last element, most prone to error
    
    def test_array(self):
        tpe = Array([Bit64, 3])
        self.assertEqual(tpe.offset(2), 16)

    def test_array_labeled(self):
        tpe = ArrayLabeled([Bit64, 'x', 'y', 'z'])
        self.assertEqual(tpe.offset('z'), 16)

    def test_clutch(self):
        tpe = Clutch([Bit32, Bit64])
        self.assertEqual(tpe.offset(1), 4)  

    def test_clutch_labeled(self):
        tpe = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64])       
        self.assertEqual(tpe.offset('color'), 9)

    def test_clutch_in_array(self):
        tpe = Array([Clutch([Bit32, Bit64]), 7])
        self.assertEqual(tpe.offset(6), 72)
                                                 
# class TestTypes(unittest.TestCase):

    # def setUp(self):
        # self.ptr = Pointer([Bit64])
        # self.ary = Array([Bit64, 3])
        # self.clh = Clutch([Bit32, Bit64])
        # self.clchl = ClutchLabeled(['x', Bit32, 'y', Bit32])
        
    # def test_encoding(self):
        # self.assertEqual(Bit64.encoding, Signed)

        
    # def test_typeDepth(self):
        # self.assertEqual(self.ptr.typeDepth(), 2)        
        # self.assertEqual(self.ary.typeDepth(), 2)        
        # self.assertEqual(self.clh.typeDepth(), 2) 
               
    # def test_containsTypeSingular(self):
        # # l = LocationROData('str1')
        # # self.assertEqual(l.mkRelative()(), 'str1')
        # self.assertTrue(self.ptr.containsTypeSingular()) 
        # self.assertTrue(self.ary.containsTypeSingular()) 
        # self.assertTrue(self.clh.containsTypeSingular()) 

    # def test_children_ptr(self):
        # self.assertEqual(len(self.ptr.children(['x'])), 2)
        # self.assertEqual(self.ptr.children([]), [self.ptr, Bit64])
        
   # #def test_children_clh(self):
    # #    self.assertEqual(len(self.clh.children(2)), 1)

    # #def test_children_clh(self):
        # #self.assertEqual(len(self.clh.children(['x'])), 2)
        # #self.assertEqual(self.clh.children(['x']), [self.clh, Bit32])

    # def test_children_complex(self):
        # tpe0 = Pointer([Array([ClutchLabeled( ['velocity', Bit32, 'direction', Pointer([Bit32])] ), 3] )] )
        # self.assertEqual(tpe0.byteSize, 8)
        # tpe1 = tpe0.elementType
        # self.assertEqual(tpe1.byteSize, 36)
        
        # # self.assertEqual(len(tpe.children([5, 'direction'])), 5)
        # # self.assertEqual(tpe.children([5, 'direction'])[0], tpe)
        # # self.assertEqual(tpe.children([5, 'direction'])[4], Bit32)
        # # self.assertEqual(tpe.children([5, 'direction']), [
            # # Pointer(Array(Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)}))), 
            # # Array(Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)})), 
            # # Clutch({'velocity': Bit32, 'direction': Pointer(Bit32)}), 
            # # Pointer(Bit32), 
            # # Bit32
        # # ])


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
