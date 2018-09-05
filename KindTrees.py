from operator import attrgetter

#def newId():

class MPTTNode:
  '''
  Node for an MPTT tree.
  Can be composed/superclassed with contents, or used as a 
  template.
  '''

  def __init__(self):
      self._in = None
      self._out = None
      
  def toString(self):
      return "MPTTNode(_in: {}, _out: {})".format(
          self._in,
          self._out,
          )
      
  def __repr__(self):
      return self.toString()
      
      
      
class Node(MPTTNode):
    '''
    TestNode for an MPTT tree.
    '''
    _id = 0

    def __init__(self):
        Node._id += 1 
        self.id = Node._id
        super().__init__()

      
    def toString(self):
        return "Node(id: {}, _in: {}, _out: {})".format(
            self.id,
            self._in,
            self._out,
            )

      
      

          
# need insert (not so much delete)
# but insert can be slow
# need parents and children, above all
# also, common parent (may be helpful)
class MPTT():
    def __init__(self, initial_node):
        initial_node._in = 0
        initial_node._out = 1        
        self.underlying = []
        self.underlying.append(initial_node)
       
    def insert(self, parentNode, node):
        pIn = parentNode._in
        pOut = parentNode._out
       
        # update all to right
        for e in self.underlying:
            if (e._in >= pOut):
                e._in += 2
            if (e._out >= pOut):
                e._out += 2
                   
        # set new node
        self.underlying.append(node)
        node._in = pOut
        node._out = pOut + 1
        return node
        
    def parents(self, childNode):
        '''
        Parents of the given node.
        Includes the node itself.
        '''
        pIn = childNode._in
        pOut = childNode._out
        return [e for e in self.underlying if (e._in <= pIn and e._out >= pOut)]
        
    def children(self, parentNode):
        '''
        Children of the given node.
        Excludes the given node.
        '''
        pIn = parentNode._in
        pOut = parentNode._out
        return [e for e in self.underlying if (e._in > pIn and e._out < pOut)]

    def isChild(self, node, otherNode):
        '''
        Test if otherNode is a child of node.
        '''
        return (otherNode._in > node._in and otherNode._out < node._out)
        
    def isParent(self, node, otherNode):
        '''
        Test if otherNode is a parent of node.
        '''
        return (otherNode._in <= node._in and otherNode._out >= node._out)
        
    def toStringTable(self):
        nodes = sorted(self.underlying, key=attrgetter('_in'))
        stack = []
        b = []
        for node in nodes:
            while (stack and (stack[-1] < node._out)):
                stack.pop()
            b.append(len(stack) * ' ')
            b.append(str(node))
            b.append('\n')
            stack.append(node._out)
        return ''.join(b)
        
    def toString(self):
        return self.toStringTable()
        
    def __repr__(self):
        return self.toString()




from Kinds import Any
from Keywords import KEY_KINDS

class KindNameNode(MPTTNode):
    '''
    MPTT tree node for Kind names.
    '''
    def __init__(self, name):
        self.name = name
        super().__init__()

    def toString(self):
        return "KindNameNode(name: '{}', _in: {}, _out: {})".format(
            self.name,
            self._in,
            self._out,
            )
          
          
#! I want this for registering Kind names and
# detecting their structure (not typechecking)
# Handles names of Kinds, not Kinds themselves.
# We have issues in here. For example, List[_] is a subtype of 
# List[Integer]. Although function types can be broken up, e.g. 
# (Int => Float)
# So registering names is not enough for establishing
# heirarchy of types.
class KindNameTree(MPTT):
    '''
    Register valid kinds.
    The tree is pre-initialised with KEY_KINDS.
    The tree is only for registering kind names and 
    establishing/reporting on a structure between them. It is not for 
    typechecking.
    '''
    # The tree is used for finding parents and children.
    # this is boosted with a link table for fast lookup of names
    # (the tree can do this, but is slow, and in Python has a 
    # non-intuitive API. Alright, I can get round the API, but anyway).
    def __init__(self):
        initial_name = 'Any'
        initial_node = KindNameNode(initial_name)
        super().__init__(initial_node)
        self.nameToNode = {initial_name: initial_node}
        for e in KEY_KINDS:
            self.insert(e[1], e[0])

    #Test the kindname is not there?
    # if it's a complex kind, it needs to be broken up to register 
    # the names
    def insert(self, parentName, name):
        '''
        Insert a name into the tree.
        Will throw an assert if the name exists.
        '''
        parentNode = self.find(parentName)
        assert parentNode, "Parent node not found in tree parentName:{} nodeName:{}".format(
            parentName,
            name
            )
        node = KindNameNode(name)
        self.nameToNode[name] = node
        return super().insert(parentNode, node)
    
    def contains(self, name):
        return (name in self.nameToNode)
        
    #! this is internal, surely?
    #? and called ...getOrErrorNode
    def find(self, name):
        '''
        Find a name.
        @return A tree node, or None if not exists.
        '''
        return self.nameToNode.get(name)
    
    def narrow(self, name, otherName):
        '''
        Return the most specialised of two kinds.
        @return the most specialised kind, or None (if kinds not in same tree)
        '''
        node = self.find(name)
        otherNode = self.find(otherName)
        if(self.isParent(node, otherNode)): 
            return node.name
        elif(self.isChild(node, otherNode)): 
            return otherNode.name
        else:
            return None

    def widen(self, name, otherName):
        '''
        Return the least specialised of two kinds.
        @return the least specialised kind, or None (if kinds not in same tree)
        '''
        node = self.find(name)
        otherNode = self.find(otherName)
        if(self.isParent(node, otherNode)): 
            return otherNode.name
        elif(self.isChild(node, otherNode)): 
            return node.name
        else:
            return None
