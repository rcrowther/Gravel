#!/usr/bin/python3


#from trees.Trees import *

#import newNames

# as in Global

class CompilationUnit:
    '''
    Would usually represent one source file, or similar.
    Composes the source file with derived data such as the 
    AST tree/marktables/live ranges etc. As the tree is 
    transformed, maintains the connection with source data and 
    error reporting.
    '''
    def __init__(self, source):
      #? rename 'src' for consistency
      self.source = source
      #self.reporter = reporter
      self.tree = None
      self.markTable = None
      self.kindTree = None

      # May seem an odd addition,
      # But the temp names are associated 
      # with a compilation unit
      #self.newNames = newNames.NewName()

      self.liveRanges = None
      # the builder as blocks.
      self.mCode = None
      # status report calls?
      # final code (icode)?
      # namegenerators?
      #dependencies?
            
    def __repr__(self):
        return 'CompilationUnit(src:{})'.format(
            self.source,
            )
