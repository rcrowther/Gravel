
#import collections




class Builder():
    def __init__(self):
        self.headers = []
        self.sections = {"data":[], "bss":[], "rodata":[]}
        self.funcCode = []
        self.declarations = []

    def extendFuncCode(self, declList):
        self.funcCode.extend(declList)
        
    def append(self, declList):
        self.declarations.append(declList)
        
    def extend(self, declList):
        self.declarations.extend(declList)
        
    def frame(self, frame):
        return frame.format(
            "\n".join(self.headers),
            "\n    ".join(self.sections["data"]),
            "\n    ".join(self.sections["rodata"]),
            "\n    ".join(self.sections["bss"]),
            "\n    ".join(self.funcCode),
            "\n    ".join(self.declarations)
           )      
        
    def concat(self, b):
        b.append("headers:")
        b.extend(self.headers)
        b.append("data:")
        b.extend(self.sections["data"])
        b.append("rodata:")
        b.extend(self.sections["rodata"])
        b.append("bss:")
        b.extend(self.sections["bss"])
        b.append("declarations:")
        b.extend(self.declarations)
        return b

    def __str__(self):
        b = []
        self.concat(b)
        return "Builder({})".format(", ".join(b)) 

Empty = Builder()

