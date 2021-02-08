#!/usr/bin/env python3

import unittest
from tpl_codeBuilder import *



class TestBuilder(unittest.TestCase):
    
    def setUp(self):
        self.b = Builder()
        
    def test_func_init(self):
        b = Builder()
        b.funcBegin('goNorth', True)
        self.assertEqual(b.currentFunc.name, 'goNorth')

    def test_func_stored(self):
        b = Builder()
        b.funcBegin('goNorth', True)
        b.funcEnd()
        writtenFuncs = b.funcs
        firstFunc = writtenFuncs[0]
        self.assertEqual(firstFunc.name, 'goNorth')


class TestBuilderFuncs(unittest.TestCase):
    
    def test_func_name(self):     
        b = Builder()
        b.funcBegin('goNorth', True)
        b.funcEnd()        
        self.assertEqual(b.funcs[0].name, 'goNorth')

    def test_func_stackAlloc(self):
        b = Builder()
        b.funcBegin('goNorth', True)
        b.stackAlloc(8)
        b.funcEnd()
        self.assertEqual(b.funcs[0].stackAllocSize, 8)
    
    def test_func_stackAlloc_accumulates(self):
        b = Builder()
        b.funcBegin('goNorth', True)
        b.stackAlloc(8)
        b.stackAlloc(8)
        b.funcEnd()
        self.assertEqual(b.funcs[0].stackAllocSize, 16)

    def test_func_name_duplicate_error(self):     
        b = Builder()
        b.funcBegin('goNorth', True)
        b.funcEnd()   
        b.funcBegin('goNorth', True)
        with self.assertRaises(ValueError):
            b.funcEnd()   
        
        
from template import builderResolveCode
import architecture
class TestBuilderResolution(unittest.TestCase):
    def setUp(self):
    #    self.b = Builder()
        self.arch = architecture.architectureSolve(architecture.x64)       
         
    def test_func_code(self):
        # do appends get placed in resolved functions? 
        b = Builder()
        b.funcBegin('goNorth', True)
        b += '; stuff'
        b.funcEnd()
        builderResolveCode(self.arch, b)
        self.assertEqual(b._code[1], '; stuff')

    def test_func_alloc(self):     
        b = Builder()
        b.funcBegin('goNorth', True)
        b.stackAlloc(8)
        b.funcEnd()        
        builderResolveCode(self.arch, b)
        self.assertEqual(b._code[1],  'mov rsp, rsp - 8')
        
    def test_func_returnAuto(self):     
        b = Builder()
        b.funcBegin('goNorth', True)
        b.funcEnd()        
        builderResolveCode(self.arch, b)
        self.assertEqual(b._code[-1], 'ret')

    def test_func_returnAuto_false(self):     
        b = Builder()
        b.funcBegin('main', False)
        b.funcEnd()        
        builderResolveCode(self.arch, b)
        self.assertNotEqual(b._code[-1], 'ret')

                                
if __name__ == '__main__':
    unittest.main()
