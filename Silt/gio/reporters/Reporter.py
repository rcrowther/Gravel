from .Message import Message
#! https://contributors.scala-lang.org/t/improving-the-compilation-error-reporting-of-sbt/935

class ReporterSummary():
    def __init__(errorCount, warningCount, infoCount):
        self.infoCount = infoCount
        self.warningCount = warningCount
        self.errorCount = errorCount

    def __repr__(self):
        return "ReporterSummary(errorCount:{}, warningCount:{}, infoCount:{})".format(
            self.errorCount,
            self.warningCount,
            self.infoCount,
        )

        #? need a flush?
#? need a print
class Reporter:
    '''
    IO of Message instances.
     
    All reporters can return a summary string. 
    This base class is a common API
    It enables classing of messages by status. So it can return some 
    info on that.
    See sublasses for details of how a reporter deals with output.
    '''
    def __init__(self, lineOffsetFrom, lineCountFrom):
        self.lineOffsetFrom = lineOffsetFrom
        self.lineCountFrom = lineCountFrom
        self.errorCount = 0
        self.warningCount = 0
        self.infoCount = 0
        
    def reset(self):
        self.errorCount = 0
        self.warningCount = 0
        self.infoCount = 0

    def isEmpty(self):
        return ((self.errorCount == 0) and (self.warningCount == 0) and (self.infoCount == 0)) 

    def error(self, msg):
        '''
        Test message for type and Increment counts. To be overridden
        '''
        assert isinstance(msg, Message), "Type error: value given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.errorCount += 1

    def warning(self, msg):
        '''
        Test message for type and Increment counts. To be overridden
        '''
        assert isinstance(msg, Message), "Type error: value given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.warningCount += 1

    def info(self, msg):
        '''
        Test message for type and Increment counts. To be overridden
        '''
        assert isinstance(msg, Message), "Type error: value given to reporter is not message class: val: {}: type:{}: ".format(
            type(msg),
            msg
            )
        self.infoCount += 1        


    def _pluralize(self, b, text, v):
        b.append(text)
        if (v > 1):
          b.append('s')

    #! should print, or just use a neutral output?
    def toSummary(self):
        return ReporterSummary(
            self.errorCount,
            self.warningCount,
            self.infoCount
        )

    def summary(self):
        raise NotImplemented()
        
    def __repr__(self):
        return "Reporter(errorCount:{}, warningCount:{}, infoCount:{})".format(
            self.errorCount,
            self.warningCount,
            self.infoCount,
        )
