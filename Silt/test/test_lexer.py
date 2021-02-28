#!/usr/bin/env python3

import unittest
from gio.iterators.TrackingIterator import FileIteratorTracking
#from reporters.Position import Position
from gio.reporters.Sources import FileSource
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole
from Lexer import Lexer
import Tokens



# python3 -m unittest test
#python3 -m unittest test/test_token_iterator.py
#python3 -m unittest test.TestTokenIterator
#python3 -m unittest test.test_toke_iterator

class TestLexer(unittest.TestCase):
    def setUp(self):
        self.fp = 'test/test_doc_rubble'
        self.it = FileIteratorTracking(self.fp)
        self.reporter = ReporterStreamConsole(1, 1)
        self.tkIt = Lexer(FileSource(self.fp), self.it, self.reporter)
    
    def test_source(self):
        loc = self.tkIt.src.locationStr()
        self.assertEqual(loc, "test/test_doc_rubble")

    def test_token_count(self):
        i = 0
        for tok in self.tkIt:
            i += 1
        self.assertEqual(i, 58)
        
    def test_tok_start(self):
        tkIt = Lexer(FileSource(self.fp), self.it, self.reporter)
        tok = next(tkIt)
        self.assertEqual(tok, Tokens.LINEFEED)
        tok = next(tkIt)
        self.assertEqual(tok, Tokens.IDENTIFIER)
        
    def test_tok_end(self):
        for t in self.tkIt:
            tok = t
        self.assertEqual(tok, Tokens.RBRACKET)

    def test_tokens_all(self):
        fp = 'test/test_doc_tokens_all'
        it = FileIteratorTracking(fp)
        tkIt = Lexer(FileSource(self.fp), it, self.reporter)
        outStream = [tok for tok in tkIt]
        anticipatedStream = [
            Tokens.COMMENT,
            Tokens.MULTILINE_COMMENT,
            Tokens.LINEFEED,
            Tokens.STRING,
            Tokens.LINEFEED,
            Tokens.MULTILINE_STRING,
            Tokens.LINEFEED,
            Tokens.INT_NUM, Tokens.FLOAT_NUM,
            Tokens.LINEFEED,
            Tokens.COMMA, Tokens.COLON, Tokens.LBRACKET, Tokens.RBRACKET,
            Tokens.LINEFEED,
            Tokens.IDENTIFIER, Tokens.IDENTIFIER, Tokens.STRING,
        ]
        self.assertEqual(outStream, anticipatedStream)
