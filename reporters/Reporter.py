


from Position import NoPosition

#! need a flush?
#! need a print
class Reporter:

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

    def error(self, m, pos = NoPosition):
        self.errorCount += 1

    def warning(self, m, pos = NoPosition):
        self.warningCount += 1

    def info(self, m, pos = NoPosition):
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


