from Syntaxer import Syntaxer
from tpl_codeBuilder import Builder


class Compiler(Syntaxer):

    def __init__(self, tokenIt):
        super().__init__(tokenIt)
        self.b = Builder()
        exprMap = {
        'frameStart' : b.frameStart(),
        'frameEnd' : b.frameEnd(),
        }
    
    def commentCB(self, text):
        print('Compiler comment with "' + text)

    def exprCB(self, name, args):
        print('Compiler expr {}({})'.format(name, args))

    def result(self):
        return self.b
        
if __name__ == "__main__":
    main()
