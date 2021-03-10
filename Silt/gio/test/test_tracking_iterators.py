#!/usr/bin/env python3

import unittest
from gio.iterators.TrackingIterator import *


# python3 -m unittest gio.test.test_tracking_iterators
class TestFileIterator(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_iterate_char_count(self):
        i = 0
        #with self.assertRaises(StopIteration):
        for c in FileIteratorTracking("gio/test/test_doc"):
            i += 1
        self.assertEqual(i, 352)

    def test_next(self):
        # Statts on line one, doesn't move
        it = FileIteratorTracking("gio/test/test_doc_tracker")
        c = chr(next(it))
        for ce in it:
            pass
        self.assertEqual(c, 'B')

    def test_offset_init(self):
        # Statts on line one, doesn't move
        it = FileIteratorTracking("gio/test/test_doc_tracker")
        c = chr(next(it))
        self.assertEqual(it.lineOffset, 0)

    def test_line_count_final(self):
        # Statts on line one, doesn't move
        it = FileIteratorTracking("gio/test/test_doc_tracker")
        for ce in it:
            pass
        self.assertEqual(it.lineCount, 1)
                    
    def get_it_part_consumed(self):
        it = FileIteratorTracking("gio/test/test_doc_tracker")
        while (it.lineCount != 1):
            next(it)
        return it
        
    def test_partconsumed_offset(self):
        it = self.get_it_part_consumed()
        self.assertEqual(it.lineOffset, 0)

    def test_partconsumed_next(self):
        # Will move down to line 1
        it = self.get_it_part_consumed()
        self.assertEqual(chr(next(it)), 'a')
                

        


                        
if __name__ == '__main__':
    unittest.main()
