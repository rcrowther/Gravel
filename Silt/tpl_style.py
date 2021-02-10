def styleSolve(style):
    '''
    Pack the style with defaults
    Avoids constant explicit ''if'
    '''
    selectors = ['*', 'label', 'funcBlock', 'loopBlock', 'condBlock']

    # ensure missing selectors
    for selector in selectors:
        if (not(selector in style)):
            style[selector] = {}
            
    # ensure missing rules
    for selector, rules in style.items():
        if (not('indent' in rules)):
            style[selector]['indent'] = 0
        if (not('newline-top' in rules)):
            style[selector]['newline-top'] = False
    return style

def applyStyleToLine(indent, currentStyle, line):
    l = ''
    if (currentStyle['newline-top']):
        l = '\n'
    l += (" " * indent)
    l += line 
    return l
    
def addStyle(stack, currentStyle, addStyle):
    stack.append(newStyle)
    currentStyle['indent'] += addStyle['indent']
    
def rmStyle(stack, currentStyle, rmStyle):
    currentStyle['indent'] -= rmStyle['indent']
    currentStyle.pop()

def builderCode(style, code):
    '''
    Return a string of code data, inflected by style
    '''
    styleBase = style['*'].copy()
    styleStack = []
    currentStyle = styleBase
    indent = styleBase['indent']
    
    b = []
    selfClose = False
    for line in code:
        b.append('\n') 

        if line.endswith(':'):
            styleStack.append(currentStyle)            
            currentStyle = style['label']
            indent += currentStyle['indent']
            # Remove the style immediately after the line is written
            selfClose = True
        if line.startswith('; beginFunc'):
            styleStack.append(currentStyle)            
            currentStyle = style['funcBlock']
            indent += currentStyle['indent']
        if line.startswith('; beginLoop'):
            styleStack.append(currentStyle)            
            currentStyle = style['loopBlock']
            indent += currentStyle['indent']
            
        b.append(applyStyleToLine(indent, currentStyle, line)) 

        if (line.startswith('; end') or (selfClose)):
            indent -= currentStyle['indent']
            currentStyle = styleStack.pop()
            selfClose = False
    return ''.join(b)
    
def sectionCode(style, bCode):
    '''
    Return a string of section data, inflected by style
    '''
    indent = style['*']['indent']
    indent_str = " " * indent
    joinIndent = '\n' + indent_str
    return indent_str + joinIndent.join(bCode)
    
#? arch implies a frame. Or a group of frames, maybe not one 
#defining frame?
def builderPrint(frame, b, style):
    '''
    Print a builder as code
    Resolves the builder, inflects for style, wraps in a frame
    '''
    styleSolve(style)
    styledCode = {
        'externs' : '\n'.join(b._externs), 
        'data' : sectionCode(style, b._data), 
        'rodata'  : sectionCode(style, b._rodata), 
        'bss'  : sectionCode(style, b._bss), 
        'text' : '\n'.join(b._text),
        'code' : builderCode(style, b._code),
    }
    return frame(**styledCode)
     
