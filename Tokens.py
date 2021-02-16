import sys

'''
Tokens are not the same as expression symbols. Sometimes
there is a one-one map e.g. 'intNum' 'intNum'.  Sometimes names are 
revised e.g. '+' : 'add'. Sometimes symbols exist where no one token matches e.g. 'type-annotation'.
Sometimes symbols do not exist where tokens exist e.g. '(' ')'.
'''

tokenBase = {
    0 : ('empty' , 'EMPTY' ), # No token?
    1 : ('EOF' , 'EOF' ),
    2 : ('identifier' , 'IDENTIFIER' ),
    3 : ('operaterIdentifier' , 'OPERATER' ),
    4 : ('monoOperaterIdentifier' , 'MONO_OPERATER' ),
    
    # constants
    10 : ('intNum' , 'INT_NUM' ),
    11 : ('floatNum' , 'FLOAT_NUM' ),
    12 : ('multilinestring' , 'MULTILINE_STRING' ),
    13 : ('string' , 'STRING' ),
    14 : ('multilineComment', 'MULTILINE_COMMENT'),
    15 : ('comment' , 'COMMENT' ),
    
    20 : ('and' , 'AND' ),
    21 : ('or' , 'OR' ),
    22 : ('not' , 'NOT' ),
    23 : ('xor' , 'XOR' ),
    24 : ('+' , 'PLUS' ),
    25 : ('-' , 'MINUS' ),
    26 : ('%' , 'PERCENT' ),
    27 : ('*' , 'ASTERIX' ),
    28 : ('<<' , 'LGUILEMOT' ),
    29 : ('>>' , 'RGUILEMOT' ),
    30 : ('=' , 'EQUALS' ),
    #''
    # floatlit
    #intlit
    # blockend
    
    40 : ('period' , 'PERIOD' ),
    41 : ('comma' , 'COMMA' ),
    42 : ('colon' , 'COLON' ),
    43 : ('scolon' , 'SEMI_COLON' ),
    44 : ('lbracket' , 'LBRACKET' ),
    45 : ('rbracket' , 'RBRACKET' ),
    46 : ('lcurly' , 'LCURLY' ),
    47 : ('rcurly' , 'RCURLY' ),
    48 : ('lsquare' , 'LSQUARE' ),
    49 : ('rsquare' , 'RSQUARE' ),
    50 : ('solidus' , 'SOLIDUS' ),
    51 : ('linefeed' , 'LINEFEED' ),
    
    100 : ('val' , 'VAL' ),
    100 : ('var' , 'VAR' ),
    # idempotent, pure, reentrant?
    102 : ('fnp' , 'FUNCTION_PURE' ),
    102 : ('fnc' , 'FUNCTION' ),
    
    110 : ('if' , 'IF' ),
    111 : ('while' , 'WHILE' ),
}

# Set the codes as attributes on the module
# i.e. FLOAT_NUM = 5
for k, v in tokenBase.items():
    setattr(sys.modules[__name__], v[1], k)

# set a dict to return human-readable string values
# i.e. newtokenToString[4] returns 'lsquare'
tokenToString =  {
    k: v[0] for k, v in tokenBase.items()
    }

#tokens = {
#'empty' : 0,
#'EOF' : 1,
#'identifier' : 2,
#'operater' : 3,

## constants
#'intNum' : 4,
#'floatNum' : 5,
#'multilinestring' : 6,
#'string' : 7,
#'multilineComment': 8,
#'comment' : 9,

#'and' : 10,
#'or' : 11,
#'not' : 12,
#'xor' : 13,
#'+' : 20,
#'-' : 21,
#'%' : 22,
#'*' : 23,
#'<<' : 24,
#'>>' : 25,
#'=' : 31,
##''
## floatlit
##intlit
## blockend

#'period' : 40,
#'comma' : 41,
#'colon' : 42,
#'scolon' : 43,
#'lbracket' : 44,
#'rbracket' : 45,
#'lcurly' : 46,
#'rcurly' : 47,
#'lsquare' : 48,
#'rsquare' : 49,
#'solidus' : 50,
#'linefeed' : 51,

#'val' : 100,
#'fnc' : 102,

#'if' : 110,
#'while' : 111
#}


#tokenToString =  {
    #v: k for k, v in tokens.items()
    #}

#def tokensToString(tokens, sep = ', '):
    #b = []
    #for t in tokens:
       #b.append(tokenToString[t])
    #return sep.join(b)



import Codepoints

# definitive list of what is (and what is not) punctuation.
#punctuation_data = {
    #'comma': (tokens['comma'], Codepoints.COMMA),
    #'colon': (tokens['colon'], Codepoints.COLON),
    #'scolon': (tokens['scolon'], Codepoints.SEMI_COLON),
    #'solidus': (tokens['solidus'], Codepoints.SOLIDUS),
    #'period': (tokens['period'], Codepoints.PERIOD),
    #'lbracket': (tokens['lbracket'], Codepoints.LEFT_BRACKET),
    #'rbracket': (tokens['rbracket'], Codepoints.RIGHT_BRACKET),
    #'lsquare': (tokens['lsquare'], Codepoints.LEFT_SQR),
    #'rsquare': (tokens['rsquare'], Codepoints.RIGHT_SQR),
    #'lcurly': (tokens['lcurly'], Codepoints.LEFT_CURLY),
    #'rcurley': (tokens['rcurly'], Codepoints.RIGHT_CURLY),
    #'linefeed': (tokens['linefeed'], Codepoints.LINE_FEED),  
    #}

punctuationBase = {
    'comma': (COMMA, Codepoints.COMMA),
    'colon': (COLON, Codepoints.COLON),
    'scolon': (SEMI_COLON, Codepoints.SEMI_COLON),
    #'solidus': (SOLIDUS, Codepoints.SOLIDUS),
    #'period': (PERIOD, Codepoints.PERIOD),
    'lbracket': (LBRACKET, Codepoints.LEFT_BRACKET),
    'rbracket': (RBRACKET, Codepoints.RIGHT_BRACKET),
    'lsquare': (LSQUARE, Codepoints.LEFT_SQR),
    'rsquare': (RSQUARE, Codepoints.RIGHT_SQR),
    'lcurly': (LCURLY, Codepoints.LEFT_CURLY),
    'rcurley': (RCURLY, Codepoints.RIGHT_CURLY),
    'linefeed': (LINEFEED, Codepoints.LINE_FEED),  
    }

# All codepoints for Gravel punctuation
punctuationCodepoints = [
    v[1] for k, v in punctuationBase.items()
]

# dict of codepoint to token
# i.e. Codepoints.PERIOD (46) : Tokens.PERIOD (40)
punctuationCodepointToToken = {
    v[1] : v[0] for k, v in punctuationBase.items()
    }
  
