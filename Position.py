


# A position always implies a source
#? maybe should carry a source?
#? and why has it got a sourcepath anyhow?
# because we stash in the tree support data?

class Position:
    '''
    Record a position in a source.
    '''
    def __init__(self, line, offset):
        self.line = line
        self.offset = offset

    def toPositionString(self):
        return '[{}:{}]'.format(
            self.line,
            self.offset,
            )

    def toLineString(self):
        return '[{}]'.format(
            self.line
            )


    def toOffsetCaretString(self):
        return '{}{}'.format(
            ' ' * self.offset, 
            '^'
            )
                                    
    def toDisplayString(self):
        return '[{}:{}]'.format(
            self.line,
            self.offset,
            )



class _NoPosition(Position):
    def __init__(self):
        Position.__init__(self, 0, 0)

    def toPositionString(self):
        return ''
        
    def toDisplayString(self):
        return 'NoPosition'
            
NoPosition = _NoPosition()
