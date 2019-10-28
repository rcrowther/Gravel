#!/usr/bin/env python3

import os

class List():
    def __init__(self, dirPath):
        self.dirPath = dirPath
        (_, _, names) = next(os.walk(dirPath))
        self.baseNames = names

    def fullPaths(self):
        return [os.path.join(self.dirPath, name) for name in self.baseNames ]

    def _pathExtension(self, path):
        idx = path.rfind('.')
        o = ''
        if (idx != -1):
            o = path[idx + 1:]
        return o
    
    def filterExtension(self, extension):
        return [path for path in self.baseNames if (self._pathExtension(path) == extension)]

    def filterExtensionFP(self, extension):
        return [path for path in self.fullPaths() if (self._pathExtension(path) == extension)]
        
    def __repr__(self):
        return 'List(dirPath:"{}")'.format(
            self.dirPath,
            )
            
########
# TEST #
########
def main():
    l = List('../buildDir')
    print(str(l))
    print('fullpaths:')
    print(l.fullPaths())
    print('filterExtension:')
    print(l.filterExtension('asm'))
    print('done')
    
if __name__== "__main__":
    main()
