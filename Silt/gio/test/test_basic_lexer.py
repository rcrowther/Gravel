#!/usr/bin/env python3

import unittest
from gio.test.word_lexer import WordLexer
from gio.iterators.TrackingIterator import FileIteratorTracking
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
import gio.test.word_tokens as Tokens



#python3 -m unittest gio.test.test_basic_lexer
class TestBasicLexer(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)

    def test_init(self):
        lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        # Not much to look at
        self.assertEqual(lxr.tokenLineCount, 0)
        self.assertEqual(lxr.tokenStartOffset, 0)

        
class TestFirstToken(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)
        self.lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        next(self.lxr)
                
    def test_token(self):
        self.assertEqual(self.lxr.tok, Tokens.WORD)

    def test_textOf(self):
        self.assertEqual(self.lxr.textOf(), 'Born')

    def test_line_count(self):
        self.assertEqual(self.lxr.tokenLineCount, 0)
        
    def test_offset(self):
        self.assertEqual(self.lxr.tokenStartOffset, 0)



class TestExhaustion(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)
        self.lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)

    def test_iteration(self):
        expected_tokens = [3, 3, 3, 3, 4, 3, 3, 3]
        tokens = [tok for tok in self.lxr]
        self.assertEqual(expected_tokens, tokens)

    def test_source(self):
        # Now parsed, ee can look at this
        loc = self.lxr.src.locationStr()
        self.assertEqual(loc, "gio/test/test_doc_tracker")
        

class TestLast(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)
        self.lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        for x in range(0, 8):
            next(self.lxr)
        
    def test_token(self):
        self.assertEqual(self.lxr.tok, Tokens.WORD)

    def test_textOf(self):
        self.assertEqual(self.lxr.textOf(), 'give')

    def test_line_count(self):
        self.assertEqual(self.lxr.tokenLineCount, 1)
        
    def test_offset(self):
        self.assertEqual(self.lxr.tokenStartOffset, 9)
                
