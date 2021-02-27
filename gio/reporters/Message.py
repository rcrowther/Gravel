#from collections import 

#groupedMessages = {m.src.srcPath: m for m in messages}
from .Position import Position
from .Sources import Source



class Message:
    '''
    Data carrier for Reporter messages.
    Very little here. It is the job of reporters to organise 
    and format the material.
    A message has no staus.
    'pos' and 'details' attributes are optional, and reporters 
    should handle this.
    Python note: all attributes are explicitly created per instance, 
    so can be used immediately.
    If a message has a ''pos', it has a ''src', at least.
    '''
    #def __init__(self, message, pos = None):
    def __init__(self, message):
        self.msg = message
        self.src = None
        self.pos = None
        self.details = []
        self.lineCode = ''
        
    @classmethod
    def withSrc(cls, msg, src):
        assert (isinstance(src, Source)), 'Not a Source: src:{}'.format(src) 
        m = cls(msg)
        m.src = src
        return m

    @classmethod
    def withPos(cls, msg, src, pos, lineCode):
        assert (isinstance(src, Source)), 'Not a Source: src:{}'.format(src) 
        assert (isinstance(pos, Position)), 'Not a Position: type:{}'.format(type(pos)) 
        m = cls(msg)
        m.src = src
        m.pos = pos
        m.lineCode = lineCode
        return m

    def isLinePrintable(self):
        return (self.lineCode and self.pos)

    def toOffsetCaretString(self):
        return '{}^'.format(
            ' ' * self.pos.offset
            )
            
    # def toString(self):
        # return "Message(msg:'{}' src:{} pos:{})".format(
            # self.msg,
            # self.src,
            # self.pos,
            # )
            
    def __str__(self):
        return 'Message("{}")'.format(self.msg)
              
    def __repr__(self):
        return self.toString()
        
        
        
#class MessageNoPos(Message):
    #def __init__(self, message):
        #super().__init__(self, message, None)
