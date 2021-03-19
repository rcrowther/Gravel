from tpl_types import *



#? Whats 64? The registers and pointersize
class PrintX64():
    #def __init__(self, b):
    #    self.b = b
        
    def __call__(self, b, tpe, srcSnippet):
        source = srcSnippet
        if(tpe == Bit8):
            self.i8(b, source)
        elif(tpe == Bit16):
            self.i16(b, source)
        elif(tpe == Bit32):
            self.i32(b, source)
        elif(tpe == Bit64):
            self.i64(b, source)
        elif(tpe == Bit128):
            self.i128(b, source)
        elif(tpe == Bit32F):
            self.f32(b, source)
        elif(tpe == Bit64F):
            self.f64(b, source)
        elif(tpe == StrASCII):
            self.ascii(b, source)
        elif(tpe == StrUTF8):
            self.utf8(b, source)
        #elif(tpe == Pointer):
        #    self.pointer(b, tpe, source)
        #elif(tpe == Array):
        #    self.array(b, tpe, source)
        else:
            raise NotImplementedError('Print: unrecognised type. tpe:{}'.format(tpe));

    def pointer(self, b, tpe, location):
        self.dispatch(b, tpe, base + offset)
        
    def array(self, b, tpe, location):
        byteSize = tpe.elementType.byteSize
        base = location()
        for offset in (0..tpe.size):
            self.dispatch(b, tpe, base + offset)

    def protect(self, source):
        if (source in ['rdi', 'rsi' ]):
            raise ValueError('Printing clobbers RDI and RSI. address: {}'.format(source))

    def extern(self, b):
        b.externsAdd("extern printf")
 
    def flush(self, b):
        b.externsAdd("extern fflush")
        b._code.append("mov rdi, 0")
        b._code.append("call fflush")
            
    def generic(self, b, form, source):
        self.protect(source)
        self.extern(b) 
        b._code.append("mov rdi, " + form)
        b._code.append("mov rsi, " + source)
        b._code.append("call printf")

    def newline(self, b):
        self.extern(b)
        b.rodataAdd('printNewLine: db 10, 0')
        b._code.append("mov rdi, printNewLine")
        b._code.append("call printf")

    def char(self, b, source):
        b.rodataAdd('printCharFmt: db "%c", 0')
        self.generic(b, 'printCharFmt', source)
            
    def ascii(self, b, source):
        self.protect(source)
        self.extern(b)
        b._code.append("mov rdi, " + source)
        b._code.append("call printf")

    #NB if I moved to widechar for strlen() and the like,
    # I'd need to use a different format string. '%ls'.
    def utf8(self, b, source):
        # repeating ascii until we know how it behaves
        self.protect(source)
        self.extern(b)
        b._code.append("mov rdi, " + source)
        b._code.append("call printf")
        
    def i8(self, b, source):
        b.rodataAdd('print8Fmt: db "%hhi", 0')
        self.generic(b, 'print8Fmt', source) 

    def i16(self, b, source):
        b.rodataAdd('print16Fmt: db "%hi", 0')
        self.generic(b, 'print16Fmt', source) 
                        
    def i32(self, b, source):
        b.rodataAdd('print32Fmt: db "%i", 0')
        self.generic(b, 'print32Fmt', source) 

    def i64(self, b, source):
        b.rodataAdd('print64Fmt: db "%li", 0')
        self.generic(b, 'print64Fmt', source)

    def i128(self, b, source):
        b.rodataAdd('print128Fmt: db "%lli", 0')
        self.generic(b, 'print128Fmt', source)
        
    def f32(self, b, form, source):
        self.protect(source)
        self.extern(b)
        b.rodataAdd('printFloatFmt: db "%g", 0')
        b._code.append("movsd xmm0, printlnFloatFmt")
        b._code.append("mov rdi, " + source)
        b._code.append("call printf")

    # 32f usually promoted to 64f anyhow
    def f64(self, b, form, source):
        self.protect(source)
        self.extern(b)
        b.rodataAdd('printFloatFmt: db "%g", 0')
        b._code.append("movsd xmm0, printlnFloatFmt")
        b._code.append("mov rdi, " + source)
        b._code.append("call printf")
        
        
