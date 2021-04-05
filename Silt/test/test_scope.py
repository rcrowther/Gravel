#!/usr/bin/env python3

import unittest
import tpl_types as Type
from tpl_locationRoot import *
from Syntaxer import ProtoSymbol, Path, FuncBoolean
from tpl_vars import Var
from tpl_locationRoot import (
    RegisterX64, 
    RegisteredAddressX64
)
from ci_scope import Scope

from collections import namedtuple

TestEntry = namedtuple('TestEntry', ['name', 'data'])




#python3 -m unittest test.test_scope
class TestScope(unittest.TestCase):

    def setUp(self):
        self.obj1 = TestEntry('plod', 3)
        self.obj2 = TestEntry('slowly', 5)
        self.obj3 = TestEntry('on', 7)

    def test_empty(self):
        s = Scope.empty()
        self.assertEqual(s.depth, 0)

    def test_size(self):
        s = Scope.empty()
        self.assertEqual(s.size(), 0)
        
    def test_add(self):
        s = Scope.empty()
        s.add(self.obj1)
        self.assertEqual(s.depth, 0)

    def test_add_fail(self):
        s = Scope.empty()
        with self.assertRaises(AssertionError):
            s.add(5)

    def test_size_non_empty(self):
        s = Scope.empty()
        s.add(self.obj1)
        self.assertEqual(s.size(), 1)

    def test_size_multi(self):
        s = Scope.empty()
        s.add(self.obj1)
        s.add(self.obj2)
        self.assertEqual(s.size(), 2)
                            
    def test_toList(self):
        s = Scope.empty()
        s.add(self.obj1)
        s.add(self.obj2)
        self.assertEqual(s.toList(), [self.obj2, self.obj1 ])
            
    def test_call(self):
        s = Scope.empty()
        s.add(self.obj1)
        r = s('plod')
        self.assertEqual(r, self.obj1)        
        
    def test_call_fail(self):
        s = Scope.empty()
        s.add(self.obj1)
        r = s('slowly')
        self.assertEqual(r, None)
            
    def test_call_is_last_in(self):
        s = Scope.empty()
        e1 = TestEntry('plod', 3)
        s.add(e1)
        e2 = TestEntry('plod', 3)
        s.add(e2)
        e3 = TestEntry('plod', 3)
        s.add(e3)
        r = s('plod')
        self.assertEqual(r, e3)  
        
    def test_findAllByName(self):
        s = Scope.empty()
        e1 = TestEntry('plod', 3)
        s.add(e1)
        e2 = TestEntry('plod', 3)
        s.add(e2)
        e3 = TestEntry('plod', 3)
        s.add(e3)
        it = s.findAllByName('plod')
        r = [obj for obj in it]
        self.assertEqual(r, [e3, e2, e1]) 
                
    def test_nested_depth(self):
        s = Scope.empty()
        s.add(self.obj1)
        ns = s.nestedScope()
        self.assertEqual(ns.depth, 1)  

    def test_nested_inherits(self):
        s = Scope.empty()
        s.add(self.obj1)
        ns = s.nestedScope()
        r = s('plod')
        self.assertEqual(r, self.obj1) 

    def test_nested_add(self):
        s = Scope.empty()
        s.add(self.obj1)
        ns = s.nestedScope()
        ns.add(self.obj2)
        r = ns('slowly')
        self.assertEqual(r, self.obj2) 

    def test_nested_add_not_super(self):
        s = Scope.empty()
        s.add(self.obj1)
        ns = s.nestedScope()
        ns.add(self.obj2)
        r = s('slowly')
        self.assertEqual(r, None)
        

    def test_nested_findAllNested(self):
        s = Scope.empty()
        s.add(self.obj1)
        ns = s.nestedScope()
        ns.add(self.obj2)
        ns.add(self.obj3)
        it = ns.findAllNested()
        r = [obj for obj in it]
        self.assertEqual(r, [self.obj3, self.obj2]) 
                 
if __name__ == '__main__':
    unittest.main()
