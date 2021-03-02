#!/usr/bin/env python3

import unittest
from template import *
from tpl_types import *


class TestVars(unittest.TestCase):
    def setUp(self):
        self.lit = Literal(Bit32, 777)

    def test_literal(self):
        self.assertEqual(self.lit(), '777')

    def test_literal_withAnnot(self):
        self.assertEqual(self.lit.withAnnot(), 'dword 777')

                        
                        
if __name__ == '__main__':
    unittest.main()
