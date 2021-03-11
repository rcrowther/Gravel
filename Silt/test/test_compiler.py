#!/usr/bin/env python3

import unittest

from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from Compiler import Compiler
from gio.reporters.Sources import FileSource
from gio.iterators.TrackingIterator import FileIteratorTracking
from Lexer import Lexer
#import Tokens



from BuilderAPI import BuilderAPIX64


#python3 -m unittest test.test_compiler
class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.fp = 'test/test_doc_rubble'
        self.reporter = ReporterStreamConsole(1, 1)
        self.cpl = Compiler(self.reporter, BuilderAPIX64())

    def test_parse(self):
        lxr = Lexer(FileSource(self.fp), FileIteratorTracking(self.fp), self.reporter)
        self.cpl.parse(lxr)
