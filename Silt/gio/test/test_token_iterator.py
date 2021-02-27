#!/usr/bin/env python3

import unittest
from gio.iterators.TrackingIterator import FileIteratorTracking
#from reporters.Position import Position
from gio.reporters.Sources import FileSource
#from gio.reporters.Reporter import Reporter
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from gio.TokenIterator import TokenIterator


# python3 -m unittest test
#python3 -m unittest test/test_token_iterator.py
#python3 -m unittest test.TestTokenIterator
#python3 -m unittest test.test_toke_iterator

class TestTokenIterator(unittest.TestCase):
    def setUp(self):
        fp = 'gio/test/test_doc_tracker'
        self.it = FileIteratorTracking(fp)
        self.reporter = ReporterStreamConsole(0, 0)
        self.tkIt = TokenIterator(FileSource(fp), self.it, self.reporter)
    

    def test_offset(self):
        self.tkIt._next()
        off = self.tkIt.tokenStartOffset
        self.assertEqual(off, 0)

    def test_error_print(self):
        self.tkIt.error("Ouch!")
        #self.assertEqual(self.rp.errorCount, 1)

    def test_skip_whitespace(self):
        self.tkIt.skipWhitespace()
        self.assertFalse(self.tkIt.isWhitespaceOrLinefeed())

    def test_load_until(self):
        self.tkIt.skipWhitespace()
        self.tkIt._loadUntil(32)
        self.assertEqual(self.tkIt.textOf(), "Born")
        
    def test_error_print_inner(self):
        self.tkIt.skipWhitespace()
        self.tkIt._loadUntil(32)
        self.tkIt._clear() 
        self.tkIt.skipWhitespace()
        self.tkIt.stashOffsets()
        self.tkIt._loadUntil(32)
        self.tkIt.error("Again! With '" + self.tkIt.textOf() + "'")

    def test_next(self):
        with self.assertRaises(NotImplementedError):
            next(self.tkIt)

   # def tearDown(self):
   #     for c in self.tkIt:
   #         pass
            
if __name__ == '__main__':
    unittest.main()
