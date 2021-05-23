import sys

tokenBase = {
    2 : ('identifier' , 'IDENTIFIER' ),

    10 : ('int number' , 'INT_NUM' ),
    11 : ('float number' , 'FLOAT_NUM' ),
    12 : ('multiline string' , 'MULTILINE_STRING' ),
    13 : ('string' , 'STRING' ),
    14 : ('multiline comment', 'MULTILINE_COMMENT'),
    15 : ('comment' , 'COMMENT' ),
    
    
    #40 : ('period' , 'PERIOD' ),
    41 : ('comma' , 'COMMA' ),
    42 : ('colon' , 'COLON' ),
    #43 : ('scolon' , 'SEMI_COLON' ),
    44 : ('lbracket' , 'LBRACKET' ),
    45 : ('rbracket' , 'RBRACKET' ),
    # 46 : ('lcurly' , 'LCURLY' ),
    # 47 : ('rcurly' , 'RCURLY' ),
    48 : ('lsquare' , 'LSQUARE' ),
    49 : ('rsquare' , 'RSQUARE' ),
    # 50 : ('solidus' , 'SOLIDUS' ),
    51 : ('linefeed' , 'LINEFEED' ),

    60 : ('left path' , 'LPATH' ),
    61 : ('right path' , 'RPATH' ),    
    62 : ('left literal collection' , 'LCOLL' ),
    63 : ('right literal scollection' , 'RCOLL' ),
    64 : ('keyvalue mark' , 'KEY_VALUE' ),
    65 : ('repeat' , 'REPEAT' ),
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
