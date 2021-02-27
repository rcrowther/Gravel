from .Reporter import Reporter
#from Position import NoPosition
from .AnsiColor import *




## eg
# test/syntax.gv [42:4]Error: Name definition repeated. name:"map" first declaration position:test/syntax.gv [38:4]

class ReporterStreamConsole(Reporter):
    '''
    Messages are sent immediately.
    For this reason Messages are not further sorted, and can not
    be heavily configured e.g. they can not be grouped by source.
    Out put is coloued in the form:
    'in' source
    [status] [position] message
    '''
    def __init__(self, lineOffsetFrom, lineCountFrom):
        super().__init__(lineOffsetFrom, lineCountFrom)
        self.indent = '    '
        
        # set up some strings for indicating error status
        self.statusStrError = self.statusStr('error', RED)
        self.statusStrWarning = self.statusStr('warning', YELLOW)
        self.statusStrInfo = self.statusStr('info', GREEN)
        
        
    def statusStr(self, statusStr, statusColor):
        return '[{color}{status}{reset}]'.format(
            color=statusColor, status=statusStr, reset=RESET
            )
            
    def srcStr(self, b, src):
        if (src):
            b.append( ' ' )
            if (src.isFileSource()):
                b.append( UNDERLINED )
                b.append( src.locationStr() )
                b.append( RESET )
            else:
                b.append( src.locationStr() )

    def posStr(self, b, pos, printLineDisplay):
        if (pos):
            b.append(':')
            b.append( str(pos.lineNum + self.lineCountFrom) )
            if (not printLineDisplay):
                b.append('/')
                b.append( str(pos.offset + self.lineOffsetFrom) )
            b.append(':')

    def messageDisplay(self, statusStr, msg):
        # using a 'if data is there, set up the print prefix delimiter'
        # method.
        b = []
        
        # Print a status for the message
        b.append( statusStr )
        
        # Print the source string
        self.srcStr(b, msg.src)
        
        # Print a position, with or without an offset
        printLineDisplay = msg.isLinePrintable()
        self.posStr(b, msg.pos, printLineDisplay)
        
        # print the message
        b.append( ' ' )        
        b.append(msg.msg)

        # print details e.g. hints
        for detail in msg.details:
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent )
            b.append( detail )

        # if available, print the line display
        if (printLineDisplay):
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent)
            #! too epic for me
            #b.append( msg.pos.source.lineByIndex(msg.pos.lineNum) )
            #b.append( msg.src.lineByIndex(msg.pos.lineNum) )
            b.append( msg.lineCode )
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent )
            b.append( msg.toOffsetCaretString() )
        b.append('\n')       
        return ''.join(b)
        
    def error(self, msg):
        super().error(msg)
        m = self.messageDisplay(
            self.statusStrError,
            msg
            )
        print(m)

    def warning(self, msg):
        super().warning(msg)
        m = self.messageDisplay(
            self.statusStrWarning,
            msg
            )
        print(m)
        
    def info(self, msg):
        super().info(msg)
        m = self.messageDisplay(
            self.statusStrInfo,
            msg
            )
        print(m)

    def summary(self):
        b = []
        if (not(self.isEmpty())):
            if (self.infoCount != 0):
                b.append(str(self.infoCount))
                self._pluralize(b, ' info message', self.infoCount)
                b.append('\n')
            if (self.warningCount != 0):
                b.append(str(self.warningCount))
                self._pluralize(b, ' warning', self.warningCount)
                b.append('\n')
            if (self.errorCount != 0):
                b.append(str(self.errorCount))
                self._pluralize(b, ' error', self.errorCount)
                b.append('\n')
            else:
                b.append( " No errors")
            b.append('\n')              
        else:
            b.append( " No errors")
            b.append('\n')
        print(''.join(b))
