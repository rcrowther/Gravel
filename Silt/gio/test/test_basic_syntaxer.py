#!/usr/bin/env python3

import unittest
from gio.test.word_lexer import WordLexer
from gio.iterators.TrackingIterator import FileIteratorTracking
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from gio.test.word_syntaxer import WordSyntaxer
from gio.exceptions import GIOSyntaxError
import gio.test.word_tokens as Tokens



#python3 -m unittest gio.test.test_basic_syntaxer
class TestBasicSyntaxer(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)
        self.syn = WordSyntaxer(self.reporter)
        self.syn.tokenToString = Tokens.tokenToString

    def test_parse(self):
        lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        self.syn.parse(lxr)
        #self.assertEqual(syn.reporter, self.reporter)
        
    # def test_parse_error(self):
        # syn = SyntaxerBase(self.reporter)
        # lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        # # should throw an error, because no syntax there
        # with self.assertRaises(NotImplementedError):
            # syn.parse(lxr)
        
    # # def test_source(self):
        # # lxr = LexerBase(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        # # self.syn.parse(lxr)
        # # loc = self.syn.src.locationStr()
        # self.assertEqual(loc, "gio/test/test_doc_tracker")

    def test_error_raises_gioerror(self):
        lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        self.syn.parse(lxr) 
        with self.assertRaises(GIOSyntaxError):
            self.syn.error('ouch!')
        

