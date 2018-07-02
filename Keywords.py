#from Kinds import *

# does not include keywords like val?
# /home/rob/Downloads/scala-2.12.0/src/reflect/scala/reflect/internal
KEY_EXPRESSIONS = [
  '+',
  '-',
  '*',
  '/'
  ]

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
