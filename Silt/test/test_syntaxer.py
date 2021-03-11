#!/usr/bin/env python3

import unittest
from Lexer import Lexer
from gio.iterators.TrackingIterator import FileIteratorTracking
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from Syntaxer import Syntaxer
from Compiler import Compiler
#import Tokens


#python3 -m unittest test.test_syntaxer
class TestSyntaxer(unittest.TestCase):
    def setUp(self):
        self.fp = 'test/test_doc_rubble'
        self.reporter = ReporterStreamConsole(1, 1)
        self.syn = Syntaxer(self.reporter)

    # def test_parse(self):
        # lxr = Lexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        # self.syn.parse(lxr)
