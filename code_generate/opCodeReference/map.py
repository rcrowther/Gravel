import collections

# in .rodata
IC = collections.namedtuple('IntegerConstant', 'op low high') 
int_constant = {
int8: IC("db", 0, 125),
int16: IC("dw", 0, 65535),
int32: IC("dd", 0, 4294967295),
int64: IC("dq", 0, 18446744073709551616),
int128: IC("ddq", 0, None),
  }
  
def decinit_const(v, typ):
    return int_constant[typ] + ' ' + v
    
def return_const(sym):
    return '[{}]'.format(sym)
