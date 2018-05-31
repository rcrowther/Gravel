



class Position:
    def __init__(self, srcPath, line, offset):
        self.srcPath = srcPath
        self.line = line
        self.offset = offset

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

    def toDisplayString(self, msg = ''):
        return msg

NoPosition = _NoPosition()
