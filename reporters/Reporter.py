


from Position import NoPosition
from reporters.Message import Message
#! https://contributors.scala-lang.org/t/improving-the-compilation-error-reporting-of-sbt/935

#? need a flush?
#? need a print
class Reporter:
    '''
    All reporters can return a summary string. 
    The only functionality in this class is to count messages. Must be 
    sucbclassed to generate output. See sublasses for details of how a 
    reporter deals with output.
    '''
    def __init__(self):
        self.reset()
        #self.errors = []
        #self.warnings = []
        #self.infos = []

    def reset(self):
        self.errorCount = 0
        self.warningCount = 0
        self.infoCount = 0

    def hasErrors(self):
        return self.errorCount > 0

    def errorCount(self):
        return self.errorCount

    def warningCount(self):
        return self.warningCount

    def infoCount(self):
        return self.infoCount

    def error(self, msg):
        assert isinstance(msg, Message), "Type error: message given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.errorCount += 1

    def warning(self, msg):
        assert isinstance(msg, Message), "Type error: message given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.warningCount += 1

    def info(self, msg):
        assert isinstance(msg, Message), "Type error: message given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.infoCount += 1        

    def _pluralize(self, b, v):
        if (v > 1):
          b.append('s')

    #! should print, or just use a neutral output?
    def summaryString(self):
        b = []
        if (self.infoCount != 0):
          b.append(str(self.infoCount))
          b.append(' message')
          self._pluralize(b, self.infoCount)
          b.append(' ')
        if (self.warningCount != 0):
          b.append(str(self.warningCount))
          b.append(' warning')
          self._pluralize(b, self.warningCount)
          b.append(' ')
        if (self.errorCount != 0):
          b.append(str(self.errorCount))
          b.append(' error')
          self._pluralize(b, self.errorCount)
          b.append(' ')
        return ''.join(b)


