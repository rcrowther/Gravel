#from Kinds import *


# From where? C definition? because '!' '++' '--' are not infix, but
# mono-ops. What ':' is for, I do not know? The ternary op?
'''
Definition of builtin binops.
'=' is not included, because (at present) any op ending in '=' is a binop.
'''
INFIX = [
'|',
'||',
'^',
'&',
'&&',
'<',
'<<',
'>',
'>>',
#'=', 
#'!',
#??? ':'
'+', 
#'++',
'-',
#'--',
'*',
#'/',
'%',
]

MOMO_OP = [
'!',
'++',
'--'
]

# does not include keywords like val?
# /home/rob/Downloads/scala-2.12.0/src/reflect/scala/reflect/internal
# Don't modify with extend(), create new list using '+'
KEY_EXPRESSIONS = [
  #'+',
  #'-',
  #'*',
  #'/'
  ] + INFIX

# Preset Kind -> Parent
# Excludes Any
# Must be in declaration order, so the list (not dict)
# https://www.scala-lang.org/api/2.12.6/scala/index.html#AnyRef:Specializable
# https://www.scala-lang.org/api/2.12.6/scala/Predef$.html
#What about Tuple?
KEY_KINDS = [
  ('Nothing', 'Any'),
  ('AnyVal', 'Any'),
  ('NoVal', 'AnyVal'),
  ('Integer', 'AnyVal'),
  ('Float', 'AnyVal'),
  ('AnyRef', 'Any'),
  ('NoRef', 'AnyRef'),
  ('String', 'AnyRef'),
  # How to handke complex types?
  # But these derive from each other?
  # Collections, Iterable <- Seq  <- List
  # Where did this come from? Ah', the diagram...
  # base collection traits
  ('TraversableOnce', 'AnyRef'),
  ('Traversable', 'TraversableOnce'),
  ('Iterable', 'Traversable'),
  # has order
  ('Seq', 'Iterable'),
  ('Map', 'Iterable'),
  ('Set', 'Iterable'),
  # sequences
  ('IndexedSeq', 'Seq'),
  ('LinearSeq', 'Seq'),
   
  #('List', 'Seq'),
  
  #CollectionKind
  ]

KEY_KINDNAMES = [e[0] for e in KEY_KINDS]
