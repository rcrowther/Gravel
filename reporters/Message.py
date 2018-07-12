#from collections import 

#groupedMessages = {m.src.srcPath: m for m in messages}
from Position import Position
from gio.Sources import Source



class Message:
    '''
    Data carrier for Reporter messages.
    Very little here. It is the job of reporters to organise 
    and format the material.
    'src', 'pos' and 'details' attributes are optional, and reporters 
    should handle this.
    Python note: all attributes are explicitly created per instance, so can be used
    immediately.
    If a message has a ''pos', it has a ''src'.
    '''
    def __init__(self, message, src = None, pos = None):
        assert ((not src) or isinstance(src, Source)), 'Not a Source: type:{}'.format(type(src)) 
        assert ((not pos) or isinstance(pos, Position)), 'Not a Position: type:{}'.format(type(pos)) 
        self.src = src
        self.pos = pos
        self.msg = message
        self.details = []
