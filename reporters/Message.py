#from collections import 

#groupedMessages = {m.src.srcPath: m for m in messages}

class Message:
    '''
    Data carrier for Reporter messages.
    Very little here. It is the job of reporters to organise 
    and format the material.
    'src', 'pos' and 'details' attributes are optional, and reporters 
    should handle this.
    '''
    def __init__(self, message, src = None, pos = None):
        self.src = src
        self.pos = pos
        self.msg = message
        self.details = []
