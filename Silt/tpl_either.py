

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

#from collections import namedtuple
'''
Well, it's not really an Either, it's got a status too.
Faily cheap
Use 
if (either.obj is None): 
to test
'''
# Either = namedtuple('Either', ['status', 'message', 'obj'])

# def mk(status, message, obj):
    # return Either(status, message, obj)
    
# def obj(obj):
    # '''
    # When all is good
    # '''
    # return Either(NO_MESSAGE, '', obj)

# def msg(status, msg):
    # '''
    # Message without object
    # '''
    # return Either(status, msg, None)
    
# def fromEither(other, obj):
    # '''
    # Transfer either status and message to a new object
    # '''
    # assert (isinstance(other, Either)), "Not an either! other:'{}'".format(other)
    # return Either(other.status, other.message, obj)

# def isOk(either):
    # '''
    # May still have messaage if ok
    # '''
    # # NB. Not not(obj is None). Status wins
    # return (not(either.status == ERROR))
    
# def hasMessage(either):
    # return (not(either.status == NO_MESSAGE))
            
class Either():
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
        return cls(NO_MESSAGE, '', obj)

    @classmethod
    def error(cls, msg):
        '''
        Message without object
        '''
        return cls(ERROR, msg, None)

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
        return cls(INFO, msg, None)
        
    def __init__(self, status, msg, obj):
        self.status = status
        self.msg = msg
        self.obj = obj

    def isOk(self):
        '''
        May still have messaage if ok
        '''
        # NB. Not not(obj is None). Status wins
        return (not(self.status == ERROR))
    
    def hasMessage(self):
        return (not(self.status == NO_MESSAGE))

    def __repr__(self):
        return "Either(status:{}, msg:{}, obj:{})".format(
            statusToStr[self.status],
            self.msg,
            self.obj
        )

    def __str__(self):
        return "Either({})".format(
            statusToStr[self.status],
        )
