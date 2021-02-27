#!/usr/bin/env python3

import unittest
from gio.iterators.CodepointIterators import *



# python3 -m unittest test/tests.py
class TestFileIterator(unittest.TestCase):
    def test_cp_count(self):
        i = 0
        for c in FileIterator("gio/test/test_doc"):
            i += 1
        self.assertEqual(i, 352)

    def test_assert_stop(self):
        it = FileIterator("gio/test/test_doc")
        with self.assertRaises(StopIteration):
            while(True):
                next(it)
            
    def test_linestrip(self):
        pass
        
        
        
class TestStringIterator(unittest.TestCase):

    def setUp(self):
        self.test_str = "no, you jest"
        
    def test_exception_stop(self):
        i = 0
        for c in StringIterator(self.test_str):
            i += 1
        self.assertEqual(i, 13)
            
    def test_linestrip(self):
        pass



class TestStringsIterator(unittest.TestCase):

    def setUp(self):
        self.test_strs = ["no, you jest", "fnc(UnTreu)", ""]
        
    def test_exception_stop(self):
        i = 0
        for c in StringsIterator(self.test_strs):
            i += 1
        self.assertEqual(i, 26)
                            
    def test_linestrip(self):
        pass            
            
                        
if __name__ == '__main__':
    unittest.main()
