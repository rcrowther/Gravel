

from reporters.Reporter import Reporter
from Position import NoPosition

##
# Add colour

class ConsoleStreamReporter(Reporter):

    def __init__(self):
        Reporter.__init__(self) 

    def error(self, m, pos = NoPosition):
        Reporter.error(self, m, pos)
        print(pos.toDisplayString() + 'Error: ' + m)

    def warning(self, m, pos = NoPosition):
        Reporter.warning(self, m, pos)
        print(pos.toDisplayString() + 'Warning: ' + m)

    def info(self, m, pos = NoPosition):
        Reporter.info(self, m, pos)
        print(pos.toDisplayString() + 'Info: ' + m)
