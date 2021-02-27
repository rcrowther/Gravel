#!/usr/bin/env python3

import unittest
from gio.iterators.TrackingIterator import FileIteratorTracking
#from reporters.Position import Position
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from TokenIterator import TokenIterator
import Tokens



# python3 -m unittest test
#python3 -m unittest test/test_token_iterator.py
#python3 -m unittest test.TestTokenIterator
#python3 -m unittest test.test_toke_iterator

class TestTokenIterator(unittest.TestCase):
    def setUp(self):
        self.fp = 'test/test_doc_rubble'
        self.it = FileIteratorTracking(self.fp)
        self.reporter = ReporterStreamConsole(1, 1)
        self.tkIt = TokenIterator(FileSource(self.fp), self.it, self.reporter)
    
    def test_source(self):
        loc = self.tkIt.src.locationStr()
        self.assertEqual(loc, "test/test_doc_rubble")

    def test_token_count(self):
        i = 0
        for tok in self.tkIt:
            i += 1
        self.assertEqual(i, 58)
        
    def test_tok_start(self):
        tkIt = TokenIterator(FileSource(self.fp), self.it, self.reporter)
        tok = next(tkIt)
        self.assertEqual(tok, Tokens.LINEFEED)
        tok = next(tkIt)
        self.assertEqual(tok, Tokens.IDENTIFIER)
        
    def test_tok_end(self):
        for t in self.tkIt:
            tok = t
        self.assertEqual(tok, Tokens.RBRACKET)
