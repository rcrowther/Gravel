#!/usr/bin/env python3

import unittest
from tpl_codeBuilder import *



class TestBuilder(unittest.TestCase):
    
    def setUp(self):
        self.b = Builder()
        
    def test_func_start(self):
        b = Builder()
        b.funcBegin('goNorth')
        self.assertEqual(b.currentFunc.name, 'goNorth')

    def test_func_end(self):
        b = Builder()
        b.funcBegin('goNorth')
        b.funcEnd()
        writtenFucs = b.funcs
        firstFunc = writtenFucs[0]
        self.assertEqual(firstFunc.name, 'goNorth')
        
    def test_func_stackAlloc(self):
        b = Builder()
        b.funcBegin('goNorth')
        b.stackAllocAdd('mov rbp - 8', 8)
        b.funcEnd()
        writtenFucs = b.funcs
        firstFunc = writtenFucs[0]
        self.assertEqual(firstFunc.stackAllocSize, 8)



                                
if __name__ == '__main__':
    unittest.main()
