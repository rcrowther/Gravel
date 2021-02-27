#! https://contributors.scala-lang.org/t/improving-the-compilation-error-reporting-of-sbt/935

#? add soc sorting
class MessageCollection:
    '''
    Collection of Message instances.
    Some reporters will collect messages, some will act as they are 
    called.
    '''
    def __init__(self):
        self.reset()
        self.errors = []
        self.warnings = []
        self.infos = []

    def isEmpty(self):
        return (self.errors or self.warnings or self.infos) 

    def error(self, msg):
        self.errors.append(msg)

    def warning(self, msg):
        self.warnings.append(msg)

    def info(self, msg):
        self.infos.append(msg)
       

    #! should print, or just use a neutral output?
    def __repr__(self):
        return "".format(
            len(self.errors),
            len(self.warnings),
            len(self.infos),        
        )
