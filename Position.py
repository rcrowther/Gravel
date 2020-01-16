


# A position always implies a source
# because we stash in the tree support data?

class PositionBase:
    def __init__(self, source):
        self.source = source
        


class PositionNoPos(PositionBase):
    def __init__(self, source):
        super().__init__(source)
        

                
class Position:
    '''
    Record a position in a source.
    '''
    def __init__(self, source, lineNum, offset):
        self.source = source
        self.lineNum = lineNum
        self.offset = offset

    def toPositionString(self):
        return '[{}:{}]'.format(
            self.lineNum,
            self.offset,
            )

    def toLineNumString(self):
        return '[{}]'.format(
            self.lineNum
            )


    def toOffsetCaretString(self):
        return '{}{}'.format(
            ' ' * self.offset, 
            '^'
            )
                                    
    def toDisplayString(self):
        return '[{}:{}]'.format(
            self.lineNum,
            self.offset,
            )

    def __repr__(self):
        return "Position({}, {}, {})".format(
            self.source,
            self.lineNum,
            self.offset,            
            )


class _NoPosition(Position):
    def __init__(self):
        Position.__init__(self, None, 0, 0)

    def toPositionString(self):
        return ''
        
    def toDisplayString(self):
        return 'NoPosition'
            
NoPosition = _NoPosition()
