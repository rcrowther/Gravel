


# A position always implies a source
#? maybe should carry a source?
#? and why has it got a sourcepath anyhow?

class Position:
    def __init__(self, srcPath, line, offset):
        self.srcPath = srcPath
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
        return '{} [{}:{}]'.format(
            self.srcPath,
            self.line,
            self.offset,
            #msg
            )



class _NoPosition(Position):
    def __init__(self):
        Position.__init__(self, None, 0, 0)

    def toPositionString(self):
        return ''
        
    def toDisplayString(self):
        return '{}'.format(
            self.srcPath
            )
            
NoPosition = _NoPosition()
