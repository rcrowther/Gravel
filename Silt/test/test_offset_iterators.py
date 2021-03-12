#!/usr/bin/env python3

import unittest
from collections import OrderedDict
import tpl_offset_iterators as It
from tpl_types import *



#python3 -m unittest test.test_offset_iterators
class TestOffsetIterators(unittest.TestCase):

    def test_indexd_generator(self):
        it = It.OffsetIteratorIndexedGenerator(3, Bit16)
        o = [x for x in it]
        self.assertEqual(o, [(0, Bit16), (2, Bit16), (4, Bit16)])

    def test_map_cached(self):
        #c = OrderedDict('x': Types.Bit9, 'y': Types.Bit8, 'color': Types.Bit32, 'size': Types.Bit8)
        c = OrderedDict(x = Bit8, y = Bit8, color = Bit32, size = Bit8)
        it = It.OffsetIteratorMapCached(c)
        o = [x for x in it]
        self.assertEqual(o,  [(0, Bit8), (1, Bit8), (2, Bit32), (6, Bit8)])

    def test_list_cached(self):
        c = [Bit8, Bit8, Bit32, Bit8]
        it = It.OffsetIteratorListCached(c)
        o = [x for x in it]
        self.assertEqual(o,  [(0, Bit8), (1, Bit8), (2, Bit32), (6, Bit8)])


    # def test_array_labeled(self):
        # ary = ArrayLabeled([Bit64, 'x', 'y', 'z'])
        # self.assertEqual(ary.size, 3)
        
    # def test_clutch(self):
        # clc = Clutch([Bit32, Bit64])
        # self.assertEqual(clc.size, 2)        
        
    # def test_clutch_labeled(self):
        # clc = ClutchLabeled(['x', Bit32, 'y', Bit32, 'size', Bit8, 'color', Bit64])       
        # self.assertEqual(clc.size, 4)
        

                        
if __name__ == '__main__':
    unittest.main()
