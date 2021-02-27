#!/usr/bin/env python3

import unittest
from gio.iterators.TrackingIterator import *
from gio.reporters.Message import Message
from gio.reporters.Sources import FileSource
from gio.reporters.Position import Position
from gio.reporters.Reporter import Reporter
from gio.reporters.ReporterStreamConsole import ReporterStreamConsole



# python3 -m unittest test/tests
class TestMessage(unittest.TestCase):
    def setUp(self):
        self.pos = Position(0, 7)
        self.msg = Message.withPos('Rain', FileSource('some/path/end.py'), self.pos, 'return a')
    
    def test_caret(self):
        self.assertEqual(self.msg.toOffsetCaretString(), '       ^')



class TestReporter(unittest.TestCase):
    def setUp(self):
        self.pos = Position(0, 7)
        self.msg = Message.withPos('Rain', FileSource('some/path/end.py'), self.pos, 'return a')
        self.rp = Reporter(0, 0)
    
    def testerror(self):
        self.rp.error(self.msg)
        self.assertEqual(self.rp.errorCount, 1)

    def testIsEmpty(self):
        self.assertEqual(self.rp.isEmpty(), True)

    def testIsEmptyNot(self):
        self.rp.error(self.msg)
        self.assertEqual(self.rp.isEmpty(), False)        


        
class TestReporterStreamConsole(unittest.TestCase):
    def setUp(self):
        self.pos = Position(0, 7)
        self.msg = Message.withPos('Rain', FileSource('some/path/end.py'), self.pos, 'return a')
        self.rp = ReporterStreamConsole(0, 0)        

    def testerror(self):
        self.rp.error(self.msg)
        self.assertEqual(self.rp.errorCount, 1)

    def testSummary(self):
        self.rp.error(self.msg)
        self.rp.warning(self.msg)
        self.rp.info(self.msg)
        self.rp.summary()
        #self.assertEqual(self.rp.errorCount, 1)        

    def testSummaryMulti(self):
        self.rp.error(self.msg)
        self.rp.error(self.msg)
        self.rp.warning(self.msg)
        self.rp.warning(self.msg)
        self.rp.info(self.msg)
        self.rp.info(self.msg)
        self.rp.summary()
        
    def testOffsets(self):        
        rp = ReporterStreamConsole(1, 1)   
        rp.error(self.msg)
        b = []
        rp.posStr(b, self.pos, False)
        self.assertEqual("".join(b), ":1/8:")        
             
if __name__ == '__main__':
    unittest.main()
