from reporters.Reporter import Reporter
from Position import NoPosition
from library.io.AnsiColor import *




## eg
# test/syntax.gv [42:4]Error: Name definition repeated. name:"map" first declaration position:test/syntax.gv [38:4]

class ConsoleStreamReporter(Reporter):

    def __init__(self):
        Reporter.__init__(self)
        self.indent = '    '
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

    def posStr(self, b, pos, printLineDetail):
        if (pos):
            # Always a source, if there is a pos
            b.append(':')
            b.append( str(pos.lineNum) )
            if (not printLineDetail):
                b.append('/')
                b.append( str(pos.offset) )
            b.append(':')

    def messageDisplay(self, statusStr, msg):
        # using a 'if data is there, set up the print prefix delimiter'
        # method.
        b = []
        
        b.append( statusStr )
        self.srcStr(b, msg.src)
        
        printLineDetail = msg.isLinePrintable()
        self.posStr(b, msg.pos, printLineDetail)
        
        b.append( ' ' )        
        b.append(msg.msg)

        for detail in msg.details:
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent )
            b.append( detail )

        if (printLineDetail):
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent)
            #! too epic for me
            #b.append( msg.pos.source.lineByIndex(msg.pos.lineNum) )
            b.append( msg.src.lineByIndex(msg.pos.lineNum) )
            b.append('\n')
            b.append( statusStr )
            b.append( self.indent )
            b.append( msg.pos.toOffsetCaretString() )
        b.append('\n')       
        return ''.join(b)
        
    def error(self, msg):
        Reporter.error(self, msg)
        m = self.messageDisplay(
            self.statusStrError,
            msg
            )
        print(m)

    def warning(self, msg):
        Reporter.warning(self, msg)
        m = self.messageDisplay(
            self.statusStrWarning,
            msg
            )
        print(m)
        
    def info(self, msg):
        Reporter.info(self, msg)
        m = self.messageDisplay(
            self.statusStrInfo,
            msg
            )
        print(m)
