


def toPositionString(position):
    return '[{}:{}]'.format(
        position.lineNum,
        position.offset,
        )

        
class Position:
    '''
    Record a position in a source.
    '''
    def __init__(self, source, lineNum, offset):
        self.source = source
        self.lineNum = lineNum
        self.offset = offset


