
# As Subcomponent
# TODO: dependancies?


class PhaseList():
    def __init__(self, *phases):
        self.phases = phases
        self.idx = -1
        self.len = len(phases)

    def __iter__(self):
      return self
       
    def __next__(self):
        self.idx += 1
        if (self.idx == self.len):
            raise StopIteration
        else:
            return self.phases[self.idx] 
            
    def add(self, phase):
        self.phases.append(phase)
        self.len += 1

    def size(self):
       return self.len

    def indexOf(self, phaseName):
        r = -1
        for i, p in enumerate(self.phases):
          if p.name == phaseName:
             r = i
             break
        return r

    def contains(self, phaseName):
        for p in self.phases:
          if (p.name == phaseName):
            return True
        return False

    def take(self, phaseName):
        xl = []
        for p in self.phases:
          xl.append(p)
          if (p.name == phaseName):
            break
        return PhaseList(*xl)

    def toDisplayString(self):
        b = []
        for p in self.phases:
            b.append(p.toDisplayString())
            b.append("\n")
        return ''.join(b)
        
    def __repr__(self):
        return str(self.phases)
        
        
        
class Phase():
    '''
    Acts on a Compilation Unit (containing a tree and source data)
    Usually the action would be a transformaton of the tree, but
    it may be for data gathering, or other purposes.
    A phase should never throw errors. If it could throw an error,
    the Phase should carry a reporter attribute, to report.
    run() should be implemented, to perform the action.

    @param isInternal this phase is not a plugin addittion.
    '''
    def __init__(self,
        name,
        description,
        isInternal,
        after = None,
        placeAfter = [],
        placeBefore = []
        ):
        self.name = name
        self.description = description
        self.isInternal = isInternal

    def run(self, compilationUnit):
        pass

    def toDisplayString(self):
        return "{}: {}".format(self.name, self.description)
