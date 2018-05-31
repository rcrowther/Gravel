


class Mark:
    is_defined = False
    #is_reference = False
    
    def __init__(self, name):
        self.name = name

    def toString(self):
        return "Mark('{}')".format(self.name)

    def __repr__(self):
        return self.toString()


class _UndefinedMark(Mark):
    '''
    Only used to init parsed trees.
    '''
    def __init__(self):
        self.name = None

    def toString(self):
        return "UndefinedMark"
  
UndefinedMark = _UndefinedMark()

class _NoMark(Mark):
    #@property
    #def name(self):
        #raise AttributeError("'name' not available on the NoMark object")

    #@name.setter
    #def name(self, value):
        #raise AttributeError("'name' not available on the NoMark object")

    def __init__(self):
        self.name = None

    def toString(self):
        return "NoMark"
  
NoMark = _NoMark()
