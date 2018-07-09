from reporters.Reporter import Reporter
from Position import NoPosition
from library.io.AnsiColor import *

##
# Add colour
# test/syntax.gv [42:4]Error: Name definition repeated. name:"map" first declaration position:test/syntax.gv [38:4]

class ConsoleStreamReporter(Reporter):

    def __init__(self):
        Reporter.__init__(self) 

    def messageDisplay(self, pos, statusStr, statusColor, msg):
        return '{srcStyle}{srcClr}{src}{reset} {posClr}{posStr}{reset}{statusClr}{status}{reset}: {msg}'.format(
            srcStyle=UNDERLINED, srcClr=BLUE, src=pos.srcPath, reset=RESET,
            posClr=BLUE, posStr=pos.toPositionString(),
            statusClr=statusColor, status=statusStr,
            msg=msg
            )
             
    def error(self, m, pos = NoPosition):
        Reporter.error(self, m, pos)
        msg = self.messageDisplay(
            pos,
            'Error', 
            RED,
            m
            )
        print(msg)

    def warning(self, m, pos = NoPosition):
        Reporter.warning(self, m, pos)
        msg = self.messageDisplay(
            pos,
            'Warning', 
            YELLOW,
            m
            )
        print(msg)
        
    def info(self, m, pos = NoPosition):
        Reporter.info(self, m, pos)
        msg = self.messageDisplay(
            pos,
            'Info', 
            GREEN,
            m
            )
        print(msg)
