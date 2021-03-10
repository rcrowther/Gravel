#!/usr/bin/env python3

import unittest
from gio.test.word_lexer import WordLexer
from gio.iterators.TrackingIterator import FileIteratorTracking
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from gio.SyntaxerBase import SyntaxerBase



# python3 -m unittest test
#python3 -m unittest test.test_syntaxer_base
class TestSyntaxerBase(unittest.TestCase):
    def setUp(self):
        self.fp = 'gio/test/test_doc_tracker'
        self.reporter = ReporterStreamConsole(1, 1)

    def test_init(self):
        syn = SyntaxerBase(self.reporter)
        # No iterator src or tok to start, not much to look at
        self.assertEqual(syn.reporter, self.reporter)
                
    def test_no_syntax_raises_notimplemented(self):
        syn = SyntaxerBase(self.reporter)
        lxr = WordLexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        # should throw an error, because no syntax there
        with self.assertRaises(NotImplementedError):
            syn.parse(lxr)
        


        

