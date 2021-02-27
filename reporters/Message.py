#from collections import 

#groupedMessages = {m.src.srcPath: m for m in messages}
from Position import Position
from gio.Sources import Source



class Message:
    '''
    Data carrier for messages.
    Very little here. It is the job of reporters to organise 
    and format the material.
    'pos' and 'details' attributes are optional, and reporters 
    should handle this.
    Python note: all attributes are explicitly created per instance, so 
    can be used immediately.
    If a message has a ''pos', it has a ''src'.
    '''
    #def __init__(self, message, pos = None):
    def __init__(self, message):
        #assert ((not pos) or isinstance(pos, Position)), 'Not a Position: type:{}'.format(type(pos)) 
        '''
        Main constructor is a simple string message
        '''
        self.msg = message
        self.src = None
        self.pos = None
        self.details = []

    @classmethod
    def withSrc(cls, msg, src):
        '''
        Create a message with a source
        '''
        m = cls(msg)
        m.src = src
        return m

    @classmethod
    def withPos(cls, msg, src, pos):
        '''
        Create a message with a position
        This implies a source
        '''
        m = cls(msg)
        m.src = src
        m.pos = pos
        return m

    def isLinePrintable(self):
        return (self.src and self.src.isLinebasedSource() and self.pos)
                
    def toString(self):
        return "Message(msg:'{}' src:{} pos:{})".format(
            self.msg,
            self.src,
            self.pos,
            )

    def __str__(self):
        return 'Message("{}")'.format(self.msg)
              
    def __repr__(self):
        return self.toString()
        
        
        
#class MessageNoPos(Message):
    #def __init__(self, message):
        #super().__init__(self, message, None)
