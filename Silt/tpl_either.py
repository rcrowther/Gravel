


class Option():
    NO_MESSAGE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3

    statusToStr = [
        "NO_MESSAGE",
        "ERROR",
        "WARNING",
        "INFO"
    ]

        

class MessageOption(Option):

    @classmethod
    def error(cls, msg):
        '''
        MessageOption for error
        '''
        return cls(cls.ERROR, msg)

    @classmethod
    def warning(cls, msg):
        '''
        MessageOption for warning
        '''
        return cls(cls.WARNING, msg)

    @classmethod
    def info(cls, msg):
        '''
        MessageOption for info
        '''
        return cls(cls.INFO, msg)
        
    def __init__(self, status, msg):
        self.status = status
        self.msg = msg

    def isOk(self):
        '''
        May still have messaage if ok
        '''
        # NB. Not not(obj is None). Status wins
        return (not(self.status == self.ERROR))

    def notOk(self):
        '''
        May still have messaage if ok
        '''
        # NB. Not not(obj is None). Status wins
        return (self.status == self.ERROR)    

    def hasMessage(self):
        return (not(self.status == self.NO_MESSAGE))

    def __repr__(self):
        return 'MessageOption(status:{}, msg:"{}")'.format(
            self.statusToStr[self.status],
            self.msg,
        )

    def __str__(self):
        return "MessageOption({})".format(
            self.statusToStr[self.status],
        )
            
MessageOptionNone = MessageOption(
    MessageOption.NO_MESSAGE, 
    '',
) 


#! change to MessageEither            
class Either(Option):
    '''
    Well, it's not really an Either, it's got a status too.
    '''
    @classmethod
    def fromEither(cls, other, obj):
        assert (isinstance(other, Either)), "Not an either! other:'{}'".format(other)
        return cls(other.status, other.msg, obj)

    @classmethod
    def obj(cls, obj):
        '''
        When all is good
        '''
        return cls(cls.NO_MESSAGE, '', obj)

    @classmethod
    def error(cls, msg):
        '''
        Message without object
        '''
        return cls(cls.ERROR, msg, None)

    @classmethod
    def warning(cls, msg):
        '''
        Message without object
        '''
        return cls(WARNING, msg, None)

    @classmethod
    def info(cls, msg):
        '''
        Message without object
        '''
        return cls(cls.INFO, msg, None)
        
    def __init__(self, status, msg, obj):
        self.status = status
        self.msg = msg
        self.obj = obj

    def isOk(self):
        '''
        May still have messaage if ok
        '''
        # NB. Not not(obj is None). Status wins
        return (not(self.status == self.ERROR))

    def notOk(self):
        '''
        May still have messaage if ok
        '''
        # NB. Not not(obj is None). Status wins
        return (self.status == self.ERROR)
            
    def hasMessage(self):
        return (not(self.status == self.NO_MESSAGE))

    def __repr__(self):
        return 'Either(status:{}, msg:"{}", obj:{})'.format(
            self.statusToStr[self.status],
            self.msg,
            self.obj
        )

    def __str__(self):
        return "Either({})".format(
            self.statusToStr[self.status],
        )

