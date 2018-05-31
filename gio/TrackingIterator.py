
from Codepoints import LINE_FEED

## from 1
#File "s.py", line 3, in <module>
#rint("Hello")
#NameError: name 'rint' is not defined

## from 1
#/home/rob/Code/python/x64_compiler/s.scala:5: error: not found: value rintln
#rintln("Hello")
#^
#one error found

## from 1
#s.rb:5:in `<main>': undefined method `rint' for main:Object (NoMethodError)

class TrackingIterator():
    '''
    LineCount starts from 1.
    lineOffset starts from 0 (col:...).
    lineOffset and lineCount are designed to give the point
    when read after next().
    '''

    def __init__(self, codepointIt):
        self.it = codepointIt
        self._lineOffset = 0
        self._lineCount = 1
        self.lineOffset = 0
        self.lineCount = 1
                    
    def __iter__(self):
        return self
        
    def __next__(self):
        c = self.it.__next__()
        self.lineCount  = self._lineCount
        self.lineOffset = self._lineOffset
        self._lineOffset += 1
        if (c == LINE_FEED):
            self._lineCount += 1
            self._lineOffset = 0
        return c
